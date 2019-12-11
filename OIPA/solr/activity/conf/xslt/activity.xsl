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
    <iati-activities version="2.03">
        <xsl:apply-templates select="response/result/doc"/>
    </iati-activities>
  </xsl:template>

  <xsl:template match="doc">
    <iati-activity>
      <xsl:attribute name="xml:lang">
        <xsl:value-of select="str[@name='default_lang']"/>
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
      <xsl:for-each select="arr[@name='fss_xml']">
        <xsl:value-of disable-output-escaping="yes" select="."/>
      </xsl:for-each>
    </iati-activity>
  </xsl:template>
</xsl:stylesheet>
