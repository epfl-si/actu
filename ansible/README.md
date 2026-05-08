# Configuration as Code

This is an ansible playbook to deploy this application on OpenShift

## Requierments
Before running the actusible script, you need :
- Access to 'actu' team keybase
- Access to the three differents openshift environments (dev | test | prod)
- To run `docker login` to access the app image. 

Run this command to login in the GitHub registry :

```sh
docker login ghcr.io/epfl-si/actu 
```
