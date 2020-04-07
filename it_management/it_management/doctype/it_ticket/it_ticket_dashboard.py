from __future__ import unicode_literals
from frappe import _

def get_data():
    return {
        'fieldname': 'it_ticket',
        'transactions': [
            {
                'label': _('Transactions'),
                'items': ['Timesheet', 'Delivery Note', 'IT Service Report']
            }
        ]
    }

