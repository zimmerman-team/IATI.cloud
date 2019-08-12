                    SELECT
                        id,
                        vocabulary_id,
                        vocabulary_uri,
                        code,
                        CAST((
                            SELECT
                                   ROW_TO_JSON(tag_record) AS tag
                            FROM (
                                SELECT
                                       vocabulary_id AS vocabulary,
                                       vocabulary_uri AS vocabulary_uri,
                                       code AS code,
                                       JSON_AGG(ROW_TO_JSON(narrative_record)) AS narrative
                                FROM (
                                    SELECT
                                           language_id AS lang,
                                           content AS text
                                    FROM iati_narrative, django_content_type
                                    WHERE related_object_id = iati_activitytag.id
                                        AND django_content_type.model = 'activitytag'
                                        AND related_content_type_id = django_content_type.id
                                ) as narrative_record
                            ) AS tag_record
                        ) AS VARCHAR)
                    FROM iati_activitytag
                    WHERE activity_id=${activity.id}