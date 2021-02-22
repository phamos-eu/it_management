// Copyright (c) 2019, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

frappe.ui.form.on('Configuration Item', {
	refresh: function(frm) {

	},
	onload: function(frm) {
		frm.set_query("location_room", function() {
			if (frm.doc.location) {
				return {
					'filters': {
						"location" : frm.doc.location,
						"floor" : frm.doc.floor
					}
				};
			}
		});
	},
});
