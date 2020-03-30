from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        'fieldname': 'subnet',
        'non_standard_fieldnames': {
		'Issue': 'dynamic_name'
        },
        'transactions': [
	{
                'label': _('Networking'),
                'items': ['Local Area Network', 'Network Interface Controller']
        },
            {
                'label': _('Service'),
                'items': ['Issue']
            }
        ]
    }
