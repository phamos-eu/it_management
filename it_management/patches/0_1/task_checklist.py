import frappe
from frappe.exceptions import DoesNotExistError

"""
`checklist_table` in `Task` has been renamed to `task_checklist`
"""

def execute():
    try:
        frappe.get_last_doc("Task Checklist")
    except DoesNotExistError:
        return

    tc_list = frappe.get_list("Task Checklist", filters={'parentfield':'checklist_table'})

    for name in tc_list:
        tl = frappe.get_doc("Task Checklist", name)
        tl.parentfield = 'task_checklist'
        tl.save()

