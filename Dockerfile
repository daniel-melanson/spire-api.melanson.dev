FROM python:3.10-slim-bullseye as app

ENV APP_PATH=/home/app/spire-api/
RUN mkdir -p $APP_PATH

WORKDIR $APP_PATH

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update; \
    apt-get install -y --no-install-recommends wget tar; \
    wget -O geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz; \
    tar -xf geckodriver.tar.gz; \
    mv geckodriver /usr/local/bin/; \
    rm geckodriver.tar.gz;

COPY Pipfile Pipfile.lock $APP_PATH
RUN python -m pip install --upgrade pip; \
    python -m pip install pipenv; \
    pipenv install --system --deploy;

COPY . $APP_PATH

WORKDIR $APP_PATH/src

RUN if [ "${DEBUG}" = "false" ]; then \
    SECRET_KEY=dummyvalue python manage.py collectstatic --no-input; \
    fi

EXPOSE 8000

CMD ["gunicorn", "-c", "python:config.gunicorn", "config.wsgi"]
