# Model structure

To successfully deploy a model we need some metadata.
Depending on the model, it may or may not contain it.

Manager will try to infer a metadata, if its not present, but may be not as accurate.

Metadata is described if following formats:

## serving.yaml

`serving.yaml` file:

```yaml
model:
  name: "example_model"
  type: "tensorflow"
  contract: "contract.prototxt"
  payload:
    - "saved_model.pb"
    - "variables/"
```

The `model` key indicates that you are describing current model.

1. `name` field specifies a unique name of a model.
2. `type` field indicates which runtimes it should be served with. e.g. `spark:2.2`, `tensorflow`, `python:3.6`.
3. `contract` field specifies path, where CLI can find a contract file.
4. `payload` field contains list of paths, which would be sent to the manager as model itself.

## Contract file

`contract` field contains path to the ASCII serialized [ModelContract](https://github.com/Hydrospheredata/hydro-serving-protos/blob/master/src/hydro_serving_grpc/contract/model_contract.proto) message.

`contract.prototxt` example:

```protobuf
signatures {
  signature_name: "detect"
  inputs {
    field_name: "image_b64"
    info {
      dtype: DT_STRING
    }
  }
  outputs {
    field_name: "scores"
    info {
      dtype: DT_DOUBLE
      tensor_shape: {
        dim: {
            size: -1
        }
      }
    }
  }
  outputs {
    field_name: "classes"
    info {
      dtype: DT_STRING
      tensor_shape: {
        dim: {
            size: -1
        }
      }
    }
  }
}
```
