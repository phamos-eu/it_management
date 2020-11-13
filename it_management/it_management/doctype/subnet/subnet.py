
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

import re

def validateIP(ipstr,fieldname):
	fieldname = fieldname.title()
	


class Subnet(Document):
	def before_save(self):
		#Validate Subnet
		if self.subnet:
			match = re.match(r'(\d{0,3}\.){3}\d{0,3}\/\d\d$',self.subnet)
			if not match:
				fex = frappe.exceptions.ValidationError("Subnet does not conform to CIDR (e.g. 192.168.1.0/24")
				frappe.throw(title='Validation',msg='Subnet does not conform to CIDR (e.g. 192.168.1.0/24',exc=fex)

        #Validate WAN Address
		if self.wan_address:
			match = re.match(r'(\d{0,3}\.){3}\d{0,3}$',self.wan_address)
			if not match:
				msg = "IP Address of field '{fieldname}' does not conform to IP-Notation (e.g. 192.168.1.0)".format(fieldname="WAN Address")
				fex = frappe.exceptions.ValidationError(msg)
				frappe.throw(title='Validation',msg=msg,exc=fex)

	pass