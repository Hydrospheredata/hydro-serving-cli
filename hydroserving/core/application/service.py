import logging
from hydroserving.core.monitoring import METRIC_PROVIDERS, PARAMETRIC_PROVIDERS, MetricProviderSpecification, \
    MetricConfigSpecification, HealthConfigSpecification, EntryAggregationSpecification, FilterSpecification
from hydroserving.http.errors import BackendException


class ApplicationService:
    def __init__(self, connection, model_service, monitoring_service):
        self.connection = connection
        self.model_service = model_service
        self.monitoring_service = monitoring_service

    def apply(self, app, ignore_monitoring=True):
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
                self.monitoring_service.list_aggregations()
            except BackendException:
                raise ValueError("Monitoring service is unavailable. Consider --ignore-monitoring flag.")
            id_mapper_mon = self.check_monitoring_deps(app)

        found_app = self.find(app.name)
        if found_app is None:
            result = self.create(app_request)
        else:
            result = self.update(found_app['id'], app_request)

        logging.debug("Server app response")
        logging.debug(result)

        if not ignore_monitoring:
            app_id = result['id']
            self.configure_monitoring(app_id, app, id_mapper_mon)
        return result

    def create(self, application):
        """

        Args:
            application (CreateApplicationRequest):

        Returns:
            dict
        """
        return self.connection.post("/api/v2/application", application.__dict__)

    def update(self, id, application):
        update_req = application.__dict__
        update_req['id'] = int(id)
        return self.connection.put('/api/v2/application', update_req)

    def serve(self, app_name, signature_name, data):
        """

        Args:
            data (dict):
            signature_name (str):
            app_name (str):

        Returns:
            dict:
        """
        return self.connection.post(
            "/api/v2/application/serve/{0}/{1}".format(app_name, signature_name),
            data
        )

    def list(self):
        """

        Returns:
            list of dict:
        """
        return self.connection.get("/api/v2/application")

    def find(self, app_name):
        """

        Args:
            app_name (str):
        """
        for app in self.list():
            if app['name'] == app_name:
                return app
        return None

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
                        mon_app_result = self.find(mon.app)
                        logging.debug("MONAPPSEARCH")
                        logging.debug(mon.__dict__)
                        logging.debug(mon_app_result)
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
        model_name, model_version = service.model_version.split(':', maxsplit=2)
        model_res = self.model_service.find_version(model_name, int(model_version))
        if model_res is None:
            raise ValueError("Can't find required model: {}".format(service.model_version))
        id_mapper[service.model_version] = model_res['id']

        return id_mapper

    def configure_monitoring(self, app_id, app, id_mapper_mon):
        """

        Args:
            id_mapper_mon (dict):
            app (Application):
            app_id (int):
        """
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
                results.append(self.monitoring_service.create_aggregation(aggregation))
        return results
