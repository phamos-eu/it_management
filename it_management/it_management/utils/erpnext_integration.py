# -*- coding: utf-8 -*-
# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Utilities for ERPNext integration management.
Handles dynamic field creation/removal based on ERPNext availability and settings.
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
	custom_field_name = f"{doctype}-{fieldname}"
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
	custom_field_name = f"{doctype}-{fieldname}"
	
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
		frappe.log_error(f"Error deleting custom field {custom_field_name}: {e}")
		return False


def update_field_visibility(doctype, fieldname, hide=False):
	"""
	Update field visibility using depends_on.
	
	Args:
		doctype: The doctype
		fieldname: The fieldname
		hide: If True, hide the field; if False, show it
	"""
	try:
		meta = frappe.get_meta(doctype)
		field = meta.get_field(fieldname)
		if field:
			if hide:
				field.depends_on = "eval:False"
			else:
				field.depends_on = ""
			meta.save()
			return True
	except Exception as e:
		frappe.log_error(f"Error updating field visibility for {doctype}.{fieldname}: {e}")
		return False
	

def sync_erpnext_fields_for_doctype(doctype):
	"""
	Synchronize ERPNext fields for a specific doctype based on settings.
	
	This function:
	1. Checks if ERPNext is installed
	2. Checks the IT Management Settings
	3. Shows/hides or creates/removes fields accordingly
	
	Args:
		doctype: The doctype to sync
	"""
	from frappe.utils import getdate
	
	# Get the field mapping for this doctype
	mapping = get_erpnext_doctype_fields_mapping()
	if doctype not in mapping:
		return False
	
	config = mapping[doctype]
	erpnext_fields = config.get("erpnext_fields", [])
	itm_fields = config.get("itm_fields", [])
	
	if not erpnext_fields:
		return False
	
	# Get settings
	try:
		settings = frappe.get_single("IT Management Settings")
		use_erpnext = settings.use_erpnext_links if settings else True
	except Exception:
		use_erpnext = True
	
	# Check if ERPNext is installed
	erpnext_installed = is_erpnext_installed()
	
	# Determine if ERPNext fields should be visible
	show_erpnext_fields = erpnext_installed and use_erpnext
	
	# For each ERPNext field, update visibility
	for fieldname in erpnext_fields:
		# Check if the target doctype exists (only if ERPNext field)
		field_meta = get_field_metadata(doctype, fieldname)
		if field_meta and field_meta.fieldtype == "Link":
			target_doctype = field_meta.options
			# Check if target doctype exists
			try:
				frappe.get_meta(target_doctype)
				target_exists = True
			except Exception:
				target_exists = False
			
			# If target doesn't exist, hide the field
			if not target_exists:
				update_field_visibility(doctype, fieldname, hide=True)
				continue
			
		# Update visibility based on settings
		update_field_visibility(doctype, fieldname, hide=not show_erpnext_fields)
	
	# For ITM fields, show them when ERPNext fields are hidden
	for fieldname in itm_fields:
		update_field_visibility(doctype, fieldname, hide=show_erpnext_fields)
	
	return True


def sync_all_erpnext_fields():
	"""
	Synchronize ERPNext fields for all configured doctypes.
	
	This should be called when:
	- IT Management Settings are saved
	- The app is installed/updated
	- ERPNext is installed/uninstalled
	"""
	mapping = get_erpnext_doctype_fields_mapping()
	
	for doctype in mapping.keys():
		sync_erpnext_fields_for_doctype(doctype)
	
	# Also clear any cached meta
	frappe.clear_cache(doctype=True)
