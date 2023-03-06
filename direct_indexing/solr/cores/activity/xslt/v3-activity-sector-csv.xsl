<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xal="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text" encoding="UTF-8"/>
    <xsl:param name="delim" select="','"/>
    <xsl:param name="quote" select="'&quot;'"/>
    <xsl:param name="deliminquote" select="'&quot;,&quot;'"/>
    <xsl:param name="break" select="'&#13;'"/>
    <xsl:param name="iati-identifier" select="iati-identifier" />
    <xsl:variable name="apos">'</xsl:variable>
    <xsl:template match="/">
    </xsl:template>
    <xsl:template match="/">
        <xsl:apply-templates select="response/lst/lst"/>
        <xsl:apply-templates select="response/result/doc"/>
    </xsl:template>
    <xsl:template match="response/lst/lst">
        <xsl:if test="ancestor::response/descendant::str[@name='lang']">
            <xsl>lang,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::str[@name='default-currency']">
            <xsl>default-currency,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::str[@name='humanitarian']">
            <xsl>humanitarian,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::str[@name='hierarchy']">
            <xsl>hierarchy,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::str[@name='iati-identifier']">
            <xsl>iati-identifier,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::str[@name='reporting-org.ref']">
            <xsl>reporting-org.ref,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::str[@name='reporting-org.type']">
            <xsl>reporting-org.type,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::str[@name='reporting-org.secondary-reporter']">
            <xsl>reporting-org.secondary-reporter,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='reporting-org.narrative']/str">
            <xsl>reporting-org.narrative,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='title.narrative']/str">
            <xsl>title.narrative,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='description.narrative']/str">
            <xsl>description.narrative,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='participating-org.ref']/str">
            <xsl>participating-org.ref,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='participating-org.type']/str">
            <xsl>participating-org.type,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='participating-org.role']/str">
            <xsl>participating-org.role,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='participating-org.narrative']/str">
            <xsl>participating-org.narrative,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='other-identifier.ref']/str">
            <xsl>other-identifier.ref,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='other-identifier.owner-org.ref']/str">
            <xsl>other-identifier.owner-org.ref,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='other-identifier.owner-org.narrative']/str">
            <xsl>other-identifier.owner-org.narrative,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::str[@name='activity-status.code']">
            <xsl>activity-status.code,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='activity-date.iso-date']/date">
            <xsl>activity-date.iso-date,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='activity-date.type']/str">
            <xsl>activity-date.type,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='contact-info.organisation.narrative']/str">
            <xsl>contact-info.organisation.narrative,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='contact-info.department.narrative']/str">
            <xsl>contact-info.department.narrative,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='contact-info.person-name.narrative']/str">
            <xsl>contact-info.person-name.narrative,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='contact-info.job-title.narrative']/str">
            <xsl>contact-info.job-title.narrative,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='contact-info.telephone']/str">
            <xsl>contact-info.telephone,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='contact-info.email']/str">
            <xsl>contact-info.email,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='contact-info.website']/str">
            <xsl>contact-info.website,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='contact-info.mailing-address.narrative']/str">
            <xsl>contact-info.mailing-address.narrative,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::str[@name='activity-scope.code']">
            <xsl>activity-scope.code,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='recipient-country.code']/str">
            <xsl>recipient-country.code,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='recipient-country.percentage']/double">
            <xsl>recipient-country.percentage,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='recipient-region.code']/str">
            <xsl>recipient-region.code,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='recipient-region.percentage']/double">
            <xsl>recipient-region.percentage,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='location.ref']/str">
            <xsl>location.ref,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='location.location-id.code']/str">
            <xsl>location.location-id.code,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='location.location-id.vocabulary']/str">
            <xsl>location.location-id.vocabulary,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='location.location-reach.code']/str">
            <xsl>location.location-reach.code,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='location.name.narrative']/str">
            <xsl>location.name.narrative,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='location.description.narrative']/str">
            <xsl>location.description.narrative,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='location.activity-description.narrative']/str">
            <xsl>location.activity-description.narrative,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='location.administrative.code']/str">
            <xsl>location.administrative.code,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='location.administrative.vocabulary']/str">
            <xsl>location.administrative.vocabulary,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='location.administrative.level']/str">
            <xsl>location.administrative.level,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='location.point.pos']/str">
            <xsl>location.point.pos,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='location.exactness.code']/str">
            <xsl>location.exactness.code,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='location.location-class.code']/str">
            <xsl>location.location-class.code,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='location.feature-designation.code']/str">
            <xsl>location.feature-designation.code,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='sector.vocabulary']/str">
            <xsl>sector.vocabulary,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='sector.code']/str">
            <xsl>sector.code,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='sector.percentage']/double">
            <xsl>sector.percentage,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='tag.code']/str">
            <xsl>tag.code,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='tag.vocabulary']/str">
            <xsl>tag.vocabulary,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='tag.narrative']/str">
            <xsl>tag.narrative,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::str[@name='country-budget-items.vocabulary']">
            <xsl>country-budget-items.vocabulary,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='country-budget-items.budget-item.code']/str">
            <xsl>country-budget-items.budget-item.code,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='country-budget-items.budget-item.percentage']/double">
            <xsl>country-budget-items.budget-item.percentage,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='country-budget-items.budget-item.description.narrative']/str">
            <xsl>country-budget-items.budget-item.description.narrative,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='humanitarian-scope.type']/str">
            <xsl>humanitarian-scope.type,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='humanitarian-scope.vocabulary']/str">
            <xsl>humanitarian-scope.vocabulary,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='humanitarian-scope.code']/str">
            <xsl>humanitarian-scope.code,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='humanitarian-scope.narrative']/str">
            <xsl>humanitarian-scope.narrative,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='policy-marker.vocabulary']/str">
            <xsl>policy-marker.vocabulary,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='policy-marker.code']/str">
            <xsl>policy-marker.code,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='policy-marker.significance']/str">
            <xsl>policy-marker.significance,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::str[@name='collaboration-type.code']">
            <xsl>collaboration-type.code,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::str[@name='default-flow-type.code']">
            <xsl>default-flow-type.code,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::str[@name='default-finance-type.code']">
            <xsl>default-finance-type.code,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='default-aid-type.code']/str">
            <xsl>default-aid-type.code,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='default-aid-type.vocabulary']/str">
            <xsl>default-aid-type.vocabulary,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::str[@name='default-tied-status.code']">
            <xsl>default-tied-status.code,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='budget.type']/str">
            <xsl>budget.type,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='budget.status']/str">
            <xsl>budget.status,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='budget.period-start.iso-date']/date">
            <xsl>budget.period-start.iso-date,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='budget.period-end.iso-date']/date">
            <xsl>budget.period-end.iso-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='budget.value.currency']/str">
            <xsl>budget.value.currency,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='budget.value.value-date']/date">
            <xsl>budget.value.value-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='budget.value']/double">
            <xsl>budget.value,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='planned-disbursement.type']/str">
            <xsl>planned-disbursement.type,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='planned-disbursement.period-start.iso-date']/date">
            <xsl>planned-disbursement.period-start.iso-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='planned-disbursement.period-end.iso-date']/date">
            <xsl>planned-disbursement.period-end.iso-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='planned-disbursement.value.currency']/str">
            <xsl>planned-disbursement.value.currency,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='planned-disbursement.value.value-date']/date">
            <xsl>planned-disbursement.value.value-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='planned-disbursement.value']/double">
            <xsl>planned-disbursement.value,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='planned-disbursement.provider-org.provider-activity-id']/str">
            <xsl>planned-disbursement.provider-org.provider-activity-id,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='planned-disbursement.provider-org-type']/str">
            <xsl>planned-disbursement.provider-org.type,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='planned-disbursement.provider-org.ref']/str">
            <xsl>planned-disbursement.provider-org.ref,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='planned-disbursement.provider-org.narrative']/str">
            <xsl>planned-disbursement.provider-org.narrative,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::double[@name='capital-spend.percentage']">
            <xsl>capital-spend.percentage,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::arr[@name='transaction.ref']/str">
            <xsl>transaction.ref,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.humanitarian']/str">
            <xsl>transaction.humanitarian,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.type']/str">
            <xsl>transaction.transaction-type.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.transaction-date.iso-date']/date">
            <xsl>transaction.transaction-date.iso-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.value.currency']/str">
            <xsl>transaction.value.currency,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.value.value-date']/date">
            <xsl>transaction.value.value-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.value']/double">
            <xsl>transaction.value,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.provider-org.provider-activity-id']/str">
            <xsl>transaction.provider-org.provider-activity-id,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.provider-org.type']/str">
            <xsl>transaction.provider-org.type,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.provider-org.ref']/str">
            <xsl>transaction.provider-org.ref,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.provider-org.narrative']/str">
            <xsl>transaction.provider-org.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.receiver-org.receiver-activity-id']/str">
            <xsl>transaction.receiver-org.receiver-activity-id,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.receiver-org.type']/str">
            <xsl>transaction.receiver-org.type,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.receiver-org.ref']/str">
            <xsl>transaction.receiver-org.ref,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.receiver-org.narrative']/str">
            <xsl>transaction.receiver-org.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.disbursement-channel.code']/str">
            <xsl>transaction.disbursement-channel.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.sector.vocabulary']/str">
            <xsl>transaction.sector.vocabulary,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.sector.code']/str">
            <xsl>transaction.sector.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.recipient-country.code']/str">
            <xsl>transaction.recipient-country.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.recipient-region.code']/str">
            <xsl>transaction.recipient-region.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.receipient-region.vocabulary']/str">
            <xsl>transaction.recipient-region.vocabulary,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.flow-type.code']/str">
            <xsl>transaction.flow-type.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.finance-type.code']/str">
            <xsl>transaction.finance-type.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.aid-type.code']/str">
            <xsl>transaction.aid-type.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.aid-type.vocabulary']/str">
            <xsl>transaction.aid-type.vocabulary,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='transaction.tied-status.code']/str">
            <xsl>transaction.tied-status.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='document-link.format']/str">
            <xsl>document-link.format,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='document-link.url']/str">
            <xsl>document-link.url,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='document-link.title.narrative']/str">
            <xsl>document-link.title.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='document-link.category.code']/str">
            <xsl>document-link.category.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='document-link.document-date.iso-date']/date">
            <xsl>document-link.document-date.iso-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='related-activity.ref']/str">
            <xsl>related-activity.ref,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='related-activity.type']/str">
            <xsl>related-activity.type,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='legacy-data.name']/str">
            <xsl>legacy-data.name,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='legacy-data.value']/str">
            <xsl>legacy-data.value,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='legacy-data.iati-equivalent']/str">
            <xsl>legacy-data.iati-equivalent,</xsl>
        </xsl:if>
        <xsl:if test="ancestor::response/descendant::str[@name='conditions.attached']">
            <xsl>conditions.attached,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='conditions.condition.type']/str">
            <xsl>conditions.condition.type,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='conditions.condition.narrative']/str">
            <xsl>conditions.condition.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.type']/str">
            <xsl>result.type,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.aggregation-status']/str">
            <xsl>result.aggregation-status,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.title.narrative']/str">
            <xsl>result.title.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.description.narrative']/str">
            <xsl>result.description.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.document-link.format']/str">
            <xsl>result.document-link.format,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.document-link.url']/str">
            <xsl>result.document-link.url,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.document-link.title.narrative']/str">
            <xsl>result.document-link.title.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.document-link.description.narrative']/str">
            <xsl>result.document-link.description.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.document-link.category.code']/str">
            <xsl>result.document-link.category.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.document-link.language.code']/str">
            <xsl>result.document-link.language.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.document-link.document-date.iso-date']/date">
            <xsl>result.document-link.document-date.iso-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.reference.vocabulary']/str">
            <xsl>result.reference.vocabulary,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.reference.code']/str">
            <xsl>result.reference.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.reference.vocabulary']/str">
            <xsl>result.reference.vocabulary-uri,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.measure']/str">
            <xsl>result.indicator.measure,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.ascending']/str">
            <xsl>result.indicator.ascending,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.aggregation-status']/str">
            <xsl>result.indicator.aggregation-status,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.title.narrative']/str">
            <xsl>result.indicator.title.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.description.narrative']/str">
            <xsl>result.indicator.description.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.document-link.format']/str">
            <xsl>result.indicator.document-link.format,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.document-link.url']/str">
            <xsl>result.indicator.document-link.url,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.document-link.title.narrative']/str">
            <xsl>result.indicator.document-link.title.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.document-link.description.narrative']/str">
            <xsl>result.indicator.document-link.description.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.document-link.category.code']/str">
            <xsl>result.indicator.document-link.category.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.document-link.language.code']/str">
            <xsl>result.indicator.document-link.language.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.document-link.document-date.iso-date']/date">
            <xsl>result.indicator.document-link.document-date.iso-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.reference.code']/str">
            <xsl>result.indicator.reference.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.reference.vocabulary']/str">
            <xsl>result.indicator.reference.vocabulary,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.reference.vocabulary-uri']/str">
            <xsl>result.indicator.reference.vocabulary-uri,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.baseline.year']/int">
            <xsl>result.indicator.baseline.year,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.baseline.iso-date']/date">
            <xsl>result.indicator.baseline.iso-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.baseline.value']/str">
            <xsl>result.indicator.baseline.value,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.baseline.location.ref']/str">
            <xsl>result.indicator.baseline.location.ref,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.baseline.dimension.name']/str">
            <xsl>result.indicator.baseline.dimension.name,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.baseline.dimension.value']/str">
            <xsl>result.indicator.baseline.dimension.value,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.baseline.document-link.format']/str">
            <xsl>result.indicator.baseline.document-link.format,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.baseline.document-link.url']/str">
            <xsl>result.indicator.baseline.document-link.url,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.baseline.document-link.title.narrative']/str">
            <xsl>result.indicator.baseline.document-link.title.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.baseline.document-link.description.narrative']/str">
            <xsl>result.indicator.baseline.document-link.description.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.baseline.document-link.category.code']/str">
            <xsl>result.indicator.baseline.document-link.category.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.baseline.document-link.language.code']/str">
            <xsl>result.indicator.baseline.document-link.language.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.baseline.document-link.document-date.iso-date']/date">
            <xsl>result.indicator.baseline.document-link.document-date.iso-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.baseline.comment.narrative']/str">
            <xsl>result.indicator.baseline.comment.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.period-start.iso-date']/date">
            <xsl>result.indicator.period.period-start.iso-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.period-end.iso-date']/date">
            <xsl>result.indicator.period.period-end.iso-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.target.value']/str">
            <xsl>result.indicator.period.target.value,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.target.location.ref']/str">
            <xsl>result.indicator.period.target.location.ref,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.target.dimension.name']/str">
            <xsl>result.indicator.period.target.dimension.name,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.target.dimension.value']/str">
            <xsl>result.indicator.period.target.dimension.value,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.target.comment.narrative']/str">
            <xsl>result.indicator.period.target.comment.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.target.document-link.format']/str">
            <xsl>result.indicator.period.target.document-link.format,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.target.document-link.url']/str">
            <xsl>result.indicator.period.target.document-link.url,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.target.document-link.title.narrative']/str">
            <xsl>result.indicator.period.target.document-link.title.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.target.document-link.description.narrative']/str">
            <xsl>result.indicator.period.target.document-link.description.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.target.document-link.category.code']/str">
            <xsl>result.indicator.period.target.document-link.category.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.target.document-link.language.code']/str">
            <xsl>result.indicator.period.target.document-link.language.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.target.document-link.document-date.iso-date']/date">
            <xsl>result.indicator.period.target.document-link.document-date.iso-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.value']/str">
            <xsl>result.indicator.period.actual.value,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.location.ref']/str">
            <xsl>result.indicator.period.actual.location.ref,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.dimension.name']/str">
            <xsl>result.indicator.period.actual.dimension.name,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.dimension.value']/str">
            <xsl>result.indicator.period.actual.dimension.value,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.comment.narrative']/str">
            <xsl>result.indicator.period.actual.comment.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.document-link-format']/str">
            <xsl>result.indicator.period.actual.document-link.format,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.document-link.url']/str">
            <xsl>result.indicator.period.actual.document-link.url,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.document-link.title.narrative']/str">
            <xsl>result.indicator.period.actual.document-link.title.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.document-link.description.narrative']/str">
            <xsl>result.indicator.period.actual.document-link.description.narrative,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.document-link.category.code']/str">
            <xsl>result.indicator.period.actual.document-link.category.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.document-link.language.code']/str">
            <xsl>result.indicator.period.actual.document-link.language.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.document-link.document-date.iso-date']/date">
            <xsl>result.indicator.period.actual.document-link.document-date.iso-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs-add.other-flags.code']/str">
            <xsl>crs-add.other-flags.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs-add.other-flags.significance']/str">
            <xsl>crs-add.other-flags.significance,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs-add.loan-terms.rate-1']/str">
            <xsl>crs-add.loan-terms.rate-1,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs-add.loan-terms.rate-2']/str">
            <xsl>crs-add.loan-terms.rate-2,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs-add.loan-terms.repayment-type.code']/str">
            <xsl>crs-add.loan-terms.repayment-type.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs-add.loan-terms.repayment-plan.code']/str">
            <xsl>crs-add.loan-terms.repayment-plan.code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs-add.loan-terms.commitment-date.iso-date']/date">
            <xsl>crs-add.loan-terms.commitment-date.iso-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs-add.loan-terms.repayment-first-date.iso-date']/date">
            <xsl>crs-add.loan-terms.repayment-first-date.iso-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs-add.loan-terms.repayment-final-date.iso-date']/date">
            <xsl>crs-add.loan-terms.repayment-final-date.iso-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs-add.loan-status.year']/int">
            <xsl>crs-add.loan-status.year,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs-add.loan-status.currency']/str">
            <xsl>crs-add.loan-status.currency,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs-add.loan-status.value-date']/date">
            <xsl>crs-add.loan-status.value-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs-add.loan-status.interest-received']/double">
            <xsl>crs-add.loan-status.interest-received,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs-add.loan-status.principal-outstanding']/double">
            <xsl>crs-add.loan-status.principal-outstanding,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='crs-add.channel-code']/str">
            <xsl>crs-add.channel-code,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::date[@name='fss.extraction-date']">
            <xsl>fss.extraction-date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::str[@name='fss.priority']">
            <xsl>fss.priority,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='fss.phaseout-year']/int">
            <xsl>fss.phaseout-year,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='fss.forecast.year']/int">
            <xsl>fss.forecast.year,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='fss.forecast.date']/date">
            <xsl>fss.forecast.date,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='fss.forecast.currency']/str">
            <xsl>fss.forecast.currency,</xsl>
        </xsl:if>
        <xsl:if
                test="ancestor::response/descendant::arr[@name='fss.forecast']/double">
            <xsl>fss.forecast,</xsl>
        </xsl:if>
        <xsl:value-of select="$break"/>
    </xsl:template>
    <xsl:template match="response/result/doc">
        <xsl:for-each select="arr[@name='sector.code']/str">
            <xsl:value-of select="ancestor::doc/descendant::str[@name='lang']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='lang']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='default-currency']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='default-currency']">
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
            <xsl:value-of select="ancestor::doc/descendant::str[@name='iati-identifier']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='iati-identifier']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='reporting-org.ref']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='reporting-org.ref']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='reporting-org.type']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='reporting-org.type']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='reporting-org.secondary-reporter']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='reporting-org.secondary-reporter']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='reporting-org.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='reporting-org.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='title.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='title.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='description.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='description.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='participating-org.ref']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='participating-org.ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='participating-org.type']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='participating-org.type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='participating-org.role']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='participating-org.role']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='participating-org.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='participating-org.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='other-identifier.ref']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='other-identifier.ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='other-identifier.owner-org.ref']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='other-identifier.owner-org.ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='other-identifier.owner-org.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='other-identifier.owner-org.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='activity-status.code']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='activity-status.code']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='activity-date.iso-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='activity-date.iso-date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='activity-date.type']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='activity-date.type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact-info.organisation.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='contact-info.organisation.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact-info.department.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='contact-info.department.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact-info.person-name.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='contact-info.person-name.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact-info.job-title.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='contact-info.job-title.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact-info.telephone']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='contact-info.telephone']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact-info.email']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='contact-info.email']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact-info.website']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='contact-info.website']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='contact-info.mailing-address.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='contact-info.mailing-address.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='activity-scope.code']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='activity-scope.code']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='recipient-country.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='recipient-country.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='recipient-country.percentage']/double"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='recipient-country.percentage']/double">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='recipient-region.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='recipient-region.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='recipient-region.percentage']/double"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='recipient-region.percentage']/double">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location.ref']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location.ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location.location-id.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location.location-id.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location.location-id.vocabulary']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location.location-id.vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location.location-reach.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location.location-reach.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location.name.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location.name.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location.description.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location.description.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location.activity-description.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location.activity-description.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location.administrative.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location.administrative.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location.administrative.vocabulary']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location.administrative.vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location.administrative.level']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location.administrative.level']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location.point.pos']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location.point.pos']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location.exactness.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location.exactness.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location.location-class.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location.location-class.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='location.feature-designation.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='location.feature-designation.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:variable name="sector.position" select="position()"/> <!--this give the position of current sector-code-->
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='sector.vocabulary']/str[$sector.position]"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='sector.vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="self::str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='sector.code']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='sector.percentage']/double[$sector.position]"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='sector.percentage']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='tag.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='tag.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='tag.vocabulary']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='tag.vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='tag.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='tag.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='country-budget-items.vocabulary']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='country-budget-items.vocabulary']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='country-budget-items.budget-item.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='country-budget-items.budget-item.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='country-budget-items.budget-item.percentage']/double"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='country-budget-items.budget-item.percentage']/double">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='country-budget-items.budget-item.description.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='country-budget-items.budget-item.description.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='humanitarian-scope.type']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='humanitarian-scope.type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='humanitarian-scope.vocabulary']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='humanitarian-scope.vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='humanitarian-scope.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='humanitarian-scope.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='humanitarian-scope.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='humanitarian-scope.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='policy-marker.vocabulary']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='policy-marker.vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='policy-marker.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='policy-marker.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='policy-marker.significance']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='policy-marker.significance']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='collaboration-type.code']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='collaboration-type.code']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='default-flow-type.code']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='default-flow-type.code']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='default-finance-type.code']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='default-finance-type.code']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='default-aid-type.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='default-aid-type.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='default-aid-type.vocabulary']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='default-aid-type.vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='default-tied-status.code']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='default-tied-status.code']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget.type']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='budget.type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget.status']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='budget.status']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget.period-start.iso-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='budget.period-start.iso-date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget.period-end.iso-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='budget.period-end.iso-date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget.value.currency']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='budget.value.currency']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget.value.value-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='budget.value.value-date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='budget.value']/double"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='budget.value']/double">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned-disbursement.type']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='planned-disbursement.type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned-disbursement.period-start.iso-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='planned-disbursement.period-start.iso-date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned-disbursement.period-end.iso-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='planned-disbursement.period-end.iso-date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned-disbursement.value.currency']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='planned-disbursement.value.currency']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned-disbursement.value.value-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='planned-disbursement.value.value-date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned-disbursement.value']/double"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='planned-disbursement.value']/double">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned-disbursement.provider-org.provider-activity-id']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='planned-disbursement.provider-org.provider-activity-id']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned-disbursement.provider-org.type']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='planned-disbursement.provider-org.type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned-disbursement.provider-org.ref']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='planned-disbursement.provider-org.ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='planned-disbursement.provider-org.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='planned-disbursement.provider-org.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:value-of select="ancestor::doc/descendant::double[@name='capital-spend.percentage']"/>
            <xsl:if
                    test="ancestor::response/descendant::double[@name='capital-spend.percentage']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.ref']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.humanitarian']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.humanitarian']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.type']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.transaction-date.iso-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.transaction-date.iso-date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.value.currency']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.value.currency']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.value.value-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.value.value-date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.value']/double"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.value']/double">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.provider-org.provider-activity-id']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.provider-org.provider-activity-id']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.provider-org.type']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.provider-org.type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.provider-org.ref']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.provider-org.ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.provider-org.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.provider-org.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.receiver-org.receiver-activity-id']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.receiver-org.receiver-activity-id']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.receiver-org.type']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.receiver-org.type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.receiver-org.ref']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.receiver-org.ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.receiver-org.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.receiver-org.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.disbursement-channel.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.disbursement-channel.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.sector.vocabulary']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.sector.vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.sector.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.sector.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.recipient-country.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.recipient-country.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.recipient-region.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.recipient-region.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.recipient-region.vocabulary']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.recipient-region.vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.flow-type.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.flow-type.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.finance-type.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.finance-type.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.aid-type.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.aid-type.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.aid-type.vocabulary']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.aid-type.vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='transaction.tied-status.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='transaction.tied-status.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='document-link.format']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='document-link.format']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='document-link.url']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='document-link.url']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='document-link.title.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='document-link.title.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='document-link.category.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='document-link.category.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='document-link.document-date.iso-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='document-link.document-date.iso-date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='related-activity.ref']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='related-activity.ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='related-activity.type']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='related-activity.type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='legacy-data.name']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='legacy-data.name']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='legacy-data.value']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='legacy-data.value']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='legacy-data.iati-equivalent']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='legacy-data.iati-equivalent']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:value-of select="ancestor::doc/descendant::str[@name='conditions.attached']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='conditions.attached']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='conditions.condition.type']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='conditions.condition.type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='conditions.condition.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='conditions.condition.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.type']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.type']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.aggregation-status']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.aggregation-status']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.title.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.title.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.description.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.description.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.document-link.format']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.document-link.format']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.document-link.url']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.document-link.url']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.document-link.title.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.document-link.title.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.document-link.description.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.document-link.description.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.document-link.category.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.document-link.category.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.document-link.language.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.document-link.language.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.document-link.document-date.iso-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.document-link.document-date.iso-date']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.reference.vocabulary']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.reference.vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.reference.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.reference.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.reference.vocabulary-uri']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.reference.vocabulary-uri']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.measure']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.measure']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.ascending']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.ascending']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.aggregation-status']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.aggregation-status']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.title.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.title.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.description.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.description.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.document-link.format']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.document-link.format']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.document-link.url']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.document.link-uri']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.document-link.title.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.document-link.title.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.document-link.description.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.document-link.description.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.document-link.category.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.document-link.category.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.document-link.language.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.document-link.language.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.document-link.document-date.iso-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.document-link.document-date.iso-date']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.reference.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.reference.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.reference.vocabulary']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.reference.vocabulary']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.reference.vocabulary-uri']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.reference.vocabulary-uri']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.baseline.year']/int"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.baseline.year']/int">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.baseline.iso-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.baseline.iso-date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.baseline.value']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.baseline.value']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.baseline.location.ref']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.baseline.location.ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.baseline.dimension.name']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.baseline.dimension.name']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.baseline.dimension.value']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.baseline.dimension.value']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.baseline.document-link.format']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.baseline.document-link.format']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.baseline.document-link.url']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.baseline.document-link.url']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.baseline.document-link.title.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.baseline.document-link.title.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.baseline.document-link.description.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.baseline.document-link.description.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.baseline.document-link.category.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.baseline.document-link.category.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.baseline.document-link.language.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.baseline.document-link.language.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.baseline.document-link.document-date.iso-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.baseline.document-link.document-date.iso-date']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.baseline.comment.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.baseline.comment.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.period-start.iso-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.period-start.iso-date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.period-end.iso-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.period-end.iso-date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.target.value']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.target.value']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.target.location.ref']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.target.location.ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.target.dimension.name']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.target.dimension.name']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.target.dimension.value']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.target.dimension.value']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.target.comment.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.target.comment.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.target.document-link.format']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.target.document-link.format']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.target.document-link.url']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.target.document-link.url']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.target.document-link.title.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.target.document-link.title.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.target.document-link.description.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.target.document-link.description.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.target.document-link.category.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.target.document-link.category.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.target.document-link.language.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.target.document-link.language.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.target.document-link.document-date.iso-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.target.document-link.document-date.iso-date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.actual.value']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.value']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.actual.location.ref']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.location.ref']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.actual.dimension.name']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.dimension.name']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.actual.dimension.value']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.dimension.value']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.actual.comment.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.comment.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.actual.document-link.format']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.document-link.format']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.actual.document-link.url']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.document-link.url']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.actual.document-link.title.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.document-link.title.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.actual.document-link.description.narrative']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.document-link.description.narrative']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.actual.document-link.category.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.document-link.category.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.actual.document-link.language.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.document-link.language.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='result.indicator.period.actual.document-link.document-date.iso-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='result.indicator.period.actual.document-link.document-date.iso-date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs-add.other-flags.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs-add.other-flags.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs-add.other-flags.significance']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs-add.other-flags.significance']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs-add.loan-terms.rate-1']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs-add.loan-terms.rate-1']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs-add.loan-terms.rate-2']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs-add.loan-terms.rate-2']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs-add.loan-terms.repayment-type.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs-add.loan-terms.repayment-type.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs-add.loan-terms.repayment-plan.code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs-add.loan-terms.repayment-plan.code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs-add.loan-terms.commitment-date.iso-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs-add.loan-terms.commitment-date.iso-date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs-add.loan-terms.repayment-first-date.iso-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs-add.loan-terms.repayment-first-date.iso-date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs-add.loan-terms.repayment-final-date.iso-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs-add.loan-terms.repayment-final-date.iso-date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs-add.loan-status.year']/int"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs-add.loan-status.year']/int">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs-add.loan-status.currency']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs-add.loan-status.currency']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs-add.loan-status.value-date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs-add.loan-status.value-date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs-add.loan-status.interest-received']/double"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs-add.loan-status.interest-received']/double">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs-add.loan-status.principal-outstanding']/double"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs-add.loan-status.principal-outstanding']/double">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='crs-add.channel-code']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='crs-add.channel-code']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:value-of select="date[@name='fss.extraction-date']"/>
            <xsl:if
                    test="ancestor::response/descendant::date[@name='fss.extraction-date']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:value-of select="str[@name='fss.priority']"/>
            <xsl:if
                    test="ancestor::response/descendant::str[@name='fss.priority']">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='fss.phaseout-year']/int"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='fss.phaseout-year']/int">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='fss.forecast.year']/int"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='fss.forecast.year']/int">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='fss.forecast.date']/date"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='fss.forecast.value-date']/date">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='fss.forecast.currency']/str"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='fss.forecast.currency']/str">
                <xsl:value-of select="$delim"/>
            </xsl:if>
            <xsl:apply-templates select="ancestor::doc/descendant::arr[@name='fss.forecast']/double"/>
            <xsl:if
                    test="ancestor::response/descendant::arr[@name='fss.forecast']/double">
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
    <xsl:template match="arr[contains(@name,'-narrative')]/str">
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
    <xsl:template match="arr[contains(@name,'-title')]/str">
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
    <xsl:template match="arr[contains(@name,'-description')]/str">
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
