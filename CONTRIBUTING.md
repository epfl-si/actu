# Contributing

## Prerequisite

- Access to the Keybase team `epfl_actu`.

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
