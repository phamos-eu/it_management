from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'heatmap': True,
		'heatmap_message': _('Activity based on ?'),
		'fieldname': 'configuration_item',
		'transactions': [
			{
				'label': _('Location'),
				'items': ['Location Room', 'Location Address']
			},
      {
				'label': _('Network'),
				'items': ['IP Address', 'Host Domain']
			},
      {
				'label': _('Software'),
				'items': ['Licence', 'Software Version']
			},
      {
				'label': _('Hardware'),
				'items': ['Manufacturer', 'Item']
			},
		]
	}
