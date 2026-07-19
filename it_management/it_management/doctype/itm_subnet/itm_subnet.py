# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ITMSubnet(Document):
	def validate(self):
		self._sync_from_lan()

	def _sync_from_lan(self):
		"""Landscape (and empty location) always follow the selected LAN."""
		if not self.itm_local_area_network:
			return

		lan = frappe.db.get_value(
			"ITM Local Area Network",
			self.itm_local_area_network,
			["itm_landscape", "itm_location"],
			as_dict=True,
		)
		if not lan:
			frappe.throw(
				_("Local Area Network {0} was not found.").format(self.itm_local_area_network),
				title=_("Invalid LAN"),
			)

		self.itm_landscape = lan.itm_landscape
		if not self.itm_location and lan.itm_location:
			self.itm_location = lan.itm_location
