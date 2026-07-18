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

		if not self.lifecycle_status:
			self.lifecycle_status = "Implementing"
		if not self.health_status:
			self.health_status = "Unknown"

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

	def on_update(self):
		from it_management.it_management.utils.status import (
			cascade_host_lifecycle_to_software_instances,
			solutions_linked_to_host,
			update_solution_health,
		)

		if self.has_value_changed("lifecycle_status"):
			cascade_host_lifecycle_to_software_instances(self.name, self.lifecycle_status)

		before = self.get_doc_before_save()
		before_solutions = {
			row.itm_solution
			for row in (before.get("itm_host_item_solution_table") if before else []) or []
			if row.itm_solution
		}
		after_solutions = {
			row.itm_solution
			for row in self.get("itm_host_item_solution_table") or []
			if row.itm_solution
		}
		membership_changed = before_solutions != after_solutions

		if (
			self.has_value_changed("lifecycle_status")
			or self.has_value_changed("health_status")
			or membership_changed
		):
			for solution in solutions_linked_to_host(self):
				update_solution_health(solution)

	def after_insert(self):
		from it_management.it_management.utils.status import (
			solutions_linked_to_host,
			update_solution_health,
		)

		for solution in solutions_linked_to_host(self):
			update_solution_health(solution)
