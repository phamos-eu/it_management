"""
Create a Solution Type for each option of the former Selection.
Reason: Solution -> Type changed from Select to Link.
"""
import frappe
from frappe.exceptions import DoesNotExistError


def execute():
    solution_types = [
        "Network",
        "Prozess",
        "Backup",
        "Industry related",
        "Other"
    ]

    for name in solution_types:
        solution_type = frappe.get_doc({
            "doctype": "Solution Type",
            "title": name
        })
        solution_type.save()
