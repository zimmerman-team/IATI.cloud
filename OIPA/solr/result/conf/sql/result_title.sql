                    SELECT
                        id,
                        CAST((
                            SELECT
                                JSON_AGG(ROW_TO_JSON(title_records)) as title
                            FROM (
                                SELECT
                                       language_id AS lang,
                                       content AS narrative
                                FROM iati_narrative, django_content_type
                                WHERE related_object_id = iati_resulttitle.id
                                    AND django_content_type.model = 'resulttitle'
                                    AND related_content_type_id = django_content_type.id
                                ) as title_records
                        ) AS VARCHAR)
                    FROM iati_resulttitle
                    /*
                    WHERE result_id=${activity_result.id}
                     */