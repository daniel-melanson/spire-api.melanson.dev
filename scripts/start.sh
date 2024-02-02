#!/bin/bash
apt install 
pip3 install pipenv
pipenv install
cd ./src/
pipenv run python manage.py collectstatic
pipenv run gunicorn -c python:config.gunicorn config.wsgi
