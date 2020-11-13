// Copyright (c) 2019, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

frappe.ui.form.on('Software Instance', {
	refresh: function(frm) {

	},
	onload: function(frm) {
		//Filter for parent_software_instance
		frm.set_query("parent_software_instance", function() {  
			if (frm.doc.configuration_item) {   
				return {
					'filters': {
						"configuration_item" : frm.doc.configuration_item
					}
				};
			}
		});
	}
});


