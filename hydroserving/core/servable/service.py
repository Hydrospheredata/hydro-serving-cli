class ServableService:
    def __init__(self, conn):
        self.conn = conn

    def list(self):
        return self.conn.get("/api/v2/servable").json()

    def create(self, model_name, model_version):
        pass

    def delete(self, servable_name):
        res = self.conn.delete("/api/v2/servable/{}".format(servable_name))
        if res.ok:
            return res.json()
        else:
            return None

    def get(self, servable_name):
        res = self.conn.get("/api/v2/servable/{}".format(servable_name))
        if res.ok:
            return res.json()
        else:
            return None