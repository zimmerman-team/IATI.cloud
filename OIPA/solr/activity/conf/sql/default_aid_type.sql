                    SELECT
                           aid_type_id,
                           vocabulary_id,
                           ica.code AS category_code,
                           ica.name AS category_name,
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
                    LEFT OUTER JOIN iati_codelists_aidtypecategory ica on iati_codelists_aidtype.category_id = ica.code
                    /*
                    WHERE activity_id=${activity.id}
                        AND iati_activitydefaultaidtype.aid_type_id = iati_codelists_aidtype.code
                     */