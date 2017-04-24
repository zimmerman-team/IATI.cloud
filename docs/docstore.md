--------
## Docstore Scope :
--------

Docstore is a collection of IATI activities documents contents. Those docs are associated into IATI activities by the publishers.

For more details about the documents content, it is highly recommended to look at the IATI standard reference:

http://iatistandard.org/202/activity-standard/iati-activities/iati-activity/document-link/

OIPA is a boulding a search engine named "Docstore" that is collecting docs published in IATI activities. It is offering a word look up and generating a list of documents that is matching users queries.

--------
## Docstore Data Loading and Indexing :
--------
The Docstore Data can be loaded through the OIPA queue admin interface. The task responsible to load the data under "Document Tasks": "Collect Documents".

After adding the docstore task and its execution. The OIPA docstore is containing the whole pdf documents associated to the available OIPA activities.

The docstore documents indexation can be performed by using the command line:

'
./manage.py update_ft_indexes_documents
'


--------
## Docstore API Usage
--------

The docstore API endpoint is available under :

http://localhost:8000/api/documents/

The Docstore search can be performed using the following query params:

http://localhost:8000/api/documents/?document_q="aids"
