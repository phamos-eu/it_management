"""Migrate Task Checklist to IT Management Table."""
import frappe
from frappe.exceptions import DoesNotExistError


def execute():
    try:
        frappe.get_last_doc("Task Checklist")
    except DoesNotExistError:
        return

    filters = {'parenttype':("=", "Task")}
    task_checklist = frappe.get_all("Task Checklist", filters=filters, fields="*")

    for checklist_row in task_checklist:
        try:
            task = frappe.get_doc("Task", checklist_row['parent'])
        except DoesNotExistError:
            continue
            
        task.append('it_management_table', {
            'idx': checklist_row['idx'],
            'note': checklist_row['custom'],
            'dynamic_type': 'Configuration Item',
            'dynamic_name': checklist_row['configuration_item'],
            'checked': checklist_row['check']
        })
        task.save()
