FROM ubuntu:16.04

RUN apt-get -y clean && apt-get -y update

RUN apt-get -y install python-dev python-virtualenv postgresql-client \
    git \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    python-dev \
    virtualenv \
    python-virtualenv \
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
    uwsgi-plugin-python

RUN mkdir /app
RUN virtualenv /venv
ENV PATH /venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
RUN pip install -U pip setuptools

# Install Python dependencies
ADD OIPA/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

ENV PYTHONUNBUFFERED 1
EXPOSE 8000
ENV PYTHONPATH /app/src
WORKDIR /app/src/OIPA
ADD . /app/src

RUN groupadd -r uwsgi -g 1000 && useradd -u 1000 -r -g 1000 uwsgi
RUN mkdir -p /app/src/public && chown -R uwsgi:uwsgi /app/src/public

USER 1000

CMD ["/app/src/bin/docker-cmd.sh"]
