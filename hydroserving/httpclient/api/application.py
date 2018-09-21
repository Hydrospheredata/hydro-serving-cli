class ModelServiceRequest:
    def __init__(self, model_version_id, runtime_id, environment_id, signature_name, weight):
        """

        Args:
            weight (int or None): from 100 to 0
            signature_name (str or None):
            environment_id (int or None):
            runtime_id (int):
            model_version_id (int):
        """
        self.weight = weight
        self.signatureName = signature_name
        self.environmentId = environment_id
        self.runtimeId = runtime_id
        self.modelVersionId = model_version_id


class ApplicationStageRequest:
    def __init__(self, services):
        """

        Args:
            services (list of ModelServiceRequest):
        """
        self.services = services


class ApplicationExecutionGraphRequest:
    def __init__(self, stages):
        """

        Args:
            stages (list of ApplicationStageRequest):
        """
        self.stages = stages


class KafkaStreamingParams:
    def __init__(self, source_topic, destination_topic):
        """

        Args:
            destination_topic (str): 
            source_topic (str): 
        """
        self.destinationTopic = destination_topic
        self.sourceTopic = source_topic


class CreateApplicationRequest:
    def __init__(self, name, execution_graph, kafka_streaming):
        """

        Args:
            kafka_streaming (list of KafkaStreamingParams):
            execution_graph (ApplicationExecutionGraphRequest): 
            name (str): 
        """
        self.kafkaStreaming = kafka_streaming
        self.executionGraph = execution_graph
        self.name = name


class ApplicationAPI:
    def __init__(self, connection):
        self.connection = connection

    def create(self, application):
        """

        Args:
            application (CreateApplicationRequest):

        Returns:
            dict
        """
        return self.connection.post("/api/v1/applications", application.__dict__)

    def update(self, id, application):
        update_req = application.__dict__
        update_req['id'] = int(id)
        return self.connection.put('/api/v1/applications', update_req)

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
            "/api/v1/applications/serve/{0}/{1}".format(app_name, signature_name),
            data
        )

    def list(self):
        """

        Returns:
            list of dict:
        """
        return self.connection.get("/api/v1/applications")

    def find(self, app_name):
        """

        Args:
            app_name (str):
        """
        for app in self.list():
            if app['name'] == app_name:
                return app
        return None