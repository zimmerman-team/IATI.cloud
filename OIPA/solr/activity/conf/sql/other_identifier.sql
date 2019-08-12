                    SELECT
                        id,
                        identifier,
                        type_id,
                        owner_ref,
                        CAST((
                            SELECT
                                   ROW_TO_JSON(other_identifier_record) AS other_identifier
                            FROM (
                                SELECT
                                       identifier AS ref,
                                       type_id AS type,
                                       owner_ref AS owner_org_ref,
                                       JSON_AGG(ROW_TO_JSON(narrative_record)) AS owner_org_narrative
                                FROM (
                                    SELECT
                                           language_id AS lang,
                                           content AS text
                                    FROM iati_narrative, django_content_type
                                    WHERE related_object_id = iati_otheridentifier.id
                                        AND django_content_type.model = 'otheridentifier'
                                        AND related_content_type_id =
                                            django_content_type.id
                                ) as narrative_record
                            ) AS other_identifier_record
                        ) AS VARCHAR)
                    FROM iati_otheridentifier
                    /* WHERE activity_id=${activity.id}