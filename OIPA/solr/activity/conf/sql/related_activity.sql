                    SELECT
                        ref,
                        type_id,
                        CAST((
                            SELECT
                                   ROW_TO_JSON(related_activity_record) AS related_activity
                            FROM (
                                SELECT
                                       ref AS ref,
                                       type_id AS type
                            ) AS related_activity_record
                        ) AS VARCHAR)

                    FROM iati_relatedactivity
                    /*
                    WHERE current_activity_id=${activity.id}
                     */
                    ORDER BY id