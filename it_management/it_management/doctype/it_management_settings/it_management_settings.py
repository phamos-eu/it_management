# -*- coding: utf-8 -*-
# Copyright (c) 2020, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _


class ITManagementSettings(Document):
	def validate(self):
		"""Validate settings before saving."""
		if self.use_erpnext_links:
			from it_management.it_management.utils.erpnext_integration import is_erpnext_installed

			if not is_erpnext_installed():
				frappe.throw(
					_("ERPNext is not installed. Please install ERPNext to use ERPNext link fields."),
					title=_("ERPNext Required"),
				)

	def on_update(self):
		"""Create/retire ERPNext Custom Fields and neutralize remaining Links."""
		from it_management.it_management.utils.erpnext_integration import (
			sync_erpnext_custom_fields,
			sync_erpnext_link_fields,
		)

		# Managed DocTypes (ITM Host Item): Custom Fields driven by this toggle
		sync_erpnext_custom_fields()
		# Other DocTypes still shipping standard Links: Property Setter safety net
		sync_erpnext_link_fields()
