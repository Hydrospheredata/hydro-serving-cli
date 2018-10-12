class ProfilerAPI:
    def __init__(self, connection):
        self.connection = connection

    def push(self, model_version_id, filename, create_encoder_callback=None):
        uid = self.connection.multipart_post(
            url="/profiler/batch/{}/csv".format(model_version_id),
            data={},
            files={"csv": ("filename", open(filename, "rb"), "application/octet-stream")},
            create_encoder_callback=create_encoder_callback
        )
        return uid

    def status(self, uid):
        return self.connection.get(
            url="/profiler/batch/{}/status".format(uid)
        )
