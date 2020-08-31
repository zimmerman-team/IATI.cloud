<!--This file is moved to XSL repository and no longer used in Solr. Please
refer to XSL repository. -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text" encoding="utf-8"/>
  <xsl:param name="delim" select="','"/>
  <xsl:param name="quote" select="'&quot;'"/>
  <xsl:param name="deliminquote" select="'&quot;,&quot;'"/>
  <xsl:param name="break" select="'&#xA;'"/>
  <xsl:param name="iati_identifier" select="iati_identifier" />
  <xsl:variable name="apos">'</xsl:variable>
  <xsl:template match="/">
    <xsl:apply-templates select="response/lst/lst"/>
    <xsl:apply-templates select="response/result/doc"/>
  </xsl:template>
  <xsl:template match="lst">
      <xsl>iati_identifier,</xsl>
      <xsl>reporting_org_ref,</xsl>
      <xsl>title,</xsl>
      <xsl>activity_description,</xsl>
      <xsl>activity_recipient_country,</xsl>
      <xsl>activity_recipient_region,</xsl>
      <xsl>activity_sector,</xsl>
    <xsl>transaction_ref,</xsl>
    <xsl>transaction_humanitarian,</xsl>
    <xsl>transaction_type,</xsl>
    <xsl>transaction_date_iso_date,</xsl>
    <xsl>transaction_value_currency,</xsl>
    <xsl>transaction_value_date,</xsl>
    <xsl>transaction_value,</xsl>
    <xsl>transaction_provider_org_ref,</xsl>
    <xsl>transaction_provider_org_provider_activity_id,</xsl>
    <xsl>transaction_provider_org_type,</xsl>
    <xsl>transaction_provider_org_narrative,</xsl>
    <xsl>transaction_receiver_org_ref,</xsl>
    <xsl>transaction_receiver_org_receiver_activity_id,</xsl>
    <xsl>transaction_receiver_org_type,</xsl>
    <xsl>transaction_receiver_org_narrative,</xsl>
    <xsl>transaction_disburstment_channel_code,</xsl>
    <xsl>transaction_sector_vocabulary,</xsl>
    <xsl>transaction_sector_code,</xsl>
    <xsl>transaction_recipient_country_code,</xsl>
    <xsl>transaction_recipient_region_code,</xsl>
    <xsl>transaction_flow_type_code,</xsl>
    <xsl>transaction_finance_type_code,</xsl>
    <xsl>transaction_aid_type_code,</xsl>
    <xsl>transaction_aid_type_vocabulary,</xsl>
    <xsl>transaction_tied_status_code,</xsl>
    <xsl:value-of select="$break"/>
  </xsl:template>
  <xsl:template match="doc">
      <xsl:value-of select="$quote"/>
      <xsl:value-of select="str[@name='iati_identifier']"/>
      <xsl:value-of select="$quote"/>
      <xsl:value-of select="$delim"/>
      <xsl:value-of select="str[@name='reporting_org_ref']"/>
      <xsl:value-of select="$delim"/>
      <xsl:value-of select="$quote"/>
      <xsl:apply-templates select="arr[@name='title_narrative']/str"/>
      <xsl:value-of select="$quote"/>
      <xsl:value-of select="$delim"/>
      <xsl:value-of select="$quote"/>
      <xsl:apply-templates select="arr[@name='activity_description_narrative']/str"/>
      <xsl:value-of select="$quote"/>
      <xsl:value-of select="$delim"/>
      <xsl:value-of select="$quote"/>
      <xsl:apply-templates select="arr[@name='activity_recipient_country_code']/str"/>
      <xsl:value-of select="$quote"/>
      <xsl:value-of select="$delim"/>
      <xsl:value-of select="$quote"/>
      <xsl:apply-templates select="arr[@name='activity_recipient_region_code']/str"/>
      <xsl:value-of select="$quote"/>
      <xsl:value-of select="$delim"/>
      <xsl:value-of select="$quote"/>
      <xsl:apply-templates select="arr[@name='activity_sector_code']/str"/>
      <xsl:value-of select="$quote"/>
      <xsl:value-of select="$delim"/>
    <xsl:value-of select="str[@name='transaction_ref']"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="str[@name='transaction_humanitarian']"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="str[@name='transaction_type']"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="str[@name='transaction_date_iso_date']"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="str[@name='transaction_value_currency']"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="date[@name='transaction_value_date']"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="double[@name='transaction_value']"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="str[@name='transaction_provider_org_ref']"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="str[@name='transaction_provider_org_provider_activity_id']"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="str[@name='transaction_provider_org_type']"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="$quote"/>
    <xsl:value-of select="str[@name='transaction_provider_org_narrative_text']"/>
    <xsl:value-of select="$quote"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="str[@name='transaction_receiver_org_ref']"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="str[@name='transaction_receiver_org_receiver_activity_id']"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="str[@name='transaction_receiver_org_type']"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="$quote"/>
    <xsl:apply-templates select="arr[@name='transaction_receiver_org_narrative']/str"/>
    <xsl:value-of select="$quote"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="str[@name='transaction_disburstment_channel_code']"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="$quote"/>
    <xsl:apply-templates select="arr[@name='transaction_sector_vocabulary']/str"/>
    <xsl:value-of select="$quote"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="$quote"/>
    <xsl:apply-templates select="arr[@name='transaction_sector_code']/str"/>
    <xsl:value-of select="$quote"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="str[@name='transaction_recipient_country_code']"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="str[@name='transaction_recipient_region_code']"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="str[@name='transaction_flow_type_code']"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="str[@name='transaction_finance_type_code']"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="$quote"/>
    <xsl:apply-templates select="arr[@name='transaction_aid_type_code']/str"/>
    <xsl:value-of select="$quote"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="$quote"/>
    <xsl:apply-templates select="arr[@name='transaction_aid_type_vocabulary']/str"/>
    <xsl:value-of select="$quote"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="str[@name='transaction_tied_status_code']"/>
    <xsl:value-of select="$delim"/>
    <xsl:value-of select="$break"/>
  </xsl:template>
  <xsl:template match="arr[*]/str">
    <xsl:value-of select="concat(normalize-space(), $delim)"/>
  </xsl:template>
  <xsl:template match="arr[*]/int">
    <xsl:value-of select="concat(normalize-space(), $delim)"/>
  </xsl:template>
  <xsl:template match="arr[*]/double">
    <xsl:value-of select="concat(normalize-space(), $delim)"/>
  </xsl:template>
  <xsl:template match="arr[*]/date">
    <xsl:value-of select="concat(normalize-space(), $delim)"/>
  </xsl:template>
  <xsl:template match="arr[contains(@name,'_narrative')]/str">
    <xsl:value-of select="concat($apos, normalize-space(), $apos, $delim)"/>
  </xsl:template>
  <xsl:template match="arr[contains(@name,'_title')]/str">
    <xsl:value-of select="concat($apos, normalize-space(), $apos, $delim)"/>
  </xsl:template>
  <xsl:template match="arr[contains(@name,'_description')]/str">
    <xsl:value-of select="concat($apos, normalize-space(), $apos, $delim)"/>
  </xsl:template>
</xsl:stylesheet>