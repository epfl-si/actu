#!/usr/bin/env bash

cp -r static/* /public/static/
python src/manage.py migrate
exec gunicorn -c /app/src/gunicorn.conf.py configs.wsgi:application
