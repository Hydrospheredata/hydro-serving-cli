import os

HOME_PATH = "~/.hs"
HOME_PATH_EXPANDED = os.path.expanduser(HOME_PATH)
CONFIG_FILE = "config.yaml"
CONFIG_PATH = os.path.join(HOME_PATH_EXPANDED, CONFIG_FILE)

TARGET_FOLDER = ".hs"

SEGMENT_DIVIDER = "================================"

CLUSTER_COMPONENTS_INFO = [
    "/api/buildinfo",
    "/gateway/buildinfo",
    "/monitoring/buildinfo",
    "rootcause/buildinfo",
    "stat/buildinfo",
    "visualization/buildinfo",
]