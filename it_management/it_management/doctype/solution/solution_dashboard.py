from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'solution',
		'transactions': [
			{
				'label': _('Support & Projects'),
				'items': ['Project','Task']
			},
      {
				'label': _('User Accounts and Groups'),
				'items': ['User Account','User Group']
			},
      {
				'label': _('Software Instances'),
				'items': ['Software Instance']
			},
			{
				'label': _('Configuration Items & Solutions'),
				'items': ['Configuration Item','Solution']
			},
		]
}
