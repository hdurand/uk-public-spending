# -*- coding: utf-8 -*-
"""This script scrapes spending data from http://data.gov.uk/.

"""

import urllib2
import urllib
import json
import csv
import unicodecsv
import math
import time
import re
import sys

# Settings
# Search query for spending files.
SEARCH_QUERY = '*:spend%20OR%20*:spent%20OR%20*:expenditure'

def import_dataset(url):
	"""Return CKAN dataset.

	Parameters:
	url (str): url of the dataset

	"""
	print('Get: ' + url)
	try:
		# Make the HTTP request.
		response = urllib2.urlopen(url)
		assert response.code == 200
	except urllib2.URLError as e:
		if hasattr(e, 'code'):
			print('The server couldn\'t fulfill the request.')
			print('Error code: ' + str(e.code))
		elif hasattr(e, 'reason'):
			print('Failed to reach the server.')
			print('Reason: ' + str(e.reason))
		sys.exit(0)
	except AssertionError:
		print('Unexpected response code from the server.')
		print('Response code: ' + str(response.code))
		sys.exit(0)
	else:
		try:
			# Use the json module to load CKAN's response into a dictionary.
			response_dict = json.loads(response.read())
		except ValueError:
			print('Response content is not a valid JSON document.')
			sys.exit(0)
		else:
			try:
				# Check the contents of the response.
				assert response_dict['success'] is True
			except AssertionError:
				print('API request failed.')
				sys.exit(0)
			else:
				result = response_dict.get('result', {})
				return result
	
def get_organization_data(organization):
	"""Return dict of organization data from a CKAN dataset.

	Parameters:
	organization (dict): CKAN organization

	"""
	# Get the data.
	publisher = {'id': '', 'title': '', 'type': '', 'contact': '', 'email': '', 'parent_id': '', 'homepage': ''}
	if organization.get('name'):
		publisher['id'] = organization.get('name')
	if organization.get('title'):
		publisher['title'] = organization.get('title')
	if organization.get('extras'):
		extras = organization.get('extras')
		for extra in extras:
			if extra.get('key') == 'category' and extra.get('value'):
				publisher['type'] = extra.get('value')
			elif extra.get('key') == 'contact-name' and extra.get('value'):
				publisher['contact'] = extra.get('value')
			elif extra.get('key') == 'contact-email' and extra.get('value'):
				publisher['email'] = re.sub('mailto:|email ', '', extra.get('value'))
	if organization.get('groups'):
		groups = organization.get('groups')
		parent = ''
		for group in groups:
			if parent and group.get('name'):
				parent += ' / ' + group.get('name')
			elif group.get('name'):
				parent += group.get('name')
		publisher['parent_id'] = parent
	if publisher['id']:
		publisher['homepage'] = 'http://data.gov.uk/publisher/' + publisher['id']
	
	return publisher
	
def get_sample_organizations(url_base):
	"""Return sample list of publishers."""
	# Get organizations.
	url = url_base + '3/action/organization_list?all_fields=True&include_groups=True&include_extras=True'
	print('Scraping publishers...')
	organization_list = import_dataset(url)
	time.sleep(0.3)
	print('Scraping publishers... Done')
	
	# Get data for each organization.
	print('Loading publishers data...')
	publishers = []
	sample = organization_list[0:30]
	for organization in sample:
		organization_data = get_organization_data(organization)
		publishers.append(organization_data)
	print('Loading publishers data... Done')
	print('Scraped: ' + str(len(sample)) + ' publishers')
	
	return publishers

def get_all_organizations(url_base):
	"""Return list of publishers."""
	# Get organizations.
	url = url_base + '3/action/organization_list?all_fields=True&include_groups=True&include_extras=True'
	print('Scraping publishers...')
	organization_list = import_dataset(url)
	time.sleep(0.3)
	print('Scraping publishers... Done')
	
	# Get data for each organization.
	print('Loading publishers data...')
	publishers = []
	for organization in organization_list:
		organization_data = get_organization_data(organization)
		publishers.append(organization_data)
	print('Loading publishers data... Done')
	print('Scraped: ' + str(len(organization_list)) + ' publishers')
	
	return publishers

def get_count(url):
	"""Return number of results.

	Parameters:
	url (str): url with a query

	"""
	result = import_dataset(url)
	
	# Get the count.
	count = ''
	if result.get('count'):
		count = result.get('count')
	
	return count

