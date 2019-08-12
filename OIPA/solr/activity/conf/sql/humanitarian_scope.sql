                    SELECT 
                        id, 
                        type_id, 
                        vocabulary_id, 
                        vocabulary_uri, 
                        code,
                        CAST((
                            SELECT
                                   ROW_TO_JSON(humanitarian_scope_record) AS humanitarian_scope
                            FROM (
                                SELECT
                                       type_id AS type, 
                                       vocabulary_id AS vocabulary, 
                                       vocabulary_uri AS vocabulary_uri, 
                                       code AS code,
                                       JSON_AGG(ROW_TO_JSON(narrative_record)) AS narrative
                                FROM (
                                    SELECT
                                           language_id AS lang,
                                           content AS text
                                    FROM iati_narrative, django_content_type
                                    WHERE related_object_id = iati_humanitarianscope.id
                                        AND django_content_type.model = 'humanitarianscope'
                                        AND related_content_type_id = django_content_type.id
                                ) as narrative_record
                            ) AS humanitarian_scope_record
                        ) AS VARCHAR)  
                    FROM iati_humanitarianscope 
                    /* WHERE activity_id=${activity.id} */