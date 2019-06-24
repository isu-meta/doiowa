"""Objects and functions for working with metadata in doiowa."""
import datetime

from lxml import etree
from lxml.builder import E


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


def get_doi_batch_id_from_xml(xml_file, schema_version="4.4.1"):
    """Get the DOI batch ID from an XML file

    Extract the DOI batch ID from the provided file. The schema_version
    argument is optional and only needed for working with historical XML
    files. Prior to 2019-06-21, we used version 4.3.7 of the Crossref
    metadata deposit schema and may have used others before that. We have
    switched to the current version, 4.4.1.

    Parameters
    ----------
    xml_file : str
        Path to an XML file.
    schema_version : str
        Version number for the schema to use. Defaults to '4.4.1'.

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
    """Foundation of all diowa Metadata classes.

    This class collects all the metadata needed to create a DOI for an
    object and produces the XML for the digital object.

    Parameters
    ----------
    contributors : list of dict
        The digital object's authors. Dict take the form of 
        {"given_name": "name", "surname": "name"} or
        {"organization": "name"}.
    title :str
        Title of the digital object.
    edition_number : int
        Edition number of the object. Defaults to 0.
    month : str
        Zero-padded numerical representation of the month of publication.
        Defaults to "01".
    day : str
        Zero-padded numerical representation of the day of publication.
        Defaults to "01".
    year : str
        Zero-padded numerical representation of the year of publication.
        Defaults to "0001".
    publisher_name : str
        Name of the publisher.
    publisher_place : str
        Location of the publisher.
    institution_name : str
        Name of the organization that hosted or sponsored the digital object.
    institution_acronym : str
        Acronym used to refer to the organization that hosted or sponsored
        the digital object.
    institution_place : str
        The location of the organization that hosted or sponsored the digital
        object.
    institution_department :str
        The department that the creators of the digital object worked in. 
    doi : str
        Digital Object Identifier.
    resource: str
        The URL for the digital object.
    media_type : str
        Publication medium. Valid values are: 'print' or 'electronic'.
    type_ : str
        Digital object's publication type. Valid values are : 'journal',
        'journal article', 'book', 'book chapter', 'reference work',
        'conference proceedings', 'report', 'standard', 'dataset',
        'dissertation', 'preprint', 'peer review', 'component', and 'grant'.
    """

    def __init__(
        self,
        contributors=[],
        title="",
        edition_number=0,
        month="01",
        day="01",
        year="0001",
        publisher_name="",
        publisher_place="",
        institution_name="",
        institution_acronym="",
        institution_place="",
        institution_department="",
        doi="",
        resource="",
        media_type="",
        type_="",
    ):
        self.contributors = contributors
        self.title = title
        self.edition_number = edition_number
        self.month = month
        self.day = day
        self.year = year
        self.publisher_name = publisher_name
        self.publisher_place = publisher_place
        self.institution_name = institution_name
        self.institution_place = institution_place
        self.institution_acronym = institution_acronym
        self.institution_department = institution_department
        self.doi = doi
        self.resource = resource
        self.media_type = media_type
        self.type = type_
        self.timestamp = datetime.datetime.now().isoformat()

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
        if self.type == "report":
            root = etree.fromstring(
                '<report-paper><report-paper_metadata language="en"></report-paper_metadata></report-paper>'
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

    def _xml_title(self):
        """Returns title XML as lxml.etree.

        Returns
        -------
        lxml.etree
        """
        title = E.titles(E.title(self.title))

        return title

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
            E.month(self.month),
            E.day(self.day),
            E.year(self.year),
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

    def _xml_doi_data(self):
        """Returns DOI data XML as lxml.etree.

        Returns
        -------
        lxml.etree
        """
        doi_data = E.doi_data(E.doi(self.doi), E.resource(self.resource))

        return doi_data
