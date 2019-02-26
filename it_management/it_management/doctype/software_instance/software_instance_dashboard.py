from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'licence',
		'transactions': [
			{
				'label': _('Users and Accounts'),
				'items': ['User Account']
			}
		]
	}
