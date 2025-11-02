FROM python:3.10-slim

WORKDIR /srv

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/requirements-devel.txt ./requirements-devel.txt

RUN pip install --no-cache-dir -r requirements-devel.txt

COPY src/ ./src/

WORKDIR /srv

CMD ["python"]