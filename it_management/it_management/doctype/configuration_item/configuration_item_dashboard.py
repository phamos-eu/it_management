from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'configuration_item',
		'transactions': [
			{
				'label': _('Location'),
				'items': ['Location Room']
			},
      {
				'label': _('Network'),
				'items': ['IP Address', 'Host Domain']
			},
      {
				'label': _('Software'),
				'items': ['Software Instance']
			},
      {
				'label': _('Hardware'),
				'items': ['Manufacturer', 'Item']
			},
		]
	}
