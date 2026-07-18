# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class ITMHostItem(Document):
	def onload(self):
		"""Hide ITM link fields while ERPNext Link Custom Fields are active."""
		from it_management.it_management.utils.erpnext_integration import (
			use_erpnext_link_fields,
			get_erpnext_doctype_fields_mapping,
		)

		show_erpnext_fields = use_erpnext_link_fields()
		itm_fields = (
			get_erpnext_doctype_fields_mapping()
			.get("ITM Host Item", {})
			.get("itm_fields", [])
		)

		if not (hasattr(self, "meta") and hasattr(self.meta, "get_field")):
			return

		for fieldname in itm_fields:
			field = self.meta.get_field(fieldname)
			if field:
				field.depends_on = "eval:False" if show_erpnext_fields else ""

	def validate(self):
		"""Validate ERPNext link targets when those Custom Fields are in use."""
		from it_management.it_management.utils.erpnext_integration import (
			use_erpnext_link_fields,
			get_erpnext_doctype_fields_mapping,
		)

		if use_erpnext_link_fields():
			erpnext_fields = (
				get_erpnext_doctype_fields_mapping()
				.get("ITM Host Item", {})
				.get("erpnext_fields", [])
			)
			for fieldname in erpnext_fields:
				value = self.get(fieldname)
				if not value:
					continue
				field_meta = self.meta.get_field(fieldname)
				if not (field_meta and field_meta.fieldtype == "Link" and field_meta.options):
					continue
				try:
					frappe.get_meta(field_meta.options)
				except frappe.DoesNotExistError:
					frappe.throw(
						_(
							"The doctype '{0}' does not exist. Please install ERPNext or disable "
							"'Use ERPNext Link Fields' in IT Management Settings."
						).format(field_meta.options),
						title=_("Missing Doctype"),
					)

		self._validate_deployment_hosting()

		if self.get("itm_host_item_solution_table"):
			solutions = [
				row.itm_solution
				for row in self.itm_host_item_solution_table
				if row.itm_solution
			]
			if len(solutions) != len(set(solutions)):
				frappe.throw(
					_("A solution can only be linked once to a host item"),
					title=_("Duplicate Solution"),
				)

	def _validate_deployment_hosting(self):
		"""Physical hosts clear hosting links; Virtual hosts require a Software Instance."""
		if not self.deployment:
			self.deployment = "Physical"

		if self.deployment == "Physical":
			self.hosted_by_software_instance = None
			self.hosted_on = None
			return

		if self.deployment != "Virtual":
			return

		if not self.hosted_by_software_instance:
			frappe.throw(
				_("Virtual hosts must be linked to a hosting Software Instance."),
				title=_("Missing Hosting Software Instance"),
			)

		# Keep hosted_on in sync even if fetch_from did not run (e.g. API/import)
		parent_host = frappe.db.get_value(
			"ITM Software Instance",
			self.hosted_by_software_instance,
			"itm_host_item",
		)
		self.hosted_on = parent_host

		if self.hosted_on and self.hosted_on == self.name:
			frappe.throw(
				_("A host item cannot be hosted on itself."),
				title=_("Invalid Hosting"),
			)
