import datetime
from io import BytesIO
from os.path import basename
import re

from PyPDF2 import PdfFileReader
import requests

from doiowa.md import BaseMetadata


class Metadata(BaseMetadata):
    def from_pdf_url(self, pdf_url, write_out=False):
        self.resource = pdf_url
        self.from_pdf(self._download_pdf(pdf_url, write_out))

    def from_pdf(self, pdf_file):
        pdf = PdfFileReader(pdf_file)

        self.xmp = pdf.getXmpMetadata()
        self.doc_info = pdf.getDocumentInfo()

        self.contributors = self._get_contributors()
        self.title = self._get_title()
        self.edition_number = 0
        self.publication_date = self._get_date()
        self.year = str(self.publication_date.year)
        self.month = str(self.publication_date.month).zfill(2)
        self.day = str(self.publication_date.day).zfill(2)
        self.publisher_name = "Crop Protection Netework"
        self.publisher_place = "United States of America"
        self.institution_name = "Crop Protection Network"
        self.institution_acronym = "CPN"
        self.institution_place = "United States of America"
        self.institution_department = ""
        self.doi = ""
        self.media_type = "online"
        self.type = "report"

    def _reformat_tz(self, datestring):
        return re.sub(r"'", "", datestring)

    def _datestring_to_datetime(self, datestring):
        datestring_format = "D:%Y%m%d%I%M%S%z"

        datestring = self._reformat_tz(datestring)
        date = datetime.datetime.strptime(datestring, datestring_format)

        return date

    def _get_contributors(self):
        contributors = []

        if self.xmp.dc_creator:
            contributors = [
                self._contributor_to_dict(c)
                for c in self.xmp.dc_creator
                if self._contributor_to_dict(c) is not None
            ]
        else:
            try:
                contributors = [
                    self._contributor_to_dict(c)
                    for c in self.doc_info["/Author"]
                    if self._contributor_to_dict(c) is not None
                ]
            except KeyError:
                pass

        return contributors

    def _contributor_to_dict(self, name):
        by_prefix_pattern = re.compile(r"^.+ by")
        parentheses_pattern = re.compile(r"\(.*\)")
        filter_words = [
            "University",
            "Agriculture",
            "USDA",
            "OMAFRA",
            "NCERA",
            "Extension",
            "Research",
        ]

        name = name.strip()

        if name:
            name = re.sub(by_prefix_pattern, "", name)
            name = re.sub(parentheses_pattern, "", name)
            if "," in name:
                name = name.split(",")[0]
        else:
            return None

        if name == "Crop Protection Network":
            return {"organization": name}

        for word in filter_words:
            if word in name:
                return None

        name_parts = name.rpartition(" ")
        return {"given_name": name_parts[0], "surname": name_parts[2]}

    def _get_title(self):
        title = ""

        if self.xmp.dc_title:
            if self.xmp.dc_title["x-default"]:
                title = self.xmp.dc_title["x-default"]
        else:
            try:
                title = self.doc_info["/Title"]
            except KeyError:
                pass

        return title

    def _get_date(self):
        date = datetime.datetime(1, 1, 1)

        if self.xmp.xmp_createDate:
            date = self.xmp.xmp_createDate
        else:
            try:
                date = self._datestring_to_datetime(self.doc_info["/CreationDate"])
            except KeyError:
                pass

        return date

    def _download_pdf(self, pdf, write_out=False):
        file_name = f"{pdf.split('/')[-1]}.pdf"
        r = requests.get(pdf)
        pdf_content = r.content

        if write_out:
            with open(file_name, "wb") as fh:
                fh.write(pdf_content)

        return BytesIO(pdf_content)
