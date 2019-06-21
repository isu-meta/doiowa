import datetime

from lxml import etree
from lxml.builder import E


def add_dois_to_md_objects(prefix, collection, md_objects):
    for n, md in enumerate(md_objects):
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
        self.root.insert(0, depositor_xml)

    def insert_item_metadata(self, md):
        self.root[-1].append(md)

    def to_xml(self):
        return self.root


class Depositor:
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
    def __init__(
        self,
        contributors=[],
        title="",
        edition_number=0,
        month=None,
        day=None,
        year=None,
        publisher_name="",
        publisher_place="",
        institution_name="",
        institution_place="",
        institution_acronym="",
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
        date = datetime.date.today().strftime("%Y%m%d")

        # As of 2019, our practice is to build DOIs using the following
        # format: our DOI prefix, followed by a slash, followed by a
        # collection acronym (For BePress this is the OAI-PMH-searchable
        # acronym used in BePress. May differ for other platforms.),
        # followed by a hyphen, followed by the date in condensed
        # ISO 8601 format (YYYYMMDD), followed by a hyphen, followed
        # by the sequence number, which is three digits wide and
        # includes leading zeros for numbers with fewer than three
        # digits.
        #
        # An example from the Animal Industry Report collection:
        # 10.31274/ans_air-190411-001
        #
        # This pattern is not used for digital press materials,
        # which will have DOIs generated from within Janeway.
        self.doi = f"{prefix}/{collection}-{date}-{str(seq_num).zfill(3)}"

    def to_xml(self):
        if self.type == "report":
            root = etree.fromstring(
                '<report-paper><report-paper_metadata language="en"></report-paper_metadata></report-paper>'
            )

        contributors = self._xml_contributors()
        if contributors:
            root[-1][-1].append(contributors)

        root[-1][-1].append(self._xml_title())
        root[-1][-1].append(self._xml_edition_number())
        root[-1][-1].append(self._xml_publication_date())
        root[-1][-1].append(self._xml_publisher())
        root[-1][-1].append(self._xml_institution())
        root[-1][-1].append(self._xml_doi_data())

        return root

    def _xml_contributors(self):
        contributors = E.contributors()

        if self.contributors:
            for c in self.contributors:
                try:
                    c_xml = E.person_name(
                        E.given_name(c["given_name"]),
                        E.surname(c["surname"]),
                        sequence="first",
                        contributor_role="author",
                    )
                except KeyError:
                    c_xml = E.organization(
                        c["organization"], sequence="first", contributor_role="author"
                    )

                contributors.append(c_xml)

                return contributors
        else:
            return None

    def _xml_title(self):
        title = E.titles(E.title(self.title))

        return title

    def _xml_edition_number(self):
        edition_number = E.edition_number(str(self.edition_number))
        return edition_number

    def _xml_publication_date(self):
        publication_date = E.publication_date(
            E.month(self.month),
            E.day(self.day),
            E.year(self.year),
            media_type=self.media_type,
        )

        return publication_date

    def _xml_publisher(self):
        publisher = E.publisher(
            E.publisher_name(self.publisher_name),
            E.publisher_place(self.publisher_place),
        )

        return publisher

    def _xml_institution(self):
        institution = E.institution(E.institution_name(self.institution_name))

        if self.institution_acronym:
            institution.append(E.institution_acronym(self.institution_acronym))

        institution.append(E.institution_place(self.institution_place))

        if self.institution_department:
            institution.append(E.institution_department(self.institution_department))

        return institution

    def _xml_doi_data(self):
        doi_data = E.doi_data(E.doi(self.doi), E.resource(self.resource))

        return doi_data
