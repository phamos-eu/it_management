# Copyright (c) 2025, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ITMSolution(Document):
	def validate(self):
		from it_management.it_management.utils.status import compute_solution_health

		if not self.lifecycle_status:
			self.lifecycle_status = "Implementing"

		# Health is derived from linked Running Host Items
		solution_name = self.name or self.get("name1")
		self.health_status = compute_solution_health(solution_name)
