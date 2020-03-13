from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        'fieldname': 'user_account',
        'non_standard_fieldnames': {
			'Issue': 'dynamic_name'
        },
        'transactions': [
            {
                'label': _('Used in'),
                'items': ['Solution', 'User Account', 'User Group', 'Licence']
            },
            {
                'label': _('Service'),
                'items': ['Issue', 'Task']
            }
        ]
    }
