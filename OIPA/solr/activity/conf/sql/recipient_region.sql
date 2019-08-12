                    SELECT
                        id,
                        region_id,
                        percentage,
                        vocabulary_id,
                        vocabulary_uri,
                        CAST((
                            SELECT
                                   ROW_TO_JSON(recipient_region_record) AS recipient_region
                            FROM (
                                SELECT
                                       region_id AS code,
                                       vocabulary_id AS vocabulary,
                                       vocabulary_uri AS vocabulary_uri,
                                       percentage AS percentage,
                                       JSON_AGG(ROW_TO_JSON(narrative_record)) AS narrative
                                FROM (
                                    SELECT
                                           language_id AS lang,
                                           content AS text
                                    FROM iati_narrative, django_content_type
                                    WHERE related_object_id = iati_activityrecipientregion.id
                                        AND django_content_type.model = 'activityrecipientregion'
                                        AND related_content_type_id = django_content_type.id
                                ) as narrative_record
                            ) AS recipient_region_record
                        ) AS VARCHAR)
                    FROM iati_activityrecipientregion
                    WHERE activity_id=${activity.id}