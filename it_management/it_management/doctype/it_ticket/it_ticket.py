# -*- coding: utf-8 -*-
# Copyright (c) 2019, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json
from frappe import _
from frappe.utils.data import nowdate
from frappe.utils import flt


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
def make_sales_invoice(source_name, item_code=None, customer=None):
	target = frappe.new_doc("Sales Invoice")
	total_hours = 0
	timesheet_list = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `it_ticket` = '{it_ticket}'""".format(it_ticket=source_name), as_dict=1)
	
	for _timesheet in timesheet_list:
		timesheet = frappe.get_doc('Timesheet', _timesheet.name)
		if timesheet.total_billable_hours:
			if not timesheet.total_billable_hours == timesheet.total_billed_hours:
				hours = flt(timesheet.total_billable_hours) - flt(timesheet.total_billed_hours)
				billing_amount = flt(timesheet.total_billable_amount) - flt(timesheet.total_billed_amount)
				billing_rate = billing_amount / hours
				
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
			'qty': total_hours,
			'rate': billing_rate
		})
		
	target.run_method("calculate_billing_amount_for_timesheet")
	target.run_method("set_missing_values")

	return target