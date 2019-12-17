from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        'fieldname': 'location',
        'non_standard_fieldnames': {
            #'IT Ticket': 'dynamic_name'
			'Issue': 'dynamic_name'
        },
        'transactions': [
            {
                'label': _('Rooms'),
                'items': ['Location Room']
            },
            {
                'label': _('Service'),
                'items': ['Issue']#IT Ticket']
            }
        ]
    }
