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


# FormMeta.add_search_fields() (Frappe v15) throws when a Link field's options
# DocType is missing. depends_on/hidden do NOT skip that check.
# Neutralize options to "[Select]" (excluded by FormMeta) when ERPNext is absent.
ERPNEXT_LINK_PS_MODULE = "IT Management"
NEUTRALIZED_LINK_OPTIONS = "[Select]"
NEUTRALIZED_DEPENDS_ON = "eval:False"
_ERPNEXT_LINK_PS_PROPERTIES = ("options", "depends_on")


def _iter_erpnext_link_fields():
	"""Yield (doctype, fieldname) pairs from the integration mapping."""
	mapping = get_erpnext_doctype_fields_mapping()
	for doctype, config in mapping.items():
		for fieldname in config.get("erpnext_fields", []):
			yield doctype, fieldname


def _delete_erpnext_link_property_setters(doctype, fieldname):
	"""Remove IT Management property setters used to neutralize ERPNext links."""
	names = frappe.get_all(
		"Property Setter",
		filters={
			"doc_type": doctype,
			"field_name": fieldname,
			"property": ["in", list(_ERPNEXT_LINK_PS_PROPERTIES)],
			"module": ERPNEXT_LINK_PS_MODULE,
		},
		pluck="name",
	)
	for name in names:
		frappe.delete_doc("Property Setter", name, force=1, ignore_permissions=True)


def _upsert_property_setter(doctype, fieldname, property_name, value, property_type):
	"""Replace any prior IT Management setter, then create a fresh one."""
	existing = frappe.get_all(
		"Property Setter",
		filters={
			"doc_type": doctype,
			"field_name": fieldname,
			"property": property_name,
			"module": ERPNEXT_LINK_PS_MODULE,
		},
		pluck="name",
	)
	for name in existing:
		frappe.delete_doc("Property Setter", name, force=1, ignore_permissions=True)

	frappe.make_property_setter(
		{
			"doctype": doctype,
			"doctype_or_field": "DocField",
			"fieldname": fieldname,
			"property": property_name,
			"value": value,
			"property_type": property_type,
		},
		ignore_validate=True,
		validate_fields_for_doctype=False,
		is_system_generated=True,
		module=ERPNEXT_LINK_PS_MODULE,
	)


def neutralize_erpnext_link_field(doctype, fieldname):
	"""
	Clear invalid ERPNext Link targets so form meta can load without ERPNext.

	Sets options to [Select] (skipped by FormMeta.add_search_fields) and hides
	the field via depends_on.
	"""
	if not frappe.db.exists("DocType", doctype):
		return False

	meta = frappe.get_meta(doctype)
	field = meta.get_field(fieldname)
	if not field or field.fieldtype != "Link":
		return False

	# Already neutralized
	if field.options == NEUTRALIZED_LINK_OPTIONS and field.depends_on == NEUTRALIZED_DEPENDS_ON:
		return False

	_upsert_property_setter(
		doctype, fieldname, "options", NEUTRALIZED_LINK_OPTIONS, "Text"
	)
	_upsert_property_setter(
		doctype, fieldname, "depends_on", NEUTRALIZED_DEPENDS_ON, "Data"
	)
	frappe.clear_cache(doctype=doctype)
	return True


def restore_erpnext_link_field(doctype, fieldname):
	"""Remove neutralization setters so DocType JSON defaults apply again."""
	if not frappe.db.exists("DocType", doctype):
		return False

	before = frappe.get_all(
		"Property Setter",
		filters={
			"doc_type": doctype,
			"field_name": fieldname,
			"property": ["in", list(_ERPNEXT_LINK_PS_PROPERTIES)],
			"module": ERPNEXT_LINK_PS_MODULE,
		},
		pluck="name",
	)
	if not before:
		return False

	_delete_erpnext_link_property_setters(doctype, fieldname)
	frappe.clear_cache(doctype=doctype)
	return True


def sync_erpnext_link_fields():
	"""
	Ensure ERPNext Link fields are safe for the current install.

	- ERPNext missing: neutralize options/depends_on via Property Setters
	- ERPNext present: remove those setters so standard Link targets work
	"""
	erpnext_installed = is_erpnext_installed()
	changed = []

	for doctype, fieldname in _iter_erpnext_link_fields():
		try:
			if erpnext_installed:
				if restore_erpnext_link_field(doctype, fieldname):
					changed.append("{0}.{1} (restored)".format(doctype, fieldname))
			else:
				if neutralize_erpnext_link_field(doctype, fieldname):
					changed.append("{0}.{1} (neutralized)".format(doctype, fieldname))
		except Exception:
			frappe.log_error(
				title="ERPNext link field sync failed for {0}.{1}".format(doctype, fieldname)
			)

	return changed
