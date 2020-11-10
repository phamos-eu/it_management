from __future__ import unicode_literals
from frappe import _

#This has been created from
# https://github.com/frappe/frappe/pull/8336

# the `data` argument is generated first at the doctype-level,
# and passed along to the next app to be modified
def get_dashboard_data(data):
    return {
        'fieldname': 'contact_person',
        'non_standard_fieldnames': {
            'Issue':'contact',
            'User Account':'contact'

        },
        'transactions': [
            {
                'label': _('CRM'),
                'items': ['Opportunity']
            },
            {
                'label': _('Selling'),
                'items': ['Quotation', 'Sales Order', 'Sales Invoice']
            },
            {
                'label': _('Support'),
                'items': ['Maintenance Visit', 'Issue']
            },
            {
                'label': _('IT Management'),
                'items': ['User Account']
            }
        ]
    }