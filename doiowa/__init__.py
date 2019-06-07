from datetime.date import today


def generate_doi(prefix, collection, seq_num):
    date = today().strftime("%Y%m%d")

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
    doi = f"{prefix}/{collection}-{date}-{str(seq_num).zfill(3)}"

    return doi


def add_dois_to_md_objects(prefix, collection, md_objects):
    for n, md in enumerate(md_objects):
        md.doi = generate_doi(prefix, collection, n)


class Metadata:
    def __init__(
        self,
        contributors=[],
        title="",
        edition_number=1,
        publication_date="",
        publisher_name="",
        publisher_place="",
        institution_name="",
        institution_place="",
        institution_department="",
        doi="",
        resource="",
    ):
        self.contributors = contributors
        self.title = title
        self.edition_number = edition_number
        self.publication_date = publication_date
        self.publisher_name = publisher_name
        self.publisher_place = publisher_place
        self.institution_name = institution_name
        self.institution_place = institution_place
        self.institution_department = institution_department
        self.doi = doi
        self.resource = resource

    def to_xml(self):
        pass
