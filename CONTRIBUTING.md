# Contributing

## Prerequisites

- Access to the Keybase team `epfl_actu`.
- Access to the three different OpenShift environments (dev | test | prod)

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

## Clone Database

```bash
make local-clone      # Clones production database into the local environment.
# or
make dev-clone        # Clones production database to the dev environment.
# or
make staging-clone    # Clones production database to the staging environment.
```

## Release

1. Update the [CHANGELOG.md](CHANGELOG.md).
1. Bump `app_image_tag` to the new version in all three Ansible inventory files:
   - `ansible/inventory/dev.yml`
   - `ansible/inventory/test.yml`
   - `ansible/inventory/prod.yml`
1. Push and merge to `main` branch.
1. Create and push a new tag:  
   `git tag -a <version_number> -m "Actu - <version_number>"`  
   `git push origin main --tags`
1. Wait for the new image to be built.

## Deploy

Run the actusible script with an environment :

```sh
./ansible/actusible [ --dev | --test | --prod ]
```
