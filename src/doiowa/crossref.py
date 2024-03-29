"""Functions for working with the Crossref API."""
from crossref.restful import Depositor, Etiquette, Works

from doiowa import __name__, __version__, __author__, __email__


def print_response(r):
    """Print a response's status code and text.

    Parameters
    ----------
    r : requests.Response

    Returns
    -------
    None
    """
    print(f"Response status: {r.status_code}")
    print(r.text)


def submit_xml(doi_batch_id, xml, prefix, username, password, use_test_server=False):
    """Register DOIs with Crossref.
    
    Submit XML to the Crossref API to register DOIs.

    Parameters
    ----------
    doi_batch_id : str or int
        Batch ID for the registration submission.
    xml : str
        XML file to submit to Crossref API.
    prefix : str
        Your organization's DOI prefix.
    username : str
        Crossref username.
    password : str
        Crossref password.
    use_test_server : bool
        If True submit to the test server instead of actually attempting to
        register DOIs. Defaults to False.

    Returns
    -------
    requests.Response
    """
    etiquette = Etiquette(__name__, __version__, __author__, __email__)
    depositor = Depositor(prefix, username, password, etiquette, use_test_server)

    response = depositor.register_doi(doi_batch_id, xml)

    return response


def check_status_by_filename(
    file_name, prefix, username, password, use_test_server=False, data_type="result"
):
    """Get the status of a submission by file name.

    Parameters
    ----------
    file_name : str
        Name of the XML file submitted.
    prefix : str
        Your organization's DOI prefix.
    username : str
        Crossref username.
    password : str
        Crossref password.
    use_test_server : bool
        If True submit to the test server instead of actually attempting to
        register DOIs. Defaults to False.
    data_type : str
        The data type you want in response. "result" will return the status
        of your submission. "content" will return the XML submitted. Defaults
        to "result".

    Returns
    -------
    requests.Response
    """
    etiquette = Etiquette(__name__, __version__, __author__, __email__)
    depositor = Depositor(prefix, username, password, etiquette, use_test_server)

    response = depositor.request_doi_status_by_filename(file_name, data_type)

    return response


def check_status_by_doi_batch_id(
    doi_batch_id, prefix, username, password, use_test_server=False, data_type="result"
):
    """Get the status of a submission by DOI batch ID.

    Parameters
    ----------
    doi_batch_id : str or int
        Batch ID for the registration submission you wish to check on.
    prefix : str
        Your organization's DOI prefix.
    username : str
        Crossref username.
    password : str
        Crossref password.
    use_test_server : bool
        If True submit to the test server instead of actually attempting to
        register DOIs. Defaults to False.
    data_type : str
        The data type you want in response. "result" will return the status
        of your submission. "content" will return the XML submitted. Defaults
        to "result".

    Returns
    -------
    requests.Response
    """
    etiquette = Etiquette(__name__, __version__, __author__, __email__)
    depositor = Depositor(prefix, username, password, etiquette, use_test_server)

    response = depositor.request_doi_status_by_batch_id(doi_batch_id, data_type)

    return response


def get_metadata_by_doi(doi):
    works = Works()
    return works.doi(doi)
