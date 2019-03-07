from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'software_solution',
		'transactions': [
      {
				'label': _('Installations'),
				'items': ['Software Instance']
			},
      {
				'label': _('Users and Groups'),
				'items': ['Access Account']
			},
		]
	}
