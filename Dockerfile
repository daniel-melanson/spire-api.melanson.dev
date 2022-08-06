FROM python:3.10-slim-bullseye as app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_PATH=/home/django/app/

RUN mkdir -p $APP_PATH
WORKDIR $APP_PATH

RUN addgroup -S django; \
    adduser --system django --ingroup django;

RUN apt-get update; \
    apt-get install -y --no-install-recommends wget tar; \
    wget -O geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz; \
    tar -xf geckodriver.tar.gz; \
    mv geckodriver /usr/local/bin/; \
    rm geckodriver.tar.gz;

RUN chown -R django:django /home/django
USER django

COPY Pipfile Pipfile.lock $APP_PATH
RUN python -m pip install --upgrade pip; \
    python -m pip install pipenv; \
    pipenv install --deploy;

COPY ./src $APP_PATH/src

WORKDIR $APP_PATH/src

RUN SECRET_KEY=dummyvalue python manage.py collectstatic --no-input

EXPOSE 8000

CMD ["gunicorn", "-c", "python:config.gunicorn", "config.wsgi"]
