# pull official base image
FROM python:3.8.1-buster

# set work directory
WORKDIR /usr/src/autocusto

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/autocusto/requirements.txt
RUN pip install -r requirements.txt

# install pdftk
RUN apt-get update
RUN apt-get upgrade
RUN apt-get install -y pdftk


# copy project
COPY . /usr/src/autocusto


