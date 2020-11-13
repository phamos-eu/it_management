from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        'fieldname': 'location',
        'non_standard_fieldnames': {
			'Issue': 'dynamic_name'
        },
        'transactions': [
            {
                'label': _('Rooms'),
                'items': ['Location Room']
            },
            {
                'label': _('Service'),
                'items': ['Issue']
            },
	    {
                'label': _('Networking'),
                'items': ['Subnet']
            }
        ]
    }
