--------
## API
--------

The OIPA API is currently based on IATI 2.02 output. 


--------
## Endpoints
--------

The different endpoints can be found at `http://<oipa_url>/api/`.

--------
## Activities endpoint
--------

URL: `http://<oipa_url>/api/activities/`.

### Usage examples

TODO


--------
## Organisations endpoint
--------

URL: `http://<oipa_url>/api/organisations/`.


--------
## Results endpoint
--------

URL: `http://<oipa_url>/api/results/`.


--------
## Transactions endpoint
--------

URL: `http://<oipa_url>/api/transactions/`.


TODO add info on other endpoints.


--------
## Aggregation endpoint
--------

URL: `http://<oipa_url>/api/activities/aggregations/`.

The following GET paramaters *have* to be specified in order to get an aggregation result:

* group_by
* aggregations

For up-to-date information on the group_by / aggregations options, see the docs on top of the API URL at `http://<oipa_url>/api/activities/aggregations/`.

TODO add info on other aggregation endpoints.

### Percentage based aggregations

The *recipient_country*, *recipient_region* and *sector* IATI fields provide a percentage field. In the percentage_weighted aggregations we use these values to calculate the final transaction values.

Percentages for all reported sectors must add up to 100%. Additionally, the percentage fields for all reported *recipient_country* and *recipient_region* percentage fields must also add up to 100%.

The *sector*, *recipient_country* and *recipient_region* fields are related to IATI transactions as pictured below. Every IATI activity has one or multiple transactions and one or multiple sector, recipient_country and recipient_region elements directly related to them.

<div style="text-align: center;padding:10px 0 30px;">
    <img src="../images/group_by.png" />
</div>

The percentage weighted aggregations are calculated based on whether the percentage field is reported in the given IATI activity or not (this example assumes sector, the same holds for the other fields)

#### Percentage reported
If the percentage field is reported, calculate for every sector their share of the transaction value as indicated by the percentage value. 

Hence, the following will hold:

sector_aggregation_value = sector_percentage * total_transaction_value

#### Percentage not reported

If the percentage field is not reported, assume a uniform distribution for the percentages.

For example, when 3 sectors are reported with no percentage field, assume a percentage value of 33.33% for each sector field. Continue with 1.

<hr />

These steps are repeated for every IATI activity that was found for the selected filters. The result will be the aggregate of these steps.

### Usage examples

TODO

--------
