FROM python:3.11.0-slim

ENV APP_HOME=/app
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

LABEL maintainer="goswamibabin06@gmail.com"
LABEL designation="MTS"
LABEL description="Development Image for Real Estate Project"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Installing necessary packages without PostgreSQL client
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev gettext netcat-openbsd gcc && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

# Copying and installing dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

# Copying entrypoint and start scripts
COPY ./docker/local/django/entrypoint/ /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./docker/local/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY ./docker/local/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./docker/local/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower

# Setting entrypoint
ENTRYPOINT [ "/entrypoint" ]
