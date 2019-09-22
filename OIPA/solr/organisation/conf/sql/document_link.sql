                    SELECT
                        id,
                        url,
                        file_format_id,
                        language_id,
                        TO_CHAR(iso_date::timestamp, 'YYYY-MM-DD') AS iso_date,
                        CAST((
                            SELECT
                                ROW_TO_JSON(document_link_record) AS document_link
                            FROM (
                                SELECT
                                    url AS url,
                                    file_format_id AS format,
                                    TO_CHAR(iso_date::timestamp, 'YYYY-MM-DD') AS document_date,
                                    (
                                        SELECT
                                            JSON_AGG(ROW_TO_JSON(recipient_country_record)) AS recipient_country
                                        FROM (
                                            SELECT
                                                iati_organisation_documentlinkrecipientcountry.recipient_country_id AS code,
                                                (
                                                    SELECT
                                                        JSON_AGG(ROW_TO_JSON(narrative_record)) AS narrative
                                                    FROM (
                                                        SELECT
                                                               language_id AS lang,
                                                               content AS narrative
                                                        FROM iati_organisation_organisationnarrative, django_content_type
                                                        WHERE object_id=iati_organisation_documentlinkrecipientcountry.id
                                                            AND django_content_type.model='documentlinkrecipientcountry'
                                                            AND content_type_id=django_content_type.id
                                                    ) as narrative_record
                                                )
                                            FROM iati_organisation_documentlinkrecipientcountry
                                            WHERE iati_organisation_documentlinkrecipientcountry.document_link_id = iati_organisation_organisationdocumentlink.id
                                        ) AS recipient_country_record
                                    ),
                                    (
                                        SELECT
                                            ROW_TO_JSON(title_record) AS title
                                        FROM (
                                            SELECT
                                                language_id AS lang,
                                                content AS narrative
                                            FROM iati_organisation_organisationnarrative,
                                                 django_content_type,
                                                 iati_organisation_documentlinktitle
                                            WHERE object_id=iati_organisation_documentlinktitle.id
                                                AND django_content_type.model='documentlinktitle'
                                                AND content_type_id=django_content_type.id
                                                AND iati_organisation_documentlinktitle.document_link_id = iati_organisation_organisationdocumentlink.id

                                        ) AS title_record
                                    ),
                                    (
                                        SELECT
                                            ROW_TO_JSON(description_record) AS description
                                        FROM (
                                            SELECT
                                                language_id AS lang,
                                                content AS narrative
                                            FROM iati_organisation_organisationnarrative,
                                                 django_content_type,
                                                 iati_organisation_documentlinkdescription
                                            WHERE object_id=iati_organisation_documentlinkdescription.id
                                                AND django_content_type.model='documentlinkdescription'
                                                AND content_type_id=django_content_type.id
                                                AND iati_organisation_documentlinkdescription.document_link_id = iati_organisation_organisationdocumentlink.id

                                        ) AS description_record
                                    ),
                                    (
                                        SELECT
                                            JSON_AGG(ROW_TO_JSON(category_record)) AS category
                                        FROM (
                                            SELECT
                                                category_id AS code
                                            FROM iati_organisation_organisationdocumentlinkcategory
                                            WHERE iati_organisation_organisationdocumentlinkcategory.document_link_id = iati_organisation_organisationdocumentlink.id

                                        ) AS category_record
                                    ),
                                    (
                                        SELECT
                                            JSON_AGG(ROW_TO_JSON(language_record)) AS language
                                        FROM (
                                            SELECT
                                                language_id AS code
                                            FROM iati_organisation_organisationdocumentlinklanguage
                                            WHERE iati_organisation_organisationdocumentlinklanguage.document_link_id = iati_organisation_organisationdocumentlink.id

                                        ) AS language_record
                                    )
                                ) as document_link_record
                        ) AS VARCHAR)
                    FROM iati_organisation_organisationdocumentlink
                    /*
                    WHERE iati_organisation_organisationdocumentlink.organisation_id = ${organisation.id}
                     */