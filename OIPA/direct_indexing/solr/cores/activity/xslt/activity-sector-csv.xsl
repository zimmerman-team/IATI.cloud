<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xal="http://www.w3.org/1999/XSL/Transform">
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
        <xsl:if test="ancestor::response/descendant::str[@name='default_lang']">
            <xsl>default_lang,</xsl>
        </xsl:if>

        <xsl:if test="ancestor::response/descendant::str[@name='default_currency']">
            <xsl>default_currency,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::str[@name='humanitarian']">
            <xsl>humanitarian,</xsl>
        </xsl:if>

        <xsl:if test="ancestor::response/descendant::str[@name='hierarchy']">
            <xsl>hierarchy,</xsl>
        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::str[@name='iati_identifier']">
            <xsl>iati_identifier,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::str[@name='reporting_org_ref']">
            <xsl>reporting_org_ref,</xsl>
        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::str[@name='reporting_org_type_code']">
            <xsl>reporting_org_type_code,</xsl>
        </xsl:if>

        <xsl:if test="ancestor::response/descendant::str[@name='reporting_org_secondary_reporter']">
            <xsl>reporting_org_secondary_reporter,</xsl>
        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='reporting_org_narrative']/str">
            <xsl>reporting_org_narrative,</xsl>
        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='title_narrative']/str">
            <xsl>title_narrative,</xsl>
        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='description_narrative']/str">
            <xsl>description_narrative,</xsl>
        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='participating_org_ref']/str">
            <xsl>participating_org_ref,</xsl>
        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='participating_org_type']/str">
            <xsl>participating_org_type,</xsl>
        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='participating_org_role']/str">
            <xsl>participating_org_role,</xsl>
        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='participating_org_narrative']/str">
            <xsl>participating_org_narrative,</xsl>
        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='other_identifier_ref']/str">
            <xsl>other_identifier_ref,</xsl>
        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='other_identifier_owner_org_ref']/str">
            <xsl>other_identifier_owner_org_ref,</xsl>
        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='other_identifier_owner_org_narrative']/str">
            <xsl>other_identifier_owner_org_narrative,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::str[@name='activity_status_code']">
            <xsl>activity_status_code,</xsl>
        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='activity_date_iso_date']/date">
            <xsl>activity_date_iso_date,</xsl>
        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='activity_date_type']/str">
            <xsl>activity_date_type,</xsl>
        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='contact_info_organisation_narrative']/str">
            <xsl>contact_info_organisation_narrative,</xsl>
        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='contact_info_department_narrative']/str">
            <xsl>contact_info_department_narrative,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='contact_info_person_name_narrative']/str">
            <xsl>contact_info_person_name_narrative,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='contact_info_job_title_narrative']/str">
            <xsl>contact_info_job_title_narrative,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='contact_info_telephone']/str">
            <xsl>contact_info_telephone,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='contact_info_email']/str">
            <xsl>contact_info_email,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='contact_info_website']/str">
            <xsl>contact_info_website,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='contact_info_mailing_address_narrative']/str">
            <xsl>contact_info_mailing_address_narrative,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::str[@name='activity_scope_code']">
            <xsl>activity_scope_code,</xsl>

        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='recipient_country_code']/str">
            <xsl>recipient_country_code,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='recipient_country_percentage']/double">
            <xsl>recipient_country_percentage,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='recipient_region_code']/str">
            <xsl>recipient_region_code,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='recipient_region_percentage']/double">
            <xsl>recipient_region_percentage,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='location_ref']/str">
            <xsl>location_ref,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='location_id_code']/str">
            <xsl>location_id_code,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='location_id_vocabulary']/str">
            <xsl>location_id_vocabulary,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='location_reach_code']/str">
            <xsl>location_reach_code,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='location_name_narrative']/str">
            <xsl>location_name_narrative,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='location_description_narrative']/str">
            <xsl>location_description_narrative,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='location_activity_description_narrative']/str">
            <xsl>location_activity_description_narrative,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='location_administrative_code']/str">
            <xsl>location_administrative_code,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='location_administrative_vocabulary']/str">
            <xsl>location_administrative_vocabulary,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='location_administrative_level']/str">
            <xsl>location_administrative_level,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='location_point_pos']/str">
            <xsl>location_point_pos,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='location_exactness_code']/str">
            <xsl>location_exactness_code,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='location_class_code']/str">
            <xsl>location_class_code,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='location_feature_designation_code']/str">
            <xsl>location_feature_designation_code,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='sector_vocabulary']/str">
            <xsl>sector_vocabulary,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='sector_code']/str">
            <xsl>sector_code,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='sector_percentage']/double">
            <xsl>sector_percentage,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='tag_code']/str">
            <xsl>tag_code,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='tag_vocabulary']/str">
            <xsl>tag_vocabulary,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='tag_narrative']/str">
            <xsl>tag_narrative,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::str[@name='country_budget_items_vocabulary']">
            <xsl>country_budget_items_vocabulary,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='country_budget_items_budget_item_code']/str">
            <xsl>country_budget_items_budget_item_code,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='country_budget_items_budget_item_percentage']/double">
            <xsl>country_budget_items_budget_item_percentage,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='country_budget_items_budget_description_narrative']/str">
            <xsl>country_budget_items_budget_description_narrative,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='humanitarian_scope_type']/str">
            <xsl>humanitarian_scope_type,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='humanitarian_scope_vocabulary']/str">
            <xsl>humanitarian_scope_vocabulary,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='humanitarian_scope_code']/str">
            <xsl>humanitarian_scope_code,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='humanitarian_scope_narrative']/str">
            <xsl>humanitarian_scope_narrative,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='policy_marker_vocabulary']/str">
            <xsl>policy_marker_vocabulary,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='policy_marker_code']/str">
            <xsl>policy_marker_code,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='policy_marker_significance']/str">
            <xsl>policy_marker_significance,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::str[@name='collaboration_type_code']">
            <xsl>collaboration_type_code,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::str[@name='default_flow_type_code']">
            <xsl>default_flow_type_code,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::str[@name='default_finance_type_code']">
            <xsl>default_finance_type_code,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='default_aid_type_code']/str">
            <xsl>default_aid_type_code,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='default_aid_type_vocabulary']/str">
            <xsl>default_aid_type_vocabulary,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::str[@name='default_tied_status_code']">
            <xsl>default_tied_status_code,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='budget_type']/str">
            <xsl>budget_type,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='budget_status']/str">
            <xsl>budget_status,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='budget_period_start_iso_date']/date">
            <xsl>budget_period_start_iso_date,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='budget_period_end_iso_date']/date">
            <xsl>budget_period_end_iso_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='budget_value_currency']/str">
            <xsl>budget_value_currency,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='budget_value_date']/date">
            <xsl>budget_value_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='budget_value']/double">
            <xsl>budget_value,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='planned_disbursement_type']/str">
            <xsl>planned_disbursement_type,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='planned_disbursement_period_start_iso_date']/date">
            <xsl>planned_disbursement_period_start_iso_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='planned_disbursement_period_end_iso_date']/date">
            <xsl>planned_disbursement_period_end_iso_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='planned_disbursement_value_currency']/str">
            <xsl>planned_disbursement_value_currency,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='planned_disbursement_value_date']/date">
            <xsl>planned_disbursement_value_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='planned_disbursement_value']/double">
            <xsl>planned_disbursement_value,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='planned_disbursement_provider_org_provider_activity_id']/str">
            <xsl>planned_disbursement_provider_org_provider_activity_id,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='planned_disbursement_provider_org-type']/str">
            <xsl>planned_disbursement_provider_org_type,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='planned_disbursement_provider_org_ref']/str">
            <xsl>planned_disbursement_provider_org_ref,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='planned_disbursement_provider_org_narrative']/str">
            <xsl>planned_disbursement_provider_org_narrative,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::double[@name='capital_spend_percentage']">
            <xsl>capital_spend_percentage,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::arr[@name='transaction_ref']/str">
            <xsl>transaction_ref,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_humanitarian']/str">
            <xsl>transaction_humanitarian,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_type']/str">
            <xsl>transaction_type_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_date_iso_date']/date">
            <xsl>transaction_date_iso_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_value_currency']/str">
            <xsl>transaction_value_currency,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_value_date']/date">
            <xsl>transaction_value_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_value']/double">
            <xsl>transaction_value,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_provider_org_provider_activity_id']/str">
            <xsl>transaction_provider_org_provider_activity_id,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_provider_org_type']/str">
            <xsl>transaction_provider_org_type,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_provider_org_ref']/str">
            <xsl>transaction_provider_org_ref,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_provider_org_narrative']/str">
            <xsl>transaction_provider_org_narrative,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_receiver_org_receiver_activity_id']/str">
            <xsl>transaction_receiver_org_receiver_activity_id,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_receiver_org_type']/str">
            <xsl>transaction_receiver_org_type,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_receiver_org_ref']/str">
            <xsl>transaction_receiver_org_ref,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_receiver_org_narrative']/str">
            <xsl>transaction_receiver_org_narrative,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_disbursement_channel_code']/str">
            <xsl>transaction_disburstment_channel_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_sector_vocabulary']/str">
            <xsl>transaction_sector_vocabulary,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_sector_code']/str">
            <xsl>transaction_sector_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_recipient_country_code']/str">
            <xsl>transaction_recipient_country_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_recipient_region_code']/str">
            <xsl>transaction_recipient_region_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_receipient_region_vocabulary']/str">
            <xsl>transaction_recipient_region_vocabulary,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_flow_type_code']/str">
            <xsl>transaction_flow_type_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_finance_type_code']/str">
            <xsl>transaction_finance_type_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_aid_type_code']/str">
            <xsl>transaction_aid_type_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_aid_type_vocabulary']/str">
            <xsl>transaction_aid_type_vocabulary,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction_tied_status_code']/str">
            <xsl>transaction_tied_status_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='document_link_format']/str">
            <xsl>document_link_format,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='document_link_url']/str">
            <xsl>document_link_url,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='document_link_title_narrative']/str">
            <xsl>document_link_title_narrative,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='document_link_category_code']/str">
            <xsl>document_link_category_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='document_link_document_date_iso_date']/date">
            <xsl>document_link_document_date_iso_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='related_activity_ref']/str">
            <xsl>related_activity_ref,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='related_activity_type']/str">
            <xsl>related_activity_type,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='legacy_data_name']/str">
            <xsl>legacy_data_name,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='legacy_data_value']/str">
            <xsl>legacy_data_value,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='legacy_data_iati_equivalent']/str">
            <xsl>legacy_data_iati_equivalent,</xsl>

        </xsl:if>

        <xsl:if test="ancestor::response/descendant::str[@name='conditions_attached']">
            <xsl>conditions_attached,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='conditions_condition_type']/str">
            <xsl>conditions_condition_type,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='conditions_condition_narrative']/str">
            <xsl>conditions_condition_narrative,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_type']/str">
            <xsl>result_type,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_aggregation_status']/str">
            <xsl>result_aggregation_status,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_title_narrative']/str">
            <xsl>result_title_narrative,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_description_narrative']/str">
            <xsl>result_description_narrative,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_document_link_format']/str">
            <xsl>result_document_link_format,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_document_link_url']/str">
            <xsl>result_document_link_url,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_document_link_title_narrative']/str">
            <xsl>result_document_link_title_narrative,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_document_link_description_narrative']/str">
            <xsl>result_document_link_description_narrative,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_document_link_category_code']/str">
            <xsl>result_document_link_category_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_document_link_language_code']/str">
            <xsl>result_document_link_language_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_document_link_document_date_iso_date']/date">
            <xsl>result_document_link_document_date_iso_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_reference_vocabulary']/str">
            <xsl>result_reference_vocabulary,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_reference_code']/str">
            <xsl>result_reference_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_reference_vocabulary']/str">
            <xsl>result_reference_vocabulary_uri,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_measure']/str">
            <xsl>result_indicator_measure,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_ascending']/str">
            <xsl>result_indicator_ascending,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_aggregation_status']/str">
            <xsl>result_indicator_aggregation_status,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_title_narrative']/str">
            <xsl>result_indicator_title_narrative,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_description_narrative']/str">
            <xsl>result_indicator_description_narrative,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_document_link_format']/str">
            <xsl>result_indicator_document_link_format,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_document_link_url']/str">
            <xsl>result_indicator_document_link_url,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_document_link_title_narrative']/str">
            <xsl>result_indicator_document_link_title_narrative,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_document_link_description_narrative']/str">
            <xsl>result_indicator_document_link_description_narrative,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_document_link_category_code']/str">
            <xsl>result_indicator_document_link_category_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_document_link_language_code']/str">
            <xsl>result_indicator_document_link_language_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_document_link_document_date_iso_date']/date">
            <xsl>result_indicator_document_link_document_date_iso_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_reference_code']/str">
            <xsl>result_indicator_reference_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_reference_vocabulary']/str">
            <xsl>result_indicator_reference_vocabulary,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_reference_vocabulary_uri']/str">
            <xsl>result_indicator_reference_vocabulary_uri,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_baseline_year']/int">
            <xsl>result_indicator_baseline_year,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_baseline_iso_date']/date">
            <xsl>result_indicator_baseline_iso_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_baseline_value']/str">
            <xsl>result_indicator_baseline_value,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_baseline_location_ref']/str">
            <xsl>result_indicator_baseline_location_ref,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_baseline_dimension_name']/str">
            <xsl>result_indicator_baseline_dimension_name,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_baseline_dimension_value']/str">
            <xsl>result_indicator_baseline_dimension_value,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_baseline_document_link_format']/str">
            <xsl>result_indicator_baseline_document_link_format,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_baseline_document_link_url']/str">
            <xsl>result_indicator_baseline_document_link_url,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_baseline_document_link_title']/str">
            <xsl>result_indicator_baseline_document_link_title,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_baseline_document_link_description']/str">
            <xsl>result_indicator_baseline_document_link_description,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_baseline_document_link_category_code']/str">
            <xsl>result_indicator_baseline_document_link_category_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_baseline_document_link_language_code']/str">
            <xsl>result_indicator_baseline_document_link_language_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_baseline_document_link_document_date_iso_date']/date">
            <xsl>result_indicator_baseline_document_link_document_date_iso_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_baseline_comment_narrative']/str">
            <xsl>result_indicator_baseline_comment_narrative,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_period_start_iso_date']/date">
            <xsl>result_indicator_period_period_start_iso_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_period_end_iso_date']/date">
            <xsl>result_indicator_period_period_end_iso_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_target_value']/str">
            <xsl>result_indicator_period_target_value,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_target_location_ref']/str">
            <xsl>result_indicator_period_target_location_ref,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_target_dimension_name']/str">
            <xsl>result_indicator_period_target_dimension_name,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_target_dimension_value']/str">
            <xsl>result_indicator_period_target_dimension_value,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_target_comment_narrative']/str">
            <xsl>result_indicator_period_target_comment_narrative,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_target_document_link_format']/str">
            <xsl>result_indicator_period_target_document_link_format,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_target_document_link_url']/str">
            <xsl>result_indicator_period_target_document_link_url,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_target_document_link_title_narrative']/str">
            <xsl>result_indicator_period_target_document_link_title_narrative,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_target_document_link_description_narrative']/str">
            <xsl>result_indicator_period_target_document_link_description_narrative,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_target_document_link_category_code']/str">
            <xsl>result_indicator_period_target_document_link_category_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_target_document_link_language_code']/str">
            <xsl>result_indicator_period_target_document_link_language_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_target_document_link_document_date_iso_date']/date">
            <xsl>result_indicator_period_target_document_link_document_date_iso_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_value']/str">
            <xsl>result_indicator_period_actual_value,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_location_ref']/str">
            <xsl>result_indicator_period_actual_location_ref,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_dimension_name']/str">
            <xsl>result_indicator_period_actual_dimension_name,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_dimension_value']/str">
            <xsl>result_indicator_period_actual_dimension_value,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_comment_narrative']/str">
            <xsl>result_indicator_period_actual_comment_narrative,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_document_link-format']/str">
            <xsl>result_indicator_period_actual_document_link_format,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_document_link_url']/str">
            <xsl>result_indicator_period_actual_document_link_url,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_document_link_title_narrative']/str">
            <xsl>result_indicator_period_actual_document_link_title_narrative,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_document_link_description_narrative']/str">
            <xsl>result_indicator_period_actual_document_link_description_narrative,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_document_link_category_code']/str">
            <xsl>result_indicator_period_actual_document_link_category_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_document_link_language_code']/str">
            <xsl>result_indicator_period_actual_document_link_language_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_document_link_document_date_iso_date']/date">
            <xsl>result_indicator_period_actual_document_link_document_date_iso_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs_add_other_flags_code']/str">
            <xsl>crs_add_other_flags_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs_add_other_flags_significance']/str">
            <xsl>crs_add_other_flags_significance,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs_add_loan_terms_rate_1']/str">
            <xsl>crs_add_loan_terms_rate_1,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs_add_loan_terms_rate_2']/str">
            <xsl>crs_add_loan_terms_rate_2,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs_add_loan_terms_repayment_type_code']/str">
            <xsl>crs_add_loan_terms_repayment_type_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs_add_loan_terms_repayment_plan_code']/str">
            <xsl>crs_add_loan_terms_repayment_plan_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs_add_loan_terms_commitment_date_iso_date']/date">
            <xsl>crs_add_loan_terms_commitment_date_iso_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs_add_loan_terms_repayment_first_date_iso_date']/date">
            <xsl>crs_add_loan_terms_repayment_first_date_iso_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs_add_loan_terms_repayment_final_date_iso_date']/date">
            <xsl>crs_add_loan_terms_repayment_final_date_iso_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs_add_loan_status_year']/int">
            <xsl>crs_add_loan_status_year,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs_add_loan_status_currency']/str">
            <xsl>crs_add_loan_status_currency,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs_add_loan_status_value_date']/date">
            <xsl>crs_add_loan_status_value_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs_add_loan_status_interest_received']/double">
            <xsl>crs_add_loan_status_interest_received,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs_add_loan_status_principal_outstanding']/double">
            <xsl>crs_add_loan_status_principal_outstanding,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs_add_channel_code']/str">
            <xsl>crs_add_channel_code,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::date[@name='fss_extraction_date']">
            <xsl>fss_extraction_date,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::str[@name='fss_priority']">
            <xsl>fss_priority,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='fss_phaseout_year']/int">
            <xsl>fss_phaseout_year,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='fss_forecast_year']/int">
            <xsl>fss_forecast_year,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='fss_forecast_value_date']/date">
            <xsl>fss_forecast_value_date,</xsl>

        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='fss_forecast_currency']/str">
            <xsl>fss_forecast_currency,</xsl>

        </xsl:if>

        <xsl:if
                test="ancestor::response/descendant::arr[@name='fss_forecast_value']/double">
            <xsl>fss_forecast_value,</xsl>

        </xsl:if>
        <xsl:value-of select="$break"/>

    </xsl:template>

    <xsl:template match="response/result/doc">

        <xsl:for-each select="arr[@name='sector_code']/str">
            <xsl:value-of select="ancestor::doc/descendant::str[@name='default_lang']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='default_lang']">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:value-of select="ancestor::doc/descendant::str[@name='default_currency']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='default_currency']">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:value-of select="ancestor::doc/descendant::str[@name='humanitarian']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='humanitarian']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='hierarchy']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='hierarchy']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='iati_identifier']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='iati_identifier']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='reporting_org_ref']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='reporting_org_ref']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='reporting_org_type_code']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='reporting_org_type_code']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='reporting_org_secondary_reporter']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='reporting_org_secondary_reporter']">
                <xsl:value-of select="$delim"/>
                <!--<xsl:value-of select="$quote"/>-->
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='reporting_org_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='reporting_org_narrative']/str">
                <!--<xsl:value-of select="$deliminquote"/>-->
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='title_narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='title_narrative']/str">
                <!--<xsl:value-of select="$deliminquote"/>-->
                <xsl:value-of select="$delim"/>

            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='description_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='description_narrative']/str">
                <!-- <xsl:value-of select="$deliminquote"/>-->
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='participating_org_ref']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='participating_org_ref']/str">
                <!--<xsl:value-of select="$deliminquote"/>-->
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='participating_org_type']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='participating_org_type']/str">
                <!--<xsl:value-of select="$deliminquote"/>-->
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='participating_org_role']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='participating_org_role']/str">
                <!--<xsl:value-of select="$deliminquote"/>-->
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='participating_org_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='participating_org_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='other_identifier_ref']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='other_identifier_ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='other_identifier_owner_org_ref']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='other_identifier_owner_org_ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='other_identifier_owner_org_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='other_identifier_owner_org_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:value-of select="ancestor::doc/descendant::str[@name='activity_status_code']"/>

            <xsl:if
                    test="ancestor::response/descendant::str[@name='activity_status_code']">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='activity_date_iso_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='activity_date_iso_date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='activity_date_type']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='activity_date_type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact_info_organisation_narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='contact_info_organisation_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact_info_department_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='contact_info_department_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact_info_person_name_narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='contact_info_person_name_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact_info_job_title_narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='contact_info_job_title_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact_info_telephone']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='contact_info_telephone']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact_info_email']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='contact_info_email']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact_info_website']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='contact_info_website']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact_info_mailing_address_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='contact_info_mailing_address_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:value-of select="ancestor::doc/descendant::str[@name='activity_scope_code']"/>

            <xsl:if
                    test="ancestor::response/descendant::str[@name='activity_scope_code']">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='recipient_country_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='recipient_country_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='recipient_country_percentage']/double"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='recipient_country_percentage']/double">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='recipient_region_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='recipient_region_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='recipient_region_percentage']/double"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='recipient_region_percentage']/double">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_ref']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location_ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_id_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location_id_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_id_vocabulary']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location_id_vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_reach_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location_reach_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_name_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location_name_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_description_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location_description_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_activity_description_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location_activity_description_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_administrative_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location_administrative_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_administrative_vocabulary']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location_administrative_vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_administrative_level']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location_administrative_level']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_point_pos']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location_point_pos']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_exactness_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location_exactness_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_class_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location_class_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location_feature_designation_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location_feature_designation_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:variable name="sector_position" select="position()"/> <!--this give the position of current sector-code-->
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='sector_vocabulary']/str[$sector_position]"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='sector_vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="self::str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='sector_code']">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='sector_percentage']/double[$sector_position]"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='sector_percentage']">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='tag_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='tag_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='tag_vocabulary']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='tag_vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='tag_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='tag_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:value-of select="ancestor::doc/descendant::str[@name='country_budget_items_vocabulary']"/>

            <xsl:if
                    test="ancestor::response/descendant::str[@name='country_budget_items_vocabulary']">
                <xsl:value-of select="$delim"/>

            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='country_budget_items_budget_item_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='country_budget_items_budget_item_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='country_budget_items_budget_item_percentage']/double"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='country_budget_items_budget_item_percentage']/double">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='country_budget_items_budget_description_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='country_budget_items_budget_description_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='humanitarian_scope_type']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='humanitarian_scope_type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='humanitarian_scope_vocabulary']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='humanitarian_scope_vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='humanitarian_scope_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='humanitarian_scope_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='humanitarian_scope_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='humanitarian_scope_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='policy_marker_vocabulary']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='policy_marker_vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='policy_marker_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='policy_marker_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='policy_marker_significance']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='policy_marker_significance']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:value-of select="ancestor::doc/descendant::str[@name='collaboration_type_code']"/>

            <xsl:if
                    test="ancestor::response/descendant::str[@name='collaboration_type_code']">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:value-of select="ancestor::doc/descendant::str[@name='default_flow_type_code']"/>

            <xsl:if
                    test="ancestor::response/descendant::str[@name='default_flow_type_code']">
                <xsl:value-of select="$delim"/>
            </xsl:if>


            <xsl:value-of select="ancestor::doc/descendant::str[@name='default_finance_type_code']"/>

            <xsl:if
                    test="ancestor::response/descendant::str[@name='default_finance_type_code']">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='default_aid_type_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='default_aid_type_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='default_aid_type_vocabulary']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='default_aid_type_vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:value-of select="ancestor::doc/descendant::str[@name='default_tied_status_code']"/>

            <xsl:if
                    test="ancestor::response/descendant::str[@name='default_tied_status_code']">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget_type']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='budget_type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget_status']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='budget_status']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget_period_start_iso_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='budget_period_start_iso_date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget_period_end_iso_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='budget_period_end_iso_date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget_value_currency']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='budget_value_currency']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget_value_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='budget_value_date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget_value']/double"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='budget_value']/double">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned_disbursement_type']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='planned_disbursement_type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned_disbursement_period_start_iso_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='planned_disbursement_period_start_iso_date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned_disbursement_period_end_iso_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='planned_disbursement_period_end_iso_date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned_disbursement_value_currency']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='planned_disbursement_value_currency']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned_disbursement_value_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='planned_disbursement_value_date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned_disbursement_value']/double"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='planned_disbursement_value']/double">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned_disbursement_provider_org_provider_activity_id']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='planned_disbursement_provider_org_provider_activity_id']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned_disbursement_provider_org_type']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='planned_disbursement_provider_org_type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned_disbursement_provider_org_ref']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='planned_disbursement_provider_org_ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned_disbursement_provider_org_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='planned_disbursement_provider_org_narrative']/str">

                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:value-of select="ancestor::doc/descendant::double[@name='capital_spend_percentage']"/>

            <xsl:if
                    test="ancestor::response/descendant::double[@name='capital_spend_percentage']">
                <xsl:value-of select="$delim"/>

            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_ref']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_humanitarian']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_humanitarian']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_type']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_date_iso_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_date_iso_date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_value_currency']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_value_currency']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_value_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_value_date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_value']/double"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_value']/double">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_provider_org_provider_activity_id']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_provider_org_provider_activity_id']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_provider_org_type']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_provider_org_type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_provider_org_ref']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_provider_org_ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_provider_org_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_provider_org_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_receiver_org_receiver_activity_id']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_receiver_org_receiver_activity_id']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_receiver_org_type']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_receiver_org_type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_receiver_org_ref']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_receiver_org_ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_receiver_org_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_receiver_org_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_disburstment_channel_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_disbursement_channel_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_sector_vocabulary']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_sector_vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_sector_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_sector_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_recipient_country_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_recipient_country_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_recipient_region_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_recipient_region_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_recipient_region_vocabulary']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_recipient_region_vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_flow_type_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_flow_type_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_finance_type_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_finance_type_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_aid_type_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_aid_type_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_aid_type_vocabulary']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_aid_type_vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction_tied_status_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction_tied_status_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='document_link_format']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='document_link_format']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='document_link_url']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='document_link_url']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='document_link_title_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='document_link_title_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='document_link_category_code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='document_link_category_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='document_link_document_date_iso_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='document_link_document_date_iso_date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='related_activity_ref']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='related_activity_ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='related_activity_type']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='related_activity_type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='legacy_data_name']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='legacy_data_name']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='legacy_data_value']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='legacy_data_value']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='legacy_data_iati_equivalent']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='legacy_data_iati_equivalent']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:value-of select="ancestor::doc/descendant::str[@name='conditions_attached']"/>

            <xsl:if
                    test="ancestor::response/descendant::str[@name='conditions_attached']">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='conditions_condition_type']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='conditions_condition_type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='conditions_condition_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='conditions_condition_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_type']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_aggregation_status']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_aggregation_status']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_title_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_title_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_description_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_description_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_document_link_format']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_document_link_format']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_document_link_url']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_document_link_url']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_document_link_title_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_document_link_title_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_document_link_description_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_document_link_description_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_document_link_category_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_document_category_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_document_link_language_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_document_link_language_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_document_link_document_date_iso_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_document_link_document_date_iso_date']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_reference_vocabulary']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_reference_vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_reference_code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_reference_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_reference_vocabulary_uri']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_reference_vocabulary_uri']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_measure']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_measure']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_ascending']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_ascending']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_aggregation_status']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_aggregation_status']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_title_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_title_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_description_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_description_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_document_link_format']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_document_link_format']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_document_link_url']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_document_link_uri']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_document_link_title_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_document_link_title_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_document_link_description_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_document_link_description_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_document_link_category_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_document_link_category_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_document_link_language_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_document_link_language_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_document_link_document_date_iso_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_document_link_document_date_iso_date']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_reference_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_reference_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_reference_vocabulary']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_reference_vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_reference_vocabulary_uri']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_reference_vocabulary_uri']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_year']/int"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_baseline_year']/int">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_iso_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_baseline_iso_date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_value']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_baseline_value']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_location_ref']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_baseline_location_ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_dimension_name']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_baseline_dimension_name']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_dimension_value']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_baseline_dimension_value']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_document_link_format']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_baseline_document_link_format']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_document_link_url']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_baseline_document_link_url']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_document_link_title']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_baseline_document_link_title']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_document_link_description']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_baseline_document_link_description']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_document_link_category_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_baseline_document_link_category_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_document_link_language_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_baseline_document_link_language_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_document_link_document_date_iso_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_baseline_document_link_document_date_iso_date']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_baseline_comment_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_baseline_comment_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_period_start_iso_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_period_start_iso_date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_period_end_iso_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_period_end_iso_date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_value']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_target_value']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_location_ref']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_target_location_ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_dimension_name']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_target_dimension_name']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_dimension_value']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_target_dimension_value']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_comment_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_target_comment_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_document_link_format']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_target_document_link_format']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_document_link_url']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_target_document_link_url']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_document_link_title_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_target_document_link_title_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_document_link_description_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_target_document_link_description_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_document_link_category_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_target_document_link_category_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_document_link_language_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_target_document_link_language_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_target_document_link_document_date_iso_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_target_document_link_document_date_iso_date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_value']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_value']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_location_ref']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_location_ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_dimension_name']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_dimension_name']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_dimension_value']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_dimension_value']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_comment_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_comment_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_document_link_format']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_document_link_format']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_document_link_url']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_document_link_url']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_document_link_title_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_document_link_title_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_document_link_description_narrative']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_document_link_description_narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_document_link_category_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_document_link_category_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_document_link_language_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_document_link_language_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result_indicator_period_actual_document_link_document_date_iso_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result_indicator_period_actual_document_link_document_date_iso_date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_other_flags_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs_add_other_flags_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_other_flags_significance']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs_add_other_flags_significance']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_terms_rate_1']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs_add_loan_terms_rate_1']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_terms_rate_2']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs_add_loan_terms_rate_2']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_terms_repayment_type_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs_add_loan_terms_repayment_type_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_terms_repayment_plan_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs_add_loan_terms_repayment_plan_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_terms_commitment_date_iso_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs_add_loan_terms_commitment_date_iso_date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_terms_repayment_first_date_iso_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs_add_loan_terms_repayment_first_date_iso_date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_terms_repayment_final_date_iso_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs_add_loan_terms_repayment_final_date_iso_date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_status_year']/int"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs_add_loan_status_year']/int">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_status_currency']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs_add_loan_status_currency']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_status_value_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs_add_loan_status_value_date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_status_interest_received']/double"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs_add_loan_status_interest_received']/double">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_loan_status_principal_outstanding']/double"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs_add_loan_status_principal_outstanding']/double">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs_add_channel_code']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs_add_channel_code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:value-of select="date[@name='fss_extraction_date']"/>

            <xsl:if
                    test="ancestor::response/descendant::date[@name='fss_extraction_date']">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:value-of select="str[@name='fss_priority']"/>

            <xsl:if
                    test="ancestor::response/descendant::str[@name='fss_priority']">
                <xsl:value-of select="$delim"/>

            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='fss_phaseout_year']/int"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='fss_phaseout_year']/int">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='fss_forecast_year']/int"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='fss_forecast_year']/int">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='fss_forecast_value_date']/date"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='fss_forcast_value_date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='fss_forecast_currency']/str"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='fss_forecast_currency']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>

            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='fss_forecast_value']/double"/>

            <xsl:if
                    test="ancestor::response/descendant::arr[@name='fss_forecast_value']/double">
                <xsl:value-of select="$quote"/>
                <xsl:value-of select="$delim"/>
            </xsl:if>

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
