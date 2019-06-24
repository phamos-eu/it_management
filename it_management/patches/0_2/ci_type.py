"""
Create a Configuration Item Type for each option of the former Selection.
Reason: Configuration Item -> Type changed from Select to Link.
"""
import frappe
from frappe.exceptions import DoesNotExistError


def execute():
    ci_types = [
        "Client",
        "Hypervisor",
        "Infrastructure",
        "Machine, Modality",
        "Network Device",
        "Peripheral",
        "Phone",
        "Printer, Scanner, Fax",
        "Server",
        "Share",
        "Sonstiges"
    ]

    for name in ci_types:
        ci_type = frappe.get_doc({
            "doctype": "Configuration Item Type",
            "title": name
        })
        ci_type.save()
