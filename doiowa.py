"""Command-line script for using diowa.

This script aims to be the primary way of interacting with the doiowa
library from the command line.

Examples
--------
To harvest metadata from a source and generate an XML file to submit
to the Crossref API, use the ``harvest`` command followed by the target
collection::

    python doiowa.py harvest cpn

Current supported collection names are ``cpn``. **Do not run** ``harvest``
against a collection that has already been harvested as this script does
not currently check to see if a DOI has been previously generated for an
object. Such functionality will be implemented in the future.

To register one or more DOIs, use the ``register`` command followed by the
XML file containing the DOIs and associated metadata, your Crossref username
and password::

    python doiowa.py register new_dois.xml username password

To check on the status of a submission, use the ``check`` command followed
by either the XML file submitted or the DOI batch ID of the submission and
your Crossref username and password::

    python doiowa.py check new_dois.xml username password

or::

    python doiowa.py check new-dois-0001 username password
"""

__version__ = "2019-06-24"

import argparse
import datetime

from doiowa.md import Depositor, get_doi_batch_id_from_xml
from doiowa import cpn, crossref, PREFIX

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="Accepted arguments: harvest, register, check")
    parser.add_argument(
        "target",
        help="""Accepted arguments after 'harvest': cpn.
    Accepted arguments after 'register': An XML file path.
    Accepted arguments after 'check': An XML file name or a DOI batch ID.""",
    )
    parser.add_argument(
        "credentials", nargs="*", help="Crossref username and password."
    )
    parser.add_argument(
        "--out",
        help="""Specify the name of the XML file to create with `harvest`.
    Otherwise, the timestamp will be used for the name.""",
    )
    parser.add_argument(
        "--sequence-number",
        help="""The last portion of our DOIs consists of a zero-padded number.
    Normally this number starts at zero, like so: 000. To start with a different
    number, use this flag followed by the start number you wish to use when
    running a 'register' command.""",
    )

    args = parser.parse_args()

    errors = []

    if args.command == "harvest":

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        depositor = Depositor(
            timestamp,
            timestamp,
            "Iowa State University. Library. Metadata Services Department.",
            "metadata@iastate.edu",
            "Iowa State University. Library",
        )

        if args.target == "cpn":
            crossref_xml = cpn.harvest.harvest(depositor)

            if args.out:
                out_file = args.out
            else:
                out_file = f"{timestamp}.xml"

            with open(out_file, "w", encoding="utf-8") as fh:
                fh.write(crossref_xml)

    if args.command == "register" or args.command == "check":
        if len(args.credentials) != 2:
            parser.error(
                "Please provide a username followed by a password.\nExample: `doiowa.py register my_file.xml username password`"
            )
        else:
            username, password = args.credentials

            if args.command == "register":
                doi_batch_id = get_doi_batch_id_from_xml(args.target)
                with open(args.target, "r", encoding="utf-8") as fh:
                    xml = fh.read()

                r = crossref.submit_xml(doi_batch_id, xml, PREFIX, username, password)
                crossref.print_response(r)

            elif args.command == "check":
                if args.target.endswith(".xml"):
                    r = crossref.check_status_by_filename(
                        args.target, PREFIX, username, password
                    )
                    crossref.print_response(r)

                else:
                    r = crossref.check_status_by_doi_batch_id(
                        args.target, PREFIX, username, password
                    )
                    crossref.print_response(r)

    for error in errors:
        with open("error.txt", "a", encoding="utf-8") as fh:
            fh.write(f"{datetime.date.today().isoformat(): {error}\n}")
