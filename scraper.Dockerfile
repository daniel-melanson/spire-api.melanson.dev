FROM python:3

ENV PYTHONUNBUFFERED 1
ENV PIP_ROOT_USER_ACTION=ignore
ENV APP_PATH=/app

RUN mkdir -p ${APP_PATH}
WORKDIR ${APP_PATH}

ENV GECKODRIVER_VERSION v0.33.0
RUN wget --progress=dot:giga https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz; \
    tar -xvzf geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz; \
    rm geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz; \
    mv geckodriver /usr/local/bin/;

COPY Pipfile Pipfile.lock ${APP_PATH}/
RUN python -m pip install --no-cache-dir pipenv; \
    python -m pipenv requirements > requirements.txt; \
    python -m pip install --no-cache-dir -r requirements.txt;

COPY ./src $APP_PATH/src

WORKDIR $APP_PATH/src

RUN SECRET_KEY=dummyvalue python manage.py collectstatic --no-input

ENTRYPOINT [ "python" , "manage.py", "scrape"]