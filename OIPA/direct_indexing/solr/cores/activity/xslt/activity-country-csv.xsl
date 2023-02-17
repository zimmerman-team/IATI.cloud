<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text" encoding="UTF-8"/>
    <xsl:param name="delim" select="','"/>
    <xsl:param name="quote" select="'&quot;'"/>
    <xsl:param name="deliminquote" select="'&quot;,&quot;'"/>
    <xsl:param name="break" select="'&#13;'"/>
    <xsl:param name="iati_identifier" select="iati_identifier" />
    <xsl:variable name="apos">'</xsl:variable>
    <xsl:template match="/">
    </xsl:template>

    <xsl:template match="/">
        <xsl:apply-templates select="response/lst/lst"/>
        <xsl:apply-templates select="response/result/doc"/>

    </xsl:template>

    <xsl:template match="response/lst/lst">
        <xsl>default_lang,</xsl>
        <xsl>default_currency,</xsl>
        <xsl>humanitarian,</xsl>
        <xsl>hierarchy,</xsl>
        <xsl>iati_identifier,</xsl>
        <xsl>reporting_org_ref,</xsl>
        <xsl>reporting_org_type_code,</xsl>
        <xsl>reporting_org_secondary_reporter,</xsl>
        <xsl>reporting_org_narrative,</xsl>
        <xsl>title_narrative,</xsl>
        <xsl>description_narrative,</xsl>
        <xsl>participating_org_ref,</xsl>
        <xsl>participating_org_type,</xsl>
        <xsl>participating_org_role,</xsl>
        <xsl>participating_org_narrative,</xsl>
        <xsl>other_identifier_ref,</xsl>
        <xsl>other_identifier_owner_org_ref,</xsl>
        <xsl>other_identifier_owner_org_narrative,</xsl>
        <xsl>activity_status_code,</xsl>
        <xsl>activity_date_iso_date,</xsl>
        <xsl>activity_date_type,</xsl>
        <xsl>contact_info_organisation_narrative,</xsl>
        <xsl>contact_info_department_narrative,</xsl>
        <xsl>contact_info_person_name_narrative,</xsl>
        <xsl>contact_info_job_title_narrative,</xsl>
        <xsl>contact_info_telephone,</xsl>
        <xsl>contact_info_email,</xsl>
        <xsl>contact_info_website,</xsl>
        <xsl>contact_info_mailing_address_narrative,</xsl>
        <xsl>activity_scope_code,</xsl>
        <xsl>recipient_country_code,</xsl>
        <xsl>recipient_country_percentage,</xsl>
        <xsl>recipient_region_code,</xsl>
        <xsl>recipient_region_percentage,</xsl>
        <xsl>location_ref,</xsl>
        <xsl>location_id_code,</xsl>
        <xsl>location_id_vocabulary,</xsl>
        <xsl>location_reach_code,</xsl>
        <xsl>location_name_narrative,</xsl>
        <xsl>location_description_narrative,</xsl>
        <xsl>location_activity_description_narrative,</xsl>
        <xsl>location_administrative_code,</xsl>
        <xsl>location_administrative_vocabulary,</xsl>
        <xsl>location_administrative_level,</xsl>
        <xsl>location_point_pos,</xsl>
        <xsl>location_exactness_code,</xsl>
        <xsl>location_class_code,</xsl>
        <xsl>location_feature_designation_code,</xsl>
        <xsl>sector_vocabulary,</xsl>
        <xsl>sector_code,</xsl>
        <xsl>sector_percentage,</xsl>
        <xsl>tag_code,</xsl>
        <xsl>tag_vocabulary,</xsl>
        <xsl>tag_narrative,</xsl>
        <xsl>country_budget_items_vocabulary,</xsl>
        <xsl>country_budget_items_budget_item_code,</xsl>
        <xsl>country_budget_items_budget_item_percentage,</xsl>
        <xsl>country_budget_items_budget_description_narrative,</xsl>
        <xsl>humanitarian_scope_type,</xsl>
        <xsl>humanitarian_scope_vocabulary,</xsl>
        <xsl>humanitarian_scope_code,</xsl>
        <xsl>humanitarian_scope_narrative,</xsl>
        <xsl>policy_marker_vocabulary,</xsl>
        <xsl>policy_marker_code,</xsl>
        <xsl>policy_marker_significance,</xsl>
        <xsl>collaboration_type_code,</xsl>
        <xsl>default_flow_type_code,</xsl>
        <xsl>default_finance_type_code,</xsl>
        <xsl>default_aid_type_code,</xsl>
        <xsl>default_aid_type_vocabulary,</xsl>
        <xsl>default_tied_status_code,</xsl>
        <xsl>budget_type,</xsl>
        <xsl>budget_status,</xsl>
        <xsl>budget_period_start_iso_date,</xsl>
        <xsl>budget_period_end_iso_date,</xsl>
        <xsl>budget_value_currency,</xsl>
        <xsl>budget_value_date,</xsl>
        <xsl>budget_value,</xsl>
        <xsl>planned_disbursement_type,</xsl>
        <xsl>planned_disbursement_period_start_iso_date,</xsl>
        <xsl>planned_disbursement_period_end_iso_date,</xsl>
        <xsl>planned_disbursement_value_currency,</xsl>
        <xsl>planned_disbursement_value_date,</xsl>
        <xsl>planned_disbursement_value,</xsl>
        <xsl>planned_disbursement_provider_org_provider_activity_id,</xsl>
        <xsl>planned_disbursement_provider_org_type,</xsl>
        <xsl>planned_disbursement_provider_org_ref,</xsl>
        <xsl>planned_disbursement_provider_org_narrative,</xsl>
        <xsl>capital_spend_percentage,</xsl>
        <xsl>transaction_ref,</xsl>
        <xsl>transaction_humanitarian,</xsl>
        <xsl>transaction_type_code,</xsl>
        <xsl>transaction_date_iso_date,</xsl>
        <xsl>transaction_value_currency,</xsl>
        <xsl>transaction_value_date,</xsl>
        <xsl>transaction_value,</xsl>
        <xsl>transaction_provider_org_provider_activity_id,</xsl>
        <xsl>transaction_provider_org_type,</xsl>
        <xsl>transaction_provider_org_ref,</xsl>
        <xsl>transaction_provider_org_narrative,</xsl>
        <xsl>transaction_receiver_org_receiver_activity_id,</xsl>
        <xsl>transaction_receiver_org_type,</xsl>
        <xsl>transaction_receiver_org_ref,</xsl>
        <xsl>transaction_receiver_org_narrative,</xsl>
        <xsl>transaction_disburstment_channel_code,</xsl>
        <xsl>transaction_sector_vocabulary,</xsl>
        <xsl>transaction_sector_code,</xsl>
        <xsl>transaction_recipient_country_code,</xsl>
        <xsl>transaction_recipient_region_code,</xsl>
        <xsl>transaction_recipient_region_vocabulary,</xsl>
        <xsl>transaction_flow_type_code,</xsl>
        <xsl>transaction_finance_type_code,</xsl>
        <xsl>transaction_aid_type_code,</xsl>
        <xsl>transaction_aid_type_vocabulary,</xsl>
        <xsl>transaction_tied_status_code,</xsl>
        <xsl>document_link_format,</xsl>
        <xsl>document_link_url,</xsl>
        <xsl>document_link_title_narrative,</xsl>
        <xsl>document_link_category_code,</xsl>
        <xsl>document_link_document_date_iso_date,</xsl>
        <xsl>related_activity_ref,</xsl>
        <xsl>related_activity_type,</xsl>
        <xsl>legacy_data_name,</xsl>
        <xsl>legacy_data_value,</xsl>
        <xsl>legacy_data_iati_equivalent,</xsl>
        <xsl>conditions_attached,</xsl>
        <xsl>conditions_condition_type,</xsl>
        <xsl>conditions_condition_narrative,</xsl>
        <xsl>result_type,</xsl>
        <xsl>result_aggregation_status,</xsl>
        <xsl>result_title_narrative,</xsl>
        <xsl>result_description_narrative,</xsl>
        <xsl>result_document_link_format,</xsl>
        <xsl>result_document_link_url,</xsl>
        <xsl>result_document_link_title_narrative,</xsl>
        <xsl>result_document_link_description_narrative,</xsl>
        <xsl>result_document_link_category_code,</xsl>
        <xsl>result_document_link_language_code,</xsl>
        <xsl>result_document_link_document_date_iso_date,</xsl>
        <xsl>result_reference_vocabulary,</xsl>
        <xsl>result_reference_code,</xsl>
        <xsl>result_reference_vocabulary_uri,</xsl>
        <xsl>result_indicator_measure,</xsl>
        <xsl>result_indicator_ascending,</xsl>
        <xsl>result_indicator_aggregation_status,</xsl>
        <xsl>result_indicator_title_narrative,</xsl>
        <xsl>result_indicator_description_narrative,</xsl>
        <xsl>result_indicator_document_link_format,</xsl>
        <xsl>result_indicator_document_link_url,</xsl>
        <xsl>result_indicator_document_link_title_narrative,</xsl>
        <xsl>result_indicator_document_link_description_narrative,</xsl>
        <xsl>result_indicator_document_link_category_code,</xsl>
        <xsl>result_indicator_document_link_language_code,</xsl>
        <xsl>result_indicator_document_link_document_date_iso_date,</xsl>
        <xsl>result_indicator_reference_code,</xsl>
        <xsl>result_indicator_reference_vocabulary,</xsl>
        <xsl>result_indicator_reference_vocabulary_uri,</xsl>
        <xsl>result_indicator_baseline_year,</xsl>
        <xsl>result_indicator_baseline_iso_date,</xsl>
        <xsl>result_indicator_baseline_value,</xsl>
        <xsl>result_indicator_baseline_location_ref,</xsl>
        <xsl>result_indicator_baseline_dimension_name,</xsl>
        <xsl>result_indicator_baseline_dimension_value,</xsl>
        <xsl>result_indicator_baseline_document_link_format,</xsl>
        <xsl>result_indicator_baseline_document_link_url,</xsl>
        <xsl>result_indicator_baseline_document_link_title,</xsl>
        <xsl>result_indicator_baseline_document_link_description,</xsl>
        <xsl>result_indicator_baseline_document_link_category_code,</xsl>
        <xsl>result_indicator_baseline_document_link_language_code,</xsl>
        <xsl>result_indicator_baseline_document_link_document_date_iso_date,</xsl>
        <xsl>result_indicator_baseline_comment_narrative,</xsl>
        <xsl>result_indicator_period_period_start_iso_date,</xsl>
        <xsl>result_indicator_period_period_end_iso_date,</xsl>
        <xsl>result_indicator_period_target_value,</xsl>
        <xsl>result_indicator_period_target_location_ref,</xsl>
        <xsl>result_indicator_period_target_dimension_name,</xsl>
        <xsl>result_indicator_period_target_dimension_value,</xsl>
        <xsl>result_indicator_period_target_comment_narrative,</xsl>
        <xsl>result_indicator_period_target_document_link_format,</xsl>
        <xsl>result_indicator_period_target_document_link_url,</xsl>
        <xsl>result_indicator_period_target_document_link_title_narrative,</xsl>
        <xsl>result_indicator_period_target_document_link_description_narrative,</xsl>
        <xsl>result_indicator_period_target_document_link_category_code,</xsl>
        <xsl>result_indicator_period_target_document_link_language_code,</xsl>
        <xsl>result_indicator_period_target_document_link_document_date_iso_date,</xsl>
        <xsl>result_indicator_period_actual_value,</xsl>
        <xsl>result_indicator_period_actual_location_ref,</xsl>
        <xsl>result_indicator_period_actual_dimension_name,</xsl>
        <xsl>result_indicator_period_actual_dimension_value,</xsl>
        <xsl>result_indicator_period_actual_comment_narrative,</xsl>
        <xsl>result_indicator_period_actual_document_link_format,</xsl>
        <xsl>result_indicator_period_actual_document_link_url,</xsl>
        <xsl>result_indicator_period_actual_document_link_title_narrative,</xsl>
        <xsl>result_indicator_period_actual_document_link_description_narrative,</xsl>
        <xsl>result_indicator_period_actual_document_link_category_code,</xsl>
        <xsl>result_indicator_period_actual_document_link_language_code,</xsl>
        <xsl>result_indicator_period_actual_document_link_document_date_iso_date,</xsl>
        <xsl>crs_add_other_flags_code,</xsl>
        <xsl>crs_add_other_flags_significance,</xsl>
        <xsl>crs_add_loan_terms_rate_1,</xsl>
        <xsl>crs_add_loan_terms_rate_2,</xsl>
        <xsl>crs_add_loan_terms_repayment_type_code,</xsl>
        <xsl>crs_add_loan_terms_repayment_plan_code,</xsl>
        <xsl>crs_add_loan_terms_commitment_date_iso_date,</xsl>
        <xsl>crs_add_loan_terms_repayment_first_date_iso_date,</xsl>
        <xsl>crs_add_loan_terms_repayment_final_date_iso_date,</xsl>
        <xsl>crs_add_loan_status_year,</xsl>
        <xsl>crs_add_loan_status_currency,</xsl>
        <xsl>crs_add_loan_status_value_date,</xsl>
        <xsl>crs_add_loan_status_interest_received,</xsl>
        <xsl>crs_add_loan_status_principal_outstanding,</xsl>
        <xsl>crs_add_channel_code,</xsl>
        <xsl>fss_extraction_date,</xsl>
        <xsl>fss_priority,</xsl>
        <xsl>fss_phaseout_year,</xsl>
        <xsl>fss_forecast_year,</xsl>
        <xsl>fss_forecast_value_date,</xsl>
        <xsl>fss_forecast_currency,</xsl>
        <xsl>fss_forecast_value,</xsl>
        <xsl:value-of select="$break"/>

    </xsl:template>

    <xsl:template match="response/result/doc">

        <xsl:for-each select="arr[@name='recipient_country_code']/str">
            <xsl:value-of select="ancestor::doc/descendant::str[@name='default_lang']"/>
            <xsl:value-of select="$delim"/>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='default_currency']"/>
            <xsl:value-of select="$delim"/>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='humanitarian']"/>
            <xsl:value-of select="$delim"/>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='hierarchy']"/>
            <xsl:value-of select="$delim"/>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='iati_identifier']"/>
            <xsl:value-of select="$delim"/>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='reporting_org_ref']"/>
            <xsl:value-of select="$delim"/>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='reporting_org_type_code']"/>
            <xsl:value-of select="$delim"/>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='reporting_org_secondary_reporter']"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates
                    select="ancestor::doc/descendant::arr[@name='reporting_org_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates
                    select="ancestor::doc/descendant::arr[@name='title_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='description_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='participating_org_ref']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='participating_org_type']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='participating_org_role']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='participating_org_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='other_identifier_ref']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='other_identifier_owner_org_ref']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='other_identifier_owner_org_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='activity_status_code']"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='activity_date_iso_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='activity_date_type']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact_info_organisation_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact_info_department_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact_info_person_name_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact_info_job_title_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact_info_telephone']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact_info_email']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact_info_website']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact_info_mailing_address_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='activity_scope_code']"/>
            <xsl:value-of select="$delim"/>
            <xsl:variable name="recipient_country_code_position" select="position()"/> <!--this give the position of current country-code-->
            <xsl:apply-templates select="self::str"/> <!--this outputs recipient-country-code-->

            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='recipient_country_percentage']/double[$recipient_country_code_position]"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='recipient_region_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='recipient_region_percentage']/double"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_ref']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_id_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_id_vocabulary']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_reach_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_name_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_description_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_activity_description_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_administrative_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_administrative_vocabulary']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_administrative_level']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_point_pos']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_exactness_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_class_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_feature_designation_code']/str"/>
            <xsl:value-of select="$delim"/>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='sector_vocabulary']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='sector_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='sector_percentage']/double"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='tag_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='tag_vocabulary']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='tag_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='country_budget_items_vocabulary']"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='country_budget_items_budget_item_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='country_budget_items_budget_item_percentage']/double"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='country_budget_items_budget_description_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='humanitarian_scope_type']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='humanitarian_scope_vocabulary']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='humanitarian_scope_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='humanitarian_scope_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='policy_marker_vocabulary']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='policy_marker_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='policy_marker_significance']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='collaboration_type_code']"/>
            <xsl:value-of select="$delim"/>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='default_flow_type_code']"/>
            <xsl:value-of select="$delim"/>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='default_finance_type_code']"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='default_aid_type_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='default_aid_type_vocabulary']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='default_tied_status_code']"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget_type']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget_status']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget_period_start_iso_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget_period_end_iso_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget_value_currency']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget_value_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget_value']/double"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned_disbursement_type']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned_disbursement_period_start_iso_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned_disbursement_period_end_iso_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned_disbursement_value_currency']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned_disbursement_value_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned_disbursement_value']/double"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned_disbursement_provider_org_provider_activity_id']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned_disbursement_provider_org_type']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned_disbursement_provider_org_ref']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned_disbursement_provider_org_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:value-of select="ancestor::doc/descendant::double[@name='capital_spend_percentage']"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_ref']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_humanitarian']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_type']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_date_iso_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_value_currency']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_value_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_value']/double"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_provider_org_provider_activity_id']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_provider_org_type']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_provider_org_ref']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_provider_org_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_receiver_org_receiver_activity_id']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_receiver_org_type']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_receiver_org_ref']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_receiver_org_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_disburstment_channel_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_sector_vocabulary']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_sector_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_recipient_country_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_recipient_region_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_recipient_region_vocabulary']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_flow_type_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_finance_type_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_aid_type_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_aid_type_vocabulary']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_tied_status_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='document_link_format']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='document_link_url']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='document_link_title_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='document_link_category_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='document_link_document_date_iso_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='related_activity_ref']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='related_activity_type']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='legacy_data_name']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='legacy_data_value']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='legacy_data_iati_equivalent']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='conditions_attached']"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='conditions_condition_type']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='conditions_condition_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_type']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_aggregation_status']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_title_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_description_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_document_link_format']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_document_link_url']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_document_link_title_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_document_link_description_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_document_link_category_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_document_link_language_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_document_link_document_date_iso_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_reference_vocabulary']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_reference_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_reference_vocabulary_uri']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_measure']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_ascending']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_aggregation_status']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_title_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_description_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_document_link_format']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_document_link_url']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_document_link_title_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_document_link_description_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_document_link_category_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_document_link_language_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_document_link_document_date_iso_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_reference_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_reference_vocabulary']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_reference_vocabulary_uri']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_year']/int"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_iso_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_value']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_location_ref']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_dimension_name']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_dimension_value']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_document_link_format']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_document_link_url']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_document_link_title']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_document_link_description']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_document_link_category_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_document_link_language_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_document_link_document_date_iso_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_comment_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_period_start_iso_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_period_end_iso_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_value']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_location_ref']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_dimension_name']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_dimension_value']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_comment_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_document_link_format']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_document_link_url']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_document_link_title_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_document_link_description_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_document_link_category_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_document_link_language_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_document_link_document_date_iso_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_value']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_location_ref']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_dimension_name']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_dimension_value']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_comment_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_document_link_format']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_document_link_url']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_document_link_title_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_document_link_description_narrative']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_document_link_category_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_document_link_language_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_document_link_document_date_iso_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_other_flags_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_other_flags_significance']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_terms_rate_1']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_terms_rate_2']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_terms_repayment_type_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_terms_repayment_plan_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_terms_commitment_date_iso_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_terms_repayment_first_date_iso_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_terms_repayment_final_date_iso_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_status_year']/int"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_status_currency']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_status_value_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_status_interest_received']/double"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_status_principal_outstanding']/double"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_channel_code']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:value-of select="date[@name='fss_extraction_date']"/>
            <xsl:value-of select="$delim"/>
            <xsl:value-of select="str[@name='fss_priority']"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='fss_phaseout_year']/int"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='fss_forecast_year']/int"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='fss_forecast_value_date']/date"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='fss_forecast_currency']/str"/>
            <xsl:value-of select="$delim"/>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='fss_forecast_value']/double"/>
            <xsl:value-of select="$delim"/>
            <xsl:value-of select="$break"/>
        </xsl:for-each>
    </xsl:template>

    <xsl:template match="arr[*]/str">
        <xsl:if test="position() = 1">
            <xsl>"</xsl>
        </xsl:if>
        <xsl:choose>
            <xsl:when test="position() = last()">
                <xsl:value-of select="."/>
                <xsl>"</xsl>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="concat(normalize-space(), $delim)"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="arr[*]/int">
        <xsl:if test="position() = 1">
            <xsl>"</xsl>
        </xsl:if>
        <xsl:choose>
            <xsl:when test="position() = last()">
                <xsl:value-of select="."/>
                <xsl>"</xsl>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="concat(normalize-space(), $delim)"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <xsl:template match="arr[*]/double">
        <xsl:if test="position() = 1">
            <xsl>"</xsl>
        </xsl:if>
        <xsl:choose>
            <xsl:when test="position() = last()">
                <xsl:value-of select="."/>
                <xsl>"</xsl>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="concat(normalize-space(), $delim)"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <xsl:template match="arr[*]/date">
        <xsl:if test="position() = 1">
            <xsl>"</xsl>
        </xsl:if>
        <xsl:choose>
            <xsl:when test="position() = last()">
                <!--we don't want timestamp at the end of the date-->
                <xsl:value-of select="substring-before(normalize-space(),'T00:00:00Z')"/>
                <xsl>"</xsl>
            </xsl:when>
            <xsl:otherwise>
                <!--we don't want time stamp at the end of the dates-->
                <xsl:value-of select="concat(substring-before(normalize-space(),'T00:00:00Z'), $delim)"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <xsl:template match="arr[contains(@name,'_narrative')]/str">
        <xsl:if test="position() = 1">
            <xsl>"</xsl>
        </xsl:if>
        <xsl:choose>
            <xsl:when test="position() = last()">
                <xsl:value-of select="."/>
                <xsl>"</xsl>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="concat(normalize-space(), $delim)"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <xsl:template match="arr[contains(@name,'_title')]/str">
        <xsl:if test="position() = 1">
            <xsl>"</xsl>
        </xsl:if>
        <xsl:choose>
            <xsl:when test="position() = last()">
                <xsl:value-of select="."/>
                <xsl>"</xsl>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="concat(normalize-space(), $delim)"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <xsl:template match="arr[contains(@name,'_description')]/str">
        <xsl:if test="position() = 1">
            <xsl>"</xsl>
        </xsl:if>
        <xsl:choose>
            <xsl:when test="position() = last()">
                <xsl:value-of select="."/>
                <xsl>"</xsl>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="concat(normalize-space(), $delim)"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>
