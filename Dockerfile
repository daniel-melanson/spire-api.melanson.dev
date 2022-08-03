FROM python:3.10-slim-bullseye as app

ENV APP_PATH=/home/app/spire-api/
RUN mkdir -p $APP_PATH

WORKDIR $APP_PATH

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY Pipfile Pipfile.lock $APP_PATH
RUN python -m pip install pipenv && pipenv install --system --deploy

COPY . $APP_PATH

WORKDIR $APP_PATH/src

RUN if [ "${DEBUG}" = "false" ]; then \
    SECRET_KEY=dummyvalue python manage.py collectstatic --no-input; \
    fi

EXPOSE 8000

CMD ["gunicorn", "-c", "python:config.gunicorn", "config.wsgi"]
