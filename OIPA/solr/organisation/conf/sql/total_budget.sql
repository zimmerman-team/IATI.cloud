                    SELECT
                        id,
                        TO_CHAR(period_start::timestamp, 'YYYY-MM-DD') AS period_start,
                        TO_CHAR(period_end::timestamp, 'YYYY-MM-DD') AS period_end,
                        value,
                        currency_id,
                        TO_CHAR(value_date::timestamp, 'YYYY-MM-DD') AS value_date,
                        CAST((
                            SELECT
                                ROW_TO_JSON(total_budget_record) AS total_budget
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
                                                iati_organisation_totalbudgetline.ref AS ref,
                                                iati_organisation_totalbudgetline.value AS value,
                                                TO_CHAR(iati_organisation_totalbudgetline.value_date::timestamp, 'YYYY-MM-DD') AS value_date,
                                                iati_organisation_totalbudgetline.currency_id AS currency,
                                                (
                                                    SELECT
                                                        JSON_AGG(ROW_TO_JSON(narrative_record)) AS narrative
                                                    FROM (
                                                        SELECT
                                                               language_id AS lang,
                                                               content AS narrative
                                                        FROM iati_organisation_organisationnarrative, django_content_type
                                                        WHERE object_id=iati_organisation_totalbudgetline.id
                                                            AND django_content_type.model='totalbudgetline'
                                                            AND content_type_id=django_content_type.id
                                                    ) as narrative_record
                                                )
                                            FROM iati_organisation_totalbudgetline
                                            WHERE iati_organisation_totalbudgetline.total_budget_id = iati_organisation_totalbudget.id
                                        ) AS budget_line_record
                                    )
                                ) as total_budget_record
                        ) AS VARCHAR)
                    FROM iati_organisation_totalbudget
                    WHERE iati_organisation_totalbudget.organisation_id=${organiation.id}