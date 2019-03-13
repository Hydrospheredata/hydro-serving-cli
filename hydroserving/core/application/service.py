import logging

from hydroserving.core.application.entities import model_variant


class ApplicationService:
    def __init__(self, connection, model_service):
        self.connection = connection
        self.model_service = model_service

    def apply(self, app):
        """
        Args:
            app (ApplicationDef):

        Returns:

        """
        logging.debug("Applying Application %s", app)
        app_request = self._convert_mv_names(app)

        found_app = self.find(app_request['name'])
        if found_app is None:
            logging.debug("Creating application: %s", app_request)
            result = self.create(app_request)
        else:
            app_request['id'] = found_app['id']
            logging.debug("Updating application: %s", app_request)
            result = self.update(app_request)

        logging.debug("Server app response")
        logging.debug(result)

        return result

    def _convert_mv_names(self, request):
        graph = request.execution_graph
        stages = []
        for stage in graph['stages']:
            variants = []
            for variant in stage['modelVariants']:
                names = variant["modelVersion"].split(":")
                if len(names) != 2:
                    raise ValueError("Invalid modelVersion name: {}".format(variant["modelVersion"]))
                mv = self.model_service.find_version(names[0], int(names[1]))
                if not mv:
                    raise ValueError("Can't find model version {}".format(variant))
                r = model_variant(mv['id'], variant["weight"])
                variants.append(r)
            stages.append({
                "modelVariants": variants
            })
        result = {
            "executionGraph": {
                "stages": stages
            },
            "name": request.name,
            "kafkaStreaming": request.kafka_streaming
        }
        return result

    def create(self, application):
        return self.connection.post_json("/api/v2/application", application).json()

    def update(self, application):
        return self.connection.put('/api/v2/application', application).json()

    def list(self):
        """

        Returns:
            list of dict:
        """
        return self.connection.get("/api/v2/application").json()

    def find(self, app_name):
        """

        Args:
            app_name (str):
        """
        resp = self.connection.get("/api/v2/application/{}".format(app_name))
        if resp.ok:
            return resp.json()
        return None
