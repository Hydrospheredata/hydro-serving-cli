# CLI commands

## Configure CLI

CLI looks for configs in `~/.hs-home/config.yaml` file.

You can manage clusters via `hs cluster` commands:

- `hs cluster`

Shows current selected cluster.

- `hs cluster list`

Shows all available cluster.

- `hs cluster add --name NAME --server SERVER`

Adds a new cluster.

- `hs cluster rm NAME`

Removes specified cluster.

## Upload model

- hs upload

Sends assembled tarball to the specified host.

## Profiler

CLI can send your training data to data profiler in the cluster.

- hs profiler --model-version MODELNAME:VERSION PATH_TO_FILE

## Work with Apache Kafka

- hs dev kafka --brokers ... --topic ... publish --file ...

Reads a message from specified file and sends it to the specific topic.

- hs dev kafka --brokers ... --topic ... read --tail N

Reads and displays N (10 by default) messages from the topic. [More](/docs/working_with_messages.md).

---

You can find more information about work with Apache Kafka [here](/docs/working_with_messages.md).