from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        'fieldname': 'configuration_item',
        'non_standard_fieldnames': {
            'IT Ticket': 'dynamic_name'
        },
        'transactions': [
            {
                'label': _('Software'),
                'items': ['Software Instance', 'User Account']
            },
            {
                'label': _('Service'),
                'items': ['IT Ticket', 'Task']
            }
        ]
    }
