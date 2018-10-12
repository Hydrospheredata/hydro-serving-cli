from hydroserving.constants.click import CONTEXT_SETTINGS, AUTO_ENVVAR_PREFIX

CONTRACT_HELP = """
Show validated model contract.
"""

ASSEMBLE_HELP = """
Assemble tar.gz archive from your payload.
"""

PACK_HELP = """
Prepare payload and validate contract.
"""

STATUS_HELP = """
Return the status of current folder.
"""

# KAFKA HELP
KAFKA_HELP = """
kafka read/write utils
"""

KAFKA_ADVERTISED_ADDR_HELP = """
KAFKA_ADVERTISED_ADDR
"""

KAFKA_TOPIC_HELP = """
KAFKA_TOPIC
"""

KAFKA_PREDICT_REQUEST_FILE_HELP = """
KAFKA_PREDICT_REQUEST_FILE
"""

KAFKA_TAIL_HELP = """
KAFKA_TAIL
"""

PUBLISH_TO_KAFKA_HELP = """
Publishes predict request to kafka.
"""

READ_FROM_KAFKA_HELP = """
Reads messages from kafka
"""

# UPLOAD HELP
UPLOAD_HELP = """
Upload current model to the manager.
"""

UPLOAD_HOST_HELP = """
Hydroserving manager host. Can be set with {}_HOST environment variable.
""".format(CONTEXT_SETTINGS[AUTO_ENVVAR_PREFIX])

UPLOAD_PORT_HELP = """
Hydroserving manager port. Can be set with {}_PORT environment variable.
""".format(CONTEXT_SETTINGS[AUTO_ENVVAR_PREFIX])

UPLOAD_SOURCE_HELP = """
Hydroserving model source. 
Define if you want to specify where to put model.
If you update an existing model, this parameter is ignored.
"""

APPLICATION_HELP = """
Application API.
"""

# PROFILER HELP
PROFILE_HELP = """
Working with data profiles
"""

PROFILE_PUSH_HELP = """
Upload training dataset to compute its profiles
"""

PROFILE_MODEL_VERSION_HELP = """
Model version in "model:version" format
"""

PROFILE_FILENAME_HELP = """
Path to csv file with data
"""

# CLUSTER HELP
CLUSTER_HELP = """
Utilities to manage hs clusters
"""

CLUSTER_USE_HELP = """
Set specified cluster as default
"""

CLUSTER_ADD_HELP = """
Add cluster
"""

CLUSTER_RM_HELP = """
Remove cluster
"""

CLUSTER_LIST_HELP = """
Show all clusters
"""

CLUSTER_DEFAULT_HELP = """
Show default cluster
"""

APPLY_HELP = """
Apply resources from files or directory.
"""

# DEV HELP
DEV_HELP = """
Developer tools
"""
