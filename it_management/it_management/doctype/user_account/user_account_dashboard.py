from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'user_account',
		'transactions': [
			{
				'label': _('Used in'),
				'items': ['Solution', 'User Account']
			},
		]
	}
