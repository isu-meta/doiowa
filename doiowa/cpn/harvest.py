"""Get metadata from Crop Protection Network PDFs.
https://cropprotectionnetwork.org/resources/publications"""

from lxml import etree, html
from PyPDF2.utils import PdfReadError
import requests

from doiowa import PREFIX
from doiowa.md import add_dois_to_md_objects, CrossrefXML
from doiowa.cpn.md import Metadata

def fetch_list_of_publication_urls():
    publications_url = "https://cropprotectionnetwork.org/resources/publications"
    base_url = "https://cropprotectionnetwork.org"

    pub_lists_xpath = "//div[@class='px-3']/ul"
    pub_urls_xpath = "./li/small/a/@href"

    r = requests.get(publications_url)

    pubs_page = html.fromstring(r.text)
    pubs_lists = pubs_page.xpath(pub_lists_xpath)
    pubs = []

    for p_list in pubs_lists:
        pub_urls = [
            "".join([base_url, rel_url])
            for rel_url in p_list.xpath(pub_urls_xpath)
            if "ceu.cropprotectionnetwork.org/exams" not in rel_url
        ]
        pubs.extend(pub_urls)

    return pubs


def harvest(depositor):
    md_list = []
    pub_urls = fetch_list_of_publication_urls()
    for url in pub_urls:
        try:
            md = Metadata()
            md.from_pdf_url(url)
            md_list.append(md)
        except PdfReadError:
            error_message = f"PDF {url} was unreadable"
            print(error_message)

    add_dois_to_md_objects(PREFIX, "cpn", md_list)

    base_xml = CrossrefXML()
    base_xml.insert_depositor(depositor.to_xml())
    for md in md_list:
        base_xml.insert_item_metadata(md.to_xml())

    xml_content = etree.tostring(
        base_xml.to_xml(),
        xml_declaration=True,
        encoding="UTF-8",
        pretty_print=True,
    ).decode("utf-8")

    return xml_content
