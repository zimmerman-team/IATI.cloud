                    SELECT 
                        ref, 
                        type_id, 
                        CASE WHEN secondary_reporter=TRUE THEN '1' ELSE '0' END AS secondary_reporter, 
                        organisation_id,
                        CAST((
                            SELECT ROW_TO_JSON(reporting_org) AS reporting_org FROM (
                                SELECT
                                    iati_activityreportingorganisation.ref AS ref,
                                    iati_activityreportingorganisation.type_id as type,
                                    CASE WHEN iati_activityreportingorganisation.secondary_reporter=TRUE THEN '1' ELSE '0' END AS secondary_reporter,
                                    primary_name AS narrative
                                FROM iati_organisation_organisation
                                WHERE iati_activityreportingorganisation.organisation_id = iati_organisation_organisation.id
                            ) reporting_org
                        ) AS VARCHAR) 
                    FROM iati_activityreportingorganisation 
                    /* WHERE activity_id=${activity.id} */
                    LIMIT 1
