# Start with python 3.11
FROM python:3.11-bullseye

# Copy all relevant files to avoid security hotspot with `COPY . /app`
COPY ./direct_indexing /app
COPY ./iaticloud /app
COPY ./legacy_currency_convert /app
COPY ./services /app
COPY ./.env /app
COPY ./.pre-commit-config.yaml /app
COPY ./commitlint.config.js /app
COPY ./manage.py /app
COPY ./requirements.txt /app
COPY ./setup.cfg /app
COPY ./static /app
WORKDIR /app

# Pre-install python dependencies
RUN pip install -r requirements.txt

# Install java 11 and set JAVA_HOME and JRE_HOME to be able to use solr post tool
RUN apt-get update && apt-get install -y --no-install-recommends openjdk-11-jdk

# Change the user and ownership to user 'iaticloud'
RUN useradd -ms /bin/bash iaticloud
RUN chown -R iaticloud:iaticloud /app
USER iaticloud
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
EXPOSE 8000

ENTRYPOINT ["./services/iaticloud/docker-entrypoint.sh"]
