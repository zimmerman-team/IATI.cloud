                    SELECT
                        id,
                        TO_CHAR(period_start::timestamp, 'YYYY-MM-DD') AS period_start,
                        TO_CHAR(period_end::timestamp, 'YYYY-MM-DD') AS period_end,
                        value,
                        currency_id,
                        TO_CHAR(value_date::timestamp, 'YYYY-MM-DD') AS value_date,
                        CAST((
                            SELECT
                                ROW_TO_JSON(recipient_region_budget_record) AS recipient_region_budget
                            FROM (
                                SELECT
                                    TO_CHAR(period_start::timestamp, 'YYYY-MM-DD') AS period_start,
                                    TO_CHAR(period_end::timestamp, 'YYYY-MM-DD') AS period_end,
                                    value,
                                    currency_id AS currency,
                                    TO_CHAR(value_date::timestamp, 'YYYY-MM-DD') AS value_date,
                                    (
                                        SELECT
                                            JSON_AGG(ROW_TO_JSON(budget_line_record)) AS budget_line
                                        FROM (
                                            SELECT
                                                iati_organisation_recipientregionbudgetline.ref AS ref,
                                                iati_organisation_recipientregionbudgetline.value AS value,
                                                TO_CHAR(iati_organisation_recipientregionbudgetline.value_date::timestamp, 'YYYY-MM-DD') AS value_date,
                                                iati_organisation_recipientregionbudgetline.currency_id AS currency,
                                                (
                                                    SELECT
                                                        JSON_AGG(ROW_TO_JSON(narrative_record)) AS narrative
                                                    FROM (
                                                        SELECT
                                                               language_id AS lang,
                                                               content AS narrative
                                                        FROM iati_organisation_organisationnarrative, django_content_type
                                                        WHERE object_id=iati_organisation_recipientregionbudgetline.id
                                                            AND django_content_type.model='recipientregionbudgetline'
                                                            AND content_type_id=django_content_type.id
                                                    ) as narrative_record
                                                )
                                            FROM iati_organisation_recipientregionbudgetline
                                            WHERE iati_organisation_recipientregionbudgetline.recipient_region_budget_id = iati_organisation_recipientregionbudget.id
                                        ) AS budget_line_record
                                    )
                                ) as recipient_region_budget_record
                        ) AS VARCHAR)
                    FROM iati_organisation_recipientregionbudget
                    /*
                    WHERE iati_organisation_recipientregionbudget.organisation_id=${organisation.id}
                     */