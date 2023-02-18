# Start with python 3.11
FROM python:3.11

COPY . /app
WORKDIR /app

# Pre-install python dependencies
RUN pip install -r requirements.txt

# Install java 11 and set JAVA_HOME and JRE_HOME to be able to use solr post tool
RUN apt-get update && apt-get install -y openjdk-11-jdk
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Expose port 8000 for django, 80 for the web server and 5555 for flower
EXPOSE 5555 8000

ENTRYPOINT ["./services/iaticloud/docker-entrypoint.sh"]
