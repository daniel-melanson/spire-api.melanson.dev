FROM python:3

ENV PYTHONUNBUFFERED 1
ENV PIP_ROOT_USER_ACTION=ignore
ENV APP_PATH=/app

RUN mkdir -p ${APP_PATH}
WORKDIR ${APP_PATH}

RUN apt-get update -y \
    && apt-get install --no-install-recommends --no-install-suggests -y tzdata ca-certificates bzip2 curl wget libc-dev libxt6 \
    && apt-get install --no-install-recommends --no-install-suggests -y `apt-cache depends firefox-esr | awk '/Depends:/{print$2}'` \
    && update-ca-certificates \
    # Cleanup unnecessary stuff
    && apt-get purge -y --auto-remove \
    -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/* /tmp/*

# install geckodriver

RUN wget --process=dot:giga https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz && \
    tar -zxf geckodriver-v0.33.0-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm geckodriver-v0.33.0-linux64.tar.gz

# install firefox

RUN FIREFOX_SETUP=firefox-setup.tar.bz2 && \
    wget --process=dot:giga -O $FIREFOX_SETUP "https://download.mozilla.org/?product=firefox-95.0.1&os=linux64" && \
    tar xjf $FIREFOX_SETUP -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm $FIREFOX_SETUP

COPY Pipfile Pipfile.lock ${APP_PATH}/
RUN python -m pip install --no-cache-dir pipenv; \
    python -m pipenv requirements > requirements.txt; \
    python -m pip install --no-cache-dir -r requirements.txt;

COPY ./src $APP_PATH/src

WORKDIR $APP_PATH/src

RUN SECRET_KEY=dummyvalue python manage.py collectstatic --no-input

ENTRYPOINT [ "python" , "manage.py", "scrape" ]