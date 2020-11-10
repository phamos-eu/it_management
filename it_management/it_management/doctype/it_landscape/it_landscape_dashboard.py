from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        'fieldname': 'it_landscape',
        'non_standard_fieldnames': {
        },
        'transactions': [
            {
                'label': _('Configuration Management'),
                'items': [
                    'Configuration Item',
                    'Solution',
                    'Socket',
                    'IT Hardware',
                    'IT Backup'
                ]
            },
            {
                'label': _('Software'),
                'items': [
                    'Licence',
                    'Software Instance',
                    'User Account',
                    'User Group'
                ]
            },
            {
                'label': _('Locations'),
                'items': [
                    'Location',
                    'Address',
                    'Location Room'
                ]
            },
            {
                'label': _('Network'),
                'items': [
                    'Host Domain',
                    'Subnet'
                ]
            },
            {
                'label': _('Service'),
                'items': [
                    'Issue',
                    'Maintenance Visit',
                    'IT Checklist',
                    'IT Service Report'
                ]
            }
        ]
    }