#!/bin/bash
cd ./src
python3.11 manage.py collectstatic
python3.11 -m gunicorn -c python:config.gunicorn config.wsgi
