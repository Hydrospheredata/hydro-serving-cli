class ProfilerService:
    def __init__(self, connection):
        self.connection = connection

    def push(self, model_version_id, filename):
        uid = self.connection.multipart_post(
            url="/profiler/batch/{}/csv".format(model_version_id),
            data={},
            files={"csv": ("filename", open(filename, "rb"), "application/octet-stream")}
        )
        return uid

    def status(self, uid):
        return self.connection.get(
            url="/profiler/batch/{}/status".format(uid)
        )
