python3.11 ./src/manage.py collectstatic
python3.11 -m gunicorn -c python:src.config.gunicorn src.config.wsgi
