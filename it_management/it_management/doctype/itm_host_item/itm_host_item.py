# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class ITMHostItem(Document):
	def onload(self):
		"""Dynamically show/hide ERPNext vs ITM fields based on settings and ERPNext availability."""
		from it_management.it_management.utils.erpnext_integration import (
			is_erpnext_installed,
			get_erpnext_doctype_fields_mapping
		)
		
		# Get settings
		try:
			settings = frappe.get_single("IT Management Settings")
			use_erpnext = settings.use_erpnext_links if settings else True
		except Exception:
			use_erpnext = True
		
		# Check if ERPNext is installed
		erpnext_installed = is_erpnext_installed()
		
		# Determine if ERPNext fields should be shown
		show_erpnext_fields = erpnext_installed and use_erpnext
		
		# Get field mapping for this doctype
		mapping = get_erpnext_doctype_fields_mapping()
		config = mapping.get("ITM Host Item", {})
		erpnext_fields = config.get("erpnext_fields", [])
		itm_fields = config.get("itm_fields", [])
		
		# Update depends_on for ERPNext fields
		if hasattr(self, 'meta') and hasattr(self.meta, 'get_field'):
			for fieldname in erpnext_fields:
				field = self.meta.get_field(fieldname)
				if field:
					# Check if target doctype exists
					if field.fieldtype == "Link":
						try:
							frappe.get_meta(field.options)
							target_exists = True
						except Exception:
							target_exists = False
					
					if target_exists and show_erpnext_fields:
						field.depends_on = ""
					else:
						field.depends_on = "eval:False"
				
			# Update depends_on for ITM fields
			for fieldname in itm_fields:
				field = self.meta.get_field(fieldname)
				if field:
					if show_erpnext_fields:
						field.depends_on = "eval:False"
					else:
						field.depends_on = ""
	
	def validate(self):
		"""Validate the document."""
		from it_management.it_management.utils.erpnext_integration import (
			is_erpnext_installed,
			get_erpnext_doctype_fields_mapping
		)
		
		# Get settings
		try:
			settings = frappe.get_single("IT Management Settings")
			use_erpnext = settings.use_erpnext_links if settings else True
		except Exception:
			use_erpnext = True
		
		# Check if ERPNext is installed
		erpnext_installed = is_erpnext_installed()
		show_erpnext_fields = erpnext_installed and use_erpnext
		
		# Get field mapping
		mapping = get_erpnext_doctype_fields_mapping()
		config = mapping.get("ITM Host Item", {})
		erpnext_fields = config.get("erpnext_fields", [])
		
		# If ERPNext fields are shown, validate that the linked doctypes exist
		if show_erpnext_fields:
			for fieldname in erpnext_fields:
				if hasattr(self, fieldname):
					value = getattr(self, fieldname)
					if value:
						# Check if the target doctype exists
						field_meta = self.meta.get_field(fieldname)
						if field_meta and field_meta.fieldtype == "Link":
							target_doctype = field_meta.options
							try:
								frappe.get_meta(target_doctype)
							except frappe.DoesNotExistError:
								frappe.throw(
									_("The doctype '{0}' does not exist. Please install ERPNext or disable 'Use ERPNext Link Fields' in IT Management Settings.").format(target_doctype),
									title=_("Missing Doctype")
								)
