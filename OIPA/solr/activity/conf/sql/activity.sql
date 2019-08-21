                SELECT
                    iati_activity.id AS id,
                    iati_identifier,
                    last_updated_datetime,
                    default_lang_id,
                    default_currency_id,
                    CASE WHEN humanitarian=TRUE THEN '1' ELSE '0' END AS humanitarian,
                    hierarchy,
                    linked_data_uri,
                    activity_status_id,
                    scope_id,
                    collaboration_type_id,
                    default_flow_type_id,
                    default_finance_type_id,
                    default_tied_status_id,
                    capital_spend,
                    iati_version
                FROM iati_activity, iati_synchroniser_dataset
                WHERE iati_activity.dataset_id=iati_synchroniser_dataset.id
