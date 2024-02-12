# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.utils import cstr, today,date_diff, nowdate

class ITMSoftware(Document):

	def validate(self):
		self.toggle_eof()
	
	def toggle_eof(self):
		
		if(self.end_of_life):
			ddfr = date_diff(self.end_of_life, nowdate())
			#print(ddfr)
			if ddfr <= 0:
				self.disabled = True
				self.status = "Outdated"
			else:
				self.disabled = False
				self.status = "Active"