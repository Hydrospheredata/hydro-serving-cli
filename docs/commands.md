# CLI commands

## Basic commands

- hs status

Shows parsed metadata.

- hs contract

Shows ASCII encoded model contract.

- hs upload --host ... --port ...

Sends assembled tarball to the specified host.

## Dev deploy

- hs dev deploy up

Creates a docker runtime with a model.

- hs dev deploy down

Removes previously started docker runtime.

 ---

You can find more information about development deployment of a model [here](/docs/dev_deploy.md).

## Work with Apache Kafka

- hs dev kafka --brokers ... --topic ... publish --file ...

Reads a message from specified file and sends it to the specific topic.

- hs dev kafka --brokers ... --topic ... read --tail N

Reads and displays N (10 by default) messages from the topic. [More](/docs/working_with_messages.md).

---

You can find more information about work with Apache Kafka [here](/docs/working_with_messages.md).