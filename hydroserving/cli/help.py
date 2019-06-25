from hydroserving.cli.context import CONTEXT_SETTINGS, AUTO_ENVVAR_PREFIX

VERBOSE_HELP = """
Enable debug output.
"""

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

# HostSelector help
HOST_SELECTOR_HELP = """
Working with host selectors
"""

HOST_SELECTOR_ADD_HELP = """
Create new host selector
"""

HOST_SELECTOR_LIST_HELP = """
List all host selectors
"""

HOST_SELECTOR_RM_HELP = """
Delete an existing host selector
"""

HOST_SELECTOR_NODE_SELECTOR_HELP = """
Kubernetes specific nodeSelector ("key:value")
"""