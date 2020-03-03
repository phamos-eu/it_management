# -*- coding: utf-8 -*-
# Copyright (c) 2019, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt

@frappe.whitelist()
def make_sales_invoice(source_name, item_code=None, customer=None):
	target = frappe.new_doc("Sales Invoice")
	total_hours = 0
	timesheet_list = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `issue` = '{issue}'""".format(issue=source_name), as_dict=1)
	
	for _timesheet in timesheet_list:
		timesheet = frappe.get_doc('Timesheet', _timesheet.name)
		if timesheet.total_billable_hours:
			if not timesheet.total_billable_hours == timesheet.total_billed_hours:
				hours = flt(timesheet.total_billable_hours) - flt(timesheet.total_billed_hours)
				billing_amount = flt(timesheet.total_billable_amount) - flt(timesheet.total_billed_amount)
				
				target.append('timesheets', {
					'time_sheet': timesheet.name,
					'billing_hours': hours,
					'billing_amount': billing_amount
				})
				
				total_hours += hours
				
	if customer:
		target.customer = customer

	if item_code:
		target.append('items', {
			'item_code': item_code,
			'qty': total_hours
		})
		
	return target
	
@frappe.whitelist()
def relink_email(doctype, name, issue):
    """Relink Email and copy comments to Issue.

    params:
    doctype -- Doctype of the reference document
    name -- Name of the reference document
    ticket_name -- Name of the Issue
    """
    comm_list = frappe.get_list("Communication", filters={
        "reference_doctype": doctype,
        "reference_name": name
    })

    for email in comm_list:
        frappe.email.relink(
            name=email.name,
            reference_doctype="Issue",
            reference_name=issue
        )

    # copy comments
    doc = frappe.get_doc(doctype, name)
    ticket = frappe.get_doc("Issue", issue)

    if doc._comments:
        for comment in json.loads(doc._comments):
            ticket.add_comment('Comment', 'Copied comment from Task <a href="/desk#Form/Task/' + doc.name + '">' + doc.name + '</a>:<br>' + comment["comment"])
			
@frappe.whitelist()
def get_it_management_table(customer=None, type=None, status=None):
	results = []
	filter = ''
	if customer or type or status:
		filter = ' WHERE '
	if customer:
		filter += " `customer` = '{customer}'".format(customer=customer)
	if type:
		if customer:
			filter += " AND `type` = '{type}'".format(type=type)
		else:
			filter += " `type` = '{type}'".format(type=type)
	if status:
		if customer or type:
			filter += " AND `status` = '{status}'".format(status=status)
		else:
			filter += " `status` = '{status}'".format(status=status)
			
	#search it checklist
	it_checklist_results = frappe.db.sql("""SELECT
											`name` AS `reference`,
											`name` AS `Link Name`,
											`customer` AS `Customer`,
											`type` AS `Type`,
											`status` AS `Status`
											FROM `tabIT Checklist`{filter}""".format(filter=filter), as_dict=True)
											
	for it_checklist_result in it_checklist_results:
		results.append(it_checklist_result)
	
	if results:
		return results
	else:
		return False
		
@frappe.whitelist()
def get_it_management_table_from_source(source="IT Checklist", reference=None):
	return frappe.get_doc(source, reference).it_management_table