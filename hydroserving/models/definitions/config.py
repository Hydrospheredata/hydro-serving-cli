class Config:
    def __init__(self, clusters_dict):
        self.clusters = clusters_dict

    def list_cluster_names(self):
        return list(self.clusters.keys())

    def get_cluster_details(self, cluster_name):
        return self.clusters.get(cluster_name)