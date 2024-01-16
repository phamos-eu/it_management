from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        'fieldname': 'configuration_item',
        'non_standard_fieldnames': {
            #'User Account': 'dynamic_name',
            'Issue': 'dynamic_name',
            #'Project': 'dynamic_name',
            'Task': 'dynamic_name',
			'IT Backup': 'source_item'
        },
        'transactions': [
            {
                'label': _('Software'),
                'items': ['Software Instance', 'User Account']
            },
            {
                'label': _('Support'),
                'items': ['Configuration Item','Issue','IT Backup']
            },
            {
                'label': _('Project'),
                'items': [
                    #'Project', 
                    'Task']
            }
        ]
    }
