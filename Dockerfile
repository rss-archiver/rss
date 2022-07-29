FROM python:3.10-slim

LABEL maintainer="Grega Vrbančič <grega.vrbancic@gmail.com"

ENV DOCKER=true

COPY requirements.txt .

COPY ./rss_archiver ./rss_archiver

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
