FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED 1

ENV PYTHONUNBUFFERED 1
RUN mkdir -p /opt/services/spire-api/

COPY . /opt/services/spire-api/
WORKDIR /opt/services/spire-api
RUN pip install pipenv && pipenv install --system

RUN python manage.py collectstatic --no-input

EXPOSE 8000
CMD ["gunicorn", "-c", "config/gunicorn/conf.py", "--bind", ":8000", "--chdir", "hello", "hello.wsgi:application"]

