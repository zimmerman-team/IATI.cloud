FROM ubuntu:16.04

RUN apt-get -y update

RUN apt-get install -y software-properties-common

RUN add-apt-repository ppa:jonathonf/python-3.6

RUN apt-get update

RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip

RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel

#TODO: all these need to be checked:
RUN apt-get -y install \
    #python-virtualenv \
    postgresql-client \
    git \
    libxml2-dev \
    libxslt1-dev \
    #virtualenv \
    #python-virtualenv \
    binutils \
    gdal-bin \
    libgeos-3.5.0 \
    libgeos-dev \
    libproj-dev \
    antiword \
    binutils \
    bzip2 \
    catdoc \
    docx2txt \
    gzip \
    html2text \
    libimage-exiftool-perl \
    odt2txt \
    perl \
    poppler-utils \
    unrar \
    unrtf \
    unzip \
    libsqlite3-dev  \
    libsqlite3-mod-spatialite \
    sqlite3 \
    libpq-dev \
    python-psycopg2 \
    uwsgi \
    uwsgi-plugin-python \
    python3-pip \
    vim

RUN mkdir /app

RUN pip3 install -U pip setuptools

ADD OIPA/requirements.txt /app/src/OIPA/requirements.txt

# Install Python dependencies
#FIXME: use cache: https://stackoverflow.com/a/25307587/2942981
RUN pip3 install -r /app/src/OIPA/requirements.txt

ADD . /app/src

ENV PYTHONPATH="$PYTHONPATH:/usr/local/lib/python3.6/dist-packages"

RUN ["chmod", "+x", "/app/src/docker-entrypoint.sh"]
