import sseclient


class ServableService:
    def __init__(self, conn):
        self.conn = conn

    def list(self):
        return self.conn.get("/api/v2/servable").json()

    def create(self, model_name, model_version):
        msg = {
            'modelName': model_name,
            'version': model_version
        }
        res = self.conn.post_json('/api/v2/servable', msg)
        if res.ok:
            return res.json()
        else:
            raise Exception(res.content)

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

    def logs(self, servable_name, follow):
        suffix = "?follow=true" if follow else ""
        return self.conn.sse(("/api/v2/servable/{}/logs" + suffix).format(servable_name))
