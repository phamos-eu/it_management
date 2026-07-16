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
		# Validate ERPNext is installed when enabling ERPNext links
		if self.use_erpnext_links:
			from it_management.it_management.utils.erpnext_integration import is_erpnext_installed
			
			if not is_erpnext_installed():
				frappe.throw(
					_("ERPNext is not installed. Please install ERPNext to use ERPNext link fields."),
					title=_("ERPNext Required")
				)
