"""
IT Ticket: Change fieldname `title` to `subject` for better EMail compatibility.
"""
import frappe
from frappe.exceptions import DoesNotExistError


def execute():
    try:
        frappe.get_last_doc("IT Ticket")
    except DoesNotExistError:
        return

    tickets = frappe.get_list("IT Ticket", filters={"title":("!=", "")})

    for name in tickets:
        ticket = frappe.get_doc("IT Ticket", name)
        ticket.subject = ticket.title
        ticket.save()
