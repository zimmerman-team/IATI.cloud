                    SELECT
                           aid_type_id,
                           vocabulary_id,
                           CAST((
                               SELECT
                                      ROW_TO_JSON(default_aid_type_record) AS default_aid_type
                               FROM (
                                    SELECT
                                           aid_type_id AS code,
                                           vocabulary_id AS vocabulary
                                ) AS default_aid_type_record
                            ) AS VARCHAR)
                    FROM iati_activitydefaultaidtype, iati_codelists_aidtype
                    WHERE iati_activitydefaultaidtype.aid_type_id = iati_codelists_aidtype.code
                        /* AND activity_id=${activity.id}
