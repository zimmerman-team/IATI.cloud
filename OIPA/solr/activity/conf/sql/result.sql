                    SELECT
                        type_id AS result_type_code,
                        iati_codelists_resulttype.name AS result_type_name,
                        CASE WHEN iati_result.aggregation_status=TRUE THEN '1' ELSE '0' END AS result_aggregation_status
                    FROM iati_result, iati_codelists_resulttype
                    WHERE activity_id=${activity.id}
                        AND iati_result.type_id = iati_codelists_resulttype.code