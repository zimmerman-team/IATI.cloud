                    SELECT
                        vocabulary_id,
                        iati_resultreference.code AS code,
                        vocabulary_uri,
                        CAST((
                            SELECT ROW_TO_JSON(resultreference_record) AS result_reference FROM
                            (
                                SELECT
                                    iati_resultreference.code AS code,
                                    vocabulary_uri,
                                    (
                                        SELECT
                                             ROW_TO_JSON(iati_vocabulary_resultvocabulary_record) AS vocabulary
                                        FROM (
                                            SELECT
                                                   iati_vocabulary_resultvocabulary.code AS code,
                                                    iati_vocabulary_resultvocabulary.name AS name
                                        ) iati_vocabulary_resultvocabulary_record
                                    )
                            ) resultreference_record
                        ) AS VARCHAR)
                    FROM iati_resultreference, iati_vocabulary_resultvocabulary
                    /*
                    WHERE result_id=${activity_result.id}
                        AND iati_resultreference.vocabulary_id = iati_vocabulary_resultvocabulary.code
                     */