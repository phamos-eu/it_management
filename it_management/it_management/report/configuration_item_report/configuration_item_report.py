# Copyright (c) 2013, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

# import frappe

def execute(filters=None):
	"""
	This returns the contents for the Configuration Item Report.

	@params
	filters = Yet unknown
	"""

	data = get_data()

	columns = [{
		"fieldname": "name",
		"label": "ID",
		"fieldtype": "Data",
		"options": "",
		"width": 300
	}]

	return conditions["columns"], data

def get_data():

	data = []

	

	return data