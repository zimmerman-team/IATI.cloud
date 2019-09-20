                    SELECT
                        id,
                        CASE WHEN attached=TRUE THEN '1' ELSE CASE WHEN attached=FALSE THEN '0' END END AS attached,
                        CAST((
                            SELECT
                                   ROW_TO_JSON(conditions_record) AS conditions
                            FROM (
                                SELECT
                                    CASE WHEN attached=TRUE THEN '1' ELSE CASE WHEN attached=FALSE THEN '0' END END AS attached,
                                    CAST((
                                        SELECT
                                            JSON_AGG(ROW_TO_JSON(condition_record)) AS condition
                                        FROM (
                                            SELECT
                                                   iati_condition.type_id AS type,
                                                   (
                                                        SELECT
                                                              JSON_AGG(ROW_TO_JSON(narative_record)) AS narrative
                                                        FROM (
                                                            SELECT
                                                                language_id AS lang,
                                                                content AS text
                                                            FROM iati_narrative, django_content_type
                                                            WHERE related_object_id = iati_condition.id
                                                                AND iati_narrative.activity_id = iati_conditions.activity_id
                                                                AND model='condition'
                                                                AND django_content_type.id = related_content_type_id
                                                        ) AS narative_record
                                                    )
                                            FROM iati_condition
                                            WHERE iati_condition.conditions_id = iati_conditions.id
                                        ) AS condition_record
                                    ) AS VARCHAR)
                            ) AS conditions_record
                        ) AS VARCHAR)
                    FROM iati_conditions
                    /*
                    WHERE activity_id=${activity.id}
                     */
                    LIMIT 1