# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ITMHostItem(Document):
	def onload(self):
		"""Dynamically show/hide ERPNext vs ITM fields based on settings"""
		settings = frappe.get_single("IT Management Settings")
		use_erpnext = settings.use_erpnext_links if settings else True
		
		# Set depends_on to control visibility
		if use_erpnext:
			# Show ERPNext fields, hide ITM fields
			if hasattr(self, 'meta'):
				if hasattr(self.meta, 'get_field'):
					customer_field = self.meta.get_field('customer')
					if customer_field:
						customer_field.depends_on = ""
					itm_customer_field = self.meta.get_field('itm_customer')
					if itm_customer_field:
						itm_customer_field.depends_on = "eval:False"
					
					item_field = self.meta.get_field('item_code')
					if item_field:
						item_field.depends_on = ""
					itm_item_field = self.meta.get_field('itm_item')
					if itm_item_field:
						itm_item_field.depends_on = "eval:False"
		else:
			# Show ITM fields, hide ERPNext fields
			if hasattr(self, 'meta'):
				if hasattr(self.meta, 'get_field'):
					customer_field = self.meta.get_field('customer')
					if customer_field:
						customer_field.depends_on = "eval:False"
					itm_customer_field = self.meta.get_field('itm_customer')
					if itm_customer_field:
						itm_customer_field.depends_on = ""
					
					item_field = self.meta.get_field('item_code')
					if item_field:
						item_field.depends_on = "eval:False"
					itm_item_field = self.meta.get_field('itm_item')
					if itm_item_field:
						itm_item_field.depends_on = ""