def get_number_pages(count):
	"""Return the number of pages for 1000 results per page."""
	pages = math.ceil(float(count) / 1000)
	return int(pages)

def get_results(url_base, query):
	"""Return result packages.

	Parameters:
	url_base (str): CKAN API url
	query (str): query to search for packages

	"""
	# Get the number of results.
	url_count = 'http://data.gov.uk/api/action/package_search?q=' + query + '&rows=1'
	print('Scraping number of packages...')
	count = get_count(url_count)
	print('Scraping number of packages... Done')
	print('Number of packages to scrape: ' + str(count))
	time.sleep(0.3)
	
	# Get the number of pages.
	pages = get_number_pages(count)
	print('Maximum number of packages per page: 1000')
	print('Number of results pages to scrape: ' + str(pages))
	
	# Get the results.
	print('Scraping packages...')
	results = []
	for i in range(0, pages):
		url = url_base + 'action/package_search?q=' + query + '&rows=1000&start=' + str(i * 1000)
		result = import_dataset(url)
		time.sleep(0.3)
		if result.get('results'):
			results.append(result['results'])
	print('Scraping packages... Done')
		
	return results

def clean_format(format_value, url):
	"""Return cleaned format string.

	Parameters:
	format_value (str): format value of the resource
	url (str): url of the resource

	"""
	url = url.strip()

	# Get format from file extension or format value in resource
	if re.search('\.csv$', url, re.I) or re.search('csv', format_value, re.I):
		cleaned = 'CSV'
	elif re.search('\.xls[xm]?$', url, re.I) or re.search('xls', format_value, re.I):
		cleaned = 'XLS'
	elif re.search('\.pdf$', url, re.I) or re.search('pdf', format_value, re.I):
		cleaned = 'PDF'
	elif re.search('\.xml$', url, re.I) or re.search('xml', format_value, re.I):
		cleaned = 'XML'
	elif re.search('\.(html|htm|php|aspx)$', url, re.I) or re.search('htm|aspx|php|web', format_value, re.I):
		cleaned = 'HTML'
	elif re.search('\.zip$', url, re.I) or re.search('zip', format_value, re.I):
		cleaned = 'ZIP'
	elif re.search('\.ods$', url, re.I) or re.search('ods', format_value, re.I):
		cleaned = 'ODS'
	elif re.search('\.doc[x]?$', url, re.I) or re.search('doc|word', format_value, re.I):
		cleaned = 'DOC'
	elif re.search('\.json$', url, re.I) or re.search('json', format_value, re.I):
		cleaned = 'JSON'
	elif re.search('\.jpg$', url, re.I) or re.search('jpg', format_value, re.I):
		cleaned = 'JPG'
	elif re.search('\.txt$', url, re.I) or re.search('txt', format_value, re.I):
		cleaned = 'TXT'
	else:
		cleaned = ''

	return cleaned

def get_datafile_data(package, resource):
	"""Return dict of data of a resource.

	Parameters:
	package (dict): CKAN package
	resource (dict): CKAN resource from package

	"""
	# Get data of datafile.
	datafile = {'id': '', 'url': '', 'format': '', 'last_modified': '', 'period': '', 'title': '', 'publisher_id': ''}
	if resource.get('id'):
		datafile['id'] = resource.get('id')
	if resource.get('url'):
		datafile['url'] = resource.get('url')
	if resource.get('format'):
		datafile['format'] = clean_format(resource['format'], datafile['url'])
	else:
		datafile['format'] = clean_format('', datafile['url'])
	if resource.get('last_modified'):
		datafile['last_modified'] = resource.get('last_modified')
	if resource.get('date'):
		datafile['period'] = resource.get('date')
	title = ''
	if package.get('title'):
		title += package.get('title')
	if title and resource.get('description'):
		title += ' / ' + resource.get('description')
	elif resource.get('description'):
		title += resource.get('description')
	datafile['title'] = title
	if package.get('organization'):
		organization = package.get('organization')
		if organization.get('name'):
			datafile['publisher_id'] = organization.get('name')

	return datafile

