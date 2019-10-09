#!/bin/sh
dt=$(date "+%Y%m%d%H%M%S");
curl --request POST -sL \
  --url "http://iati.solr.internal:8983/solr/$1/dataimport?command=full-import&clean=true&commit=true" \
  --output "$2/$1.$dt.log";
