# Copyright (c) 2013, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

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

	"""
	Ein riesen großes Problem ist es, dass im ERPNext wenn der Server
	in der Production Mode läuft kein Logging möglich ist.
	Dadurch bekommen wir kein Feedback.
	"""

	return columns, data

def get_data():
	"""
	#TODO Initial Report Template ( first try )
	Under Construction:
	The goal is it to get data in the form of an array from the database via frappe.get_list(...)
	"""

	data = frappe.db.get_all("Configuration Item",
		filters={
        'status': 'Open'
		},
		fields=['name'],
		page_length=30000,
		as_list=True
	)



	return data