<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:oai="http://www.openarchives.org/OAI/2.0/">

	<xsl:template match="@*|node()">
		<xsl:copy>
			<xsl:apply-templates select="@*|node()" />
		</xsl:copy>
	</xsl:template>

	<xsl:template match="oai:ListRecords">
		<oai:ListRecords>
			<xsl:for-each-group select="oai:record"
				group-by="oai:metadata">
				<xsl:apply-templates select="." />
			</xsl:for-each-group>
		</oai:ListRecords>
	</xsl:template>
</xsl:stylesheet>