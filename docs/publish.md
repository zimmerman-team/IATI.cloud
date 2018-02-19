# Permissions

The models used for permissions are defined in https://github.com/zimmerman-zimmerman/OIPA/blob/master/OIPA/iati/permissions/models.py

There are two groups available for permissions in OIPA:
* OrganisationAdminGroup
* OrganisationGroup

Every OrganisationAdminGroup and OrganisationGroup are associated with exactly one publisher.

Users that are in the admin group have full permissions for:
* Writing and updating activities owned by the corresponding publisher
* Updating the organisation that is associated with the corresponding publisher
* Adding/removing users from the admin group and organisation group

Users that are in the organisation group have no extra privileges at this time.

## Authenticating for the API

In order for a user to join the admin group, the user must first authenticate with the IATI registry.

For verifying the API key the following endpoints exist:

### **POST** `/api/publisher/<publisher_id>/api_key/verify/` 

Requires two arguments:
* **apiKey**: the IATI registry CKAN api key
* **userId**: the IATI regisry CKAN user id

This validates the user with the API registry and creates the corresponding OrganisationGroup and OrganisationAdminGroup models if they do not exist yet.

Note: this API call assumes that `publisher_iati_id` is defined correctly on the organisation in the IATI registry. This must map directly to the iati identifier for the main organisation that reports this organisation.

This API call returns a **token** that must be used in subsequent activity and organisation API calls. Using this token the user can perform activity and organisation CRUD and add/remove users from the groups.

### *POST* `/api/publisher/<publisher_id>/api_key/remove/` 

Disassociates the user from the publisher by removing the user from the OrganisationAdminGroup and OrganisationGroup

# Publish IATI flow

In order to publish IATI, the user must validated his API key with the IATI registry.

There are two steps to publishing IATI with OIPA:
1. Make changes to activities
2. Mark activities that you want with the publish as ready\_to\_publish flag
3. Export the activities to XML
4. Get the XML result from the task queue
5. Host the XML file on a publicly available URL
6. Update the IATI Registry Dataset

## 1. Make changes to activities
These changes should happen through the ActivityCRUD APIs. These APIs make sure that the modified flag is appropriately updated. If you make changes by hand, make sure to set the modified flag to False. 

## 2. Mark activities as ready\_to\_publish
Marking the activity as ready to publish can be done through the API with the `/api/publisher/<publisher_id>/activities/<activity_id>/mark_ready_to_publish/`. If you do this manually you can set the ready\_to\_publish flag directly on the activity.

## 3. Export the activities XML
This can be done through the API at `/api/publisher/<publisher_id>/activities/next_published_activities/`. This will then put the export task into the task queue.

To get the result, query `/api/publisher/<publisher_id>/activities/next_published_activities/<job_id>` where job\_id is the id returned from the export task.

## 5. Host the XML
The resulting XML should then be hosted in a public space. You can host this on your own server on any URL.

## 6. Update the IATI Registry Dataset
Creating the dataset should be done through the API at the endpoint `/api/datasets/<publisher_id>/publish_activities/`. This will take all activities marked as ready\_to\_publish and change this flag to false. Then it will create the dataset given. To later update the dataset, the API endpoint `/api/datasets/<publisher_id>/publish_activities/<dataset_id>` can be used.

Both these endpoints require the following arguments:
* **source\_url**: the URL where the activity XML is being served.

After this, the dataset is published to the IATI registry, and new modifications can be made (back to 1.).
