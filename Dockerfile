FROM python:3.10-slim-bullseye as app

ENV APP_PATH=/home/app/spire-api/
RUN mkdir -p $APP_PATH

WORKDIR $APP_PATH

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN sudo apt-get install wget \
    wget -O /home/app/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz \
    tar -xzf /home/app/geckodriver.tar.gz \
    mv ./home/app/geckodriver /usr/local/bin/ \
    rm /home/app/geckodriver.tar.gz

COPY Pipfile Pipfile.lock $APP_PATH
RUN python -m pip install pipenv && pipenv install --system --deploy

COPY . $APP_PATH

WORKDIR $APP_PATH/src

RUN if [ "${DEBUG}" = "false" ]; then \
    SECRET_KEY=dummyvalue python manage.py collectstatic --no-input; \
    fi

EXPOSE 8000

CMD ["gunicorn", "-c", "python:config.gunicorn", "config.wsgi"]
