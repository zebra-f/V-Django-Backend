FROM python:3.10-slim-bookworm

WORKDIR /django_app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  # netcat for the entrypoint.sh script
  && apt-get install -y --no-install-recommends netcat-traditional \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY . .

RUN sed -i 's/\r$//g' ./compose/prod/django/celery/beat/entrypoint.sh
RUN chmod +x ./compose/prod/django/celery/beat/entrypoint.sh

RUN sed -i 's/\r$//g' ./compose/prod/django/celery/workers/entrypoint.sh
RUN chmod +x ./compose/prod/django/celery/workers/entrypoint.sh

RUN sed -i 's/\r$//g' ./compose/prod/django/entrypoint.sh
RUN chmod +x ./compose/prod/django/entrypoint.sh

ENTRYPOINT [ "./compose/prod/django/entrypoint.sh" ]
