"""Metadata object for working with Crop Protection Network metadata."""

import datetime
from io import BytesIO
from os.path import basename
import re

from PyPDF2 import PdfFileReader
import requests

from doiowa.md import BaseMetadata


class Metadata(BaseMetadata):
    """Metadata class for Crop Protection Network publications.

    This class collects all the metadata needed to create a DOI for 
    CPN publications and produces the XML for them.

    Parameters
    ----------
    contributors : list of dict
        The digital object's authors. Dict take the form of 
        {"given_name": "name", "surname": "name"} or
        {"organization": "name"}.
    title :str
        Title of the digital object.
    edition_number : int
        Edition number of the object. Defaults to 0.
    month : str
        Zero-padded numerical representation of the month of publication.
        Defaults to "01".
    day : str
        Zero-padded numerical representation of the day of publication.
        Defaults to "01".
    year : str
        Zero-padded numerical representation of the year of publication.
        Defaults to "0001".
    publisher_name : str
        Name of the publisher.
    publisher_place : str
        Location of the publisher.
    institution_name : str
        Name of the organization that hosted or sponsored the digital object.
    institution_acronym : str
        Acronym used to refer to the organization that hosted or sponsored
        the digital object.
    institution_place : str
        The location of the organization that hosted or sponsored the digital
        object.
    institution_department :str
        The department that the creators of the digital object worked in. 
    doi : str
        Digital Object Identifier.
    resource: str
        The URL for the digital object.
    media_type : str
        Publication medium. Valid values are: 'print' or 'electronic'.
    type_ : str
        Digital object's publication type. Valid values are : 'journal',
        'journal article', 'book', 'book chapter', 'reference work',
        'conference proceedings', 'report', 'standard', 'dataset',
        'dissertation', 'preprint', 'peer review', 'component', and 'grant'.
    """

    def from_pdf_url(self, pdf_url, write_out=False):
        """Get metadata from an online PDF.

        Sets self.resouce to pdf_url. Calls self._download_pdf to
        download the PDF and passes it to self.from_pdf to extract the
        PDF's metadata.

        Parameters
        ----------
        pdf_url : str
            The HTTP or HTTPS URL for the PDF to be downloaded.
        write_out : bool
            If True the downloaded PDF file will be saved to disk
            in the current working directory. Defaults to False.
        
        Returns
        -------
        None
        """
        self.resource = pdf_url
        self.from_pdf(self._download_pdf(pdf_url, write_out))

    def from_pdf(self, pdf_file):
        """Get metadata from a PDF file.

        Extracts XMP and Document Information metadata streams from the PDF,
        saving them into self.xmp and self.doc_info, respectively. This
        method then uses that metadata to populate the Metadata object's
        attributes.

        Parameters
        ----------
        pdf_file : file-like object
            The PDF document.
        
        Returns
        -------
        None
        """
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
        self.media_type = "electronic"
        self.type = "report"

    def _download_pdf(self, pdf, write_out=False):
        """Downloads a PDF file from a URL.

        Downloads a PDF from the web and returns it
        as a file-like object.

        Parameters
        ----------
        pdf : str
            The URL to fetch the PDF from.
        write_out : bool
            If True the PDF is saved in the current working directory.
            Defaults to False.

        Returns
        -------
        file-like object
            The PDF wrapped in io.BytesIO.
        """
        file_name = f"{pdf.split('/')[-1]}.pdf"
        r = requests.get(pdf)
        pdf_content = r.content

        if write_out:
            with open(file_name, "wb") as fh:
                fh.write(pdf_content)

        return BytesIO(pdf_content)

    def _reformat_tz(self, datestring):
        """Reformats datestring timezone declartion.

        Reformats the datestring's timezone declaration from NN'NN' to NNNN
        so that the datestring can be parsed in self._datestring_to_datetime.

        Parameters
        ----------
        datestring : str
            A datestring with apostrophes in the timezone offset.

        Returns
        -------
        str
        """
        return re.sub(r"'", "", datestring)

    def _datestring_to_datetime(self, datestring):
        """Converts a datestring to a dateime object.

        Takes a datestring formated like D:19990312043055-05'00' and returns
        a datetime object.

        Parameters
        ----------
        datestring : str

        Returns
        -------
        datetime
        """
        datestring_format = "D:%Y%m%d%I%M%S%z"

        datestring = self._reformat_tz(datestring)
        date = datetime.datetime.strptime(datestring, datestring_format)

        return date

    def _get_contributors(self):
        """Gets contributor list from PDF metadata.

        Checks the self.xmp.dc_creator field for a list of creators. If a list
        is present, it cleans and filters the list using
        self._contributor_to_dict. If self.xmp.dc_creator is empty, it tries
        to build the list from self.doc_info["/Author"]. If no list of
        creators is found, an empty list is returned.

        Returns
        -------
        list of dict or empty list
        """
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
        """Converts contributor string to a dict.

        Cleans and filters a contributor string to produce a dictionary
        with the format {"organization": "org name"} or 
        {"given_name": "name", "surname": "name"}. It filters out
        institution names that trail author names either after a comma or
        within parantheses, and filters out leading strings like 
        "Compiled by" or "Written by" that start some author listings.

        Sometimes author's organizations are listed as seperate list items
        from the author. In cases where a sponsoring institution is found
        on its own, it is filtered out.

        If a name can be made into an author dictionary it is returned in
        the dictionary format described above. Otherwise None is returned.

        Parameters
        ----------
        name : str

        Returns
        -------
        dict or None
        """
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
        """Gets the item's title.

        Returns the title found in either self.xmp.dc_title["x-defualt"] or
        self.doc_info["/Title"]. If no title is found, returns an empty
        string.

        Returns
        -------
        str
        """
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
        """Gets the publication date.

        Returns the date found in self.xmp.xmp_createDate or in 
        self.doc_info["/CreationDate"]. If no date is found returns the
        dummy datetime of 0001-01-01.

        Returns
        -------
        datetime
        """
        date = datetime.datetime(1, 1, 1)

        if self.xmp.xmp_createDate:
            date = self.xmp.xmp_createDate
        else:
            try:
                date = self._datestring_to_datetime(self.doc_info["/CreationDate"])
            except KeyError:
                pass

        return date
