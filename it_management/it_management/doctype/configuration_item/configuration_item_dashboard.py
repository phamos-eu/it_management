from __future__ import unicode_literals
from frappe import _


def get_data():
    return {
        'fieldname': 'configuration_item',
        'non_standard_fieldnames': {
            #'IT Ticket': 'dynamic_name',
            #'User Account': 'dynamic_name',
            'Issue': 'dynamic_name',
            #'Project': 'dynamic_name',
            'Task': 'dynamic_name',
			'IT Backup': 'source_item'
        },
        'dynamic_links': {
            
        },
        'transactions': [
            {
                'label': _('Software'),
                'items': ['Software Instance', 'User Account']
            },
            {
                'label': _('Support'),
                'items': ['Issue','IT Backup','Maintenance Schedule']
            },
            {
                'label': _('Project'),
                'items': [
                    #'Project', 
                    'Task']
            }
        ]
    }
