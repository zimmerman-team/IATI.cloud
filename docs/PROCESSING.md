# IATI.cloud dataset processing

- [IATI.cloud dataset processing](#iaticloud-dataset-processing)
  - [Introduction](#introduction)
  - [Process overview](#process-overview)
    - [Indexing the dataset](#indexing-the-dataset)
      - [Cleaning](#cleaning)
      - [Adding custom fields](#adding-custom-fields)
      - [Extracting subtypes](#extracting-subtypes)
      - [Final step](#final-step)
  - [Development entry points](#development-entry-points)

---

## Introduction

The following is an explanation of the dataset processing flow for IATI.cloud.

## Process overview

We use the code4iati dataset metadata and publisher metadata dumps to access all of the available metadata.

Publisher: We basically immediately index the publisher metadata as it is flat data.

Dataset: We download the code4iati dataset dump to access all of the available IATI datasets from the IATI Registry. If `update` is true, we check whether or not the hash has changed from the already indexed datasets. We then loop the datasets within the dataset metadata dump and trigger the `subtask_process_dataset`. For each dataset we clean the dataset metadata (where we extract the nested `resources` and `extras`). We then retrieve the filepath of the actual downloaded dataset based on the organisation name and dataset name. We check if the version is valid (in this case version 2). We get the type of the file from the metadata or the file content itself. We then check the dataset validation. Then we clear the existing data from this dataset if it is found in the IATI.cloud and the `update` flag is True. Then we trigger the [indexing of the actual dataset](#indexing-the-dataset). Once this is completed we store the success state of the latter to `iati_cloud_indexed` and we index the entire dataset metadata.

### Indexing the dataset

First, we parse the IATI XML dataset. We then convert it to a dict using the BadgerFish algorithm.

We apply our [cleaning](#cleaning) and [add custom fields](#adding-custom-fields). We then dump the dataset dict into a JSON file.
Latstly, we [extract the subtypes (budget, result and transactions)](#extracting-subtypes)

#### Cleaning

We then recursively clean the dataset. `@` values are removed, `@{http://www.w3.org/XML/1998/namespace}lang` is replaced with `lang`, and key-value fields are extracted. [Read more here](../direct_indexing/cleaning/dataset.py).

#### Adding custom fields

We have several "custom fields" that we enrich the IATI data with.

- [Codelist fields](../direct_indexing/custom_fields/codelists.py): These fields are 'name' representations of numeric/code values in the IATI Standard, for example an activity can report `transaction-type.code: 3`. We then enrich the activity with `transaction-type.name: Disbursement`.
- [Title narrative](../direct_indexing/custom_fields/title_narrative.py): We add a single-valued field with exclusively the first-reported title narrative.
- [Common activity dates](../direct_indexing/custom_fields/activity_dates.py): We add single value common start and end dates, so we immediately know a start and an end-date without looking through the planned and actual fields.
- [Activity status](../direct_indexing/custom_fields/activity_status.py): We add single value activity-status.text field, to present the textual status alongside the code.
- [Combined policy marker](../direct_indexing/custom_fields/policy_marker_combined.py): We add `policy-marker.combined` which is the policy marker code and its connected significance together.
- [Currency conversion](../direct_indexing/custom_fields/currency_conversion.py): Explained in depth [here](./USAGE.md#legacy-currency-convert).
- [Dataset metadata](../direct_indexing/custom_fields/dataset_metadata.py): We add interesting dataset metadata fields to the activity.
- [Hierarchy default value](../direct_indexing/custom_fields/add_default_hierarchy.py): "If hierarchy is not reported then 1 is assumed.". Ensure this is enforced.
- [JSON dumps](../direct_indexing/custom_fields/json_dumps.py): A stringified JSON object of different IATI activity fields.
- [Date quarters](../direct_indexing/custom_fields/date_quarters.py): For each iso-date reported, also include a field in which quarter they are.
- [Document link categories](../direct_indexing/custom_fields/document_link_category_combined.py): Provides a combined list of all the category codes for each document-link.
- [Currency aggregation](../direct_indexing/custom_fields/currency_aggregation.py): We add converted and aggregated values for budgets, disbursements and transactions/transaction subtypes.
- [Related activity data to parent activity](../direct_indexing/custom_fields/raise_h2_budget_data_to_h1.py): This 'raises' related activity budget data from the H2 activities to the H1 activities.

[Check it out in depth here](../direct_indexing/custom_fields/custom_fields.py)

#### Extracting subtypes

We extract the subtypes to single valued fields. [Read more here](../direct_indexing/processing/activity_subtypes.py).

Each of these is indexed separately into its respective core.

#### Final step

Lastly, if the previous steps were all successful, we index the IATI activity data.

## Development entry points

- [Django settings](../iaticloud/settings.py): contains the settings (set by the .env file).
- AIDA
  - [Django urls](../iaticloud/urls.py): contains the accessible Django API REST endpoints.
  - [Django views](../iaticloud/views.py): contains the functions used in Django URLS.
- NGINX
  - The directory `scripts/setup/nginx_host_machine` contains the Nginx configuration for iati.cloud
- Tests
  - The directory `tests/direct_indexing` contains the tests for the `direct_indexing` module.
- The [pre-commit config](../.pre-commit-config.yaml) ensures proper git commit etiquette, along with the [commitlint](../commitlint.config.js).
- `legacy_currency_convert`: The original IMF rate parser that was implemented before the full IATI.cloud rewrite, and reused for currency conversion. Work from [tasks.py](../legacy_currency_convert/tasks.py)
- `direct_indexing`: The IATI.cloud rewrite result, originally, datasets were processed into a Django postgres database, after which the dataset was retrieved and converted to a Solr dataset. This can be reviewed under the git branch `archive/iati-cloud-hybrid-django-solr`. The main entrypoint here is [tasks.py](../direct_indexing/tasks.py).
- Django admin
  - See [USAGE.md -> task management](./USAGE.md#task-management)
