#!/bin/bash
pip3 install pipenv
pipenv install
cd ./src
pipenv run python ./src/manage.py collectstatic
pipenv run gunicorn -c python:src.config.gunicorn src.config.wsgi
