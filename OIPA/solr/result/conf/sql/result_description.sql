                    SELECT
                        id,
                        CAST((
                            SELECT
                                JSON_AGG(ROW_TO_JSON(description_records)) as description
                            FROM (
                                SELECT
                                       language_id AS lang,
                                       content AS narrative
                                FROM iati_narrative, django_content_type
                                WHERE related_object_id = iati_resultdescription.id
                                    AND django_content_type.model = 'resultdescription'
                                    AND related_content_type_id = django_content_type.id
                                ) as description_records
                        ) AS VARCHAR)
                    FROM iati_resultdescription
                    /*
                    WHERE result_id=${activity_result.id}
                     */