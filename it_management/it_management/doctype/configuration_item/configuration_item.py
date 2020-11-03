# -*- coding: utf-8 -*-
# Copyright (c) 2019, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ConfigurationItem(Document):
	def save(self, *args, **kwargs):
		if self.status == 'Obsolet':
			sis = frappe.db.get_all('Software Instance',filters={'configuration_item':self.name}, fields=['name'],page_length=10000,as_list=False)
			for si in sis:
				frappe.db.set_value('Software Instance',si["name"],{
					'status':'Obsolet'
				})

		super().save(*args, **kwargs)
	pass
