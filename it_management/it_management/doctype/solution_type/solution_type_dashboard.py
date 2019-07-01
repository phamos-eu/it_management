from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        'fieldname': 'solution_type',
        'non_standard_fieldnames': {
            'Solution': 'type'
        },
        'transactions': [
            {
                'label': _('Solutions'),
                'items': ['Solution']
            }
        ]
    }
