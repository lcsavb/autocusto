# pull official base image
FROM debian:buster

# set work directory
WORKDIR /usr/src/autocusto

# install dependencies
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y
RUN apt-get install postgresql -y
RUN apt-get install postgresql-server-dev-all -y
RUN apt-get install libpq-dev -y
RUN pip3 install --upgrade pip
COPY ./requirements.txt /usr/src/autocusto/requirements.txt
RUN pip3 install -r requirements.txt

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install pdftk
RUN apt-get install -y pdftk


# copy project
COPY . /usr/src/autocusto

# create database
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate

# prepare static files for deployment
RUN  python3 manage.py collectstatic --no-input --clear
