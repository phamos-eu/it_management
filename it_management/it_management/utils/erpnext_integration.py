# -*- coding: utf-8 -*-
# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Utilities for ERPNext integration management.
Handles validation and field visibility logic for ERPNext integration.
"""

from __future__ import unicode_literals
import frappe
from frappe import _


def is_erpnext_installed():
	"""Check if ERPNext app is installed."""
	try:
		installed_apps = frappe.get_installed_apps()
		return 'erpnext' in installed_apps
	except Exception:
		return False


def validate_erpnext_required():
	"""Validate that ERPNext is installed, throw error if not."""
	if not is_erpnext_installed():
		frappe.throw(
			_("ERPNext is not installed. Please install ERPNext to use this feature."),
			title=_("ERPNext Required")
		)


def get_erpnext_doctype_fields_mapping():
	"""
	Get mapping of doctypes and their ERPNext/ITM field pairs.
	
	Returns:
		dict: {
			"ITM Host Item": {
				"erpnext_fields": ["customer", "item_code"],
				"itm_fields": ["itm_customer", "itm_item"]
			},
			...
		}
	"""
	return {
		"ITM Host Item": {
			"erpnext_fields": ["customer", "item_code"],
			"itm_fields": ["itm_customer", "itm_item"]
		},
		"Software Instance": {
			"erpnext_fields": ["customer", "supplier"],
			"itm_fields": []
		},
		"Configuration Item": {
			"erpnext_fields": ["customer", "item_code", "supplier"],
			"itm_fields": []
		},
		"IT Hardware": {
			"erpnext_fields": ["item_code"],
			"itm_fields": []
		},
		"Licence": {
			"erpnext_fields": ["item_code", "supplier"],
			"itm_fields": []
		},
		"ITM User Account": {
			"erpnext_fields": ["customer"],
			"itm_fields": []
		},
		"User Account": {
			"erpnext_fields": ["customer"],
			"itm_fields": []
		},
		"Subnet Table": {
			"erpnext_fields": ["customer"],
			"itm_fields": []
		},
		"Location Room": {
			"erpnext_fields": ["customer"],
			"itm_fields": []
		},
		"ITM Solution Table": {
			"erpnext_fields": ["customer"],
			"itm_fields": []
		},
		"User Group Table": {
			"erpnext_fields": ["customer"],
			"itm_fields": []
		},
		"IT Checklist Table": {
			"erpnext_fields": ["customer"],
			"itm_fields": []
		},
		"Solution Table": {
			"erpnext_fields": ["customer"],
			"itm_fields": []
		},
		"ITM Solution": {
			"erpnext_fields": ["customer"],
			"itm_fields": []
		}
	}


def get_field_metadata(doctype, fieldname):
	"""Get field metadata from doctype."""
	try:
		meta = frappe.get_meta(doctype)
		field = meta.get_field(fieldname)
		return field
	except Exception:
		return None


def create_custom_field(doctype, fieldname, fieldtype, options=None, label=None, **kwargs):
	"""
	Create a custom field if it doesn't exist.
	
	Args:
		doctype: The doctype to add the field to
		fieldname: The fieldname
		fieldtype: The fieldtype (Link, Data, etc.)
		options: For Link fields, the target doctype
		label: The field label
		**kwargs: Additional field properties
	"""
	# Check if field already exists in the doctype
	meta = frappe.get_meta(doctype)
	if meta.has_field(fieldname):
		return False

	# Check if it's a custom field
	custom_field_name = "{0}-{1}".format(doctype, fieldname)
	try:
		frappe.get_doc("Custom Field", custom_field_name)
		return False  # Already exists as custom field
	except frappe.DoesNotExistError:
		pass

	# Create the custom field
	custom_field = frappe.new_doc("Custom Field")
	custom_field.dt = doctype
	custom_field.fieldname = fieldname
	custom_field.fieldtype = fieldtype
	custom_field.label = label or fieldname
	
	if options:
		custom_field.options = options
	
	# Set common properties
	for key, value in kwargs.items():
		if hasattr(custom_field, key):
			setattr(custom_field, key, value)
	
	custom_field.insert(ignore_permissions=True)
	return True


def remove_custom_field(doctype, fieldname):
	"""
	Remove a custom field if it exists.
	
	Args:
		doctype: The doctype
		fieldname: The fieldname to remove
	"""
	custom_field_name = "{0}-{1}".format(doctype, fieldname)
	
	# Check if it's a standard field (not custom)
	meta = frappe.get_meta(doctype)
	if meta.has_field(fieldname):
		# It's a standard field, we can't delete it
		# But we can hide it via depends_on
		return False
	
	# Try to delete custom field
	try:
		frappe.delete_doc("Custom Field", custom_field_name, force=True)
		return True
	except frappe.DoesNotExistError:
		return False
	except Exception as e:
		frappe.log_error("Error deleting custom field {0}: {1}".format(custom_field_name, str(e)))
		return False