def get_datafiles(package):
	"""Return list of datafiles of a package.

	Parameters:
	package (dict): CKAN package

	"""
	datafiles = []
	searched = ''

	# Get datafiles for packages with 500 or 25000 in their title, name or description.
	if package.get('title'):
		searched += package['title']
	if package.get('name'):
		searched += package['name']
	if package.get('notes'):
		searched += package['notes']

	if re.search('500|25000|25 000|25,000|25K', searched, re.I):
		if 'resources' in package:
			for resource in package['resources']:
				datafile = get_datafile_data(package, resource)
				datafiles.append(datafile)
	# Get datafiles with 500 or 25000 in their description.
	else:
		if 'resources' in package:
			for resource in package['resources']:
				searched = ''
				if resource.get('description'):
					searched += resource['description']
				if re.search('500|25000|25 000|25,000|25K', searched, re.I):
					datafile = get_datafile_data(package, resource)
					datafiles.append(datafile)

	return datafiles

def make_csv(csvfile, fieldnames, dataset):
	"""Create a csv file.

	Parameters:
	csvfile (str): name of csv file to create
	fieldnames (list of str): csv header
	dataset (list of dict): each dict will be a csv row

	"""
	with open(csvfile, 'w') as data:
		writer = unicodecsv.DictWriter(data, fieldnames=fieldnames)
		writer.writeheader()
		for element in dataset:
			writer.writerow(element)
	
def make_publishers_csv_sample(csvfile):
	"""Make sample publishers csv file."""
	# Get organizations data
	publishers = get_sample_organizations('http://data.gov.uk/api/')
	
	# Make publishers csv file.
	fieldnames = ['id', 'title', 'type', 'homepage', 'contact', 'email', 'parent_id']
	print('Making ' + csvfile + '...')
	make_csv(csvfile, fieldnames, publishers)
	print('Making ' + csvfile + '... Done')

def make_publishers_csv(csvfile):
	"""Make publishers csv file."""
	# Get organizations data
	publishers = get_all_organizations('http://data.gov.uk/api/')
	
	# Make publishers csv file.
	fieldnames = ['id', 'title', 'type', 'homepage', 'contact', 'email', 'parent_id']
	print('Making ' + csvfile + '...')
	make_csv(csvfile, fieldnames, publishers)
	print('Making ' + csvfile + '... Done')

def make_datafiles_csv_sample(csvfile):
	"""Make sample datafiles csv file."""
	# Get results from http://data.gov.uk/.
	url_base = 'http://data.gov.uk/api/'
	print('Scraping sources...')
	results = get_results(url_base, SEARCH_QUERY)
	print('Scraping sources... Done')
	
	# Get sample of datafiles from results.
	resources = []
	print('Loading sources data...')
	first_page = results[0]
	sample = first_page[0:20]
	for package in sample:
		datafiles = []
		if 'unpublished' in package:
			if package['unpublished'] != 'true':
				datafiles = get_datafiles(package)
				resources += datafiles
		else:
			datafiles = get_datafiles(package)
			resources += datafiles
	package_count = len(sample)
	print('Loading sources data... Done')
	print('Scraped: ' + str(len(resources)) + ' sources from ' + str(package_count) + ' packages.')
	
	# Make datafiles csv file.
	fieldnames = ['id', 'publisher_id', 'title', 'url', 'format', 'last_modified', 'period']
	print('Making ' + csvfile + '...')
	make_csv(csvfile, fieldnames, resources)
	print('Making ' + csvfile + '... Done')

def make_datafiles_csv(csvfile):
	"""Make datafiles csv file."""
	# Get results from http://data.gov.uk/.
	url_base = 'http://data.gov.uk/api/'
	print('Scraping sources...')
	results = get_results(url_base, SEARCH_QUERY)
	print('Scraping sources... Done')
	
	# Get datafiles from results.
	resources = []
	package_count = 0
	print('Loading sources data...')
	for page in results:
		for package in page:
			datafiles = []
			if 'unpublished' in package:
				if package['unpublished'] != 'true':
					datafiles = get_datafiles(package)
					resources += datafiles
			else:
				datafiles = get_datafiles(package)
				resources += datafiles
		package_count += len(page)
	print('Loading sources data... Done')
	print('Scraped: ' + str(len(resources)) + ' sources from ' + str(package_count) + ' packages.')
	
	# Make datafiles csv file.
	fieldnames = ['id', 'publisher_id', 'title', 'url', 'format', 'last_modified', 'period']
	print('Making ' + csvfile + '...')
	make_csv(csvfile, fieldnames, resources)
	print('Making ' + csvfile + '... Done')

# Scrape a sample.
make_publishers_csv_sample('data/publishers-sample.csv')
make_datafiles_csv_sample('data/datafiles-sample.csv')

# Scrape all data.
#make_publishers_csv('data/publishers.csv')
#make_datafiles_csv('data/datafiles.csv')
