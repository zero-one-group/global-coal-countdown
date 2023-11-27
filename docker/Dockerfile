# NOTE: Python Dependencies
FROM python:3.11-slim as dependencies

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

copy requirements.txt .
RUN pip install -r requirements.txt

# NOTE: Runner base on nikolaik/docker-python-nodejs
FROM python:3.11-slim as runner

RUN apt-get update && apt-get install -y --no-install-recommends\
    build-essential curl libglu1 libxi6 libgconf-2-4 libpng-dev wget git diffutils jq wget gnupg2

RUN echo "deb https://deb.nodesource.com/node_16.x bookworm main" > /etc/apt/sources.list.d/nodesource.list && \
    wget -qO- https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
    echo "deb https://dl.yarnpkg.com/debian/ stable main" > /etc/apt/sources.list.d/yarn.list && \
    wget -qO- https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
    apt-get update && \
    apt-get install -yqq nodejs=$(apt-cache show nodejs|grep Version|grep nodesource|cut -c 10-) yarn && \
    apt-mark hold nodejs && \
    pip install -U pip && pip install pipenv && \
    rm -rf /var/lib/apt/lists/*

RUN npm install -g firebase-tools

COPY --from=dependencies /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
