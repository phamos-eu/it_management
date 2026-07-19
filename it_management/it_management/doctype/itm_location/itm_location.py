# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils.nestedset import NestedSet

# Child type → required parent type
PARENT_TYPE = {
	"Building": "Site",
	"Floor": "Building",
	"Room": "Floor",
}

GROUP_TYPES = frozenset(("Site", "Building", "Floor"))


class ITMLocation(NestedSet):
	nsm_parent_field = "parent_itm_location"

	def validate(self):
		self._normalize_location_type()
		self._apply_group_flag()
		self._validate_hierarchy()
		self._apply_address_rules()
		self._apply_landscape_rules()

	def on_update(self):
		super().on_update()
		self._cascade_landscape_to_descendants()

	def _normalize_location_type(self):
		if not self.location_type:
			self.location_type = "Site"

	def _apply_group_flag(self):
		# Site / Building / Floor are groups; Room is a leaf
		self.is_group = 1 if self.location_type in GROUP_TYPES else 0

	def _validate_hierarchy(self):
		if self.location_type == "Site":
			if self.parent_itm_location:
				frappe.throw(
					_("A Site cannot have a parent location."),
					title=_("Invalid Hierarchy"),
				)
			return

		expected_parent_type = PARENT_TYPE.get(self.location_type)
		if not self.parent_itm_location:
			frappe.throw(
				_("{0} must have a parent {1}.").format(
					_(self.location_type), _(expected_parent_type)
				),
				title=_("Missing Parent Location"),
			)

		if self.parent_itm_location == self.name:
			frappe.throw(
				_("A location cannot be its own parent."),
				title=_("Invalid Hierarchy"),
			)

		parent_type = frappe.db.get_value(
			"ITM Location", self.parent_itm_location, "location_type"
		)
		if parent_type != expected_parent_type:
			frappe.throw(
				_("{0} must be placed under a {1} (got {2}).").format(
					_(self.location_type),
					_(expected_parent_type),
					_(parent_type or _("none")),
				),
				title=_("Invalid Hierarchy"),
			)

	def _apply_address_rules(self):
		# Address only on Site and Building
		if self.location_type not in ("Site", "Building"):
			self.itm_location_address = None

	def _apply_landscape_rules(self):
		"""Landscape is editable on Site only; children inherit from parent."""
		if self.location_type == "Site":
			return

		parent_landscape = frappe.db.get_value(
			"ITM Location", self.parent_itm_location, "itm_landscape"
		)
		self.itm_landscape = parent_landscape

	def _cascade_landscape_to_descendants(self):
		"""When a Site landscape changes, push it down the whole subtree."""
		if self.location_type != "Site":
			return

		if not self.has_value_changed("itm_landscape"):
			return

		if self.lft is None or self.rgt is None:
			return

		frappe.db.sql(
			"""
			UPDATE `tabITM Location`
			SET `itm_landscape` = %s
			WHERE `lft` > %s AND `rgt` < %s
			""",
			(self.itm_landscape, self.lft, self.rgt),
		)
