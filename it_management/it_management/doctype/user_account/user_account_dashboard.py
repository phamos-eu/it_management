from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        'fieldname': 'user_account',
        'non_standard_fieldnames': {
            'IT Ticket': 'dynamic_name'
        },
        'transactions': [
            {
                'label': _('Used in'),
                'items': ['Solution', 'User Account']
            },
            {
                'label': _('Service'),
                'items': ['IT Ticket']
            }
        ]
    }
