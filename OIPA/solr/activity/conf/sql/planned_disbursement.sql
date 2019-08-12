                    SELECT
                        id,
                        type_id,
                        TO_CHAR(period_start::timestamp, 'YYYY-MM-DD') AS period_start,
                        TO_CHAR(period_end::timestamp, 'YYYY-MM-DD') AS period_end,
                        currency_id,
                        TO_CHAR(value_date::timestamp, 'YYYY-MM-DD') AS value_date,
                        value,
                        CAST((
                            SELECT
                                   ROW_TO_JSON(planned_disbursement_record) AS budget
                            FROM (
                                SELECT
                                       type_id AS type,
                                       TO_CHAR(period_start::timestamp, 'YYYY-MM-DD') AS period_start,
                                       TO_CHAR(period_end::timestamp, 'YYYY-MM-DD') AS period_end,
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
                                           SELECT ROW_TO_JSON(provider_org_record) AS provider_org
                                           FROM (
                                               SELECT
                                                      provider_activity_ref AS provider_activity_id,
                                                      iati_planneddisbursementprovider.type_id AS type,
                                                      ref AS ref,
                                                      (
                                                          SELECT
                                                                JSON_AGG(ROW_TO_JSON(narrative_record)) AS narrative
                                                          FROM (
                                                                SELECT
                                                                       language_id AS lang,
                                                                       content AS text
                                                                FROM iati_narrative, django_content_type
                                                                WHERE related_object_id = iati_planneddisbursementprovider.id
                                                                    AND django_content_type.model = 'planneddisbursementprovider'
                                                                    AND related_content_type_id =
                                                                        django_content_type.id
                                                          ) as narrative_record
                                                      )
                                               FROM iati_planneddisbursementprovider
                                               WHERE planned_disbursement_id = iati_planneddisbursement.id
                                           ) AS provider_org_record
                                       ),
                                       (
                                           SELECT ROW_TO_JSON(receiver_org_record) AS receiver_org
                                           FROM (
                                               SELECT
                                                      receiver_activity_ref AS receiver_activity_id,
                                                      iati_planneddisbursementreceiver.type_id AS type,
                                                      ref AS ref,
                                                      (
                                                          SELECT
                                                                JSON_AGG(ROW_TO_JSON(narrative_record)) AS narrative
                                                          FROM (
                                                                SELECT
                                                                       language_id AS lang,
                                                                       content AS text
                                                                FROM iati_narrative, django_content_type
                                                                WHERE related_object_id = iati_planneddisbursementreceiver.id
                                                                    AND django_content_type.model = 'planneddisbursementreceiver'
                                                                    AND related_content_type_id =
                                                                        django_content_type.id
                                                          ) as narrative_record
                                                      )
                                               FROM iati_planneddisbursementreceiver
                                               WHERE planned_disbursement_id = iati_planneddisbursement.id
                                           ) AS receiver_org_record
                                       )
                            ) AS planned_disbursement_record
                        ) AS VARCHAR)
                    FROM iati_planneddisbursement
                    WHERE activity_id=${activity.id}