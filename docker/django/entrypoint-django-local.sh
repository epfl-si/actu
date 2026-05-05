#!/usr/bin/env bash

python src/manage.py migrate
python -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:5678 src/manage.py runserver 0.0.0.0:8000
