"""
"""
from __future__ import unicode_literals
from frappe import _


def get_data():
    """
    """
    return {
        'fieldname': 'licence',
        'non_standard_fieldnames': {
			'Issue': 'dynamic_name'
        },
        'transactions': [
            {
                'label': _('Software'),
                'items': ['Software Instance']
            },
            {
                'label': _('Service'),
                'items': ['Issue']
            }
        ]
    }
