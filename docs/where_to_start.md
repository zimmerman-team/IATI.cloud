## Which data to load and where to do this

All data loading happens from the task queue at `/admin/task_queue/`. 

Minimum required tasks to get all IATI datasets loaded in:

-   `Update codelists from IATI registry`
-   `Add/update country data` (To also get country center points / polygons from the API)
-   `Add new sources from IATI registry and parse all sources`


For more information on the specific tasks (some of which cover additional use cases) see [Task queue -> Available tasks](http://docs.oipa.nl/en/latest/admin_interface/#available-tasks).


TODO: This chapter only covers the basics. It should provide more guidance on general use and provide some scenario's to use OIPA based on use cases. 
