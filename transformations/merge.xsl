<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0"
                xmlns:crossref="http://www.crossref.org/schema/4.3.7"
>
    <xsl:output method="xml" encoding="utf-8" indent="no"/>
    <xsl:template match="/">
        <xsl:copy>
            <xsl:apply-templates mode="rootcopy"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="node()" mode="rootcopy">
        <xsl:copy>
            <xsl:variable name="folderURI" select="resolve-uri('.',base-uri())"/>
            <xsl:for-each select="collection(concat($folderURI, '?select=*.xml;recurse=no'))/*/node()">
                <xsl:apply-templates mode="copy" select="."/>
            </xsl:for-each>
        </xsl:copy>
    </xsl:template>

    <!-- Deep copy template -->
    <xsl:template match="node()|@*" mode="copy">
        <xsl:copy>
            <xsl:apply-templates mode="copy" select="@*"/>
            <xsl:apply-templates mode="copy"/>
        </xsl:copy>

    </xsl:template>

    <xsl:template name="sorting">
        <xsl:for-each select="crossref:dissertation/crossref:person_name">
            <xsl:sort select="crossref:surname"/>
            <xsl:sort select="crossref:given_name"/>
        </xsl:for-each>
    </xsl:template>


    <!-- Handle default matching -->
    <xsl:template match="*"/>
</xsl:stylesheet>
