                    SELECT
                        id,
                        TO_CHAR(period_start::timestamp, 'YYYY-MM-DD') AS period_start,
                        TO_CHAR(period_end::timestamp, 'YYYY-MM-DD') AS period_end,
                        value,
                        currency_id,
                        TO_CHAR(value_date::timestamp, 'YYYY-MM-DD') AS value_date,
                        CAST((
                            SELECT
                                ROW_TO_JSON(recipient_org_budget_record) AS recipient_org_budget
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
                                                iati_organisation_recipientorgbudgetline.ref AS ref,
                                                iati_organisation_recipientorgbudgetline.value AS value,
                                                TO_CHAR(iati_organisation_recipientorgbudgetline.value_date::timestamp, 'YYYY-MM-DD') AS value_date,
                                                iati_organisation_recipientorgbudgetline.currency_id AS currency,
                                                (
                                                    SELECT
                                                        JSON_AGG(ROW_TO_JSON(narrative_record)) AS narrative
                                                    FROM (
                                                        SELECT
                                                               language_id AS lang,
                                                               content AS narrative
                                                        FROM iati_organisation_organisationnarrative, django_content_type
                                                        WHERE object_id=iati_organisation_recipientorgbudgetline.id
                                                            AND django_content_type.model='recipientorgbudgetline'
                                                            AND content_type_id=django_content_type.id
                                                    ) as narrative_record
                                                )
                                            FROM iati_organisation_recipientorgbudgetline
                                            WHERE iati_organisation_recipientorgbudgetline.recipient_org_budget_id = iati_organisation_recipientorgbudget.id
                                        ) AS budget_line_record
                                    )
                                ) as recipient_org_budget_record
                        ) AS VARCHAR)
                    FROM iati_organisation_recipientorgbudget
                    /*
                    WHERE iati_organisation_recipientorgbudget.organisation_id=${organisation.id}
                     */
