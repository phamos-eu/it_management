from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        'fieldname': 'software_instance',
        'non_standard_fieldnames': {
		'Issue': 'dynamic_name'
		'Task': 'dynamic_name'
        },
        'transactions': [
            {
                'label': _('Users and Accounts'),
                'items': ['User Account']
            },
            {
                'label': _('Service'),
                'items': ['Issue', 'Task']
            }
        ]
    }
