import csv
import datetime
from urllib.parse import urljoin

from lxml import etree
from nameparser import HumanName
import requests

from doiowa import md, PREFIX

def get_page(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0"}
    if not (url.endswith("full") or url.endswith("full/")):
        # Have to make sure the base URL ends with a slash or urljoin
        # will absolutely mangle the URL due to an amazingly terrible
        # design decision, but will deduplicate "//" if the original
        # base URL already ended with a slash.
        url = urljoin(f"{url}/", "full")
    print(url)
    return requests.get(url, headers=headers).text


def scrape_page(url):
    print(url)
    html = get_page(url)
    print(html)
    m = {}
    tree = etree.HTML(html)
    abstract_xpath = "string(//td[text() = 'dc.description.abstract']/following-sibling::td[1]/text())"
    author_xpath = "string(//td[text() = 'dc.contributor.author']/following-sibling::td[1]/text())"
    date_xpath = "string(//td[text() = 'dc.date.issued']/following-sibling::td[1]/text())"
    degree_xpath = "string(//td[text() = 'thesis.degree.discipline']/following-sibling::td[1]/text())"
    department_xpath = "string(//td[text() = 'dc.contributor.department']/following-sibling::td[1]/text())"
    title_xpath = "string(//td[text() = 'dc.title']/following-sibling::td[1]/text())"
    uri_xpath = "string(//td[text() = 'dc.identifier.uri']/following-sibling::td[1]/text())"

    m["dc.description.abstract"] = tree.xpath(abstract_xpath)
    m["dc.contributor.author"] = tree.xpath(author_xpath)
    m["dc.date.issued"] = tree.xpath(date_xpath)
    m["thesis.degree.name[en_US]"] = tree.xpath(degree_xpath)
    m["dc.contributor.department[en_US]"] = tree.xpath(degree_xpath)
    m["dc.title"] = tree.xpath(title_xpath)
    m["dc.identifier.uri"] = tree.xpath(uri_xpath)

    print(m)

    return m


def load_csv(csv_path):
    with open(csv_path, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return [row for row in reader]


def get_author(m):
    name = HumanName(m["dc.contributor.author"])
    return md.name_to_dict(name)


def get_acceptance_date(md):
    parts = md["dc.date.issued"].split("-")
    print(parts)
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


def generate_xml(sources, collection, timestamp, csv_or_url="csv", genre="dissertation"):
    xml = md.CrossrefXML()
    depositor = md.Depositor(
        doi_batch_id = timestamp,
        timestamp = timestamp,
    )
    xml.insert_depositor(depositor.to_xml())
    for source in sources:
        if csv_or_url == "csv":
            mds = load_csv(source)
        else:
            mds = [scrape_page(source)]
            print(mds[0])
        for i, m in enumerate(mds):
            date = get_acceptance_date(m)
            item = md.ItemMetadata(
                date = date,
                doi = f"{PREFIX}/{collection}-{datetime.datetime.now().strftime('%Y%m%d')}-{i}",
                resource = m["dc.identifier.uri"],
                title = m["dc.title"],
            )
            print(f"Genre is {genre}")
            if genre == "dissertation":
                item.abstract = m["dc.description.abstract"]
                item.degree = m["thesis.degree.name[en_US]"]
                item.institution_department = m["dc.contributor.department[en_US]"]
                item.institution_name = "Iowa State University"
                item.institution_place = "Ames (Iowa)"
                item.kind = "dissertation"
                item.media_type = "print" if int(date["year"]) < 2006 else "online"
                item.person_name = get_author(m)
            elif genre == "report":
                item.contributors = [get_author(m)]
                item.kind = "report"
                item.media_type = "online"

            print(f"Kind: {item.kind}, {type(item.kind)}")

            xml.insert_item_metadata(item.to_xml())

    return xml
