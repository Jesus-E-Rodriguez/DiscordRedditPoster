FROM python:3.10-alpine

RUN apk update && apk upgrade && \
    apk add --no-cache bash

WORKDIR /app
COPY requirements/base.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]