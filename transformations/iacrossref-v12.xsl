<?xml version='1.0' encoding='UTF-8'?>
<!-- ======================================================== -->
<!-- This stylesheet transforms OAI XML data to CrossRef XML. Created by 
	Ryan Wolfslayer, Iowa State University -->
<!-- ======================================================== -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:crossref="http://www.crossref.org/schema/4.3.7" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:oai="http://www.openarchives.org/OAI/2.0/" version="2.0">
	<xsl:output method="xml" indent="yes" encoding="UTF-8"/>

	<!-- Variables -->
	<!-- ['conference', 'dissertation', 'report-paper', 'journal(not complete)', 
		'book(not complete)' -->
	<xsl:variable name="doctype">
		<xsl:text>report-paper</xsl:text>
	</xsl:variable>
	<xsl:variable name="acronym">
		<xsl:text>farmprogressreports</xsl:text>
	</xsl:variable>
	<xsl:variable name="doi_prefix">
		<xsl:text>10.999999</xsl:text>
	</xsl:variable>
	<xsl:variable name="registrant">
		<xsl:text>Iowa State University, Digital Repository</xsl:text>
	</xsl:variable>
	<xsl:variable name="registrant_acronym">
		<xsl:text>ISU</xsl:text>
	</xsl:variable>
	<xsl:variable name="location">
		<xsl:text>Ames</xsl:text>
	</xsl:variable>
	<xsl:variable name="depositor">
		<xsl:text>Ryan Wolfslayer</xsl:text>
	</xsl:variable>
	<xsl:variable name="email">
		<xsl:text>rwolfsla@iastate.edu</xsl:text>
	</xsl:variable>
	<xsl:variable name="website">
		<xsl:text>https://lib.dr.iastate.edu/</xsl:text>
	</xsl:variable>
	<xsl:variable name="doi_date">
		<xsl:value-of select="format-date(current-date(),'[Y01][M01][D01]')"/>
	</xsl:variable>
	<xsl:variable name="issn">
		<xsl:text/>
	</xsl:variable>
	<xsl:variable name="journal_abbrev">
		<xsl:text/>
	</xsl:variable>

	<xsl:template match="/">
		<crossref:doi_batch xmlns:crossref="http://www.crossref.org/schema/4.3.7" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="4.3.7" xsi:schemaLocation="http://www.crossref.org/schema/4.3.7 http://www.crossref.org/schema/deposit/crossref4.3.7.xsd">
			<xsl:variable name="date" select="adjust-date-to-timezone(current-date(), ())"/>
			<xsl:variable name="time" select="adjust-time-to-timezone(current-time(), ())"/>
			<xsl:variable name="tempdatetime" select="concat($date,'',$time)"/>
			<xsl:variable name="datetime" select="translate($tempdatetime,':-.','')"/>
			<crossref:head>
				<crossref:doi_batch_id>
					<xsl:value-of select="$datetime"/>
				</crossref:doi_batch_id>
				<crossref:timestamp>
					<xsl:value-of select="$datetime"/>
				</crossref:timestamp>
				<crossref:depositor>
					<crossref:depositor_name>
						<xsl:value-of select="$depositor"/>
					</crossref:depositor_name>
					<crossref:email_address>
						<xsl:value-of select="$email"/>
					</crossref:email_address>
				</crossref:depositor>
				<crossref:registrant>
					<xsl:value-of select="$registrant"/>
				</crossref:registrant>
			</crossref:head>
			<crossref:body>
				<xsl:apply-templates/>
			</crossref:body>
		</crossref:doi_batch>
	</xsl:template>
	<!-- REMOVE FIELDS -->
	<xsl:template match="text()">
		<xsl:value-of select="normalize-space(.)"/>
	</xsl:template>
	<xsl:template match="oai:responseDate"/>
	<xsl:template match="oai:request"/>
	<xsl:template match="oai:header"/>


	<xsl:template match="oai:ListRecords">



		<!-- JOURNAL -->
		<xsl:if test="$doctype = 'journal'">
			<xsl:for-each-group select="oai:record/oai:metadata/document-export/documents" group-by="string-join(tokenize(document/submission-path, '/')[position() lt last()], '/')">

				<crossref:journal>
					<!-- May not be needed -->
					<xsl:variable name="urltestsource" select="document/coverpage-url"/>
					<!-- see above -->
					<!-- Assumes english laguage, change xpath if needed -->
					<crossref:journal_metadata>
						<xsl:attribute name="language">en</xsl:attribute>
						<crossref:full_title>
							<xsl:value-of select="normalize-space(document/publication-title)"/>
						</crossref:full_title>

						<crossref:abbrev_title>
							<xsl:value-of select="$journal_abbrev"/>
						</crossref:abbrev_title>
						<crossref:issn>
							<xsl:attribute name="media_type">electronic</xsl:attribute>
							<xsl:value-of select="$issn"/>
						</crossref:issn>

					</crossref:journal_metadata>

					<crossref:journal_issue>

						<xsl:choose>
							<xsl:when test="fields/field[@name='publication_date']">
								<xsl:apply-templates select="document/fields/field[@name='publication_date']"/>
							</xsl:when>

							<xsl:otherwise>
								<crossref:publication_date>
									<crossref:year>
										<xsl:value-of select="year-from-dateTime(xs:dateTime(document/publication-date))"/>
									</crossref:year>
								</crossref:publication_date>
							</xsl:otherwise>
						</xsl:choose>
						<crossref:journal_volume>
							<crossref:volume>
								<xsl:value-of select="translate(string-join(tokenize(document/submission-path, '/')[position() = 2], '/'),'vol', '')"/>
							</crossref:volume>
						</crossref:journal_volume>
						<crossref:issue>
							<xsl:value-of select="translate(string-join(tokenize(document/submission-path, '/')[position() = 3], '/'), 'iss', '')"/>
						</crossref:issue>
					</crossref:journal_issue>


					<!-- Journal Article -->

					<xsl:for-each select="current-group()">
						<crossref:journal_article>
							<xsl:attribute name="publication_type">full_text</xsl:attribute>
							<xsl:apply-templates select="document/title"/>
							<crossref:contributors>
								<xsl:apply-templates select="document/authors"/>
							</crossref:contributors>
							<xsl:choose>
								<xsl:when test="fields/field[@name='publication_date']">
									<xsl:apply-templates select="document/fields/field[@name='publication_date']"/>
								</xsl:when>

								<xsl:otherwise>
									<crossref:publication_date>
										<crossref:year>
											<xsl:value-of select="year-from-dateTime(xs:dateTime(document/publication-date))"/>
										</crossref:year>
									</crossref:publication_date>
								</xsl:otherwise>
							</xsl:choose>
							<xsl:apply-templates select="document/fields/field[@name='pages']"/>
							<xsl:variable name="numb">
								<xsl:number format="1" level="any"/>
							</xsl:variable>
							<crossref:publisher_item>
								<crossref:item_number>
									<xsl:value-of select="document/context-key"/>
								</crossref:item_number>
							</crossref:publisher_item>
							<crossref:doi_data>
								<crossref:doi>
									<xsl:value-of select="string(concat($doi_prefix,'/',$acronym,'-',$doi_date, '-', $numb))"/>
								</crossref:doi>
								<crossref:resource>
									<xsl:value-of select="document/fulltext-url"/>
								</crossref:resource>
							</crossref:doi_data>

							<!-- Citations pulled from second xml file, see citationFinder.py -->
							<!-- Comment out or replace if citation can be found in metadata -->
							<xsl:variable name="citationtest">
								<xsl:value-of select="document/fulltext-url"/>
							</xsl:variable>
							<crossref:citation_list>
								<xsl:for-each select="document('citationsfound.xml')/*/citationlist">
									<xsl:if test="$citationtest = ./@file">
										<xsl:for-each select="citation">
											<crossref:citation>
												<xsl:attribute name="key"> <xsl:value-of select="@key"/></xsl:attribute>
												<xsl:for-each select="issn">
													<xsl:if test="position()=1">
														<crossref:issn>
															<xsl:value-of select="."/>
														</crossref:issn>
													</xsl:if>
												</xsl:for-each>
												<crossref:journal_title>
													<xsl:value-of select="journal_title"/>
												</crossref:journal_title>
												<crossref:author>
													<xsl:value-of select="author"/>
												</crossref:author>
												<crossref:volume>
													<xsl:value-of select="volume"/>
												</crossref:volume>
												<crossref:issue>
													<xsl:value-of select="issue"/>
												</crossref:issue>
												<crossref:first_page>
													<xsl:value-of select="first_page"/>
												</crossref:first_page>
												<crossref:cYear>
													<xsl:value-of select="cYear"/>
												</crossref:cYear>

											</crossref:citation>
										</xsl:for-each>



									</xsl:if>
								</xsl:for-each>
							</crossref:citation_list>
						</crossref:journal_article>

					</xsl:for-each>
				</crossref:journal>
			</xsl:for-each-group>
		</xsl:if>

		<!-- CONFERENCE SERIES -->
		<xsl:if test="$doctype = 'conference'">
			<xsl:for-each-group select="oai:record/oai:metadata/document-export/documents" group-by="document/publication-title">

				<crossref:conference>

					<xsl:variable name="urltestsource" select="document/coverpage-url"/>

					<crossref:proceedings_title>
						<xsl:value-of select="normalize-space(current-grouping-key())"/>
					</crossref:proceedings_title>
					<crossref:proceedings_subject/>

					<crossref:publisher>
						<crossref:publisher_name>
							<xsl:value-of select="$registrant"/>
						</crossref:publisher_name>
					</crossref:publisher>
					<xsl:variable name="yearstring">
						<xsl:value-of select="year-from-dateTime(document/publication-date)"/>
					</xsl:variable>
					<xsl:for-each-group select="current-group()" group-by="$yearstring">
						<crossref:publication_date>
							<xsl:attribute name="media_type">online</xsl:attribute>

							<crossref:year>
								<xsl:value-of select="current-grouping-key()"/>
							</crossref:year>
						</crossref:publication_date>

						<!-- This section is intended to pull data from a second xml file, 
							customize as needed -->

						<xsl:variable name="urlref" select="string(concat($website, $acronym, '/',current-grouping-key()))"/>
						<xsl:if test="contains($urltestsource, $urlref)">
							<xsl:for-each select="document('suppdata.xml')/*/item">
								<xsl:if test="contains($urlref, resourceurl)">
									<crossref:conference_name>
										<xsl:value-of select="normalize-space(title/value)"/>
									</crossref:conference_name>
									<crossref:conference_theme/>
									<crossref:conference_acronym/>
									<crossref:conference_sponsor/>
									<crossref:conference_number/>
									<xsl:variable name="var" select="dateandtime"/>
									<xsl:variable name="value" select="substring-after($var, '(')"/>
									<xsl:variable name="no1" select="substring-before($value, ')')"/>


									<crossref:conference_location>
										<xsl:value-of select="$no1"/>
									</crossref:conference_location>
									<crossref:conference_date>
										<xsl:value-of select="substring-before(dateandtime, '(')"/>
									</crossref:conference_date>

								</xsl:if>
							</xsl:for-each>
						</xsl:if>


						<xsl:variable name="numb">
							<xsl:number format="1" level="any"/>
						</xsl:variable>
						<crossref:isbn/>
						<crossref:doi_data>
							<crossref:doi>
								<xsl:value-of select="string(concat($doi_prefix,'/',$acronym,'-',$doi_date, '-c', $numb))"/>
							</crossref:doi>
							<crossref:resource>
								<xsl:value-of select="string(concat($website, $acronym, '/',current-grouping-key()))"/>
							</crossref:resource>
						</crossref:doi_data>


						<xsl:for-each-group select="current-group()" group-by="document/publication-title">
							<crossrefproceedings_title>
								<xsl:value-of select="normalize-space(current-grouping-key())"/>
							</crossrefproceedings_title>


							<!-- CONFERENCE PAPER -->

							<xsl:for-each select="current-group()">
								<crossref:conference_paper>
									<crossref:contributors>
										<xsl:apply-templates select="document/authors"/>
									</crossref:contributors>
									<xsl:apply-templates select="document/title"/>
									<xsl:apply-templates select="document/fields/field[@name='publication_date']"/>
									<xsl:apply-templates select="document/fields/field[@name='pages']"/>
									<xsl:variable name="numb">
										<xsl:number format="1" level="any"/>
									</xsl:variable>
									<crossref:publisher_item>
										<crossref:item_number>
											<xsl:value-of select="document/context-key"/>
										</crossref:item_number>
									</crossref:publisher_item>
									<crossref:doi_data>
										<crossref:doi>
											<xsl:value-of select="string(concat($doi_prefix,'/',$acronym,'-',$doi_date, '-', $numb))"/>
										</crossref:doi>
										<crossref:resource>
											<xsl:choose>
												<xsl:when test="document/fulltext-url">
													<xsl:value-of select="document/fulltext-url"/>
												</xsl:when>
												<xsl:otherwise>
													<xsl:value-of select="document/coverpage-url"/>
												</xsl:otherwise>
											</xsl:choose>
										</crossref:resource>
									</crossref:doi_data>
								</crossref:conference_paper>
							</xsl:for-each>

						</xsl:for-each-group>
					</xsl:for-each-group>
				</crossref:conference>

			</xsl:for-each-group>


		</xsl:if>
		<xsl:if test="$doctype = 'dissertation'">
			<xsl:apply-templates select="./oai:record/oai:metadata/document-export/documents/document"/>
		</xsl:if>
		<xsl:if test="$doctype = 'report-paper'">
			<xsl:apply-templates select="./oai:record/oai:metadata/document-export/documents/document"/>
		</xsl:if>

	</xsl:template>

	<xsl:template match="documents/document">



		<xsl:if test="$doctype = 'journal'"/>
		<xsl:if test="$doctype = 'book'"/>


		<!-- Dissertation -->
		<xsl:if test="$doctype = 'dissertation'">


			<crossref:dissertation>
				<xsl:apply-templates select="authors"/>
				<xsl:apply-templates select="title"/>
				<crossref:approval_date>
					<xsl:attribute name="media_type">online</xsl:attribute>
					<crossref:year>
						<xsl:value-of select="year-from-dateTime(xs:dateTime(./fields/field[@name='publication_date']/value))"/>
					</crossref:year>
				</crossref:approval_date>
				<crossref:institution>
					<!-- Assumes institutions are those of registrant -->
					<crossref:institution_name>
						<xsl:value-of select="$registrant"/>
					</crossref:institution_name>
					<crossref:institution_acronym>
						<xsl:value-of select="$registrant_acronym"/>
					</crossref:institution_acronym>
					<crossref:institution_place>
						<xsl:value-of select="$location"/>
					</crossref:institution_place>
					<xsl:for-each select="fields/field[@name='department']">
						<crossref:institution_department>
							<xsl:value-of select="value"/>
						</crossref:institution_department>
					</xsl:for-each>
				</crossref:institution>
				<crossref:degree>
					<xsl:choose>
						<xsl:when test="not(./fields/field[@name='degree_name']/value)">
							<xsl:text>other</xsl:text>
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="./fields/field[@name='degree_name']/value"/>

						</xsl:otherwise>
					</xsl:choose>
				</crossref:degree>
				<crossref:publisher_item>
					<crossref:item_number>
						<xsl:value-of select="./context-key"/>
					</crossref:item_number>
				</crossref:publisher_item>
				<xsl:variable name="numb">
					<xsl:number format="1" level="any"/>
				</xsl:variable>
				<crossref:doi_data>
					<crossref:doi>
						<xsl:value-of select="string(concat($doi_prefix,'/',$acronym,'-',$doi_date, '-', $numb))"/>
					</crossref:doi>
					<xsl:if test="fulltext-url/text()">
						<crossref:resource>
							<xsl:value-of select="fulltext-url"/>
						</crossref:resource>
					</xsl:if>
				</crossref:doi_data>

			</crossref:dissertation>

		</xsl:if>


		<!-- REPORT -->
		<xsl:if test="$doctype = 'report-paper'">
			<crossref:report-paper>
				<crossref:report-paper_metadata>
					<xsl:choose>
						<xsl:when test="./fields/field[@name='language']/value">
							<xsl:attribute name="language"><xsl:value-of select="./fields/field[@name='language']/value"/></xsl:attribute>
						</xsl:when>
						<xsl:otherwise>
							<xsl:attribute name="language"><xsl:text>en</xsl:text></xsl:attribute>
						</xsl:otherwise>
					</xsl:choose>
					<xsl:if test="./authors/author">
						<crossref:contributors>
							<xsl:apply-templates select="authors"/>
						</crossref:contributors>
					</xsl:if>
					<xsl:apply-templates select="./title"/>
					<!-- Current script for edition number is a placeholder -->
					<xsl:if test="./fields/field[@name='edition']/value">
						<crossref:edition_number>
							<xsl:value-of select="./fields/field[@name='edition']/value"/>
						</crossref:edition_number>
					</xsl:if>
					<!-- assumes media_type=online, please change in template if otherwise -->
					<xsl:apply-templates select="./fields/field[@name='publication_date']"/>
					<!-- assumes registrant is publisher, change in template as needed -->
					<crossref:publisher>
						<crossref:publisher_name>
							<xsl:value-of select="$registrant"/>
						</crossref:publisher_name>
						<crossref:publisher_place>
							<xsl:value-of select="$location"/>
						</crossref:publisher_place>
					</crossref:publisher>
					<!-- Write XPATH to appropriate field if needed -->
					<!-- Placeholder code -->
					<xsl:if test="path/to/insitution">
						<crossref:institution>
							<crossref:institution_name>
								<xsl:value-of select="path/to/institution"/>
							</crossref:institution_name>
							<crossref:instution_acronym>
								<xsl:value-of select="path/to/acronym"/>
							</crossref:instution_acronym>
							<crossref:institution_place>
								<xsl:value-of select="path/to/institutionplace"/>
							</crossref:institution_place>
							<crossref:institution_department>
								<xsl:value-of select="path/to/instutiondepartment"/>
							</crossref:institution_department>
						</crossref:institution>
					</xsl:if>
					<!-- End of institution placeholder -->
					<crossref:publisher_item>
						<crossref:item_number>
							<xsl:value-of select="./context-key"/>
						</crossref:item_number>
						<xsl:if test="./fields/field[@name='report_number']/value">
							<crossref:identifier>
								<xsl:attribute name="id_type"><xsl:text>report-number</xsl:text></xsl:attribute>
								<xsl:value-of select="./fields/field[@name='report_number']/value"/>
							</crossref:identifier>
						</xsl:if>
					</crossref:publisher_item>

					<xsl:for-each select=".">
						<xsl:variable name="numb">
							<xsl:number format="1" level="any"/>
						</xsl:variable>
						<crossref:doi_data>
							<crossref:doi>
								<xsl:value-of select="string(concat($doi_prefix,'/',$acronym,'-',$doi_date, '-', $numb))"/>
							</crossref:doi>
							<crossref:resource>
								<xsl:choose>
									<xsl:when test="./fulltext-url">
										<xsl:value-of select="./fulltext-url"/>
									</xsl:when>
									<xsl:otherwise>
										<xsl:value-of select="./coverpage-url"/>
									</xsl:otherwise>
								</xsl:choose>
							</crossref:resource>
						</crossref:doi_data>
					</xsl:for-each>

				</crossref:report-paper_metadata>
			</crossref:report-paper>
		</xsl:if>


	</xsl:template>

	<!-- AUTHORS -->
	<xsl:template match="authors">
		<xsl:for-each select="./author">
			<xsl:choose>
				<xsl:when test="$doctype = 'dissertation'">
					<xsl:if test="position()=1">
						<crossref:person_name>
							<xsl:attribute name="sequence">
				<xsl:if test="position()=1"><xsl:text>first</xsl:text></xsl:if>
				</xsl:attribute>
							<xsl:attribute name="contributor_role"><xsl:value-of select="./name()"/></xsl:attribute>
							<xsl:if test="./fname">
								<crossref:given_name>
									<xsl:choose>
										<xsl:when test="./mname">
											<xsl:value-of select="replace(./fname,'[,0-9]+','')"/>
											<xsl:text> </xsl:text>
											<xsl:value-of select="replace(./mname,'[,0-9]+','')"/>
										</xsl:when>
										<xsl:otherwise>
											<xsl:value-of select="replace(./fname,'[,0-9]+','')"/>
										</xsl:otherwise>
									</xsl:choose>
								</crossref:given_name>
							</xsl:if>
							<crossref:surname>
								<xsl:value-of select="./lname"/>
							</crossref:surname>
							<xsl:if test="./institution">
								<crossref:affiliation>
									<xsl:value-of select="./institution"/>
								</crossref:affiliation>
							</xsl:if>
						</crossref:person_name>
					</xsl:if>
					<xsl:if test="position()&gt;1"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:if test="./lname">
						<crossref:person_name>
							<xsl:attribute name="sequence">
				<xsl:if test="position()=1"><xsl:text>first</xsl:text></xsl:if>
				<xsl:if test="position()&gt;1"><xsl:text>additional</xsl:text></xsl:if>
				</xsl:attribute>
							<xsl:attribute name="contributor_role"><xsl:value-of select="./name()"/></xsl:attribute>
							<xsl:if test="./fname">
								<crossref:given_name>
									<xsl:choose>
										<xsl:when test="./mname">
											<xsl:value-of select="replace(./fname,'[,0-9]+','')"/>
											<xsl:text> </xsl:text>
											<xsl:value-of select="replace(./mname,'[,0-9]+','')"/>
										</xsl:when>
										<xsl:otherwise>
											<xsl:value-of select="replace(./fname,'[,0-9]+','')"/>
										</xsl:otherwise>
									</xsl:choose>
								</crossref:given_name>
							</xsl:if>
							<crossref:surname>
								<xsl:value-of select="./lname"/>
							</crossref:surname>
							<xsl:if test="./institution">
								<crossref:affiliation>
									<xsl:value-of select="./institution"/>
								</crossref:affiliation>
							</xsl:if>
						</crossref:person_name>
					</xsl:if>
					<xsl:if test="./organization">
						<crossref:organization>
							<xsl:attribute name="sequence">
					<xsl:if test="position()=1"><xsl:text>first</xsl:text></xsl:if>
				<xsl:if test="position()&gt;1"><xsl:text>additional</xsl:text></xsl:if>
					</xsl:attribute>
							<xsl:attribute name="contributor_role"><xsl:value-of select="./name()"/></xsl:attribute>
							<xsl:value-of select="./organization"/>
						</crossref:organization>
					</xsl:if>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:for-each>
	</xsl:template>


	<!--TITLE -->
	<xsl:template match="document/title">
		<crossref:titles>
			<xsl:for-each select=".">
				<crossref:title>
					<xsl:value-of select="normalize-space(.)"/>
				</crossref:title>
			</xsl:for-each>
		</crossref:titles>
	</xsl:template>

	<!-- Fields -->

	<!-- Publication Date -->
	<xsl:template match="fields/field[@name='publication_date']">

		<crossref:publication_date>
			<xsl:attribute name="media_type">online</xsl:attribute>
			<xsl:if test="xs:integer(month-from-dateTime(xs:dateTime(./value)))&gt;1 and xs:integer(day-from-dateTime(xs:dateTime(./value)))&gt;1">

				<crossref:month>
					<xsl:value-of select="month-from-dateTime(xs:dateTime(./value))"/>
				</crossref:month>
				<crossref:day>
					<xsl:value-of select="day-from-dateTime(xs:dateTime(./value))"/>
				</crossref:day>
			</xsl:if>
			<crossref:year>
				<xsl:value-of select="year-from-dateTime(xs:dateTime(./value))"/>
			</crossref:year>
		</crossref:publication_date>
	</xsl:template>

	<!-- Pages -->
	<xsl:template match="fields/field[@name='pages']">
		<xsl:if test="./value">
			<crossref:pages>
				<xsl:choose>
					<xsl:when test="contains(./value, '-')">
						<crossref:first_page>
							<xsl:value-of select="substring-before(value,'-')"/>
						</crossref:first_page>
						<crossref:last_page>
							<xsl:value-of select="substring-after(value,'-')"/>
						</crossref:last_page>
					</xsl:when>
					<xsl:otherwise>
						<crossref:first_page>
							<xsl:value-of select="value"/>
						</crossref:first_page>
						<crossref:last_page>
							<xsl:value-of select="value"/>
						</crossref:last_page>
					</xsl:otherwise>
				</xsl:choose>


			</crossref:pages>

		</xsl:if>

	</xsl:template>



	<!-- DOI -->

	<xsl:template match="oai:resumptionToken"/>
</xsl:stylesheet>
