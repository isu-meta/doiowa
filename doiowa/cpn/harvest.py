"""Get metadata from Crop Protection Network PDFs.
https://cropprotectionnetwork.org/resources/publications"""

from lxml import html
import requests

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
