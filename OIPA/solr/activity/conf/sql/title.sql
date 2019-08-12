                    SELECT 
                        id,
                        CAST((
                            SELECT
                                JSON_AGG(ROW_TO_JSON(title)) as title
                            FROM (
                                SELECT
                                       language_id AS lang,
                                       content AS narrative
                                FROM iati_narrative, django_content_type
                                WHERE related_object_id=iati_title.id
                                    AND django_content_type.model='title'
                                    AND related_content_type_id=django_content_type.id
                                ) as title
                        ) AS VARCHAR)
                    FROM iati_title
                    WHERE activity_id=${activity.id}