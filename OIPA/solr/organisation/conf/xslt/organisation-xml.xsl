<!--
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 -->

<!--
  Simple transform of Solr query response into Solr Update XML compliant XML.
  When used in the xslt response writer you will get UpdaateXML as output.
  But you can also store a query response XML to disk and feed this XML to
  the XSLTUpdateRequestHandler to index the content. Provided as example only.
  See http://wiki.apache.org/solr/XsltUpdateRequestHandler for more info
 -->
<xsl:stylesheet version='1.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>
  <xsl:output media-type="text/xml" method="xml" indent="yes"/>
  <xsl:template match='/'>
    <iati-organisations version="2.03">
        <xsl:apply-templates select="response/result/doc"/>
    </iati-organisations>
  </xsl:template>
  <xsl:template match="doc">
    <iati-organisation>
      <xsl:if test="str[@name='organisation_default_currency_code']">
        <xsl:attribute name="default-currency">
          <xsl:value-of select="str[@name='organisation_default_currency_code']"/>
        </xsl:attribute>
      </xsl:if>
      <xsl:if test="date[@name='organisation_last_updated_datetime']">
        <xsl:attribute name="last-updated-datetime">
          <xsl:value-of select="date[@name='organisation_last_updated_datetime']"/>
        </xsl:attribute>
      </xsl:if>
      <xsl:attribute name="xml:lang">
        <xsl:value-of select="str[@name='organisation_default_lang_code']"/>
      </xsl:attribute>
      <organisation-identifier>
        <xsl:value-of select="str[@name='organisation_identifier']"/>
      </organisation-identifier>
      <xsl:for-each select="str[@name='organisation_name_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="str[@name='organisation_reported_org_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='organisation_total_budget_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='organisation_recipient_org_budget_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='organisation_recipient_region_budget_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='organisation_recipient_country_budget_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='organisation_total_expenditure_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
      <xsl:for-each select="arr[@name='organisation_document_link_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
    </iati-organisation>
  </xsl:template>
</xsl:stylesheet>
