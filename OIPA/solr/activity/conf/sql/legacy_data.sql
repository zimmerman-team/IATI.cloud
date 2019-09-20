                    SELECT
                        name,
                        value,
                        iati_equivalent,
                        CAST((
                            SELECT
                                   ROW_TO_JSON(legacy_data_record) AS legacy_data
                            FROM (
                                SELECT
                                       name AS name,
                                       value AS value,
                                       iati_equivalent AS iati_equivalent
                            ) AS legacy_data_record
                        ) AS VARCHAR)
                    FROM iati_legacydata
                    /*
                    WHERE activity_id=${activity.id}
                     */
                    ORDER BY id