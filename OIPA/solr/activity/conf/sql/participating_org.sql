                   SELECT
                        id,
                        ref,
                        type_id,
                        role_id,
                        CAST((
                            SELECT
                                   ROW_TO_JSON(participating_org_record) AS participating_org
                            FROM (
                                SELECT
                                       ref AS ref,
                                       role_id AS role,
                                       type_id AS type,
                                       JSON_AGG(ROW_TO_JSON(narrative_record)) AS narrative
                                FROM (
                                    SELECT
                                           language_id AS lang,
                                           content AS narrative
                                    FROM iati_narrative, django_content_type
                                    WHERE related_object_id=iati_activityparticipatingorganisation.id
                                        AND django_content_type.model='activityparticipatingorganisation'
                                        AND related_content_type_id=django_content_type.id
                                        AND activity_id=${activity.id}
                                ) AS narrative_record
                            ) AS participating_org_record
                        ) AS VARCHAR)
                    FROM iati_activityparticipatingorganisation
                    WHERE activity_id=${activity.id}