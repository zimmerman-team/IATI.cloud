FROM ubuntu:16.04

RUN apt-get -y update

RUN apt-get install -y software-properties-common

RUN add-apt-repository ppa:jonathonf/python-3.6

RUN apt-get update

RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip python3.6-venv

RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel

RUN echo "alias python='/usr/bin/python3.6'" >> ~/.bash_profile

RUN /bin/bash -c "source ~/.bash_profile"
RUN /bin/bash -c "source ~/.bashrc"

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
    python3-pip

RUN mkdir /app
#RUN virtualenv /venv

#XXX: is this needed?:
ENV PATH /venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

RUN pip3 install -U pip setuptools

# Install Python dependencies
ADD OIPA/requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt
RUN pip3 show django
#XXX: this shows /usr/local/lib/python3.5:
#RUN pip3 show django

ENV PYTHONUNBUFFERED 1
EXPOSE 8000
#ENV PYTHONPATH /app/src
ENV PYTHONPATH="$PYTHONPATH:/usr/local/lib/python3.6/dist-packages"
WORKDIR /app/src/OIPA
ADD . /app/src

#RUN groupadd -r uwsgi -g 1000 && useradd -u 1000 -r -g 1000 uwsgi
#RUN mkdir -p /app/src/public && chown -R uwsgi:uwsgi /app/src/public

#USER 1000

#RUN /bin/bash -c "source /venv/bin/activate"

CMD ["/app/src/bin/docker-cmd.sh"]

#RUN rm -f /usr/bin/python && ln -s /usr/bin/python /usr/bin/python3.6

RUN python -V
RUN cat ~/.bash_profile
