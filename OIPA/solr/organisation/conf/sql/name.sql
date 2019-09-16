                     SELECT
                        id,
                        CAST((
                            SELECT
                                JSON_AGG(ROW_TO_JSON(name_record)) AS name
                            FROM (
                                SELECT
                                       language_id AS lang,
                                       content AS narrative
                                FROM iati_organisation_organisationnarrative, django_content_type
                                WHERE object_id=iati_organisation_organisationname.id
                                    AND django_content_type.model='organisationname'
                                    AND content_type_id=django_content_type.id
                                ) as name_record
                        ) AS VARCHAR)
                    FROM iati_organisation_organisationname
                    /*
                    WHERE iati_organisation_organisationname.organisation_id=${organiation.id}
                     */