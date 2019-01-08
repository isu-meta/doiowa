<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:oai="http://www.openarchives.org/OAI/2.0/">


	<xsl:output method="xml" encoding="utf-8" indent="yes" />

	<!-- Identity template : copy all text nodes, elements and attributes -->
	<xsl:template match="@*|node()">
		<xsl:copy>
			<xsl:apply-templates select="@*|node()" />
		</xsl:copy>
	</xsl:template>

	<!-- When matching DataSeriesBodyType: do nothing -->
	<xsl:template match="oai:record">
		<xsl:for-each select="oai:metadata">
			<xsl:choose>
				<!--Change xpath expression to split by additional elements -->
				<xsl:when
					test="document-export/documents/document/publication-title[contains(text(),'Graduate Theses and Dissertations')]">
					<xsl:copy-of select="parent::node()" />
				</xsl:when>
				<xsl:otherwise />
			</xsl:choose>
		</xsl:for-each>

	</xsl:template>
	<xsl:template match="text()" priority="2">
		<xsl:value-of select="normalize-space(.)" />
	</xsl:template>

</xsl:stylesheet>
