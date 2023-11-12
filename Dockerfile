FROM python:3.10.6-slim-buster

WORKDIR /usr/share/my_cookbook/cookbook

COPY requirements.txt /usr/share/my_cookbook/requirements.txt
RUN pip install -r /usr/share/my_cookbook/requirements.txt

COPY cookbook /usr/share/my_cookbook/cookbook
COPY bot /usr/share/my_cookbook/bot

ENV PYTHONPATH="${PYTHONPATH}:/usr/share/my_cookbook/cookbook"
