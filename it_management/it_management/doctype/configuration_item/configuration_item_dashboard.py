from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'configuration_item',
		'transactions': [
			{
				'label': _('Support History'),
				'items': ['Task']
			},
			{
				'label': _('Software'),
				'items': ['Software Instance', 'User Account', 'Solution']
			},
		]
	}
