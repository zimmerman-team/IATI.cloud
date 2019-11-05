                    SELECT
                        id,
                        url,
                        file_format_id,
                        TO_CHAR(iso_date::timestamp, 'YYYY-MM-DD') AS iso_date,
                        CAST((
                            SELECT
                                JSON_AGG(ROW_TO_JSON(document_link_records)) as document_link
                            FROM (
                                SELECT
                                    url AS url,
                                    file_format_id AS format,
                                    (
                                        SELECT
                                            ROW_TO_JSON(title_record) AS title
                                        FROM (
                                            SELECT
                                                JSON_AGG(ROW_TO_JSON(narrative_records)) AS narrative
                                            FROM (
                                                     SELECT language_id AS lang,
                                                            content     AS text
                                                     FROM iati_documentlinktitle,
                                                          iati_narrative,
                                                          django_content_type
                                                     WHERE iati_documentlinktitle.document_link_id = iati_documentlink.id
                                                       AND iati_narrative.related_object_id = iati_documentlinktitle.id
                                                       AND iati_narrative.activity_id = iati_documentlink.activity_id
                                                       AND django_content_type.model = 'documentlinktitle'
                                                       AND django_content_type.id = iati_narrative.related_content_type_id
                                            ) AS narrative_records
                                        ) AS title_record
                                    ),
                                    (
                                        SELECT
                                            ROW_TO_JSON(description_record) AS description
                                        FROM (
                                            SELECT
                                                JSON_AGG(ROW_TO_JSON(narrative_records)) AS narrative
                                            FROM (
                                                     SELECT language_id AS lang,
                                                            content     AS text
                                                     FROM iati_documentlinkdescription,
                                                          iati_narrative,
                                                          django_content_type
                                                     WHERE iati_documentlinkdescription.document_link_id = iati_documentlink.id
                                                       AND iati_narrative.related_object_id = iati_documentlinkdescription.id
                                                       AND iati_narrative.activity_id = iati_documentlink.activity_id
                                                       AND django_content_type.model = 'documentlinkdescription'
                                                       AND django_content_type.id = iati_narrative.related_content_type_id
                                            ) AS narrative_records
                                        ) AS description_record
                                    ),
                                    (
                                        SELECT
                                            JSON_AGG(ROW_TO_JSON(category_records)) AS category
                                        FROM (
                                            SELECT
                                                   category_id AS code
                                            FROM iati_documentlinkcategory
                                            WHERE document_link_id = iati_documentlink.id
                                        ) AS category_records
                                    ),
                                    (
                                        SELECT
                                            JSON_AGG(ROW_TO_JSON(language_records)) AS language
                                        FROM (
                                            SELECT
                                                   language_id AS code
                                            FROM iati_documentlinklanguage
                                            WHERE document_link_id = iati_documentlink.id
                                        ) AS language_records
                                    ),
                                    (
                                        SELECT
                                            ROW_TO_JSON(document_date_record) AS document_date
                                        FROM (
                                            SELECT
                                                   TO_CHAR(iso_date::timestamp, 'YYYY-MM-DD') AS iso_date
                                        ) AS document_date_record
                                    )
                                ) AS document_link_records
                        ) AS VARCHAR)
                    FROM iati_documentlink
                    /*
                    WHERE result_id=${activity_result.id}
                        AND activity_id=${activity_result.activity_id}
                     */