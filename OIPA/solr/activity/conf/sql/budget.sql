                    SELECT
                        type_id,
                        status_id,
                        TO_CHAR(period_start::timestamp, 'YYYY-MM-DD') AS period_start,
                        TO_CHAR(period_end::timestamp, 'YYYY-MM-DD') AS period_end,
                        currency_id,
                        TO_CHAR(value_date::timestamp, 'YYYY-MM-DD') AS value_date,
                        value,
                        CAST((
                            SELECT
                                   ROW_TO_JSON(budget_record) AS budget
                            FROM (
                                SELECT
                                       type_id AS type,
                                       status_id AS status,
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
                                       )
                            ) AS budget_record
                        ) AS VARCHAR)
                    FROM iati_budget
                    /* WHERE activity_id=${activity.id} */