# -*- coding: utf-8 -*-
# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Utilities for ERPNext integration management.

ERPNext Link fields (Customer, Item, …) are optional:
- Fresh DocType JSON does not ship them for managed DocTypes (ITM Host Item).
- They are created as Custom Fields when ERPNext is installed and
  IT Management Settings.use_erpnext_links is enabled.
- Disabling the setting removes empty Link Custom Fields, or converts valued
  ones to Data so values are never dropped.
"""

from __future__ import unicode_literals

import frappe
from frappe import _


def is_erpnext_installed():
	"""Check if ERPNext app is installed."""
	try:
		installed_apps = frappe.get_installed_apps()
		return "erpnext" in installed_apps
	except Exception:
		return False


def validate_erpnext_required():
	"""Validate that ERPNext is installed, throw error if not."""
	if not is_erpnext_installed():
		frappe.throw(
			_("ERPNext is not installed. Please install ERPNext to use this feature."),
			title=_("ERPNext Required"),
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
			"itm_fields": ["itm_customer", "itm_item"],
		},
		"Software Instance": {
			"erpnext_fields": ["customer", "supplier"],
			"itm_fields": [],
		},
		"Configuration Item": {
			"erpnext_fields": ["customer", "item_code", "supplier"],
			"itm_fields": [],
		},
		"IT Hardware": {
			"erpnext_fields": ["item_code"],
			"itm_fields": [],
		},
		"Licence": {
			"erpnext_fields": ["item_code", "supplier"],
			"itm_fields": [],
		},
		"ITM User Account": {
			"erpnext_fields": ["customer"],
			"itm_fields": [],
		},
		"User Account": {
			"erpnext_fields": ["customer"],
			"itm_fields": [],
		},
		"Subnet Table": {
			"erpnext_fields": ["customer"],
			"itm_fields": [],
		},
		"Location Room": {
			"erpnext_fields": ["customer"],
			"itm_fields": [],
		},
		"ITM Solution Table": {
			"erpnext_fields": ["customer"],
			"itm_fields": [],
		},
		"User Group Table": {
			"erpnext_fields": ["customer"],
			"itm_fields": [],
		},
		"IT Checklist Table": {
			"erpnext_fields": ["customer"],
			"itm_fields": [],
		},
		"Solution Table": {
			"erpnext_fields": ["customer"],
			"itm_fields": [],
		},
		"ITM Solution": {
			"erpnext_fields": ["customer", "supplier"],
			"itm_fields": [],
		},
	}


# DocTypes whose ERPNext Links are managed as Custom Fields (not in JSON).
# All ITM-* DocTypes that previously linked to Customer/Item/Supplier.
MANAGED_ERPNEXT_CUSTOM_FIELDS = {
	"ITM Host Item": {
		"customer": {
			"label": "Customer",
			"options": "Customer",
			"insert_after": "customer_section",
		},
		"item_code": {
			"label": "Item",
			"options": "Item",
			"insert_after": "item_section",
		},
	},
	"ITM Location Room": {
		"customer": {
			"label": "Customer",
			"options": "Customer",
			"insert_after": "itm_location",
			"hidden": 1,
		},
	},
	"ITM Solution": {
		"customer": {
			"label": "Customer",
			"options": "Customer",
			"insert_after": "column_break_3",
			"in_list_view": 1,
			"in_standard_filter": 1,
		},
		"supplier": {
			"label": "Supplier",
			"options": "Supplier",
			"insert_after": "itm_location",
		},
	},
	"ITM Solution Table": {
		"customer": {
			"label": "Customer",
			"options": "Customer",
			"insert_after": "status",
			"hidden": 1,
		},
	},
	"ITM Trip": {
		"customer": {
			"label": "Customer",
			"options": "Customer",
			"insert_after": "employee_name",
			"reqd": 1,
			"in_list_view": 1,
		},
	},
	"ITM User Account": {
		"customer": {
			"label": "Customer",
			"options": "Customer",
			"insert_after": "general_section",
			"in_standard_filter": 1,
			"allow_in_quick_entry": 1,
		},
	},
	"ITM User Account Type": {
		"customer": {
			"label": "Customer",
			"options": "Customer",
			"insert_after": "title",
			"hidden": 1,
		},
	},
	"ITM User Group": {
		"customer": {
			"label": "Customer",
			"options": "Customer",
			"insert_after": "general_section",
		},
	},
	"ITM User Group Table": {
		"customer": {
			"label": "Customer",
			"options": "Customer",
			"insert_after": "itm_user_group",
			"hidden": 1,
		},
	},
}

# Extra Custom Field attributes copied from the former standard DocFields.
_CF_SPEC_ATTRS = (
	"hidden",
	"reqd",
	"in_list_view",
	"in_standard_filter",
	"bold",
	"read_only",
	"allow_in_quick_entry",
)

ERPNEXT_CF_MODULE = "IT Management"


def use_erpnext_link_fields():
	"""True when ERPNext is installed and the settings toggle is enabled."""
	if not is_erpnext_installed():
		return False
	try:
		settings = frappe.get_single("IT Management Settings")
		return bool(settings.use_erpnext_links) if settings else False
	except Exception:
		return False


def get_field_metadata(doctype, fieldname):
	"""Get field metadata from doctype."""
	try:
		meta = frappe.get_meta(doctype)
		return meta.get_field(fieldname)
	except Exception:
		return None


def get_custom_field(doctype, fieldname):
	"""Return Custom Field doc for dt/fieldname, or None."""
	name = frappe.db.get_value(
		"Custom Field", {"dt": doctype, "fieldname": fieldname}, "name"
	)
	if not name:
		return None
	return frappe.get_doc("Custom Field", name)


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
	meta = frappe.get_meta(doctype, cached=False)
	if meta.has_field(fieldname):
		return False

	if get_custom_field(doctype, fieldname):
		return False

	custom_field = frappe.new_doc("Custom Field")
	custom_field.dt = doctype
	custom_field.fieldname = fieldname
	custom_field.fieldtype = fieldtype
	custom_field.label = label or fieldname
	custom_field.module = kwargs.pop("module", ERPNEXT_CF_MODULE)

	if options:
		custom_field.options = options

	for key, value in kwargs.items():
		if hasattr(custom_field, key):
			setattr(custom_field, key, value)

	custom_field.insert(ignore_permissions=True)
	frappe.clear_cache(doctype=doctype)
	return True


def remove_custom_field(doctype, fieldname):
	"""Remove a custom field if it exists (never touches standard fields)."""
	custom_field = get_custom_field(doctype, fieldname)
	if not custom_field:
		return False

	frappe.delete_doc("Custom Field", custom_field.name, force=1, ignore_permissions=True)
	frappe.clear_cache(doctype=doctype)
	return True


def _table_name(doctype):
	return "tab{0}".format(doctype)


def _nonempty_value_count(doctype, fieldname):
	"""Count rows with a non-empty value in the column (0 if column missing)."""
	if not frappe.db.has_column(doctype, fieldname):
		return 0
	table = _table_name(doctype)
	return frappe.db.sql(
		"SELECT COUNT(*) FROM `{0}` WHERE IFNULL(`{1}`, '') != ''".format(table, fieldname)
	)[0][0]


def _remove_standard_docfield(doctype, fieldname):
	"""Remove a standard DocField from the DocType (runs under in_patch)."""
	if not frappe.db.exists("DocType", doctype):
		return False

	doc = frappe.get_doc("DocType", doctype)
	removed = False
	for df in list(doc.fields):
		if df.fieldname == fieldname:
			doc.remove(df)
			removed = True

	if isinstance(doc.field_order, list) and fieldname in doc.field_order:
		doc.field_order = [f for f in doc.field_order if f != fieldname]
		removed = True
	elif isinstance(doc.field_order, str) and fieldname in doc.field_order:
		# Older sites may store field_order as text
		order = [f.strip() for f in doc.field_order.split(",") if f.strip()]
		if fieldname in order:
			doc.field_order = [f for f in order if f != fieldname]
			removed = True

	if not removed:
		return False

	doc.flags.ignore_validate = True
	doc.save(ignore_permissions=True)
	frappe.clear_cache(doctype=doctype)
	return True


def _is_standard_docfield(doctype, fieldname):
	"""True if fieldname is defined on the DocType document (not only Custom Field)."""
	return bool(
		frappe.db.exists("DocField", {"parent": doctype, "fieldname": fieldname})
	)


def migrate_standard_erpnext_link_field(doctype, fieldname, label=None, cf_attrs=None):
	"""
	Data-safe removal of a standard ERPNext Link field before model sync.

	- If the column has values: preserve them as a Data Custom Field (same name).
	- If empty: drop the standard DocField only.
	"""
	if not frappe.db.exists("DocType", doctype):
		return "skipped-missing-doctype"

	_delete_erpnext_link_property_setters(doctype, fieldname)

	custom = get_custom_field(doctype, fieldname)
	standard = _is_standard_docfield(doctype, fieldname)

	if not standard:
		# Already migrated / never present as standard field
		if custom:
			return "already-custom"
		return "absent"

	label = label or fieldname.replace("_", " ").title()
	cf_attrs = cf_attrs or {}
	table = _table_name(doctype)
	tmp_col = "_{0}_mig".format(fieldname)
	value_count = _nonempty_value_count(doctype, fieldname)

	if value_count:
		# Move valued column aside so DocType save / later sync cannot drop data
		if frappe.db.has_column(doctype, tmp_col):
			frappe.db.sql_ddl("ALTER TABLE `{0}` DROP COLUMN `{1}`".format(table, tmp_col))

		frappe.db.sql_ddl(
			"ALTER TABLE `{0}` CHANGE `{1}` `{2}` varchar(140)".format(
				table, fieldname, tmp_col
			)
		)

		_remove_standard_docfield(doctype, fieldname)

		# Custom Field insert recreates `fieldname` column
		if get_custom_field(doctype, fieldname):
			remove_custom_field(doctype, fieldname)

		cf_kwargs = {"module": ERPNEXT_CF_MODULE}
		for key in _CF_SPEC_ATTRS:
			if key in cf_attrs and cf_attrs[key] is not None:
				cf_kwargs[key] = cf_attrs[key]

		create_custom_field(
			doctype,
			fieldname,
			"Data",
			label=label,
			**cf_kwargs
		)

		if frappe.db.has_column(doctype, fieldname) and frappe.db.has_column(doctype, tmp_col):
			frappe.db.sql(
				"UPDATE `{0}` SET `{1}` = `{2}`".format(table, fieldname, tmp_col)
			)
			frappe.db.sql_ddl("ALTER TABLE `{0}` DROP COLUMN `{1}`".format(table, tmp_col))

		return "preserved-as-data"

	# Empty column: safe to remove standard field (sync would drop it anyway)
	_remove_standard_docfield(doctype, fieldname)
	return "removed-empty"


def _spec_field_attrs(spec):
	"""Return Custom Field attribute kwargs from a managed-field spec."""
	attrs = {}
	for key in _CF_SPEC_ATTRS:
		if key in spec and spec[key] is not None:
			attrs[key] = spec[key]
	return attrs


def ensure_erpnext_link_custom_field(doctype, fieldname, spec):
	"""Ensure a Link Custom Field exists (upgrade Data → Link when enabling)."""
	options = spec.get("options")
	label = spec.get("label") or fieldname
	insert_after = spec.get("insert_after")
	extra = _spec_field_attrs(spec)

	custom = get_custom_field(doctype, fieldname)
	if custom:
		changed = False
		if custom.fieldtype != "Link":
			custom.fieldtype = "Link"
			changed = True
		if custom.options != options:
			custom.options = options
			changed = True
		if label and custom.label != label:
			custom.label = label
			changed = True
		if insert_after and custom.insert_after != insert_after:
			custom.insert_after = insert_after
			changed = True
		for key, value in extra.items():
			if custom.get(key) != value:
				custom.set(key, value)
				changed = True
		if changed:
			custom.save(ignore_permissions=True)
			frappe.clear_cache(doctype=doctype)
			return "upgraded-to-link"
		return "exists"

	if _is_standard_docfield(doctype, fieldname):
		# Should have been migrated already; do not create a conflicting CF
		return "blocked-by-standard"

	kwargs = {"module": ERPNEXT_CF_MODULE}
	if insert_after:
		kwargs["insert_after"] = insert_after
	kwargs.update(extra)

	created = create_custom_field(
		doctype,
		fieldname,
		"Link",
		options=options,
		label=label,
		**kwargs
	)
	return "created" if created else "skipped"


def retire_erpnext_link_custom_field(doctype, fieldname):
	"""
	When disabling ERPNext links:
	- valued Link/Data Custom Field → keep as Data
	- empty Custom Field → delete
	"""
	custom = get_custom_field(doctype, fieldname)
	if not custom:
		return "absent"

	value_count = _nonempty_value_count(doctype, fieldname)
	if value_count:
		if custom.fieldtype != "Data" or custom.options:
			custom.fieldtype = "Data"
			custom.options = ""
			custom.save(ignore_permissions=True)
			frappe.clear_cache(doctype=doctype)
			return "converted-to-data"
		return "kept-as-data"

	remove_custom_field(doctype, fieldname)
	return "deleted-empty"


def sync_erpnext_custom_fields(doctypes=None):
	"""
	Create / upgrade / retire managed ERPNext Custom Fields from settings.

	Args:
		doctypes: optional iterable of DocType names; default all managed ones.
	"""
	managed = MANAGED_ERPNEXT_CUSTOM_FIELDS
	if doctypes is not None:
		managed = {dt: managed[dt] for dt in doctypes if dt in managed}

	enabled = use_erpnext_link_fields()
	results = []

	for doctype, fields in managed.items():
		if not frappe.db.exists("DocType", doctype):
			continue
		for fieldname, spec in fields.items():
			try:
				if enabled:
					action = ensure_erpnext_link_custom_field(doctype, fieldname, spec)
				else:
					action = retire_erpnext_link_custom_field(doctype, fieldname)
				results.append("{0}.{1}: {2}".format(doctype, fieldname, action))
			except Exception:
				frappe.log_error(
					title="ERPNext custom field sync failed for {0}.{1}".format(
						doctype, fieldname
					)
				)
				results.append("{0}.{1}: error".format(doctype, fieldname))

	return results


def migrate_managed_erpnext_standard_fields(doctypes=None):
	"""Run data-safe standard-field migration for managed DocTypes."""
	managed = MANAGED_ERPNEXT_CUSTOM_FIELDS
	if doctypes is not None:
		managed = {dt: managed[dt] for dt in doctypes if dt in managed}

	results = []
	for doctype, fields in managed.items():
		for fieldname, spec in fields.items():
			try:
				action = migrate_standard_erpnext_link_field(
					doctype,
					fieldname,
					label=spec.get("label"),
					cf_attrs=_spec_field_attrs(spec),
				)
				results.append("{0}.{1}: {2}".format(doctype, fieldname, action))
			except Exception:
				frappe.log_error(
					title="ERPNext standard field migration failed for {0}.{1}".format(
						doctype, fieldname
					)
				)
				results.append("{0}.{1}: error".format(doctype, fieldname))
	return results


# ---------------------------------------------------------------------------
# Legacy Property Setter neutralization for DocTypes not yet on Custom Fields
# ---------------------------------------------------------------------------

ERPNEXT_LINK_PS_MODULE = "IT Management"
NEUTRALIZED_LINK_OPTIONS = "[Select]"
NEUTRALIZED_DEPENDS_ON = "eval:False"
_ERPNEXT_LINK_PS_PROPERTIES = ("options", "depends_on")


def _iter_erpnext_link_fields():
	"""Yield (doctype, fieldname) pairs still managed via Property Setters."""
	mapping = get_erpnext_doctype_fields_mapping()
	managed = MANAGED_ERPNEXT_CUSTOM_FIELDS
	for doctype, config in mapping.items():
		for fieldname in config.get("erpnext_fields", []):
			if doctype in managed and fieldname in managed[doctype]:
				continue
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
	"""Neutralize invalid ERPNext Link targets for non-migrated DocTypes."""
	if not frappe.db.exists("DocType", doctype):
		return False

	meta = frappe.get_meta(doctype)
	field = meta.get_field(fieldname)
	if not field or field.fieldtype != "Link":
		return False

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
	Property Setter neutralization for DocTypes not yet on Custom Fields.

	Managed DocTypes (ITM Host Item) are skipped — use sync_erpnext_custom_fields.
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
