"""Objects and functions for working with metadata in doiowa."""
import datetime

from lxml import etree
from lxml.builder import E
import requests


def add_dois_to_md_objects(prefix, collection, md_objects, start=0):
    """Create DOIs for each object in a list.

    Pass data for generating DOIs to the generate_doi method of
    each doiowa.md.BaseMetadata object in a list.

    Parameters
    ----------
    prefix : str
        The DOI prefix used by your organization. Ex. 10.99999.
    collection : str
        The collection acronym.
    md_objects : list of doiowa.md.BaseMetadata objects
        Metadata objects to add DOIs to.
    start : int
        The sequence number to start at. Optional. Default is 0.
    
    Returns
    -------
    None
    """
    for n, md in enumerate(md_objects, start):
        md.generate_doi(prefix, collection, n)


def get_doi_batch_id_from_xml(xml_file, schema_version="4.4.2"):
    """Get the DOI batch ID from an XML file

    Extract the DOI batch ID from the provided file. The schema_version
    argument is optional and only needed for working with historical XML
    files. Prior to 2019-06-21, we used version 4.3.7 of the Crossref
    metadata deposit schema and may have used others before that. Prior to
    2019-10-29, we used 4.4.1. We currently use 4.4.2.

    Parameters
    ----------
    xml_file : str
        Path to an XML file.
    schema_version : str
        Version number for the schema to use. Defaults to '4.4.2'.

    Returns
    -------
    str
        The DOI batch ID.
    """

    ns = {"crossref": f"http://www.crossref.org/schema/{schema_version}"}
    doi_batch_id_xpath = (
        "/crossref:doi_batch/crossref:head/crossref:doi_batch_id/text()"
    )
    tree = etree.parse(xml_file)

    doi_batch_id = tree.xpath(doi_batch_id_xpath, namespaces=ns)[0]

    return doi_batch_id


class CrossrefXML:
    """Object for root Crossref XML.

    This object includes methods to build a valid Crossref
    metadata deposit XML file from doiowa.md.Depositor and
    doiowa.md.BaseMetadata provided lxml.etrees.

    Attributes
    ----------
    root : lxml.etree
        XML root element and body element that conform to the Crossref
        metadata deposit metadata schema, version 4.4.1.

    """

    def __init__(self):
        self.root = etree.fromstring(
            b"""<?xml version="1.0" encoding="UTF-8"?>
<doi_batch xmlns="http://www.crossref.org/schema/4.4.1"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="4.4.1"
           xsi:schemaLocation="http://www.crossref.org/schema/4.4.1  http://data.crossref.org/schemas/crossref4.4.1.xsd">
    <body></body>
</doi_batch>"""
        )

    def insert_depositor(self, depositor_xml):
        """Adds depositor metadata to CrossrefXML.root.

        Add the lxml.etree from doiowa.md.Depositor.to_xml()
        to CrossrefXML.root.

        Parameters
        ----------
        depositor_xml : lxml.etree
            XML head element with depositor child element to insert
            into first child position of doi_batch element.

        Returns
        -------
        None
        """
        self.root.insert(0, depositor_xml)

    def insert_item_metadata(self, md):
        """Adds digital object metadata to body element in CrossrefXML.root.

        Adds the lxml.etree from doiowa.md.BaseMetadata.to_xml() to
        CrossrefXML.root.


        Parameters:
        -----------
        md : lmxl.etree
            XML item metadata to insert into the body element of
            doi_batch.

        Returns
        -------
        None
        """
        self.root[-1].append(md)

    def to_xml(self):
        """Returns self.root lxml.etree.

        Returns
        -------
        lxml.etree
        """
        return self.root


