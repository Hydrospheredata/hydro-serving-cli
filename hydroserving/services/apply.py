import os
import time

import click

from hydroserving.cli.utils import resolve_model_paths
from hydroserving.constants.package import TARGET_FOLDER
from hydroserving.helpers.file import is_yaml, get_yamls
from hydroserving.helpers.upload import upload_model
from hydroserving.httpclient.api.environment import EnvironmentAPI
from hydroserving.httpclient.api.monitoring import EntryAggregationSpecification, MetricProviderSpecification, \
    METRIC_PROVIDERS, MetricConfigSpecification, HealthConfigSpecification, FilterSpecification, PARAMETRIC_PROVIDERS
from hydroserving.httpclient.errors import HSApiError
from hydroserving.models.definitions.application import Application, PipelineStage, ModelService
from hydroserving.models.definitions.environment import Environment
from hydroserving.models.definitions.model import Model
from hydroserving.models.definitions.runtime import Runtime
from hydroserving.parsers.generic import GenericParser
from hydroserving.services.client import HttpService


class ApplyService:
    def __init__(self, http_service):
        """

        Args:
            http_service (HttpService): http client to access the cluster
        """
        self.http = http_service
        self.parser = GenericParser()

    def apply(self, paths, **kwargs):
        """

        Args:
            paths (list of str):

        Returns:
            list of dict:
        """
        results = {}
        for file in paths:
            abs_file = os.path.abspath(file)
            if os.path.isdir(file):
                click.echo("Looking for resources in {} ...".format(os.path.basename(abs_file)))
                for yaml_file in sorted(get_yamls(abs_file)):
                    yaml_res = self.apply_yaml(yaml_file, **kwargs)
                    results[yaml_file] = yaml_res
            elif is_yaml(file):
                yaml_res = self.apply_yaml(abs_file, **kwargs)
                results[file] = yaml_res
            else:
                raise UnknownFile(file)
        return results

    def apply_yaml(self, path, **kwargs):
        click.echo("Applying {} ...".format(os.path.basename(path)))
        responses = []
        for doc_obj in self.parser.parse_yaml_stream(path):
            if isinstance(doc_obj, Model):
                responses.append(self.apply_model(doc_obj, path))
            elif isinstance(doc_obj, Runtime):
                responses.append(self.apply_runtime(doc_obj))
            elif isinstance(doc_obj, Application):
                responses.append(self.apply_application(doc_obj, **kwargs))
            elif isinstance(doc_obj, Environment):
                responses.append(self.apply_environment(doc_obj))
            else:
                raise UnknownResource(doc_obj)
        return responses

    def apply_model(self, model, path):
        """

        Args:
            model (Model):
            path (str): where to build

        Returns:

        """
        model_api = self.http.model_api()
        profiler_api = self.http.profiler_api()
        folder = os.path.abspath(os.path.dirname(path))
        target_path = os.path.join(folder, TARGET_FOLDER)
        model = resolve_model_paths(folder, model)
        build_status = upload_model(model_api, profiler_api, model, target_path, is_async=False)
        print(build_status)

    def apply_runtime(self, runtime):
        """

        Args:
            runtime (Runtime):

        Returns:

        """
        runtime_api = self.http.runtime_api()
        found_runtime = runtime_api.find(runtime.name, runtime.version)
        if found_runtime is not None:
            full_runtime_name = runtime.name + ':' + runtime.version
            click.echo(full_runtime_name + " already exists")
            return None
        resp = runtime_api.create(
            name=runtime.name,
            version=runtime.version,
            rtypes=[runtime.model_type]
        )
        is_finished = False
        is_failed = False
        pull_status = None
        while not (is_finished or is_failed):
            pull_status = runtime_api.get_status(resp['id'])
            is_finished = pull_status['status'] == 'Finished'
            is_failed = pull_status['status'] == 'Failed'
            time.sleep(5)  # wait until it's finished

        if is_failed:
            raise RuntimeApplyError(pull_status)

    def apply_environment(self, env):
        env_api = EnvironmentAPI(self.http.connection())
        found_env = env_api.get(env.name)
        if found_env is not None:
            click.echo(env.name + " environment already exists")
            return None
        return env_api.create(env.name, env.selector)

    def apply_application(self, app, ignore_monitoring):
        """

        Args:
            ignore_monitoring (bool):
            app (Application):

        Returns:

        """
        application_api = self.http.app_api()

        id_mapper_app = self.check_app_deps(app)
        app_request = app.to_create_request(id_mapper_app)

        id_mapper_mon = {}
        if not ignore_monitoring:
            try:
                self.http.monitoring_api().list_aggregations()
            except HSApiError:
                raise ApplicationApplyError("Monitoring service is unavailable. Consider --ignore-monitoring flag.")
            id_mapper_mon = self.check_monitoring_deps(app)

        found_app = application_api.find(app.name)
        if found_app is None:
            result = application_api.create(app_request)
        else:
            result = application_api.update(found_app['id'], app_request)

        click.echo("Server app response")
        click.echo(result)

        if not ignore_monitoring:
            app_id = result['id']
            self.configure_monitoring(app_id, app, id_mapper_mon)
        return result

    def check_monitoring_deps(self, app):
        """

        Args:
            app (Application):
        """
        stages = app.execution_graph.as_pipeline().stages
        app_api = self.http.app_api()
        id_mapper_mon = {}
        for stage in stages:
            for mon in stage.monitoring:
                mon_type_res = METRIC_PROVIDERS.get(mon.type)
                if mon_type_res is None:
                    raise ValueError("Can't find metric provider for : {}".format(mon.__dict__))
                if mon.app is None:
                    if mon_type_res in PARAMETRIC_PROVIDERS:
                        raise ValueError("Application (app) is required for metric {}".format(mon.__dict__))
                else:
                    if mon.app not in id_mapper_mon:  # check for appName -> appId
                        mon_app_result = app_api.find(mon.app)
                        print("MONAPPSEARCH")
                        print(mon.__dict__)
                        print(mon_app_result)
                        if mon_app_result is None:
                            raise ValueError("Can't find metric application for {}".format(mon.__dict__))
                        id_mapper_mon[mon.app] = mon_app_result['id']

        return id_mapper_mon

    def check_app_deps(self, app):
        stages = app.execution_graph.as_pipeline().stages

        id_mapper_app = {}
        for stage in stages:
            id_mapper_stage = self.check_stage_deps(stage)
            id_mapper_app.update(id_mapper_stage)
        return id_mapper_app

    def check_stage_deps(self, stage):
        """

        Args:
            stage (PipelineStage):
        """
        id_mapper_stage = {}
        for service in stage.services:
            id_mapper = self.check_service_deps(service)
            id_mapper_stage.update(id_mapper)
        return id_mapper_stage

    def check_service_deps(self, service):
        """

        Args:
            service (ModelService):
        """
        id_mapper = {}
        if service.environment is not None:
            env_res = self.http.env_api().get(service.environment)
            if env_res is None:
                raise ApplicationApplyError("Can't find required environment: {}".format(service.environment))
            id_mapper[service.environment] = env_res['id']

        model_name, model_version = service.model_version.split(':', maxsplit=2)
        model_res = self.http.model_api().find_version(model_name, int(model_version))
        if model_res is None:
            raise ApplicationApplyError("Can't find required model: {}".format(service.model_version))
        id_mapper[service.model_version] = model_res['id']

        runtime_name, runtime_version = service.runtime.split(':', maxsplit=2)
        runtime_res = self.http.runtime_api().find(runtime_name, runtime_version)
        if runtime_res is None:
            raise ApplicationApplyError("Can't find required runtime: {}".format(service.runtime))
        id_mapper[service.runtime] = runtime_res['id']

        return id_mapper

    def configure_monitoring(self, app_id, app, id_mapper_mon):
        """

        Args:
            id_mapper_mon (dict):
            app (Application):
            app_id (int):
        """
        mon_api = self.http.monitoring_api()
        pipeline = app.execution_graph.as_pipeline()
        results = []
        for idx, stage in enumerate(pipeline.stages):
            for mon in stage.monitoring:
                spec = MetricProviderSpecification(
                    metric_provider_class=METRIC_PROVIDERS[mon.type],
                    config=None,
                    with_health=mon.healthcheck_on,
                    health_config=None
                )
                if mon.app is not None:
                    spec.config = MetricConfigSpecification(id_mapper_mon[mon.app])
                if mon.threshold is not None:
                    spec.healthConfig = HealthConfigSpecification(mon.threshold)

                aggregation = EntryAggregationSpecification(
                    name=mon.name,
                    metric_provider_specification=spec,
                    filter=FilterSpecification(
                        source_name=mon.input,
                        stage_id="app{}stage{}".format(app_id, idx)
                    )
                )
                results.append(mon_api.create_aggregation(aggregation))
        return results


class ApplyError(RuntimeError):
    pass


class UnknownResource(ApplyError):
    def __init__(self, res):
        super().__init__("Unknown resource: {}".format(res))
        self.resource = res


class UnknownFile(ApplyError):
    def __init__(self, path):
        super().__init__(path, "File is not supported: {}".format(path))


class ModelApplyError(ApplyError):
    def __init__(self, err):
        super().__init__("Can't apply a model: {}".format(err))


class RuntimeApplyError(ApplyError):
    def __init__(self, err):
        super().__init__("Can't create a runtime: {}".format(err))


class ApplicationApplyError(ApplyError):
    def __init__(self, err):
        super().__init__("Can't create an application: {}".format(err))
