<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:crossref="http://www.crossref.org/schema/4.4.1">
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

	<xsl:template match="crossref:conference">
		<crossref:conference>
			<crossref:event_metadata>
				<xsl:copy-of
					select="crossref:conference_name" />
				<xsl:copy-of
					select="crossref:conference_theme" />
				<xsl:copy-of
					select="crossref:conference_acronym" />
				<xsl:copy-of
					select="crossref:conference_sponsor" />
				<xsl:copy-of
					select="crossref:conference_number" />
				<xsl:copy-of
					select="crossref:conference_location" />
				<xsl:copy-of
					select="crossref:conference_date" />
			</crossref:event_metadata>
			<crossref:proceedings_metadata>
				<xsl:copy-of select="crossref:proceedings_title" />
				<xsl:copy-of select="crossref:proceedings_subject" />
				<xsl:copy-of select="crossref:publisher" />
				<xsl:copy-of select="crossref:publication_date" />
				<xsl:if test="crossref:isbn != ''">
					<xsl:copy-of select="./crossref:isbn" />
				</xsl:if>
				<xsl:if test="crossref:isbn = ''">
					<crossref:noisbn reason="simple_series">1</crossref:noisbn>
				</xsl:if>
				<xsl:copy-of select="./crossref:doi_data" />

			</crossref:proceedings_metadata>

			<xsl:copy-of select="./crossref:conference_paper" />

		</crossref:conference>

	</xsl:template>

	<xsl:template match="text()">
		<xsl:value-of select="normalize-space(.)" />
	</xsl:template>
	<!-- standard copy template -->
</xsl:stylesheet>