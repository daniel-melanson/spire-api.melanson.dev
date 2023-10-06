FROM python:3

ENV PYTHONUNBUFFERED 1
ENV PIP_ROOT_USER_ACTION=ignore
ENV APP_PATH=/app

RUN mkdir -p ${APP_PATH}
WORKDIR ${APP_PATH}

COPY Pipfile Pipfile.lock ${APP_PATH}/
RUN python -m pip install --no-cache-dir pipenv; \
    python -m pipenv requirements > requirements.txt; \
    python -m pip install -r requirements.txt;

COPY ./src $APP_PATH/src

WORKDIR $APP_PATH

RUN SECRET_KEY=dummyvalue python ./src/manage.py collectstatic --no-input
