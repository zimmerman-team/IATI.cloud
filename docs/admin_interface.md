--------
## Introduction
--------

OIPA uses the default Django administrator interface . Further (developer) documentation on Django Admin can be found at <a href="https://docs.djangoproject.com/en/1.9/ref/contrib/admin/" target="_blank">The Django admin site</a>

In the following sub-chapters, the most interesting elements of the admin interface will be high-lighted.

--------
## Admin interface
--------

The admin interface can be found at `http://<oipa_url>/admin/`. When you followed the steps at <a href="/installing/">Installing</a> to install OIPA, an account already exists and you can log in with username `vagrant`, password `vagrant`.

When you don't have a log-in yet, a superuser can be created with the Django management command: `python manage.py createsuperuser`.

The main page of the admin interface contains a list of models, the underlying pages provide forms to create/read/update/delete items. These are all basic Django and hopefully self explanatory. All odd or non-standard functionality in the admin will be handled below.

--------
## User management
--------

OIPA uses the Django user management. A user can be created at `http://<oipa_url>/admin/auth/user/add/`. *note*; by default the newly created user has no permissions to log into the admin site. This should be set by marking the 'Staff status' checkbox or 'Superuser status', dependent on your further permission configuration.

--------
## Task queue
--------

The task queue is available for superusers and can be found in the top navigation bar or at `http://<oipa_url>/admin/queue/`.

The task queue has two queues, one for all parsing tasks (parser queue) and one for all other tasks (default queue). These queues both have workers that run the tasks.

The task queues page first shows an overview of active workers and the amount of tasks in the different queues. Below the overview the user can add a task.


### Available tasks


**Update codelists from IATI registry** <br>Gets all codelist items from the different codelists at  <a href="http://iatistandard.org/201/codelists/downloads/clv1/codelist/" target="_blank">the IATI codelist API</a> and adds them to the appropriate OIPA codelist models.

**Add new sources from IATI registry and parse all sources** <br>A shortcut of both tasks below.

**Parse all IATI sources currently in OIPA** <br>Parse all sources that are currently in the list at `http://<oipa_url>/admin/iati_synchroniser/iatixmlsource/`

**Add new sources from IATI registry** <br>Use the <a href="http://www.iatiregistry.org/api/search/dataset?all_fields=1&offset=0&limit=200" target="_blank">IATI registry API</a> to add sources in `http://<oipa_url>/admin/iati_synchroniser/iatixmlsource/`

**Delete sources not found in registry in x days (and not added manually)** <br>based on the last_found_in_registry column on `http://<oipa_url>/admin/iati_synchroniser/iatixmlsource/`, this deletes all sources (and underlying activities) that are not found in the registry for the amount of days given in the input box thats shown when selecting this option. It does not delete manually added sources (added_manually column) since they never will be on the IATI registry and hence could be deleted accidentally.

**Parse all sources from a publisher** <br>Based on the publisher_iati_id in `http://<oipa_url>/admin/iati_synchroniser/publisher/` it will parse all sources found in `http://<oipa_url>/admin/iati_synchroniser/iatixmlsource/` that belong to that publisher. The publisher_iati_id can be given through a input box that shows when selecting this option.

**Force parse all sources currently in OIPA** <br>Same as "Parse all IATI sources currently in OIPA", but this task also re-parses activities that are already in OIPA and that do not require an update (because their last-updated-datetime did not change). This can be necessary when a bug is fixed in the parser or the data source that requires a re-parse of all activities.

**Force parse all sources from a publisher** <br>Same as "Parse all sources from a publisher", but this task also re-parses activities that do not require an update (same last-updated-datetime).

**Update currency exchange rates** <br>Fetches monthly currency exchange rates from the IMF. Does not reparse exchange rates when they already exist in OIPA.

**Force update currency exchange rates** <br> Fetches monthly currency exchange rates from the IMF. <u>Does</u> reparse exchange rates when they already exist in OIPA.


--------
## Custom codelists
--------

When first installing OIPA, it is advised to import all default IATI codelists using the <a href="#task-queue">task queue</a> (task 'Update codelists from IATI registry'). In case you require a codelist in an own vocabulary, which is the case if you want to parse IATI sources that use their own custom codelist. This can be done by adding items to the specific (vocabulary) codelist under `http://<oipa_url>/admin/iati_vocabulary/` and `http://<oipa_url>/admin/iati_codelists/`.

--------
## Loading geographic data
--------

Next to IATI codelists and parsing IATI data, OIPA also has functionality to load in geo meta data. This can be done through the city / admin 1 region / country / region admin pages listed at `http://<oipa_url>/admin/geodata/`. It's on our list to move this processes to the task queue.

The following (meta) can be loaded in:

- Cities: 6100+ cities and their center locations.
- Admin1 regions: First level administrative regions within countries.
- Countries: Center locations (longitude/latitude), alternative names, polygons, update relation to regions, other identifiers (UN code, alpha 3, fips10)
- Regions: Center locations (longitude/latitude)



