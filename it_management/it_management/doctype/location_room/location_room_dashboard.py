from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'location_room',
		'transactions': [
			{
				'label': _('Configuration Items'),
				'items': ['Configuration Item']
			},
		]
	}
