# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ITMSoftwareInstance(Document):
	def validate(self):
		if not self.lifecycle_status:
			self.lifecycle_status = "Implementing"
		if not self.health_status:
			self.health_status = "Unknown"
