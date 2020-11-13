
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

import re

class Subnet(Document):
	def before_save(self):
		#Validate Subnet
		if self.subnet:
			match = re.match(r'(\d{0,3}\.){3}\d{0,3}\/\d\d$',self.subnet)
			if not match:
				fex = frappe.exceptions.ValidationError("Subnet does not conform to CIDR (e.g. 192.168.1.0/24")
				frappe.throw(title='Validation',msg='Subnet does not conform to CIDR (e.g. 192.168.1.0/24',exc=fex)

	pass