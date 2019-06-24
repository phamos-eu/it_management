import frappe
from frappe.exceptions import DoesNotExistError

"""
`checklist_table` in `Task` has been renamed to `task_checklist`
"""

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
