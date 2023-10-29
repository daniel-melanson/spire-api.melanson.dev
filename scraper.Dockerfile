FROM python:3

ARG firefox_ver=119.0
ARG geckodriver_ver=0.33.0
ARG build_rev=0

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    ca-certificates \
    && update-ca-certificates \
    \
    # Install tools for building
    && toolDeps=" \
    curl bzip2 \
    " \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    $toolDeps \
    \
    # Install dependencies for Firefox
    && apt-get install -y --no-install-recommends --no-install-suggests \
    `apt-cache depends firefox-esr | awk '/Depends:/{print$2}'` \
    \
    # Download and install Firefox
    && curl -fL -o /tmp/firefox.tar.bz2 \
    https://ftp.mozilla.org/pub/firefox/releases/${firefox_ver}/linux-x86_64/en-GB/firefox-${firefox_ver}.tar.bz2 \
    && tar -xjf /tmp/firefox.tar.bz2 -C /tmp/ \
    && mv /tmp/firefox /opt/firefox \
    \
    # Download and install geckodriver
    && curl -fL -o /tmp/geckodriver.tar.gz \
    https://github.com/mozilla/geckodriver/releases/download/v${geckodriver_ver}/geckodriver-v${geckodriver_ver}-linux64.tar.gz \
    && tar -xzf /tmp/geckodriver.tar.gz -C /tmp/ \
    && chmod +x /tmp/geckodriver \
    && mv /tmp/geckodriver /usr/local/bin/ \
    \
    # Cleanup unnecessary stuff
    && apt-get purge -y --auto-remove \
    -o APT::AutoRemove::RecommendsImportant=false \
    $toolDeps \
    && rm -rf /var/lib/apt/lists/* \
    /tmp/*

ENV MOZ_HEADLESS=1
ENV PYTHONUNBUFFERED 1
ENV PIP_ROOT_USER_ACTION=ignore

ARG APP_PATH=/app

RUN mkdir -p ${APP_PATH}
WORKDIR ${APP_PATH}

RUN apt-get update                             \
    && apt-get install -y --no-install-recommends \
    ca-certificates curl firefox-esr           \
    && curl -L https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz | tar xz -C /usr/local/bin \
    && apt-get purge -y ca-certificates curl

COPY Pipfile Pipfile.lock ${APP_PATH}/
RUN python -m pip install --no-cache-dir pipenv; \
    python -m pipenv requirements > requirements.txt; \
    python -m pip install --no-cache-dir -r requirements.txt;

COPY ./src $APP_PATH/src

WORKDIR $APP_PATH/src

RUN SECRET_KEY=dummyvalue python manage.py collectstatic --no-input

ENTRYPOINT [ "python" , "manage.py", "scrape", "job", "--term", "Fall", "2023", "--group", "1" ]