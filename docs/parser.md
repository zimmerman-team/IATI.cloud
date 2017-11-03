## Supported IATI versions in the parser

* 1.01 - full support
* 1.02 - full support
* 1.03 - full support
* 1.04 - full support
* 1.05 - full support
* 2.01 - full support
* 2.02 - full support
* 2.03 - not released yet at the moment of writing (2017-11), planned for release on 2018-01-08


## Technical information

The parser is located at `/iati/parser/`. Parsing can be triggered using a task in the task queue or by manually calling the process method of the Dataset model. 


<div style="text-align: center;padding:10px 0 30px;">
    <img src="../images/parser_sequence_diagram.png" />
    <br/>&nbsp;<br/>
    Figure 1. A pseudo sequence diagram for parsing a dataset 
</div>

The above sequence diagram is simplified in certain areas. Below texts will run you through all steps and will ellaborate on the parts that are left out. 


#### Dataset.process(force_reparse)

The process method kicks off the parsing process, after that's done it updates the last_updated datetime field of the dataset and saves the dataset.

The method has a force_reparse parameter which changes the behaviour upon reparsing the dataset. We have two ways to check if an activity needs updating:

* We generate a checksum of the file and check if it is equal to the checksum it generated last time we parsed the dataset. If the same, nothing changed and we don't reparse the file.

* Every activity in IATI has a last-updated-datetime attribute. If that remains unchanged we do not reparse the activity.

If the force_reparse parameter is set to True, we do not perform the above 2 checks and reparse every activity in the file. 


#### Parsemanager.init

Downloads the file, creates the file hash, checks the IATI version of the file and filetype (activity / organisation standard), based upon the version and filetype, creates and prepares the correct Parser version.


#### Parse.parse(element)

Runs through each element it finds in the XML file. If it is an valid IATI element it performs validation and creates the Django models for it.


#### Parse.save_all_models(element)

Saves all the models that were created in the previous step.


#### Parse.post_save_file(element)

Sets some relations and fields that could not be set at the Parse.parse sub methods since the models did not exist there and/or the functionality needs to know everything that's in the activity before being able to run it.

* set_related_activities
* set_participating_organisation_activity_id
* set_transaction_provider_receiver_activity
* set_derived_activity_dates
* set_activity_aggregations
* update_activity_search_index
* set_country_region_transaction
* set_sector_transaction
* set_sector_budget


## Future plans

OIPA has a POST API since the beginning of 2017. This has validation separated from it. Currently the parser does not use this validation yet, in the future it would be good to combine these efforts.