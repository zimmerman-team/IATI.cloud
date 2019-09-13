                    SELECT
                        id,
                        file_format_id,
                        url,
                        TO_CHAR(iso_date::timestamp, 'YYYY-MM-DD') AS iso_date,
                        CAST((
                            SELECT
                                   ROW_TO_JSON(document_link_record) AS document_link
                            FROM (
                                SELECT
                                       file_format_id AS format,
                                       url AS url,
                                       (
                                            SELECT
                                                JSON_AGG(ROW_TO_JSON(title_record)) AS title
                                            FROM (
                                                SELECT
                                                       language_id AS lang,
                                                       content AS text
                                                FROM iati_narrative, django_content_type, iati_documentlinktitle
                                                WHERE iati_documentlinktitle.document_link_id = iati_documentlink.id
                                                    AND related_object_id = iati_documentlinktitle.id
                                                    AND django_content_type.model = 'documentlinktitle'
                                                    AND related_content_type_id = django_content_type.id
                                            ) as title_record
                                        ),
                                        (
                                            SELECT
                                                JSON_AGG(ROW_TO_JSON(category_record)) AS category
                                            FROM (
                                                SELECT
                                                       iati_documentlinkcategory.category_id AS code,
                                                       name AS name
                                                FROM iati_documentlinkcategory, iati_codelists_documentcategory
                                                WHERE iati_documentlinkcategory.document_link_id = iati_documentlink.id
                                                    AND iati_documentlinkcategory.category_id = iati_codelists_documentcategory.code
                                            ) as category_record
                                        ),
                                        (
                                            SELECT
                                                JSON_AGG(ROW_TO_JSON(language_record)) AS language
                                            FROM (
                                                SELECT
                                                       language_id AS code
                                                FROM iati_documentlinklanguage
                                                WHERE iati_documentlinklanguage.document_link_id = iati_documentlink.id
                                            ) as language_record
                                        ),
                                        (
                                            SELECT
                                                JSON_AGG(ROW_TO_JSON(language_record)) AS language
                                            FROM (
                                                SELECT
                                                       language_id AS code
                                                FROM iati_documentlinklanguage
                                                WHERE iati_documentlinklanguage.document_link_id = iati_documentlink.id
                                            ) as language_record
                                        ),
                                        (
                                            SELECT
                                                JSON_AGG(ROW_TO_JSON(document_date_record)) AS document_date
                                            FROM (
                                                SELECT
                                                    TO_CHAR(iso_date::timestamp, 'YYYY-MM-DD') AS iso_date
                                            ) AS document_date_record
                                        )
                            ) AS document_link_record
                        ) AS VARCHAR)
                    FROM iati_documentlink
                    /*
                    WHERE activity_id=${activity.id}
                        AND result_id IS NULL
                        AND result_indicator_id IS NULL
                        AND result_indicator_baseline_id IS NULL
                        AND result_indicator_period_actual_id IS NULL
                        AND result_indicator_period_target_id IS NULL
                     */