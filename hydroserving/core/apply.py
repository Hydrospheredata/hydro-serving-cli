import os
import sys

import click

from hydroserving.cli.upload import upload_model
from hydroserving.cli.utils import resolve_model_paths
from hydroserving.config.settings import TARGET_FOLDER
from hydroserving.core.application import Application
from hydroserving.core.host_selector import HostSelector
from hydroserving.core.model.model import Model
from hydroserving.core.model.package import assemble_model
from hydroserving.core.monitoring import METRIC_PROVIDERS, PARAMETRIC_PROVIDERS, MetricProviderSpecification, \
    MetricConfigSpecification, HealthConfigSpecification, EntryAggregationSpecification, FilterSpecification
from hydroserving.core.parsers.generic import GenericParser
from hydroserving.filesystem.utils import get_yamls, is_yaml
from hydroserving.http.errors import BackendException


class ApplyService:
    def __init__(self, model_service, selector_service, application_service, profiler_service):
        self.profiler_service = profiler_service
        self.application_service = application_service
        self.selector_service = selector_service
        self.model_service = model_service
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
            if file == "-":  # special case for stdin redirect
                click.echo("Applying resource from <STDIN> ...")
                yaml_res = self.apply_yaml(file, **kwargs)
                results["<STDIN>"] = yaml_res
            elif os.path.isdir(file):
                click.echo("Looking for resources in {} ...".format(os.path.basename(abs_file)))
                for yaml_file in sorted(get_yamls(abs_file)):
                    click.echo("Applying {} ...".format(os.path.basename(yaml_file)))
                    yaml_res = self.apply_yaml(yaml_file, **kwargs)
                    results[yaml_file] = yaml_res
            elif is_yaml(file):
                click.echo("Applying {} ...".format(os.path.basename(file)))
                yaml_res = self.apply_yaml(abs_file, **kwargs)
                results[file] = yaml_res
            else:
                raise UnknownFile(file)
        return results

    def apply_yaml(self, path, **kwargs):
        responses = []
        if path == "-":
            path = os.getcwd()
            stream = self.parser.parse_yaml_file(sys.stdin)
        else:
            stream = self.parser.parse_yaml_stream(path)
        for doc_obj in stream:
            if isinstance(doc_obj, Model):
                responses.append(self.apply_model(doc_obj, path))
            elif isinstance(doc_obj, Application):
                responses.append(self.apply_application(doc_obj, **kwargs))
            elif isinstance(doc_obj, HostSelector):
                responses.append(self.apply_hostselector(doc_obj))
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
        tar = assemble_model(model, path)
        result = upload_model(self.model_service, self.profiler_service, model, tar, is_async=False)
        return result

    def apply_hostselector(self, env):
        found_env = self.selector_service.get(env.name)
        if found_env is not None:
            click.echo(env.name + " environment already exists")
            return None
        return self.selector_service.create(env.name, env.selector)

    def apply_application(self, app, ignore_monitoring):
        """

        Args:
            ignore_monitoring (bool):
            app (Application):

        Returns:

        """

        app_request = app.to_create_request()

        id_mapper_mon = {}
        if not ignore_monitoring:
            try:
                self.profiler_service.list_aggregations()
            except BackendException:
                raise ApplicationApplyError("Monitoring service is unavailable. Consider --ignore-monitoring flag.")
            id_mapper_mon = self.check_monitoring_deps(app)

        found_app = self.application_service.find(app.name)
        if found_app is None:
            result = self.application_service.create(app_request)
        else:
            result = self.application_service.update(found_app['id'], app_request)

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
                        mon_app_result = self.application_service.find(mon.app)
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
            env_res = self.selector_service.get(service.environment)
            if env_res is None:
                raise ApplicationApplyError("Can't find required environment: {}".format(service.environment))
            id_mapper[service.environment] = env_res['id']

        model_name, model_version = service.model_version.split(':', maxsplit=2)
        model_res = self.model_service.find_version(model_name, int(model_version))
        if model_res is None:
            raise ApplicationApplyError("Can't find required model: {}".format(service.model_version))
        id_mapper[service.model_version] = model_res['id']

        return id_mapper

    def configure_monitoring(self, app_id, app, id_mapper_mon):
        """

        Args:
            id_mapper_mon (dict):
            app (Application):
            app_id (int):
        """
        mon_api = self.profiler_service
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
