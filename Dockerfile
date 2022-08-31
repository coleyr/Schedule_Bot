FROM python:3.9

COPY requirements.txt requirements.txt
RUN apt-get update  
RUN pip install -r requirements.txt

WORKDIR /usr/src/app

COPY ./app /usr/src/app
