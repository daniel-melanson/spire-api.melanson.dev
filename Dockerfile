FROM python:3.10-slim-bullseye as app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_PATH=/home/django/app/

RUN mkdir -p $APP_PATH
WORKDIR $APP_PATH

RUN addgroup -S django && adduser -S django -G django

RUN chown -R django:django /home/django
USER django

COPY Pipfile Pipfile.lock $APP_PATH
RUN python -m pip install --upgrade pip; \
    python -m pip install pipenv; \
    pipenv install --deploy;

COPY ./src $APP_PATH/src

WORKDIR $APP_PATH/src

RUN if [ "${DEBUG}" = "false" ]; then \
    SECRET_KEY=dummyvalue python manage.py collectstatic --no-input; \
    fi

EXPOSE 8000

CMD ["gunicorn", "-c", "python:config.gunicorn", "config.wsgi"]