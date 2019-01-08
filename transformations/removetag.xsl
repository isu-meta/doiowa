<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:crossref="http://www.crossref.org/schema/4.3.7">
	<xml:output indent="yes"/>
	<xsl:template match="/">
		<!-- https://wiki.scn.sap.com/wiki/display/XI/Remove+empty+tags+from+an+XML+via+XSLT -->
		<!-- TODO: Auto-generated template -->
		<xsl:apply-templates select="*" />
	</xsl:template>

	<xsl:template match="*">
		<xsl:if test=".!=''">
			<xsl:copy>
				<xsl:copy-of select="@*" />
				<xsl:apply-templates />
			</xsl:copy>
		</xsl:if>
	</xsl:template>

	<xsl:template match="crossref:noisbn">
		<crossref:noisbn reason="simple_series" />
	</xsl:template>

	<xsl:template match="text()">
		<xsl:value-of select="normalize-space(.)" />
	</xsl:template>
	<!-- standard copy template -->
</xsl:stylesheet>