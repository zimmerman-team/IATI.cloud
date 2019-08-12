                    SELECT
                        id,
                        ref,
                        CASE WHEN humanitarian=TRUE THEN '1' ELSE '0' END AS humanitarian,
                        transaction_type_id,
                        TO_CHAR(transaction_date::timestamp, 'YYYY-MM-DD') AS transaction_date,
                        currency_id,
                        TO_CHAR(value_date::timestamp, 'YYYY-MM-DD') AS value_date,
                        value,
                        disbursement_channel_id,
                        flow_type_id,
                        tied_status_id,
                        CAST((SELECT row_to_json(transaction) AS transaction FROM (
                            SELECT
                                ref AS ref,
                                CASE WHEN humanitarian=TRUE THEN '1' ELSE '0' END AS humanitarian,
                                transaction_type_id AS transaction_type_code,
                                transaction_date AS transaction_date_iso_date,
                                disbursement_channel_id AS disbursement_channel_code,
                                flow_type_id AS flow_type_code,
                                tied_status_id AS tied_status_code,
                                (
                                    SELECT ROW_TO_JSON(value_record) AS value
                                    FROM (
                                        SELECT
                                            currency_id AS currency,
                                            value_date AS value_date,
                                            value AS value
                                    ) AS value_record
                                ),
                                (
                                    SELECT row_to_json(provider_org) AS provider_org FROM (
                                        SELECT
                                            provider_activity_ref as provider_activity_id,
                                            ref as ref,
                                            (
                                                SELECT
                                                    JSON_AGG(ROW_TO_JSON(narrative)) as narrative
                                                FROM (
                                                    SELECT language_id AS lang, content as text FROM iati_narrative, django_content_type
                                                    WHERE related_object_id=iati_transactionprovider.id
                                                        AND django_content_type.model='transactionprovider'
                                                        AND related_content_type_id=django_content_type.id
                                                    ) as narrative
                                            )
                                        FROM iati_transactionprovider
                                        WHERE transaction_id=iati_transaction.id
                                    ) provider_org
                                ),
                                (
                                    SELECT row_to_json(receiver_org) AS receiver_org FROM (
                                        SELECT
                                            receiver_activity_ref as receiver_activity_id,
                                            ref as ref,
                                            (
                                                SELECT
                                                    JSON_AGG(ROW_TO_JSON(narrative)) as narrative
                                                FROM (
                                                    SELECT language_id AS lang, content as text FROM iati_narrative, django_content_type
                                                    WHERE related_object_id=iati_transactionreceiver.id
                                                        AND django_content_type.model='transactionreceiver'
                                                        AND related_content_type_id=django_content_type.id
                                                    ) as narrative
                                            )
                                        FROM iati_transactionreceiver
                                        WHERE transaction_id=iati_transaction.id
                                    ) receiver_org
                                ),
                                (
                                    SELECT JSON_AGG(ROW_TO_JSON(aid_type)) AS aid_type FROM (
                                        SELECT
                                            iati_codelists_aidtype.code as code,
                                            iati_codelists_aidtype.vocabulary_id as vocabulary_id
                                        FROM iati_codelists_aidtype, iati_transactionaidtype
                                        WHERE iati_codelists_aidtype.code=iati_transactionaidtype.aid_type_id
                                            AND transaction_id=iati_transaction.id
                                    ) aid_type
                                )
                        ) transaction) AS VARCHAR)
                    FROM iati_transaction
                    WHERE activity_id=${activity.id}