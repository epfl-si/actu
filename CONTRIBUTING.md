# Contributing

## Prerequisite

- Access to the Keybase team `epfl_actu`.
- Access to the three differents openshift environments (dev | test | prod)

## Setup

Clone the repository:

```bash
git clone git@github.com:epfl-si/actu.git
```

Optionally, for better integration with IDEs:

1. Install [pyenv](https://github.com/pyenv/pyenv).
1. `make create-venv`.

## Help

```bash
make help
```

## Build / Run

```bash
make local-up     # local Django development server (automatic reloads)
```

## Tests

Lint code, unit tests and integration tests

```bash
make test
```
Coverage

```bash
make coverage        # text report
# or
make coverage-html   # html report
```

## Deployment

For deploying this application on OpenShift you need to login in th GitHub registry :

```sh
docker login ghcr.io/epfl-si/actu 
```

Run the actusible script with an environment :

```sh
./ansible/actusible [ --dev | --test | --prod ]
```
