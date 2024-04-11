FROM python:3.11-slim-buster

ARG API_VERSION=?
ARG GUNICORN_WORKERS=1
ARG TIMEOUT_SECOND=60
ARG API_DOCS=false

ENV API_VERSION=$API_VERSION \
	GUNICORN_WORKERS=$GUNICORN_WORKERS \
	TIMEOUT_SECOND=$TIMEOUT_SECOND \
	API_DOCS=$API_DOCS

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./src /app/

RUN addgroup --gid 1000 app
RUN adduser --gecos "" --uid 1000 --ingroup app --shell /bin/sh --disabled-password app

WORKDIR /app
USER 1000:1000
EXPOSE 8000

CMD ["sh", "-c", "gunicorn \
  --workers $GUNICORN_WORKERS \
  --worker-class uvicorn.workers.UvicornWorker \
  --logger-class settings.logging.GunicornLogger \
  --bind 0.0.0.0:8000 \
  main:app"]
