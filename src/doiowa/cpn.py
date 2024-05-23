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
    authors_xpath = "//h3[text() = 'Authors' or strong/text() = 'Authors']/following-sibling::p[1]/strong/text()"
    authors = tree.xpath(authors_xpath)
    parsed_names = parse_names(authors)

    return parsed_names


def get_reviewers(tree):
    # Sometimes the reviewers heading is an <h3>, sometimes it's a <p>, so catch both
    reviewers_xpath = "//*[text() = 'Reviewers']/following-sibling::p[1]/strong/text()"
    # Sometimes reviewer names aren't wrapped in <strong> tags and are in invdividual
    # <p> tags instead of all within the same paragraph
    reviewers_no_strong_xpath = "//*[text() = 'Reviewers']/following-sibling::p/text()"
    # Sometimes some reviewers are listed under an "Additional Reviewers heading"
    additional_reviewers = "//*[text() = 'Additional Reviewers']/following-sibling::p[1]/strong/text()"
    reviewers = tree.xpath(reviewers_xpath)

    # If there are no reviewers found by the reviewers_xpath, it's possible
    # their names aren't wrapped in <strong> tags, so we can try searching
    # without that tag, but it will require more parsing.
    if len(reviewers) == 0:
        # without the <strong> tag wrapping the reviewer's name, we'd end up
        # feeding parse_names() an array of strings like "First M. Name,
        # University of Whatever." This is no good, so split the name strings
        # on the comma and take only the personal name part
        reviewers = [
            r.split(",")[0]
            for r
            in tree.xpath(reviewers_no_strong_xpath)
            # Try to filter out any non-name paragraphs by hoping
            # they have 0 or 2 or more commas to distinguish them
            # from the Name, Employer form
            if len(r.split(",")) == 2
        ]

    reviewers.extend(tree.xpath(additional_reviewers))

    return parse_names(reviewers)


def get_metadata(tree, uri):
    # test function against:
    # * https://cropprotectionnetwork.org/publications/adjuvants-with-herbicides-when-and-why-they-are-needed
    # * https://cropprotectionnetwork.org/publications/an-overview-of-phytophthora-root-and-stem-rot
    # * need to refind the page that had "Authors" in a <p> tag
    # to capture the variations in how authors and reviewers are listed
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
