# hydro-serving-cli

CLI tool for [hydro-serving](https://github.com/Hydrospheredata/hydro-serving).

## Installation

```bash
pip install hs
```

## Usage

### hs cluster

Since 0.1.0 the tool uses configurable endpoints called cluster:
They can be managed with:
- `hs cluster` - shows default cluster
- `hs cluster add --name local --server http://localhost` - creates entry with name `local`
and address `http://localhost`.
- `hs cluster use local` - uses the previously created `local` cluster as default
- `hs cluster rm local` - removes `local` cluster entry

The default cluster is used as endpoint for all API calls made from the CLI tool.

### hs upload

When you use `hs upload`, the tool looks for `serving.yaml` file in current dir.
`serving.yaml` defines model metadata and contract

```yaml
kind: Model
name: "example_model"
model-type: "tensorflow:1.3.0"
payload:
  - "saved_model.pb"
  - "variables/"
  
contract:
  detect:  # the name of signature
    inputs:  # signature input fields
      image_b64:
        type: string
    outputs:  # signature output fields
      scores:
        shape: [-1]
        type: double
      classes:
        shape: [-1]
        type: string
```

### hs apply

The command takes `-f` path parameter to yaml file or directory containing yaml files.
Then, it will read the yaml documents and apply them sequentially.

These files can contain definition of a resource defined below:

#### Model

The model definition is the same as in `serving.yaml` file.

#### Runtime

Example of runtime definition:

```yaml
kind: Runtime
name: hydrosphere/serving-runtime-tensorflow
version: 1.7.0-latest
model-type: tensorflow:1.7.0
```

#### Environment

Example of environment definition:

```yaml
kind: Environment
name: xeon-cpu
selector: "/* INSTANCE SELECTOR */"
```

Note that selector is a string that defines platform specific filter on instances.

#### Application

For the sake of simplicity CLI provides simplified structures for major use cases:

- Single model app:

```yaml
kind: Application
name: demo-app
singular:
  monitoring:
    - name: ks
      input: user_profile
      type: Kolmogorov-Smirnov
      healthcheck:
        enabled: true
  model: demo_model:2
  runtime: hydrosphere/serving-runtime-python:3.6-latest
```

- Pipeline app

```yaml
kind: Application
name: demo-pipeline-app

pipeline:
  - signature: normalize
    model: demo-preprocessing:1
    runtime: hydrosphere/serving-runtime-python:3.6-latest
    environment: cpu
  - signature: predict
    monitoring:
      - name: ks
        input: feature_42
        type: Kolmogorov-Smirnov
        healthcheck:
          enabled: true
    modelservices:
      - model: demo-model:1
        runtime: hydrosphere/serving-runtime-python:3.6-latest
        environment: xeon
        weight: 80
      - model: demo-model:2
        runtime: hydrosphere/serving-runtime-python:3.6-latest
        weight: 20
```
