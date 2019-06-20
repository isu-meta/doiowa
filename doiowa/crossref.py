from crossref.restful import Depositor, Etiquette

from doiowa import __name__, __version__, __author__, __email__


def submit_xml(doi_batch_id, xml, prefix, username, password, use_test_server=False):
    etiquette = Etiquette(__name__, __version__, __author__, __email__)
    depositor = Depositor(prefix, username, password, etiquette, use_test_server)

    response = depositor.register_doi(doi_batch_id, xml)

    return response


def check_status_by_filename(
    file_name, prefix, username, password, use_test_server=False, data_type="result"
):
    etiquette = Etiquette(__name__, __version__, __author__, __email__)
    depositor = Depositor(prefix, username, password, etiquette, use_test_server)

    response = depositor.request_doi_status_by_filename(file_name, data_type)

    return response


def check_status_by_doi_batch_id(
    doi_batch_id, prefix, username, password, use_test_server=False, data_type="result"
):
    etiquette = Etiquette(__name__, __version__, __author__, __email__)
    depositor = Depositor(prefix, username, password, etiquette, use_test_server)

    response = depositor.request_doi_status_by_batch_id(doi_batch_id, data_type)

    return response
