FROM python:3.7.6

WORKDIR /app

RUN pip install flask waitress

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD python server.py