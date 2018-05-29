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
    name: "image_b64"
    dtype: DT_STRING
  }
  outputs {
    name: "scores"
    dtype: DT_DOUBLE
    shape {
      dim: {
        size: -1
      }
    }
  }
  outputs {
    name: "classes"
    dtype: DT_STRING
    shape {
      dim: {
        size: -1
      }
    }
  }
}
```

Developer documentation is available [here](/docs/index.md).
