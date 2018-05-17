# hydro-serving-cli

CLI tool for [hydro-serving](https://github.com/Hydrospheredata/hydro-serving).

## Installation

```bash
pip install hs
```

## Usage

1. Show metadata: `hs status`
2. Show human-readable contract: `hs contract`
3. Upload a model to the server: `hs upload --host $HOST --port $PORT`
4. CLI help: `hs --help`

## Model

The tool operates on folders with `serving.yaml` file in it. If there is no `serving.yaml` file, you can fill required fields with arguments, for instance:

```bash
hs --name demo_model --contract model_contract.prototxt upload
```

### serving.yaml

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

### Contract

`contract` field contains path to the ASCII serialized [ModelContract](https://github.com/Hydrospheredata/hydro-serving-protos/blob/master/src/hydro_serving_grpc/contract/model_contract.proto) message.

`contract.prototxt` example:

```hocon
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

Developer documentation is available [here](/docs/index.md).