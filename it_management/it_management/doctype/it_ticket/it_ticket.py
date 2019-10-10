# -*- coding: utf-8 -*-
# Copyright (c) 2019, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json
from frappe import _
from frappe.utils.data import nowdate


class ITTicket(Document):
    def onload(self):
        if self.contact:
            # load contact data to be displayed
            self.set_onload("contact_list", [
                            frappe.get_doc("Contact", self.contact)])

    def before_insert(self):
        if self.task and not self.project:
            self.project = frappe.get_value("Task", self.task, "project")
            
        if self.project and not self.customer:
            self.customer = frappe.get_value("Project", self.project, "customer")



@frappe.whitelist()
def relink_email(doctype, name, it_ticket):
    """Relink Email and copy comments to IT Ticket.

    params:
    doctype -- Doctype of the reference document
    name -- Name of the reference document
    ticket_name -- Name of the IT Ticket
    """
    comm_list = frappe.get_list("Communication", filters={
        "reference_doctype": doctype,
        "reference_name": name,
    })

    for email in comm_list:
        frappe.email.relink(
            name=email.name,
            reference_doctype="IT Ticket",
            reference_name=it_ticket
        )

    # copy comments
    doc = frappe.get_doc(doctype, name)
    ticket = frappe.get_doc("IT Ticket", it_ticket)

    if doc._comments:
        for comment in json.loads(doc._comments):
            ticket.add_comment(comment["comment"])

@frappe.whitelist()
def create_sinv(it_ticket):
	it_ticket = frappe.get_doc("IT Ticket", it_ticket)
	if not it_ticket.customer:
		frappe.throw(_("Please define Customer!"))
	if len(get_timesheet_details_for_sinv(it_ticket.name)) < 1:
		frappe.throw(_("The Timesheets are already billed!"))
	sinv = frappe.get_doc({"doctype": "Sales Invoice"})
	sinv.due_date = nowdate()
	sinv.customer = it_ticket.customer
	# which item should be taken?
	sinv.append('items', {
				'item_code': 'test_item',
				'qty': 1
			})
	sinv.insert()
	add_timesheets_to_sinv(it_ticket.name, sinv)
	return sinv

def add_timesheets_to_sinv(it_ticket, sinv):
	sinv.set('timesheets', [])
	for data in get_timesheet_details_for_sinv(it_ticket):
		sinv.append('timesheets', {
				'time_sheet': data.parent,
				'billing_hours': data.billing_hours,
				'billing_amount': data.billing_amt,
				'timesheet_detail': data.name
			})

	sinv.calculate_billing_amount_for_timesheet()
	sinv.save()

def get_timesheet_details_for_sinv(it_ticket):
	timesheet_list = """SELECT `name` FROM `tabTimesheet` WHERE `it_ticket` = '{it_ticket}'""".format(it_ticket=it_ticket)
	return frappe.db.sql("""SELECT `name`, `parent`, `billing_hours`, `billing_amount` as `billing_amt`
		FROM `tabTimesheet Detail` WHERE `parenttype` = 'Timesheet' AND `docstatus` = 1 AND `parent` IN ({timesheet_list}) AND `billable` = 1
		AND `sales_invoice` IS NULL""".format(timesheet_list=timesheet_list), as_dict=1)