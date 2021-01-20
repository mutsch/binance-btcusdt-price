MS_CONFIG_PREFIX = "microservice_"
DB_CONFIG_PREFIX = "db_"

MICROSERVICE_CRAWLER = "microservice_crawler"
MICROSERVICE_STORER = "microservice_storer"
MICROSERVICE_CONVERTER = "microservice_converter"

DB_INFLUX = "db_influx"

CONFIG_CLUSTER_HOST_FIELD = "cluster_host"
CONFIG_CLUSTER_PORT_FIELD = "cluster_port"
CONFIG_NODE_PORT_FIELD = "node_port"


def load_configuration(cluster_name: str, configuration: dict):
    config = {}
    for name, subconf in configuration.items():
        if name.startswith(MS_CONFIG_PREFIX):
            config[name] = Configuration(subconf[CONFIG_CLUSTER_HOST_FIELD],
                                         subconf[CONFIG_CLUSTER_PORT_FIELD],
                                         subconf[CONFIG_NODE_PORT_FIELD])
        elif name.startswith(DB_CONFIG_PREFIX):
            config[name] = Configuration(subconf[CONFIG_CLUSTER_HOST_FIELD],
                                         subconf[CONFIG_CLUSTER_PORT_FIELD])
    for name, subconf in config.items():
        if name != cluster_name:
            config[cluster_name].add_cluster(name, subconf)
    return config[cluster_name]


class Configuration:
    def __init__(self, cluster_host: str, cluster_port: str, node_port: str = ""):
        self.cluster_host = cluster_host
        self.cluster_port = cluster_port
        self.node_port = node_port
        self.clusters = {}

    def add_cluster(self, name: str, configuration):
        self.clusters[name] = configuration
