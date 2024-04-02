import datetime
import pathlib
import re

from lxml import etree
from nameparser import HumanName
import requests

from doiowa import md, PREFIX


def get_title(tree):
    title_xpath = "string(//h1/text())"
    return tree.xpath(title_xpath)


def get_publication_date(tree):
    date_xpath = "string(//div/p[starts-with(text(), 'Published')]/text())"
    date_pattern = re.compile(r"(\d+)/(\d+)/(\d+)")
    date_string = tree.xpath(date_xpath)
    month, day, year = date_pattern.search(date_string).groups()

    return {"year": year, "month": month, "day": day}


def parse_names(names):
    return [md.name_to_dict(HumanName(name)) for name in names if name.strip() != ""]


def get_authors(tree):
    authors_xpath = "//h3[text() = 'Authors']/following-sibling::p[1]/strong/text()"
    authors = tree.xpath(authors_xpath)
    parsed_names = parse_names(authors)

    return parsed_names


def get_reviewers(tree):
    reviewers_h3_xpath = "//h3[text() = 'Reviewers']/following-sibling::p[1]/strong/text()"
    reviewers_p_xpath = "//p[strong/text() = 'Reviewers']/following-sibling::p[1]/strong/text()"
    reviewers = tree.xpath(reviewers_h3_xpath)
    if len(reviewers) == 0:
        reviewers = tree.xpath(reviewers_p_xpath)

    return parse_names(reviewers)


def get_metadata(tree, uri):
    md = {}
    md["title"] = get_title(tree)
    md["date"] = get_publication_date(tree)
    md["authors"] = get_authors(tree)
    md["reviewers"] = get_reviewers(tree)
    md["resource"] = uri

    return md


def generate_xml(sources, timestamp):
    mds = []
    for source in sources:
        tree = etree.HTML(requests.get(source).text)
        mds.append(get_metadata(tree, source))

    xml = md.CrossrefXML()
    depositor = md.Depositor(
        doi_batch_id = timestamp,
        timestamp = timestamp,
    )
    xml.insert_depositor(depositor.to_xml())


    for i, m in enumerate(mds):
        item = md.ItemMetadata(
            authors = m["authors"],
            date = m["date"],
            doi = f"{PREFIX}/cpn-{datetime.datetime.now().strftime('%Y%m%d')}-{i}",
            kind = "report",
            media_type = "online",
            publisher_name = "Crop Protection Network",
            publisher_place = "United States",
            resource = m["resource"],
            reviewers = m["reviewers"],
            title = m["title"]

        )
        xml.insert_item_metadata(item.to_xml())

    return xml
