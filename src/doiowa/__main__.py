import argparse
import datetime

from lxml import etree

from doiowa.md import Depositor, get_doi_batch_id_from_xml
from doiowa import cpn, crossref, dr, PREFIX


def name_output_file(name="", timestamp=f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xml"):
    if name:
        out_xml_file = name
    else:
        out_xml_file = f"{timestamp}.xml"

    return out_xml_file


def main():
    """
    To generate an XML file for submission to Crossref using metadata from
    an external source, use the ``generate`` command followed by the target
    collection and the ``--sources`` flag followed by the source file(s) or
    URL(s) to harvest metadata from::

        python doiowa.py generate cpn https://... https://...

    Current supported collections are ``cpn``. You may optionally specify the
    name of the XML file doiowa will generate using the ``--out`` flag followed
    by the name of the file. If the file name is not specified a timestamp
    will be used as the file name.

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

    To get the current metadata for a DOI use the ``query`` command followed
    by the DOI::

        python doiowa.py query 10.99999/fake-doi-abc-1
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="Accepted arguments: generate, register, check")
    parser.add_argument(
        "target",
        help="""Accepted arguments after 'generate': cpn, dr-csv, dr-web. 'generate' also
    requires the '--sources' argument.
    Accepted arguments after 'register': An XML file path.
    Accepted arguments after 'check': An XML file name or a DOI batch ID.
    Accepted arguments after 'query': A DOI.""",
    )
    parser.add_argument("credentials", nargs="*", help="Crossref username and password.")
    parser.add_argument(
        "--out",
        help="""Specify the name of the XML file to create with `generate`.
    Otherwise, the timestamp will be used for the name.""",
    )
    parser.add_argument(
        "--sequence-number",
        help="""The last portion of our DOIs consists of a number.
    Normally this number starts at zero. To start with a different
    number, use this flag followed by the start number you wish to use when
    running a 'register' command.""",
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        help="""A list of file paths or URLs from which to generate DOI
    metadata.""",
    )
    parser.add_argument(
        "--collection",
        help="""An acronym for the institutional repository collection an XML file
    is being generated for. Use 'td' for Theses and Dissertations and 'cc' for Creative
    Components. This argument is required for 'generate dr-csv' and is unused otherwise."""
    )
    parser.add_argument(
        "--genre",
        help="""The genre to generate. This argument is currently only used with the
        `generate dr-web` arguments to specify whether to create thesis or report xml.
        Accepted options are 'dissertation' or 'report'. `generate dr-csv` defaults to
        'dissertation', although this might change in the future. `generate cpn` defaults
        to 'report'. This behavior is unlikely to change."""
    )

    args = parser.parse_args()

    errors = []

    if args.command == "generate":
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        out_xml_file = name_output_file(args.out, timestamp)
        if args.target == "cpn":
            xml = cpn.generate_xml(args.sources, timestamp)
            etree.ElementTree(xml.to_xml()).write(out_xml_file, encoding="utf-8", pretty_print=True)
        elif args.target == "dr-csv":
            if args.collection:
                xml = dr.generate_xml(args.sources, args.collection, timestamp)
                etree.ElementTree(xml.to_xml()).write(out_xml_file, encoding="utf-8", pretty_print=True)
            else:
                print("Sorry, the '--collection' argument is required for generating XML for the digital repository.")
        elif args.target == "dr-web":
            xml = dr.generate_xml(args.sources, args.collection, timestamp, "uri", args.genre)
            etree.ElementTree(xml.to_xml()).write(out_xml_file, encoding="utf-8", pretty_print=True)
        else:
            print(f"Sorry, doiowa does not currently support generating XML from{args.target}!")
    elif args.command == "query":
        md = crossref.get_metadata_by_doi(args.target)
        print(md)
    elif args.command == "register" or args.command == "check":
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

if __name__ == "__main__":
    main()
