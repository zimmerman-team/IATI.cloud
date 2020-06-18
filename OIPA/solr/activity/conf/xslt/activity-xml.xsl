<xsl:stylesheet version='1.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>
  <xsl:output media-type="text/xml" method="xml" indent="yes"/>

  <xsl:template match='/'>
    <iati-activities version="2.03">
        <xsl:apply-templates select="response/result/doc"/>
    </iati-activities>
  </xsl:template>

  <xsl:template match="doc">
    <iati-activity>
      <xsl:attribute name="xml:lang">
        <xsl:value-of select="str[@name='default_lang']"/>
      </xsl:attribute>
        <xsl:attribute name="last-updated-datetime">
            <xsl:value-of select="str[@name='last_updated_datetime']"/>
        </xsl:attribute>
        <xsl:attribute name="default-currency">
            <xsl:value-of select="str[@name='default_currency']"/>
        </xsl:attribute>
        <xsl:attribute name="humanitarian">
            <xsl:value-of select="str[@name='humanitarian']"/>
        </xsl:attribute>
        <xsl:attribute name="linked-data-uri">
            <xsl:value-of select="str[@name='linked_data_uri']"/>
        </xsl:attribute>
      <iati-identifier>
        <xsl:value-of select="str[@name='iati_identifier']"/>
      </iati-identifier>
      <xsl:for-each select="arr[@name='reporting_org_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='title_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='description_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='participating_org_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='other_identifier_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='activity_status_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='activity_date_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='contact_info_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='activity_scope_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='recipient_country_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='recipient_region_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='location_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='sector_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='tag_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='country_budget_items_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='policy_marker_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='humanitarian_scope_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='collaboration_type_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='default_flow_type_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='default_finance_type_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='default_aid_type_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='default_tied_status_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='budget_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='planned_disbursement_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='capital_spend_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='transaction_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='document_link_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='related_activity_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='legacy_data_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='conditions_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='result_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='crs_add_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='fss_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
    </iati-activity>
  </xsl:template>
</xsl:stylesheet>
