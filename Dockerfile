FROM python:3.11-slim

WORKDIR /workspace
COPY requirements.txt .

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl git

RUN pip install -U pip \
    && pip install --no-cache-dir --upgrade -r requirements.txt
