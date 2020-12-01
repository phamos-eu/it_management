from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        'heatmap': True,
		'heatmap_message': _('This is based on all the below Doctypes'),
        'fieldname': 'it_landscape',
        'non_standard_fieldnames': {
        },
        'transactions': [
            {
                'label': _('Configuration Management'),
                'items': [
                    'Configuration Item',
                    'Solution',
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
                    'IT Checklist'
                ]
            },
            {
                'label': _('Projects'),
                'items': [
                    'Project',
                    'Task'
                ]
            }
        ]
    }