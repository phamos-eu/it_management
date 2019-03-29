import frappe

"""
`checklist_table` in `Task` has been renamed to `task_checklist`
"""

def execute():
    tc_list = frappe.get_list("Task Checklist", filters={'parentfield':'checklist_table'})

    for name in tc_list:
        tl = frappe.get_doc("Task Checklist", name)
        tl.parentfield = 'task_checklist'
        tl.save()

