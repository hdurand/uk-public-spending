# -*- coding: utf-8 -*-
"""This script scrapes spending data from http://data.gov.uk/.

"""

import urllib2
import urllib
import json
import pprint

def import_dataset(url):
	"""Return CKAN dataset.

	Parameters:
	url (str): url of the dataset

	"""
	# Make the HTTP request.
	response = urllib2.urlopen(url)
	assert response.code == 200

	# Use the json module to load CKAN's response into a dictionary.
	response_dict = json.loads(response.read())

	# Check the contents of the response.
	assert response_dict['success'] is True
	result = response_dict['result']
	#pprint.pprint(result)
	
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
	publisher = {'id': '', 'title': '', 'type': '', 'parent': '', 'homepage': '', 'homepage_for_data': ''}
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
	#if 'packages' in organization_data:
	#	publisher['packages'] = organization_data['packages']
	#print(publisher)
	
	return publisher