class Depositor:
    """Crossref depositor metadata.

    This object contains the metadata for the Crossref metadata
    deposit schema's depositor element and associated children, and
    a to_xml method to return an lxml.etree of the depositor metadata
    that can be inserted into a doiowa.md.CrossrefXML object to 
    build a valid Crossref XML document.

    Parameters
    ----------
    doi_batch_id : str or int
        Batch ID for this DOI registration submission. Must be
        unique from all other batch IDs used. We currently use a
        timestamp with the format YYYYMMDDHHMMSS.
    timestamp : int
        Timestamp for the submission. Currently this uses the
        format YYYYMMDDHHMMSS.
    depositor_name : str
        The name of the organization depositing the DOI metadata.
        Defaults to 'Iowa State University. Library. Metadata
        Services Department'.
    email_address : str
        The email address of the depositor. Defaults to 
        'metadata@iastate.edu'.
    registrant : str
        The name of the organization that owns the information
        being registered. Defaults to 'Iowa State University. Library'.

    Attributes
    ----------
    doi_batch_id : str or int
        Batch ID for this DOI registration submission.
    timestamp : int
        Timestamp for the submission.
    depositor_name : str
        The name of the organization depositing the DOI metadata.
    email_address : str
        The email address of the depositor.
    registrant : str
        The name of the organization that owns the information
        being registered.
    """

    def __init__(
        self,
        doi_batch_id,
        timestamp,
        depositor_name="Iowa State University. Library. Metadata Services Department",
        email_address="metadata@iastate.edu",
        registrant="Iowa State University. Library",
    ):
        self.doi_batch_id = doi_batch_id
        self.timestamp = timestamp
        self.depositor_name = depositor_name
        self.email_address = email_address
        self.registrant = registrant

    def to_xml(self):
        """Returns self.root lxml.etree.

        Returns
        -------
        lxml.etree
        """
        head = E.head(
            E.doi_batch_id(self.doi_batch_id),
            E.timestamp(self.timestamp),
            E.depositor(
                E.depositor_name(self.depositor_name),
                E.email_address(self.email_address),
            ),
            E.registrant(self.registrant),
        )

        return head


class BaseMetadata:
    """Foundation of all metadata classes. Includes methods used by both
    AggregateMetadata and ItemMetadata."""

    def __init__(
        self,
        *,
        contributors=[],
        date={"year": "1400", "month": "01", "day": "01"},
        doi="",
        edition_number=0,
        media_type="",
        publisher_name="",
        publisher_place="",
        resource="",
        title="",
    ):
        self.contributors = contributors
        self.date = date
        self.doi = doi
        self.edition_number = edition_number
        self.media_type = media_type
        self.publisher_name = publisher_name
        self.publisher_place = publisher_place
        self.resource = resource
        self.title = title

    def _xml_contributors(self):
        """Returns contributor XML as lxml.etree.

        Returns
        -------
        lxml.etree
        """
        contributors = E.contributors()

        if self.contributors:
            for i, c in enumerate(self.contributors):
                if i == 0:
                    seq = "first"
                else:
                    seq = "additional"

                try:
                    c_xml = E.person_name(
                        E.given_name(c["given_name"]),
                        E.surname(c["surname"]),
                        sequence=seq,
                        contributor_role="author",
                    )
                except KeyError:
                    c_xml = E.organization(
                        c["organization"], sequence=seq, contributor_role="author"
                    )

                contributors.append(c_xml)

                return contributors
        else:
            return None

    def _xml_doi_data(self):
        """Returns DOI data XML as lxml.etree.

        Returns
        -------
        lxml.etree
        """
        doi_data = E.doi_data(E.doi(self.doi), E.resource(self.resource))
        return doi_data

    def _xml_edition_number(self):
        """Returns edition number XML as lxml.etree.

        Returns
        -------
        lxml.etree
        """
        edition_number = E.edition_number(str(self.edition_number))
        return edition_number

    def _xml_publication_date(self):
        """Returns publication date XML as lxml.etree.

        Returns
        -------
        lxml.etree
        """
        publication_date = E.publication_date(
            E.month(self.date["month"]),
            E.day(self.date["day"]),
            E.year(self.date["year"]),
            media_type=self.media_type,
        )

        return publication_date

    def _xml_publisher(self):
        """Returns publisher XML as lxml.etree.

        Returns
        -------
        lxml.etree
        """
        publisher = E.publisher(
            E.publisher_name(self.publisher_name),
            E.publisher_place(self.publisher_place),
        )

        return publisher

    def _xml_title(self):
        """Returns title XML as lxml.etree.

        Returns
        -------
        lxml.etree
        """
        title = E.titles(E.title(self.title))

        return title


