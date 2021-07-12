from hs.entities.cluster_config import ClusterConfig
import pytest

@pytest.mark.xfail
def test_config_read_failed():
    d = {
        'aaaaa': 'failed'
    }
    ClusterConfig.deserialize(d)

def test_config_read_successful():
    d = {
        "clusters": [
            {
                "cluster": {
                    "server": "http://localhost:9090"
                },
                "name": "local"
            }
        ],
        "current_cluster": "local",
    }
    res = ClusterConfig.parse_obj(d)
    print(res)

def test_config_write_successful():
    d = {
        "clusters": [
            {
                "cluster": {
                    "server": "http://localhost:9090"
                },
                "name": "local"
            }
        ],
        "current-cluster": "local",
    }
    res = ClusterConfig.parse_obj(d)
    dict = res.dict(by_alias=True)
    print(d, dict, sep="\n")
    assert d == dict