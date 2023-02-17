# This file is responsible for installing solr on the correct version required for this project.
# After installing solr, also copy over the core configuration files.

# Install java
sudo apt install openjdk-8-jdk openjdk-8-jre
cat >> /etc/environment <<EOL
JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
JRE_HOME=/usr/lib/jvm/java-8-openjdk-amd64/jre
EOL
cd /opt

# Download solr
cd /opt
wget https://dlcdn.apache.org/lucene/solr/8.11.2/solr-8.11.2.tgz
# OLD VERSION: wget https://archive.apache.org/dist/lucene/solr/8.2.0/solr-8.2.0.tgz
tar xzf solr-8.11.2.tgz solr-8.11.2/bin/install_solr_service.sh --strip-components=2
sudo bash ./install_solr_service.sh solr-8.11.2.tgz 
service solr status

# Install solr
