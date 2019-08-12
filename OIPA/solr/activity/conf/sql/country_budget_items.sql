                    SELECT
                        id,
                        vocabulary_id,
                        CAST((
                            SELECT
                                   ROW_TO_JSON(country_budget_items_record) AS country_budget_items
                            FROM (
                                SELECT
                                       vocabulary_id AS vocabulary,
                                       JSON_AGG(ROW_TO_JSON(budget_item_record)) AS budget_item
                                FROM (
                                    SELECT
                                           code_id AS code,
                                           percentage AS percentage,
                                           (
                                               SELECT
                                                      JSON_AGG(ROW_TO_JSON(narrative_record)) AS description
                                               FROM (
                                                    SELECT
                                                        language_id AS lang,
                                                        content AS narrative
                                                    FROM iati_narrative, django_content_type, iati_budgetitemdescription
                                                    WHERE related_object_id = iati_budgetitemdescription.id
                                                        AND iati_budgetitemdescription.budget_item_id = iati_budgetitem.id
                                                        AND django_content_type.model = 'budgetitemdescription'
                                                        AND related_content_type_id = django_content_type.id
                                               ) AS narrative_record
                                            )
                                    FROM
                                        iati_budgetitem
                                    WHERE
                                        country_budget_item_id = iati_countrybudgetitem.id
                                ) AS budget_item_record
                            ) AS country_budget_items_record
                        ) AS VARCHAR)
                    FROM iati_countrybudgetitem
                    WHERE activity_id=${activity.id}