                   SELECT
                        id,
                        type_id AS type,
                        CAST((
                            SELECT
                                   ROW_TO_JSON(description_record) AS description
                            FROM (
                                SELECT
                                       type_id as type,
                                       JSON_AGG(ROW_TO_JSON(description)) AS narrative
                                FROM (
                                    SELECT
                                           language_id AS lang,
                                           content AS narrative
                                    FROM iati_narrative, django_content_type
                                    WHERE related_object_id=iati_description.id
                                        AND django_content_type.model='description'
                                        AND related_content_type_id=django_content_type.id
                                        AND activity_id=${activity.id}
                                ) AS description
                            ) AS description_record
                        ) AS VARCHAR)
                    FROM iati_description
                    /* WHERE activity_id=${activity.id}