FROM ubuntu:20.04
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /usr/app
WORKDIR /usr/app
RUN apt-get update && apt-get install -y --no-install-recommends software-properties-common\
    curl postgresql-client
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update && apt-get -y --no-install-recommends install python3.10 python3.10-distutils\ 
    python3.10-dev
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
RUN python3.10 -m pip install --upgrade pip
COPY ./requirements.txt .
RUN python3.10 -m pip install -r requirements.txt
COPY . .