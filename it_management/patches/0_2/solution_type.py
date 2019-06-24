"""
Create a Solution Type for each option of the former Selection.
Reason: Solution -> Type changed from Select to Link.
"""
import frappe


def execute():
    solution_types = [
        "Network",
        "Prozess",
        "Backup",
        "Industry related",
        "Other"
    ]

    frappe.reload_doc('it_management', 'doctype', 'solution_type')

    for name in solution_types:
        try:
            solution_type = frappe.get_doc({
                "doctype": "Solution Type",
                "title": name
            })
            solution_type.save()
        except frappe.DuplicateEntryError:
            continue
