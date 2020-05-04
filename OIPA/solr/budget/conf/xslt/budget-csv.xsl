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
        <xsl>reporting_org_type,</xsl>
        <xsl>recipient_country_code,</xsl>
        <xsl>recipient_country_name,</xsl>
        <xsl>budget_type,</xsl>
        <xsl>budget_status,</xsl>
        <xsl>budget_period_start_iso_date,</xsl>
        <xsl>budget_period_end_iso_date,</xsl>
        <xsl>budget_value_currency,</xsl>
        <xsl>budget_value_date,</xsl>
        <xsl>budget_value,</xsl>
        <xsl:value-of select="$break"/>
    </xsl:template>
    <xsl:template match="doc">
        <xsl:value-of select="str[@name='iati_identifier']"/>
        <xsl:value-of select="$delim"/>
        <xsl:value-of select="str[@name='reporting_org_ref']"/>
        <xsl:value-of select="$delim"/>
        <xsl:value-of select="str[@name='reporting_org_type']"/>
        <xsl:value-of select="$delim"/>
        <xsl:value-of select="$quote"/>
        <xsl:apply-templates select="arr[@name='recipient_country_code']/str"/>
        <xsl:value-of select="$quote"/>
        <xsl:value-of select="$delim"/>
        <xsl:value-of select="$quote"/>
        <xsl:apply-templates select="arr[@name='recipient_country_name']/str"/>
        <xsl:value-of select="$quote"/>
        <xsl:value-of select="$delim"/>
        <xsl:value-of select="str[@name='budget_type']"/>
        <xsl:value-of select="$delim"/>
        <xsl:value-of select="str[@name='budget_status']"/>
        <xsl:value-of select="$delim"/>
        <xsl:value-of select="str[@name='budget_period_start_iso_date']"/>
        <xsl:value-of select="$delim"/>
        <xsl:value-of select="str[@name='budget_period_end_iso_date']"/>
        <xsl:value-of select="$delim"/>
        <xsl:value-of select="str[@name='budget_value_currency']"/>
        <xsl:value-of select="$delim"/>
        <xsl:value-of select="str[@name='budget_value_date']"/>
        <xsl:value-of select="$delim"/>
        <xsl:value-of select="double[@name='budget_value']"/>
        <xsl:value-of select="$delim"/>
        <xsl:value-of select="$break"/>
    </xsl:template>
    <xsl:template match="arr[*]/str">
    <xsl:value-of select="concat(normalize-space(), $delim)"/>
  </xsl:template>
</xsl:stylesheet>