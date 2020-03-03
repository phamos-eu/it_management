from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        'fieldname': 'it_software',
        'non_standard_fieldnames': {
            #'IT Ticket': 'dynamic_name'
			'Issue': 'dynamic_name',
			'Software Instance': 'software',
			'Licence': 'software',
			'IT Backup': 'software'
        },
        'transactions': [
            {
                'label': _('Software'),
                'items': ['Software Instance', 'Licence', 'IT Backup']
            },
        ]
    }
