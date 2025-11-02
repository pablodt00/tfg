FROM python:3.10-slim

WORKDIR /srv

COPY /requirements/requirements-devel.txt .
RUN pip install -r requirements-devel.txt

COPY /src .

CMD ["python"]
