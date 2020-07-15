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
      <xsl>sector_vocabulary,</xsl>
      <xsl>sector_vocabulary_uri,</xsl>
      <xsl>sector_code,</xsl>
      <xsl>sector_percentage,</xsl>

    <xsl:value-of select="$break"/>
  </xsl:template>
  <xsl:template match="doc">
      <xsl:value-of select="$quote"/>
      <xsl:value-of select="str[@name='iati_identifier']"/>
      <xsl:value-of select="$quote"/>
      <xsl:value-of select="$delim"/>
      <xsl:apply-templates select="arr[@name='sector_vocabulary']/str"/>

      <xsl:value-of select="$quote"/>
      <xsl:apply-templates select="arr[@name='sector_vocabulary_uri']/str"/>
      <xsl:value-of select="$quote"/>
      <xsl:value-of select="$delim"/>
      <xsl:value-of select="$quote"/>
      <xsl:apply-templates select="arr[@name='sector_code']/str"/>
      <xsl:value-of select="$quote"/>
      <xsl:value-of select="$delim"/>
      <xsl:value-of select="$quote"/>
      <xsl:apply-templates select="arr[@name='sector_percentage']/double"/>
      <xsl:value-of select="$quote"/>
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