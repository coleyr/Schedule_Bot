FROM ubuntu

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /code

COPY . .

CMD ["flask", "run"]