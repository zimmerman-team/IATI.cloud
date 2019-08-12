                    SELECT
                        id,
                        ref,
                        location_reach_id,
                        location_id_vocabulary_id,
                        location_id_code,
                        ST_AsText(point_pos) AS point_pos,
                        exactness_id,
                        location_class_id,
                        feature_designation_id,
                        CAST((
                            SELECT
                                   ROW_TO_JSON(location_record) AS location
                            FROM (
                                SELECT
                                       ref AS ref,
                                       location_reach_id AS location_reach_code,
                                       location_id_vocabulary_id AS location_id_vocabulary,
                                       location_id_code AS location_id_code,
                                       ST_AsText(point_pos) AS point_pos,
                                       exactness_id AS exactness_code,
                                       location_class_id AS location_class_code,
                                       feature_designation_id AS feature_designation_code,
                                       JSON_AGG(ROW_TO_JSON(name_narrative_record)) AS name_narrative,
                                       JSON_AGG(ROW_TO_JSON(description_narrative_record)) AS description_narrative,
                                       JSON_AGG(ROW_TO_JSON(administrative_record)) AS administrative
                                FROM (
                                        SELECT
                                            language_id AS lang,
                                            content AS text
                                        FROM iati_narrative, django_content_type, iati_locationname
                                        WHERE related_object_id = iati_locationname.id
                                            AND iati_locationname.location_id = iati_location.id
                                            AND django_content_type.model = 'locationname'
                                            AND related_content_type_id = django_content_type.id
                                    ) as name_narrative_record,
                                    (
                                        SELECT
                                            language_id AS lang,
                                            content AS text
                                        FROM iati_narrative, django_content_type, iati_locationdescription
                                        WHERE related_object_id = iati_locationdescription.id
                                            AND iati_locationdescription.location_id = iati_location.id
                                            AND django_content_type.model = 'locationdescription'
                                            AND related_content_type_id = django_content_type.id
                                    ) as description_narrative_record,
                                    (
                                        SELECT
                                            vocabulary_id AS vocabulary,
                                            level AS level,
                                            code  AS code
                                        FROM iati_locationadministrative
                                        WHERE iati_locationadministrative.location_id = iati_location.id
                                    ) as administrative_record
                            ) AS location_record
                        ) AS VARCHAR)
                    FROM iati_location
                    WHERE activity_id=${activity.id}
