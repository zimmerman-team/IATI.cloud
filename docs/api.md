--------
## API
--------

The OIPA API is currently based on IATI 2.01 output. 


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
## Aggregation endpoint
--------

Disclaimer: the aggregation endpoint is subject to change. We are still working on a better setup and therefore these docs might become outdated quickly. We are still waiting 

URL: `http://<oipa_url>/api/activities/aggregations/`.

The following GET paramaters *have* to be specified in order to get an aggregation result:

* group_by
* aggregations

The following fields are available for use with the group_by parameter:

* recipient_country
* recipient_region
* sector
* reporting_organisation
* participating_organisation_ref
* participating_organisation_name
* activity_status
* policy_marker
* collaboration_type
* default_flow_type
* default_aid_type
* default_finance_type
* default_tied_status
* budget_per_year
* budget_per_quarter
* transactions_per_quarter
* transaction_date_year

The following fields are available with the *aggregations* parameter:

* count
* budget
* disbursement
* expenditure
* commitment
* incoming_fund
* transaction_value
* recipient_country_percentage_weighted_incoming_fund (only in combination with recipient_country group_by)
* recipient_country_percentage_weighted_disbursement (only in combination with transaction based group_by's)
* recipient_country_percentage_weighted_expenditure (only in combination with transaction based group_by's)
* sector_percentage_weighted_budget (only in combination with budget based group_by's)
* sector_percentage_weighted_incoming_fund (only in combination with transaction based group_by's)
* sector_percentage_weighted_disbursement (only in combination with transaction based group_by's)
* sector_percentage_weighted_expenditure (only in combination with transaction based group_by's)
* sector_percentage_weighted_budget (only in combination with budget based group_by's)

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
