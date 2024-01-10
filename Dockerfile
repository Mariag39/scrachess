FROM python:3.9-slim-buster

RUN apt-get update && apt-get install -y firefox-esr

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY main.py .

VOLUME logs

ENTRYPOINT ["python","main.py"]

