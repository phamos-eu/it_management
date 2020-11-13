# -*- coding: utf-8 -*-
# Copyright (c) 2020, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
import frappe
import re

def validateIP(ipstr,fieldname):
	fieldname = fieldname.title()
	match = re.match(r'(\d{0,3}\.){3}\d{0,3}$',ipstr)
	if not match:
			msg = "IP Address of field '{fieldname}' does not conform to IP-Notation (e.g. 192.168.1.0)".format(fieldname=fieldname)
			fex = frappe.exceptions.ValidationError(msg)
			frappe.throw(title='Validation',msg=msg,exc=fex)

class NetworkInterfaceController(Document):
	def before_save(self):
		#Validate IPv4
		if self.ip_address:
			validateIP(self.ip_address,"IP Address")

		#Validate IPv6
		if self.ip_v6:
			match = re.match(r'([0-9A-Fa-f]{0,4}:){7}[0-9A-Fa-f]{0,4}$',self.ip_v6)
			if not match:
				msg = "IPv6 Address does not conform to IPv6 Notation (e.g. 2001:0db8:85a3:0000:0000:8a2e:0370:7334)"
				fex = frappe.exceptions.ValidationError(msg)
				frappe.throw(title='Validation',msg=msg,exc=fex)

		#Validate MAC
		if self.mac:
			match = re.match(r'([0-9A-Fa-f]{0,2}[:\-]){5}[0-9A-Fa-f]{0,4}$',self.mac)
			if not match:
				msg = "MAC Address does not conform to MAC Notation (e.g. a3:b6:4f:ff:ae:12)"
				fex = frappe.exceptions.ValidationError(msg)
				frappe.throw(title='Validation',msg=msg,exc=fex)

		#Transform MAC to default format with small letters and ':'
		self.mac = self.mac.replace("-",":").lower()

	pass