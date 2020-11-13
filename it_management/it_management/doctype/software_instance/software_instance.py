# -*- coding: utf-8 -*-
# Copyright (c) 2019, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import re

class SoftwareInstance(Document):
	def before_save(self):

		#Fetch IT Landscape
		if self.customer and not self.it_landscape:
			customer = frappe.get_doc("Customer",self.customer)
			self.it_landscape = customer.it_landscape

	pass
