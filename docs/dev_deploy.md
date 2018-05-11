# Development deploy

CLI can simulate simple deployment with runtime and model in it.

Consider the following `serving.yaml`:
```yaml
model:
  name: "1337_model"
  type: "tensorflow"
  payload:
    - "saved_model.pb"

local_deploy:
  name: "1337_dev_server"
  runtime:
    repository: "hydrosphere/serving-runtime-tensorflow"
    tag: "1.5.0-latest"
  port: 9091
```
`model` part defines metadata for a model, as described [here](/docs/folder_structure.md).

In addition to that, there is a `local_deploy` field that defines parameters for a development deployment. 
- `runtime` field describes an image with a grpc server which can serve specified model `type`.
- The `name` field specifies unique name for a docker container. Please note that if there is already a container with such name, deploy could fail. 
- `port` field defines outside port mapping to access the container.

Basically, when you type `hs dev up`, CLI:
1. Packs a model
2. Pulls an image defined in `runtime`.
3. Creates a docker container with the image, maps ports, and creates a volume mount to the packed model.