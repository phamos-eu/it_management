# -*- coding: utf-8 -*-
# Copyright (c) 2019, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
import fileinput
from frappe import _

@frappe.whitelist()
def make_sales_invoice(source_name, item_code=None, customer=None, project=None):
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
		
	if project:
		target.project = project

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
	
@frappe.whitelist()
def get_timesheets_from_source(source, source_ref):
	if source == 'Project':
		return frappe.db.sql("""SELECT `name`, `parent`, `billing_hours`, `billing_amount` AS `billing_amt`
				FROM `tabTimesheet Detail` WHERE `parenttype` = 'Timesheet' AND `docstatus` = 1 AND `project` = '{project}' AND `billable` = 1
				AND `sales_invoice` IS NULL""".format(project=source_ref), as_dict=True)
				
	if source == 'Task':
		return frappe.db.sql("""SELECT `name`, `parent`, `billing_hours`, `billing_amount` AS `billing_amt`
				FROM `tabTimesheet Detail` WHERE `parenttype` = 'Timesheet' AND `docstatus` = 1 AND `task` = '{task}' AND `billable` = 1
				AND `sales_invoice` IS NULL""".format(task=source_ref), as_dict=True)
				
	if source == 'Issue':
		return frappe.db.sql("""SELECT `name`, `parent`, `billing_hours`, `billing_amount` AS `billing_amt`
				FROM `tabTimesheet Detail` WHERE `parenttype` = 'Timesheet' AND `docstatus` = 1 AND `billable` = 1
				AND `sales_invoice` IS NULL AND `parent` IN(SELECT `name` FROM `tabTimesheet` WHERE `issue` = '{issue}')""".format(issue=source_ref), as_dict=True)
				
	if source == 'IT Service Report':
		it_service_report = frappe.get_doc("IT Service Report", source_ref)
		ts = frappe.get_doc("Timesheet", it_service_report.timesheet)
		if ts:
			return frappe.db.sql("""SELECT `name`, `parent`, `billing_hours`, `billing_amount` AS `billing_amt`
				FROM `tabTimesheet Detail` WHERE `parenttype` = 'Timesheet' AND `docstatus` = 1 AND `billable` = 1
				AND `sales_invoice` IS NULL AND `parent` = '{ts}'""".format(ts=ts.name), as_dict=True)
		else:
			return []
			
@frappe.whitelist()
def turn_off_auto_fetching_timesheets():
	js_file = open("/home/frappe/frappe-bench/apps/erpnext/erpnext/accounts/doctype/sales_invoice/sales_invoice.js", 'r+')
	js_file_content = js_file.readlines()
	if js_file_content[836] == "/* frappe.ui.form.on('Sales Invoice Timesheet', {\n":
		frappe.throw(_("Diese Funktion wurde bereits ausgeführt."))
	else:
		if js_file_content[825] == "frappe.ui.form.on('Sales Invoice Timesheet', {\n":
			js_file_content[825] = "/* frappe.ui.form.on('Sales Invoice Timesheet', {\n"
			js_file_content[847] = "}) */\n"
			js_file.seek(0)
			js_file.truncate()
			for line in js_file_content:
				js_file.write(line)
			js_file.close()
			
			py_file = open("/home/frappe/frappe-bench/apps/erpnext/erpnext/accounts/doctype/sales_invoice/sales_invoice.py", 'r+')
			py_file_content = py_file.readlines()
			if py_file_content[644] == "		self.set('timesheets', [])\n":
				py_file_content[644] = "		# self.set('timesheets', [])\n"
				py_file_content[645] = "		# if self.project:\n"
				py_file_content[646] = "			# for data in get_projectwise_timesheet_data(self.project):\n"
				py_file_content[647] = "				# self.append('timesheets', {\n"
				py_file_content[648] = "						# 'time_sheet': data.parent,\n"
				py_file_content[649] = "						# 'billing_hours': data.billing_hours,\n"
				py_file_content[650] = "						# 'billing_amount': data.billing_amt,\n"
				py_file_content[651] = "						# 'timesheet_detail': data.name\n"
				py_file_content[652] = "					# })\n"
				py_file_content[653] = "			# self.calculate_billing_amount_for_timesheet()\n"
				py_file_content[654] = "		return\n"
				
				py_file.seek(0)
				py_file.truncate()
				for line in py_file_content:
					py_file.write(line)
				py_file.close()
				return _("Die Files (sales_invoice.js und sales_invoice.py) wurden erfolgreich überschrieben")
			else:
				frappe.throw(_("Achtung, hier (sales_invoice.py) scheint etwas nicht zu stimmen!"))
		else:
			frappe.throw(_("Achtung, hier (sales_invoice.js) scheint etwas nicht zu stimmen!"))