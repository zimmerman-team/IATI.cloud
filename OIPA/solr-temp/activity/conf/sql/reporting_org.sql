                    SELECT
                        ref,
                        iati_activityreportingorganisation.type_id AS type_id,
                        CASE WHEN secondary_reporter=TRUE THEN '1' ELSE '0' END AS secondary_reporter,
                        organisation_id,
                        iati_codelists_organisationtype.name AS type_name,
                        CAST((
                            SELECT ROW_TO_JSON(reporting_org) AS reporting_org FROM (
                                SELECT
                                    iati_activityreportingorganisation.ref AS ref,
                                    CASE WHEN iati_activityreportingorganisation.secondary_reporter=TRUE THEN '1' ELSE '0' END AS secondary_reporter,
                                    primary_name AS narrative,
                                    (
                                        SELECT ROW_TO_JSON(type_record) AS type FROM (
                                            SELECT
                                                iati_activityreportingorganisation.type_id as code,
                                                iati_codelists_organisationtype.name as name
                                        ) type_record
                                    )
                                FROM iati_organisation_organisation, iati_codelists_organisationtype
                                WHERE iati_activityreportingorganisation.organisation_id = iati_organisation_organisation.id
                                    AND iati_organisation_organisation.type_id = iati_codelists_organisationtype.code
                            ) reporting_org
                        ) AS VARCHAR)
                    FROM iati_activityreportingorganisation, iati_organisation_organisation, iati_codelists_organisationtype
                    /* WHERE activity_id=${activity.id}
                        AND iati_activityreportingorganisation.organisation_id = iati_organisation_organisation.id
                        AND iati_organisation_organisation.type_id = iati_codelists_organisationtype.code */
                    LIMIT 1
