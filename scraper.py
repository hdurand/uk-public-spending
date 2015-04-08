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

def import_dataset(url):
	"""Return CKAN dataset.

	Parameters:
	url (str): url of the dataset

	"""
	# Make the HTTP request.
	print('HTTP request: ' + url + '...')
	response = urllib2.urlopen(url)
	assert response.code == 200

	# Use the json module to load CKAN's response into a dictionary.
	response_dict = json.loads(response.read())

	# Check the contents of the response.
	assert response_dict['success'] is True
	result = response_dict['result']
	
	return result

def get_organization_data(organization):
	"""Return dict of organization data from a CKAN dataset.

	Parameters:
	organization (str): name of the organization

	"""
	# Import dataset.
	url = 'http://data.gov.uk/api/3/action/organization_show?id=' + organization
	organization_data = import_dataset(url)
	
	# Get the data.
	publisher = {'id': '', 'name': '', 'title': '', 'type': '', 'parent': '', 'homepage': '', 'homepage_for_data': ''}
	publisher['name'] = organization
	if 'id' in organization_data:
		publisher['id'] = organization_data['id']
	if 'title' in organization_data:
		publisher['title'] = organization_data['title']
	if 'category' in organization_data:
		publisher['type'] = organization_data['category']
	if 'groups' in organization_data:
		groups = organization_data['groups']
		parent = ''
		for elt in groups:
			if 'name' in elt:
				if parent == '':
					parent += elt['name']
				else:
					parent += ' + ' + elt['name']
		publisher['parent'] = parent
	publisher['homepage'] = 'http://data.gov.uk/publisher/' + organization
	publisher['homepage_for_data'] = 'http://data.gov.uk/data/search?q=spend&unpublished=false&publisher=' + organization
	
	return publisher

def get_sample_organizations():
	"""Return sample list of publishers."""
	# Get list of organizations.
	url = 'http://data.gov.uk/api/3/action/organization_list'
	print('Get list of organizations...')
	organization_list = import_dataset(url)
	print('Sleep 6s...')
	time.sleep(6)
	
	# Get data for each organization.
	publishers = []
	print('Get organizations data...')
	sample = organization_list[0:30]
	for organization in sample:
		organization_data = get_organization_data(organization)
		print('Sleep 6s...')
		time.sleep(6)
		publishers.append(organization_data)
	print(str(len(sample)) + ' publishers')
	
	return publishers

def get_all_organizations():
	"""Return list of publishers."""
	# Get list of organizations.
	url = 'http://data.gov.uk/api/3/action/organization_list'
	print('Get list of organizations...')
	organization_list = import_dataset(url)
	print('Sleep 6s...')
	time.sleep(6)
	
	# Get data for each organization.
	publishers = []
	print('Get organizations data...')
	for organization in organization_list:
		organization_data = get_organization_data(organization)
		print('Sleep 6s...')
		time.sleep(6)
		publishers.append(organization_data)
	print(str(len(organization_list)) + ' publishers')
	
	return publishers

def get_count(url):
	"""Return number of results.

	Parameters:
	url (str): url with a query

	"""
	# Make the HTTP request.
	print('HTTP request: ' + url + '...')
	response = urllib2.urlopen(url)
	assert response.code == 200
	
	# Use the json module to load CKAN's response into a dictionary.
	response_dict = json.loads(response.read())
	
	# Get the count.
	if 'count' in response_dict:
		count = response_dict['count']
	else:
		count = ''
	
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
	url_count = url_base + 'search/package?q=' + query
	print('Get number of results...')
	count = get_count(url_count)
	print('Sleep 6s...')
	time.sleep(6)
	
	# Get the number of pages.
	print('Get number of pages...')
	pages = get_number_pages(count)
	
	# Get the results.
	print('Get results...')
	results = []
	for i in range(0, pages):
		url = url_base + 'action/package_search?q=' + query + '&rows=100000&start=' + str(i * 1000)
		result = import_dataset(url)
		print('Sleep 20s...')
		time.sleep(20)
		results.append(result['results'])
		
	return results

