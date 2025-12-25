FROM python:3.12-slim-trixie

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

COPY . /app

ENV UV_NO_DEV=1

WORKDIR /app/scraper
RUN uv sync --locked

ENTRYPOINT [ "uv", "run", "scrapy", "crawl", "eu5_spider" ]