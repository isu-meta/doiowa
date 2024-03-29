import csv
import datetime
import pathlib

from nameparser import HumanName

from doiowa import md, PREFIX

def load_csv(csv_path):
    with open(csv_path, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return [row for row in reader]

def get_author(m):
    name = HumanName(m["dc.contributor.author"])
    return md.name_to_dict(name)

def get_acceptance_date(md):
    parts = md["dc.date.issued"].split("-")
    match len(parts):
        case 1:
            date = {"year": parts[0], "month": "01", "day": "01"}
        case 2:
            date = {"year": parts[0], "month": parts[1], "day": "01"}
        case 3:
            date = {"year": parts[0], "month": parts[1], "day": "01"}
        case _:
            date = {"year": "1400", "month": "01", "day": "01"}
            print(f"Could not parse {md['dc.date.issued']}")
    return date


def generate_xml(sources, collection, timestamp):
    xml = md.CrossrefXML()
    depositor = md.Depositor(
        doi_batch_id = timestamp,
        timestamp = timestamp,
    )
    xml.insert_depositor(depositor.to_xml())
    for source in sources:
        mds = load_csv(source)
        for i, m in enumerate(mds):
            date = get_acceptance_date(m)
            item = md.ItemMetadata(
                abstract = m["dc.description.abstract"],
                date = date,
                degree = m["thesis.degree.name[en_US]"],
                doi = f"{PREFIX}/{collection}-{datetime.datetime.now().strftime('%Y%m%d')}-{i}",
                institution_department = m["dc.contributor.department[en_US]"],
                institution_name = "Iowa State University",
                institution_place = "Ames (Iowa)",
                kind = "dissertation",
                media_type = "print" if int(date["year"]) < 2006 else "online",
                person_name = get_author(m),
                resource = m["dc.identifier.uri"],
                title = m["dc.title"],
            )
            xml.insert_item_metadata(item.to_xml())

    return xml
