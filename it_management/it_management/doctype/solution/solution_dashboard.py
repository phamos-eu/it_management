from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        'fieldname': 'solution',
        'non_standard_fieldnames': {
            'IT Ticket': 'dynamic_name'
        },
        'transactions': [
            {
                'label': _('Service'),
                'items': ['IT Ticket', 'Project', 'Task']
            },
            {
                'label': _('User Accounts and Groups'),
                'items': ['User Account', 'User Group']
            },
            {
                'label': _('Software Instances'),
                'items': ['Software Instance']
            },
            {
                'label': _('Configuration Items & Solutions'),
                'items': ['Configuration Item', 'Solution']
            },
        ]
    }
