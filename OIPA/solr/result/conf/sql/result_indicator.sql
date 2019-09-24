                    SELECT
                        iati_resultindicator.id AS id,
                        iati_resultindicator.measure_id AS measure_id,
                        CASE WHEN iati_resultindicator.ascending=TRUE THEN '1' ELSE '0' END AS ascending,
                        CASE WHEN iati_resultindicator.aggregation_status=TRUE THEN '1' ELSE '0' END AS aggregation_status,
                        CAST((
                            SELECT
                                JSON_AGG(ROW_TO_JSON(indicator_records)) as indicator
                            FROM (
                                SELECT
                                    iati_resultindicator.measure_id AS measure,
                                    CASE WHEN iati_resultindicator.ascending=TRUE THEN '1' ELSE '0' END AS ascending,
                                    CASE WHEN iati_resultindicator.aggregation_status=TRUE THEN '1' ELSE '0' END AS aggregation_status,
                                    (
                                        SELECT
                                            ROW_TO_JSON(title_record) AS title
                                        FROM (
                                            SELECT
                                                JSON_AGG(ROW_TO_JSON(narrative_records)) AS narrative
                                            FROM (
                                                     SELECT language_id AS lang,
                                                            content     AS text
                                                     FROM iati_resultindicatortitle,
                                                          iati_narrative,
                                                          django_content_type
                                                     WHERE iati_resultindicatortitle.result_indicator_id = iati_resultindicator.id
                                                       AND iati_narrative.related_object_id = iati_resultindicatortitle.id
                                                       AND iati_narrative.activity_id = iati_result.activity_id
                                                       AND django_content_type.model = 'resultindicatortitle'
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
                                                     FROM iati_resultindicatordescription,
                                                          iati_narrative,
                                                          django_content_type
                                                     WHERE iati_resultindicatordescription.result_indicator_id = iati_resultindicator.id
                                                       AND iati_narrative.related_object_id = iati_resultindicatordescription.id
                                                       AND iati_narrative.activity_id = iati_result.activity_id
                                                       AND django_content_type.model = 'resultindicatordescription'
                                                       AND django_content_type.id = iati_narrative.related_content_type_id
                                            ) AS narrative_records
                                        ) AS description_record
                                    ),
                                    (
                                        SELECT
                                            JSON_AGG(ROW_TO_JSON(document_link_records)) AS document_link
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
                                            FROM iati_documentlink
                                            WHERE iati_documentlink.result_indicator_id = iati_resultindicator.id
                                        ) AS document_link_records
                                    ),
                                    (
                                        SELECT
                                            JSON_AGG(ROW_TO_JSON(reference_records)) AS reference
                                        FROM (
                                            SELECT
                                                vocabulary_id AS vocabulary,
                                                code AS code
                                            FROM iati_resultindicatorreference
                                            WHERE iati_resultindicatorreference.result_indicator_id = iati_resultindicator.id

                                        ) AS reference_records
                                    ),
                                    (
                                        SELECT
                                            JSON_AGG(ROW_TO_JSON(baseline_records)) AS baseline
                                        FROM (
                                            SELECT
                                                TO_CHAR(iso_date::timestamp, 'YYYY-MM-DD') AS iso_date,
                                                year AS year,
                                                value AS value,
                                                (
                                                    SELECT
                                                        JSON_AGG(ROW_TO_JSON(location_records)) AS location
                                                    FROM (
                                                        SELECT
                                                            ref AS ref
                                                        FROM iati_location
                                                        WHERE result_indicator_baseline_id = iati_resultindicatorbaseline.id
                                                    ) AS location_records
                                                ),
                                                (
                                                    SELECT
                                                        JSON_AGG(ROW_TO_JSON(dimension_records)) AS dimension
                                                    FROM (
                                                        SELECT
                                                            name AS name,
                                                            value AS value
                                                        FROM iati_resultindicatorbaselinedimension
                                                        WHERE result_indicator_baseline_id = iati_resultindicatorbaseline.id
                                                    ) AS dimension_records
                                                ),
                                                (
                                                    SELECT
                                                        JSON_AGG(ROW_TO_JSON(document_link_records)) AS document_link
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
                                                        FROM iati_documentlink
                                                        WHERE iati_documentlink.result_indicator_baseline_id = iati_resultindicatorbaseline.id
                                                    ) AS document_link_records
                                                ),
                                                (
                                                    SELECT
                                                        ROW_TO_JSON(comment_record) AS comment
                                                    FROM (
                                                        SELECT
                                                            JSON_AGG(ROW_TO_JSON(narrative_records)) AS narrative
                                                        FROM (
                                                            SELECT
                                                                language_id AS lang,
                                                                content     AS text
                                                            FROM iati_resultindicatorbaselinecomment, iati_narrative, django_content_type
                                                            WHERE iati_resultindicatorbaselinecomment.result_indicator_baseline_id = iati_resultindicatorbaseline.id
                                                                AND iati_narrative.related_object_id = iati_resultindicatorbaselinecomment.id
                                                                AND iati_narrative.activity_id = iati_result.activity_id
                                                                AND django_content_type.model = 'resultindicatorbaselinecomment'
                                                                AND django_content_type.id = iati_narrative.related_content_type_id
                                                        ) AS narrative_records
                                                    ) AS comment_record
                                                )
                                            FROM iati_resultindicatorbaseline
                                            WHERE iati_resultindicatorbaseline.result_indicator_id = iati_resultindicator.id
                                        ) AS baseline_records
                                    ),
                                    (
                                        SELECT
                                            JSON_AGG(ROW_TO_JSON(period_records)) AS period
                                        FROM (
                                            SELECT
                                                (
                                                    SELECT
                                                        ROW_TO_JSON(period_start_record) AS period_start
                                                    FROM (
                                                         SELECT
                                                            TO_CHAR(period_start::timestamp, 'YYYY-MM-DD') AS iso_date
                                                    ) AS period_start_record
                                                ),
                                                (
                                                    SELECT
                                                        ROW_TO_JSON(period_end_record) AS period_end
                                                    FROM (
                                                         SELECT
                                                            TO_CHAR(period_end::timestamp, 'YYYY-MM-DD') AS iso_date
                                                    ) AS period_end_record
                                                ),
                                                (
                                                    SELECT
                                                        JSON_AGG(ROW_TO_JSON(target_records)) AS target
                                                    FROM (
                                                        SELECT
                                                            iati_resultindicatorperiodtarget.value AS value,
                                                            (
                                                                SELECT
                                                                    JSON_AGG(ROW_TO_JSON(location_records)) AS location
                                                                FROM (
                                                                    SELECT
                                                                        ref AS ref
                                                                    FROM iati_resultindicatorperiodactuallocation
                                                                    WHERE result_indicator_period_actual_id = iati_resultindicatorperiodtarget.id
                                                                ) AS location_records
                                                            ),
                                                            (
                                                                SELECT
                                                                    JSON_AGG(ROW_TO_JSON(dimension_records)) AS dimension
                                                                FROM (
                                                                    SELECT
                                                                        name AS name,
                                                                        value AS value
                                                                    FROM iati_resultindicatorperiodactualdimension
                                                                        WHERE result_indicator_period_actual_id = iati_resultindicatorperiodtarget.id
                                                                ) AS dimension_records
                                                            ),
                                                            (
                                                                SELECT
                                                                    ROW_TO_JSON(comment_record) AS comment
                                                                FROM (
                                                                    SELECT
                                                                        JSON_AGG(ROW_TO_JSON(narrative_records)) AS narrative
                                                                    FROM (
                                                                        SELECT
                                                                            language_id AS lang,
                                                                            content     AS text
                                                                        FROM iati_resultindicatorperiodtargetcomment, iati_narrative, django_content_type
                                                                        WHERE iati_resultindicatorperiodtargetcomment.result_indicator_period_target_id = iati_resultindicatorperiodtarget.id
                                                                            AND iati_narrative.related_object_id = iati_resultindicatorperiodtargetcomment.id
                                                                            AND iati_narrative.activity_id = iati_result.activity_id
                                                                            AND django_content_type.model = 'resultindicatorperiodactualcomment'
                                                                            AND django_content_type.id = iati_narrative.related_content_type_id
                                                                        ) AS narrative_records
                                                                ) AS comment_record
                                                            ),
                                                            (
                                                                SELECT
                                                                    JSON_AGG(ROW_TO_JSON(document_link_records)) AS document_link
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
                                                                                    SELECT
                                                                                        language_id AS lang,
                                                                                        content     AS text
                                                                                    FROM iati_documentlinktitle, iati_narrative, django_content_type
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
                                                                                    SELECT
                                                                                        language_id AS lang,
                                                                                        content     AS text
                                                                                    FROM iati_documentlinkdescription, iati_narrative, django_content_type
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
                                                                    FROM iati_documentlink
                                                                    WHERE iati_documentlink.result_indicator_period_target_id = iati_resultindicatorperiodtarget.id
                                                                ) AS document_link_records
                                                            )
                                                        FROM iati_resultindicatorperiodtarget
                                                        WHERE iati_resultindicatorperiodtarget.result_indicator_period_id = iati_resultindicatorperiod.id
                                                    ) AS target_records
                                                ),
                                                (
                                                    SELECT
                                                        JSON_AGG(ROW_TO_JSON(actual_records)) AS actual
                                                    FROM (
                                                        SELECT
                                                            iati_resultindicatorperiodactual.value AS value,
                                                            (
                                                                SELECT
                                                                    JSON_AGG(ROW_TO_JSON(location_records)) AS location
                                                                FROM (
                                                                    SELECT
                                                                        ref AS ref
                                                                    FROM iati_resultindicatorperiodactuallocation
                                                                    WHERE result_indicator_period_actual_id = iati_resultindicatorperiodactual.id
                                                                ) AS location_records
                                                            ),
                                                            (
                                                                SELECT
                                                                    JSON_AGG(ROW_TO_JSON(dimension_records)) AS dimension
                                                                FROM (
                                                                    SELECT
                                                                        name AS name,
                                                                        value AS value
                                                                    FROM iati_resultindicatorperiodactualdimension
                                                                        WHERE result_indicator_period_actual_id = iati_resultindicatorperiodactual.id
                                                                ) AS dimension_records
                                                            ),
                                                            (
                                                                SELECT
                                                                    ROW_TO_JSON(comment_record) AS comment
                                                                FROM (
                                                                    SELECT
                                                                        JSON_AGG(ROW_TO_JSON(narrative_records)) AS narrative
                                                                    FROM (
                                                                        SELECT
                                                                            language_id AS lang,
                                                                            content     AS text
                                                                        FROM iati_resultindicatorperiodactualcomment, iati_narrative, django_content_type
                                                                        WHERE iati_resultindicatorperiodactualcomment.result_indicator_period_actual_id = iati_resultindicatorperiodactual.id
                                                                            AND iati_narrative.related_object_id = iati_resultindicatorperiodactualcomment.id
                                                                            AND iati_narrative.activity_id = iati_result.activity_id
                                                                            AND django_content_type.model = 'resultindicatorperiodactualcomment'
                                                                            AND django_content_type.id = iati_narrative.related_content_type_id
                                                                        ) AS narrative_records
                                                                ) AS comment_record
                                                            ),
                                                            (
                                                                SELECT
                                                                    JSON_AGG(ROW_TO_JSON(document_link_records)) AS document_link
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
                                                                                    SELECT
                                                                                        language_id AS lang,
                                                                                        content     AS text
                                                                                    FROM iati_documentlinktitle, iati_narrative, django_content_type
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
                                                                                    SELECT
                                                                                        language_id AS lang,
                                                                                        content     AS text
                                                                                    FROM iati_documentlinkdescription, iati_narrative, django_content_type
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
                                                                    FROM iati_documentlink
                                                                    WHERE iati_documentlink.result_indicator_period_actual_id = iati_resultindicatorperiodactual.id
                                                                ) AS document_link_records
                                                            )
                                                        FROM iati_resultindicatorperiodactual
                                                        WHERE iati_resultindicatorperiodactual.result_indicator_period_id = iati_resultindicatorperiod.id
                                                    ) AS actual_records
                                                )
                                            FROM iati_resultindicatorperiod
                                            WHERE iati_resultindicatorperiod.result_indicator_id = iati_resultindicator.id
                                        ) AS period_records
                                    )
                                ) AS indicator_records
                        ) AS VARCHAR)
                    FROM iati_resultindicator, iati_result
                    /*
                    WHERE iati_result.id = ${activity_result.id}
                        AND iati_resultindicator.result_id = iati_result.id
                     */