#!/bin/sh
curl --url "http://localhost:8983/solr/$1/replication?command=backup&name=$1"