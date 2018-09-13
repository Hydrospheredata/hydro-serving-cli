class Config:
    def __init__(self, current_cluster=None, clusters_list=None):
        """

        :param current_cluster: currect cluster to use
        :type current_cluster: str
        :param clusters_list: all clusters
        :type clusters_list: list[dict]
        """
        if clusters_list is None:
            clusters_list = []
        if not isinstance(clusters_list, list):
            raise TypeError("clusters_list is not a list", clusters_list)
        if current_cluster is not None and not isinstance(current_cluster, str):
            raise TypeError("current_cluster is not a str", current_cluster)

        self.clusters = clusters_list
        self.current_cluster = current_cluster
