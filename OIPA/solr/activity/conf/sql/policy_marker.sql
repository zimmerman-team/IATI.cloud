                    SELECT
                        id,
                        vocabulary_id,
                        vocabulary_uri,
                        code_id,
                        significance_id,
                        CAST((
                            SELECT
                                   ROW_TO_JSON(policy_marker_record) AS policy_marker
                            FROM (
                                SELECT
                                       vocabulary_id AS vocabulary,
                                       vocabulary_uri AS vocabulary_uri,
                                       code_id AS code,
                                       significance_id AS significance,
                                       JSON_AGG(ROW_TO_JSON(narrative_record)) AS narrative
                                FROM (
                                    SELECT
                                           language_id AS lang,
                                           content AS text
                                    FROM iati_narrative, django_content_type
                                    WHERE related_object_id = iati_activitypolicymarker.id
                                        AND django_content_type.model = 'activitypolicymarker'
                                        AND related_content_type_id = django_content_type.id
                                ) as narrative_record
                            ) AS policy_marker_record
                        ) AS VARCHAR)
                    FROM iati_activitypolicymarker
                    /* WHERE activity_id=${activity.id} */