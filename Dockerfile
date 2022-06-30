FROM python:3.10-alpine

ENV LISTEN_PORT=8000
EXPOSE 8000

WORKDIR /app

RUN pip3 install --upgrade pip

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev curl python3-dev libwebp-dev libffi-dev libressl-dev bzip2-dev xz-dev

RUN apk add --no-cache jpeg-dev zlib-dev
RUN apk add --no-cache --virtual .build-deps build-base linux-headers \
    && pip install Pillow

COPY server/requirements.txt ./server/

RUN python3 -m pip install -r ./server/requirements.txt && python3 -m pip install psycopg2-binary