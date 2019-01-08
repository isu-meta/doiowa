from crossref.restful import Depositor
from sys import argv

def main(file, name, prefix='yourprefix', username='yourusername', password='yourpassword',*args):
	request_xml = open(file, 'r', encoding='utf-8').read()
	depositor = Depositor(prefix, username, password)
	response = depositor.register_doi(name, request_xml)

	print (response.status_code)
	print ("-----------------------------------")
	print (response.text)
	print ("-------------------------------------")
	response = depositor.request_doi_status_by_filename('{}.xml'.format(file), data_type='result')
	print (response.text)

if __name__=="__main__":
	main(*argv[1:])
