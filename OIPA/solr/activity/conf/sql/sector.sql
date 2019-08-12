                    SELECT
                        id,
                        vocabulary_id,
                        vocabulary_uri,
                        sector_id,
                        percentage,
                        CAST((
                            SELECT
                                   ROW_TO_JSON(sector_record) AS sector
                            FROM (
                                SELECT
                                       vocabulary_id AS vocabulary,
                                       vocabulary_uri AS vocabulary_uri,
                                       sector_id AS code,
                                       percentage AS percentage,
                                       JSON_AGG(ROW_TO_JSON(narrative_record)) AS narrative
                                FROM (
                                    SELECT
                                           language_id AS lang,
                                           content AS text
                                    FROM iati_narrative, django_content_type
                                    WHERE related_object_id = iati_activitysector.id
                                        AND django_content_type.model = 'activitysector'
                                        AND related_content_type_id =
                                            django_content_type.id
                                ) as narrative_record
                            ) AS sector_record
                        ) AS VARCHAR)
                    FROM iati_activitysector
                    /* WHERE activity_id=${activity.id} */