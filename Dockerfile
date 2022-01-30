FROM ubuntu

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && pip install -r requirements.txt

WORKDIR /code

COPY ./webexteamsbot ./app
