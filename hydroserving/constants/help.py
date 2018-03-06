from hydroserving.settings import CONTEXT_SETTINGS, AUTO_ENVVAR_PREFIX

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

# LOCAL DEPLOYMENT HELP

LOCAL_HELP = """
This command works with local deployment of a model with specified runtime.
"""

START_HELP = """
Creates the runtime with current model.
"""

STOP_HELP = """
Deletes the runtime with current model.
"""

KAFKA_HELP = """
kafka read/write utils
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