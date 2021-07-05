from hs.metadata_collectors.hs import HSInfo

def test_hs_collector():
    meta = HSInfo.collect()
    print(meta)