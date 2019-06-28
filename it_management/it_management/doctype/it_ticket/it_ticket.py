# -*- coding: utf-8 -*-
# Copyright (c) 2019, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class ITTicket(Document):
    def onload(self):
        if self.contact:
            # load contact data to be displayed
            self.set_onload("contact_list", [frappe.get_doc("Contact", self.contact)])

    def before_insert(self):
        if self.project and not self.customer:
            self.customer = frappe.get_value(
                "Project", self.project, "customer")


@frappe.whitelist()
def relink_email(doctype, name, it_ticket):
    """Relink Email to IT Ticket.

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
