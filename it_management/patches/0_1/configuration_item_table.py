import frappe
from frappe.exceptions import DoesNotExistError

"""
Column `linked_configuration_item` in `Configuration Item Table` has been renamed to `configuration_item`

UPDATE `tabConfiguration Item Table`
SET configuration_item = linked_configuration_item
WHERE linked_configuration_item is not NULL and configuration_item is NULL
"""

def execute():
    try:
        frappe.get_last_doc("Configuration Item Table")
    except DoesNotExistError:
        return

    filters={'linked_configuration_item':("!=", ""), 'configuration_item':("=", "")}
    cit_list = frappe.get_list("Configuration Item Table", filters=filters)

    for name in cit_list:
        tl = frappe.get_doc("Configuration Item Table", name)
        tl.configuration_item = tl.linked_configuration_item
        tl.save()
