                   SELECT
                        id,
                        type_id,
                        telephone,
                        email,
                        website,
                        CAST((
                            SELECT
                                   ROW_TO_JSON(constact_info_record) AS constact_info
                            FROM (
                                SELECT
                                    type_id AS type,
                                    telephone AS telephone,
                                    email AS email,
                                    website AS website,
                                    JSON_AGG(ROW_TO_JSON(organisation_narrative_record)) AS organisation_narrative,
                                    JSON_AGG(ROW_TO_JSON(department_narrative_record)) AS department_narrative,
                                    JSON_AGG(ROW_TO_JSON(person_name_narrative_record)) AS person_name_narrative,
                                    JSON_AGG(ROW_TO_JSON(job_title_narrative_record)) AS job_title_narrative,
                                    JSON_AGG(ROW_TO_JSON(mailing_address_narrative_record)) AS mailing_address_narrative
                                FROM
                                     (
                                        SELECT
                                            language_id AS lang,
                                            content AS narrative
                                        FROM iati_narrative, django_content_type, iati_contactinfoorganisation
                                        WHERE related_object_id=iati_contactinfoorganisation.id
                                            AND iati_contactinfoorganisation.contact_info_id=iati_contactinfo.id
                                            AND django_content_type.model='contactinfoorganisation'
                                            AND related_content_type_id=django_content_type.id
                                    ) as organisation_narrative_record,
                                    (
                                        SELECT
                                            language_id AS lang,
                                            content AS narrative
                                        FROM iati_narrative, django_content_type, iati_contactinfodepartment
                                        WHERE related_object_id=iati_contactinfodepartment.id
                                            AND iati_contactinfodepartment.contact_info_id=iati_contactinfo.id
                                            AND django_content_type.model='contactinfodepartment'
                                            AND related_content_type_id=django_content_type.id
                                    ) as department_narrative_record,
                                    (
                                        SELECT
                                            language_id AS lang,
                                            content AS narrative
                                        FROM iati_narrative, django_content_type, iati_contactinfopersonname
                                        WHERE related_object_id=iati_contactinfopersonname.id
                                            AND iati_contactinfopersonname.contact_info_id=iati_contactinfo.id
                                            AND django_content_type.model='contactinfopersonname'
                                            AND related_content_type_id=django_content_type.id
                                    ) as person_name_narrative_record,
                                    (
                                        SELECT
                                            language_id AS lang,
                                            content AS narrative
                                        FROM iati_narrative, django_content_type, iati_contactinfojobtitle
                                        WHERE related_object_id=iati_contactinfojobtitle.id
                                            AND iati_contactinfojobtitle.contact_info_id=iati_contactinfo.id
                                            AND django_content_type.model='contactinfojobtitle'
                                            AND related_content_type_id=django_content_type.id
                                    ) as job_title_narrative_record,
                                    (
                                        SELECT
                                            language_id AS lang,
                                            content AS narrative
                                        FROM iati_narrative, django_content_type, iati_contactinfomailingaddress
                                        WHERE related_object_id=iati_contactinfomailingaddress.id
                                            AND iati_contactinfomailingaddress.contact_info_id=iati_contactinfo.id
                                            AND django_content_type.model='contactinfomailingaddress'
                                            AND related_content_type_id=django_content_type.id
                                    ) as mailing_address_narrative_record
                            ) AS constact_info_record
                        ) AS VARCHAR)
                    FROM iati_contactinfo
                    WHERE activity_id=${activity.id}