from __future__ import unicode_literals
from frappe import _

#This has been created from
# https://github.com/frappe/frappe/pull/8336

# the `data` argument is generated first at the doctype-level,
# and passed along to the next app to be modified
def get_dashboard_data(data):
    return {
        'fieldname': 'event',
        'non_standard_fieldnames': {
        },
        'transactions': [
            {
                'label': _('Activities'),
                'items': ['Trip']
            }
        ]
    }