class AggregateMetadata(BaseMetadata):
    """Foundation of aggregating parent objects such as conference
    proceedings, books with subsections needing their own DOIs and journal
    issues.
    """

    def __init__(
        self,
        *,
        conference_acronym="",
        conference_end_date={"year": "1400", "month": "01", "day": "01"},
        conference_location="",
        conference_name="",
        conference_number=0,
        conference_sponsor="",
        conference_start_date={"year": "1400", "month": "01", "day": "01"},
        conference_theme="",
        contributors=[],
        date={"year": "1400", "month": "01", "day": "01"},
        doi="",
        edition_number=0,
        isbn="",
        kind="",
        language="en",
        media_type="",
        proceedings_subject="",
        proceedings_title="",
        publisher_name="",
        publisher_place="",
        resource="",
        title="",
    ):
        self.conference_acronym = conference_acronym
        self.conference_end_date = conference_end_date
        self.conference_location = conference_location
        self.conference_name = conference_name
        self.conference_number = conference_number
        self.conference_sponsor = conference_sponsor
        self.conference_start_date = conference_start_date
        self.conference_theme = conference_theme
        self.contributors = contributors
        self.date = date
        self.doi = doi
        self.edition_number = edition_number
        self.isbn = isbn
        self.kind = kind
        self.language = language
        self.media_type = media_type
        self.proceedings_subject = proceedings_subject
        self.proceedings_title = proceedings_title
        self.publisher_name = publisher_name
        self.publisher_place = publisher_place
        self.resource = resource
        self.title = title

    def _xml_conference_date(self):
        """Returns conference start and end date XML as lxml.etree.
        
        Returns
        -------
        lxml.etree
        """
        conference_date = E.conference_date(
            start_month=self.conference_start_date["month"],
            start_year=self.conference_start_date["year"],
            start_day=self.conference_start_date["day"],
            end_month=self.conference_end_date["month"],
            end_year=self.conference_end_date["year"],
            end_day=self.conference_end_date["day"],
        )

        return conference_date

    def _xml_event_metadata(self):
        """Returns event metadata XML as lxml.etree.

        Returns
        -------
        lxml.etree
        """
        event_md = E.eventmetadata(E.conference_name(self.conference_name))

        if self.conference_theme:
            event_md.append(E.conference_theme(self.conference_theme))

        if self.conference_acronym:
            event_md.append(E.conference_acronym(self.conference_acronym))

        if self.conference_sponsor:
            event_md.append(E.conference_sponsor)

        if self.conference_number:
            event_md.append(E.conference_number(str(self.conference_number)))

        event_md.append(self._xml_conference_date())

        return event_md

    def _xml_proceedings_metadata(self):
        """Returns proceedings metadata XML as lxml.etree.

        Returns
        -------
        lxml.etree
        """
        proceedings_md = E.proceedings_metadata(
            E.proceedings_title(self.proceedings_title), language=self.language
        )

        if self.proceedings_subject:
            proceedings_md.append(self.proceedings_subject)

        proceedings_md.append(self._xml_publisher())
        proceedings_md.append(self._xml_publication_date())

        if self.isbn:
            proceedings_md.append(E.isbn(self.isbn))
        else:
            proceedings_md.append(E.noisbn("simple series"))

        if self.doi:
            proceedings_md.append(self._xml_doi_data())

        return proceedings_md

    def to_xml(self):
        if self.kind == "proceedings":
            root = E.conference()

            conference_contributors = self._xml_contributors()
            if conference_contributors is not None:
                root.append(conference_contributors)

            root.append(self._xml_event_metadata())
            root.append(self._xml_proceedings_metadata())

        return root


