FROM debian:buster

ARG MICROSERVICE

RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes python3-venv gcc libpython3-dev procps

COPY ./microservices/${MICROSERVICE}/requirements.txt /app/

WORKDIR /app

RUN python3 -m venv venv && \
    ./venv/bin/pip install --upgrade pip

RUN ./venv/bin/pip install -r requirements.txt

COPY ./microservices/${MICROSERVICE}/${MICROSERVICE} /app/${MICROSERVICE}
COPY ./common /app/common
COPY ./clusters_dev.toml /app/

ENV MICROSERVICE=$MICROSERVICE

CMD ./venv/bin/python -m ${MICROSERVICE} --config clusters_dev.toml
