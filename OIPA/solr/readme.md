## Quick start to import database DataStore in SOLR

-   Install Java Runtime Environment (JRE) version 1.8 or higher
-   Download Solr 8.1 or higher form this link: [http://lucene.apache.org/solr/downloads.html](http://lucene.apache.org/solr/downloads.html)
-   Extract to a folder in this sample the folder is "solr"
-   Download and copy JDBC driver JAR for PostgreSQL to “/contrib/dataimporthandler/lib” in your folder Solr from this [https://jdbc.postgresql.org/download/postgresql-42.2.2.jar](https://jdbc.postgresql.org/download/postgresql-42.2.2.jar) 
-   And run the Solr
```alpha
cd solr
./bin/solr start

```

-   Create a core in Solr. In this sample we will make a core for the Activity data.
```alpha
./bin/solr create -c activity

```
-   Copy solrconfig.xml from the source of the DataStore 'solr/default/conf' to 'solr/server/solr/activity/conf'.
-   Copy data-config.xml & manage-schema from 'solr/activity/conf'  to 'solr/server/solr/activity/conf'.
-   Change the database, username & password of your database in the data-config.xml on the first line. 
-   And restart your Solr
```alpha
./bin/solr restart

```