class ItemMetadata(BaseMetadata):
    """Foundation of all doiowa item-level Metadata classes.

    This class collects all the metadata needed to create a DOI for an
    object and produces the XML for the digital object. Use class for
    monographs and other non-aggregate publications such as reports, as well
    as 
    """

    def __init__(
        self,
        *,
        abstract="",
        citation_list=[],
        component_list=[],
        contributors=[],
        date={"year": "1400", "month": "01", "day": "01"},
        doi="",
        edition_number=0,
        kind="",
        institution_acronym="",
        institution_department="",
        institution_name="",
        institution_place="",
        language="en",
        media_type="",
        pages=[],
        publication_type="full_text",
        publisher_name="",
        publisher_place="",
        resource="",
        title="",
    ):
        self.abstract = abstract
        self.citation_list = citation_list
        self.component_list = component_list
        self.contributors = contributors
        self.date = date
        self.doi = doi
        self.edition_number = edition_number
        self.institution_name = institution_name
        self.institution_place = institution_place
        self.institution_acronym = institution_acronym
        self.institution_department = institution_department
        self.kind = kind
        self.language = language
        self.media_type = media_type
        self.pages = pages
        self.publication_type = publication_type
        self.publisher_name = publisher_name
        self.publisher_place = publisher_place
        self.resource = resource
        self.timestamp = datetime.datetime.now().isoformat()
        self.title = title

    def _xml_citation_list(self):
        pass

    def _xml_component_list(self):
        pass

    def _xml_conference_paper(self):
        root = E.conference_paper(publication_type=self.publication_type)
        contributors = self._xml_contributors()
        if contributors is not None:
            root.append(self._xml_contributors())
        root.append(self._xml_title())
        root.append(self._xml_publication_date())
        if self.pages:
            root.append(self._xml_pages())
        if self.citation_list:
            root.append(self._xml_citation_list())
        if self.component_list:
            root.append(self._xml_component_list())

        return root

    def _xml_institution(self):
        """Returns institution XML as lxml.etree.

        Returns
        -------
        lxml.etree
        """
        institution = E.institution(E.institution_name(self.institution_name))

        if self.institution_acronym:
            institution.append(E.institution_acronym(self.institution_acronym))

        institution.append(E.institution_place(self.institution_place))

        if self.institution_department:
            institution.append(E.institution_department(self.institution_department))

        return institution

    def _xml_pages(self):
        pages = E.pages(E.first_page(self.pages[0]), E.last_page(self.pages[1]))
        return pages

    def _xml_report(self):
        root = etree.fromstring(
            f'<report-paper><report-paper_metadata language="{self.language}"></report-paper_metadata></report-paper>'
        )

        contributors = self._xml_contributors()
        if contributors is not None:
            root[0].append(contributors)

        root[0].append(self._xml_title())
        root[0].append(self._xml_edition_number())
        root[0].append(self._xml_publication_date())
        root[0].append(self._xml_publisher())
        root[0].append(self._xml_institution())
        root[0].append(self._xml_doi_data())

        return root





    def from_crossref_dict(self, crossref_dict):
        contributors = crossref_dict.get("author", [])

        if not len(contributors) == 0:
            if "given" in contributors[0].keys():
                for i, c in enumerate(contributors):
                    contributors[i]["given_name"] = c["given"]
                    contributors[i]["surname"] = c["family"]

                    del contributors[i]["given"]
                    del contributors[i]["family"]

        date_list = []
        publication_date = {"year": "1400", "month": "01", "day": "01"}
        if "published-online" in crossref_dict.keys():
            media_type = "electronic"
            date_list = crossref_dict["published-online"]["date-parts"]

        elif "published-print" in crossref_dict.keys():
            media_type = "print"
            date_list = crossref_dict["published-print"]["date-parts"]
        else:
            media_type = ""

        if date_list:
            publication_date["year"], publication_date["month"], publication_date["day"] = date_list

        institution = crossref_dict.get("institution", dict())

        # Need to resolve the doi.org URL to the URL it points to.
        r = requests.get(crossref_dict["URL"])
        self.resource = r.url

        self.abstract = crossref_dict.get("abstract", "")
        self.citation_list = crossref_dict.get("reference", [])
        self.component_list = crossref_dict.get("component", [])
        self.contributors = contributors
        self.date = publication_date
        self.doi = crossref_dict.get("DOI", "")
        self.edition_number = crossref_dict.get("edition", 0)
        self.institution_name = institution.get("name", "")
        self.institution_place = institution.get("place", [""])[0]
        self.institution_acronym = institution.get("acronym", [""])[0]
        self.institution_department = institution.get("department", [""])[0]
        self.kind = crossref_dict.get("type", "")
        self.language = crossref_dict.get("language", "en")
        self.media_type = media_type
        self.pages = crossref_dict.get("page", "")
        self.publication_type = "full_text"
        self.publisher_name = crossref_dict.get("publisher", "")
        self.publisher_place = crossref_dict.get("publisher-location", "")
        self.timestamp = datetime.datetime.now().isoformat()
        self.title = crossref_dict.get("title", [""])[0]





    def generate_doi(self, prefix, collection, seq_num):
        """Generate the DOI for the item.

        As of June 2019, our practice is to build DOIs using the
        following format: our DOI prefix, followed by a slash, followed
        by a collection acronym (For BePress this is the OAI-PMH-searchable
        acronym used in BePress. May differ for other platforms.),
        followed by a hyphen, followed by the date in condensed
        ISO 8601 format (YYYYMMDD), followed by a hyphen, followed
        by the sequence number, which is three digits wide and
        includes leading zeros for numbers with fewer than three
        digits.

        An example from the Animal Industry Report collection:
        10.31274/ans_air-190411-001

        This pattern is not used for digital press materials,
        which will have DOIs generated from within Janeway.

        Parameters
        ----------
        prefix : str
            Your organization's DOI prefix. Ex. 10.99999.
        collection: str
            The collection abbreviation.
        seq_num : int
            Number between 0 and 999.
        """
        date = datetime.date.today().strftime("%Y%m%d")
        self.doi = f"{prefix}/{collection}-{date}-{str(seq_num).zfill(3)}"

    def to_xml(self):
        """Generate XML from attributes.

        Generates XML represented as an lxml.etree base on available
        attributes.

        Returns
        -------
        lxml.etree
        """

        if self.kind == "report":
            root = self._xml_report()
        elif self.kind == "proceedings":
            root = self._xml_conference_paper()

        return root
