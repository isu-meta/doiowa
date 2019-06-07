"""Get metadata from Crop Protection Network PDFs.
https://cropprotectionnetwork.org/resources/publications"""

from lxml import html
import requests

from doiowa import Metadata


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
            "".join([base_url, rel_url]) for rel_url in p_list.xpath(pub_urls_xpath)
        ]
        pubs.extend(pub_urls)

    return pubs


def already_has_doi(pub_url):
    pass


def download_pdf(url):
    pass


def get_pdf_metadata(pdf):
    # return dict like this:
    # {"title": "...", "contributors": [...], "date": "...."}
    pass


def make_list_of_md_objects(pub_urls):
    publisher_name = "Crop Protection Netework"
    publisher_place = "United States"

    institution_name = "Crop Protection Network"
    institution_place = "United States"
    institution_department = ""

    md_list = []

    for url in pub_urls:
        if not already_has_doi(url):
            pdf = download_pdf(url)
            pdf_md = get_pdf_metadata(pdf)

            md_obj = Metadata(
                pdf_md["contributors"],
                pdf_md["title"],
                1,
                pdf_md["date"],
                publisher_name,
                publisher_place,
                institution_name,
                institution_place,
                institution_department,
                "",
                url,
            )

            md_list.append(md_obj)

    return md_list
