"""
Create a IT Ticket Type for each option of the former Selection.
Reason: IT Ticket -> Type changed from Select to Link.
"""
import frappe
from frappe.exceptions import DoesNotExistError


def execute():
    ticket_types = [
        "Incident",
        "Problem",
        "Change"
    ]

    frappe.reload_doc('it_management', 'doctype', 'it_ticket_type')

    for name in ticket_types:
        try:
            itt = frappe.get_doc({
                "doctype": "IT Ticket Type",
                "title": name
            })
            itt.save()
        except frappe.DuplicateEntryError:
            continue
