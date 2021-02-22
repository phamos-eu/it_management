from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        'fieldname': 'host_domain',
        'non_standard_fieldnames': {
            'Configuration Item': 'domain_name',
			'Issue': 'dynamic_name'
        },
        'transactions': [
            {
                'label': _('Configuration Items'),
                'items': ['Configuration Item']
            },
            {
                'label': _('Service'),
                'items': ['Issue']
            }
        ]
    }
