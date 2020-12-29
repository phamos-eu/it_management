# -*- coding: utf-8 -*-
# Copyright (c) 2020, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
import frappe

class ITLandscape(Document):
	pass


def get_timeline_data(doctype, name):
	
	it_landscape = frappe.get_doc("IT Landscape", name)

	data = dict(frappe.db.sql('''select unix_timestamp(modified), count(*)
			from `tabIssue` where it_landscape=%s
			and modified > date_sub(curdate(), interval 1 year)
			group by date(modified)''', it_landscape.name))

	return data
    	
	