# hydro-serving-cli
CLI tool for [hydro-serving](https://github.com/Hydrospheredata/hydro-serving).

## serving.yaml
The tool operates on folders with `serving.yaml` file in it.
It defines various metadata and a contract for a model.

`serving.yaml` example:
```yaml
model:
  name: "example_model"
  type: "tensorflow"
  contract: "contract.prototxt"
  payload:
    - "saved_model.pb"
    - "variables/"
```

`contract` field contains path to the ASCII serialized [ModelContract](https://github.com/Hydrospheredata/hydro-serving-protos/blob/master/src/hydro_serving_grpc/contract/model_contract.proto) message.

`contract.prototxt` example:
```
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
