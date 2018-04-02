FROM python:2.7.14-jessie

RUN apt-get update && apt-get install -y vim && \
    pip install \
    beautifulsoup4==4.2.1 \
    jsonpickle==0.9.6 \
    pandas==0.13.1 \
    requests==2.2.1

COPY . /app

WORKDIR /app

CMD python main.py
