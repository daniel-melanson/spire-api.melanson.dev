FROM python:3

# Install redis
RUN apt-get update && \
  apt-get install --no-install-recommends -y lsb-release curl software-properties-common gpg gpg-agent && \
  curl -fsSL https://packages.redis.io/gpg | gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg && \
  echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/redis.list && \
  apt-get update && \
  apt-get install --no-install-recommends -y redis && \
  rm -rf /var/lib/apt/lists/*

RUN redis-server /etc/redis/redis.conf --daemonize yes
ENV REDIS_URL=redis://localhost:6379

ENV APP_PATH=/app
RUN mkdir -p ${APP_PATH}
WORKDIR ${APP_PATH}

COPY Pipfile Pipfile.lock ${APP_PATH}/
RUN python -m pip install --no-cache-dir pipenv && \
  python -m pipenv requirements > requirements.txt && \
  python -m pip install --no-cache-dir -r requirements.txt

COPY ./src $APP_PATH/src

WORKDIR $APP_PATH/src

RUN SECRET_KEY=dummy python manage.py collectstatic --no-input

EXPOSE 8000

CMD [ "python", "-m", "gunicorn", "-c", "python:config.gunicorn", "config.wsgi" ]