def get_datafiles(package):
	"""Return list of datafiles of a package.

	Parameters:
	package (dict): CKAN package

	"""
	datafiles = []
	
	# For each datafile, get the data.
	if 'resources' in package:
		for resource in package['resources']:
			datafile = {'id': '', 'url': '', 'package_title': '', 'file_description': '', 'format': '', 'publisher_id': '', 'publisher_name': '', 'period_start': '', 'period_end': '', 'period_length': '', 'theme_primary': ''}
			if 'id' in resource:
				datafile['id'] = resource['id']
			if 'url' in resource:
				datafile['url'] = resource['url']
			if 'description' in resource:
				datafile['file_description'] = resource['description']
			if 'format' in resource:
				if resource['format'] == '' and 'mimetype' in resource:
					datafile['format'] = resource['mimetype']
				else:
					datafile['format'] = resource['format']
			if 'title' in package:
				datafile['package_title'] = package['title']
			if 'temporal_coverage-from' in package:
				datafile['period_start'] = package['temporal_coverage-from']
			if 'temporal_coverage-to' in package:
				datafile['period_end'] = package['temporal_coverage-to']
			if 'temporal_granularity' in package:
				datafile['period_length'] = package['temporal_granularity']
			if 'theme-primary' in package:
				datafile['theme_primary'] = package['theme-primary']
			if 'organization' in package:
				if 'id' in package['organization']:
					datafile['publisher_id'] = package['organization']['id']
				if 'name' in package['organization']:
					datafile['publisher_name'] = package['organization']['name']
			# Store each datafile in datafiles.
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
	publishers = get_sample_organizations()
	
	# Make publishers csv file.
	fieldnames = ['id', 'name', 'title', 'type', 'parent', 'homepage', 'homepage_for_data']
	print('Make ' + csvfile + '...')
	make_csv(csvfile, fieldnames, publishers)

def make_publishers_csv(csvfile):
	"""Make publishers csv file."""
	# Get organizations data
	publishers = get_all_organizations()
	
	# Make publishers csv file.
	fieldnames = ['id', 'name', 'title', 'type', 'parent', 'homepage', 'homepage_for_data']
	print('Make ' + csvfile + '...')
	make_csv(csvfile, fieldnames, publishers)

def make_datafiles_csv_sample(csvfile):
	"""Make sample datafiles csv file."""
	# Get results from http://data.gov.uk/.
	url_base = 'http://data.gov.uk/api/'
	print('Get results for q=spend...')
	results = get_results(url_base, 'spend')
	
	# Get sample of datafiles from results.
	resources = []
	print('Get datafiles...')
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
	print(str(package_count) + ' packages')
	print(str(len(resources)) + ' files')
	
	# Make datafiles csv file.
	fieldnames = ['id', 'url', 'package_title', 'file_description', 'format', 'publisher_id', 'publisher_name', 'period_start', 'period_end', 'period_length', 'theme_primary']
	print('Make ' + csvfile + '...')
	make_csv(csvfile, fieldnames, resources)

def make_datafiles_csv(csvfile):
	"""Make datafiles csv file."""
	# Get results from http://data.gov.uk/.
	url_base = 'http://data.gov.uk/api/'
	print('Get results for q=spend...')
	results = get_results(url_base, 'spend')
	
	# Get datafiles from results.
	resources = []
	package_count = 0
	print('Get datafiles...')
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
	print(str(package_count) + ' packages')
	print(str(len(resources)) + ' files')
	
	# Make datafiles csv file.
	fieldnames = ['id', 'url', 'package_title', 'file_description', 'format', 'publisher_id', 'publisher_name', 'period_start', 'period_end', 'period_length', 'theme_primary']
	print('Make ' + csvfile + '...')
	make_csv(csvfile, fieldnames, resources)

# Scrape a sample.
make_publishers_csv_sample('publishers-sample.csv')
make_datafiles_csv_sample('datafiles-sample.csv')

# Scrape all data.
#make_publishers_csv('../publishers.csv')
#make_datafiles_csv('../datafiles.csv')

print('Done')

