                    SELECT 
                        id, 
                        country_id, 
                        percentage,
                        CAST((
                            SELECT
                                   ROW_TO_JSON(recipient_country_record) AS recipient_country
                            FROM (
                                SELECT
                                       country_id AS code,
                                       percentage AS percentage,
                                       JSON_AGG(ROW_TO_JSON(narrative_record)) AS narrative
                                FROM (
                                    SELECT
                                           language_id AS lang,
                                           content AS text
                                    FROM iati_narrative, django_content_type
                                    WHERE related_object_id = iati_activityrecipientcountry.id
                                        AND django_content_type.model = 'activityrecipientcountry'
                                        AND related_content_type_id =
                                            django_content_type.id
                                ) as narrative_record
                            ) AS recipient_country_record
                        ) AS VARCHAR) 
                    FROM iati_activityrecipientcountry 
                    /* WHERE activity_id=${activity.id} */