                        SELECT
                            iati_narrative.content AS content
                        FROM iati_organisation_organisationnarrative, django_content_type
                        /*
                        WHERE iati_organisation_organisationnarrative.object_id=${organisation_name.id}
                            AND iati_organisation_organisationnarrative.organisation_id=${organisation.id}
                            AND django_content_type.model='organisationname'
                            AND django_content_type.id=iati_organisation_organisationnarrative.content_type_id
                         */