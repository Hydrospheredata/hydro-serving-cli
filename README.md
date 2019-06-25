# hydro-serving-cli

[![PyPI version](https://badge.fury.io/py/hs.svg)](https://badge.fury.io/py/hs)

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
install-command: "pip install requirements.txt"  # if you need to run additional command before deployment
runtime: "hydrosphere/serving-runtime-python:3.6-latest"
payload:
  - "saved_model.pb"
  - "variables/"

monitoring:
  - name: ks
    kind: KSMetricSpec
    config:
      input: client_profile_42
    with-health: true
  - name: gan
    kind: GANMetricSpec
    with-health: true
    config:
      input: feature
      application: claims-gan-app
  - name: autoencoder
    kind: AEMetricSpec
    with-health: true
    config:
      application: claims-autoencoder-app
      input: feature
      threshold: 69
  
contract:
  name: detect  # the name of signature
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

#### HostSelector

Example of a selector definition:

```yaml
kind: HostSelector
name: xeon-cpu
node_selector: "/* INSTANCE SELECTOR */"
```

Note that selector is a string that defines platform specific filter on instances.

#### Application

For the sake of simplicity CLI provides simplified structures for major use cases:

- Single model app:

```yaml
kind: Application
name: demo-app
singular:
  model: demo_model:2
```

- Pipeline app

```yaml
kind: Application
name: demo-pipeline-app

pipeline:
  - - model: claims-preprocessing:1
  - - model: claims-model:1
      weight: 80
    - model: claims-model:2
      weight: 20
```
