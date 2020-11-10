// Copyright (c) 2020, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

frappe.ui.form.on('IT Management Settings', {
	// refresh: function(frm) {

	// }
	turn_off_auto_fetching_timesheets: function(frm) {
		frappe.call({
			"method": "it_management.utils.turn_off_auto_fetching_timesheets",
			"async": false,
			"callback": function(response) {
				if (response.message) {
					frappe.msgprint(response.message);
				} 
			}
		});
	},
	for_every_customer_create_default_landscape: function(frm) {
		frappe.call({
			"method": "it_management.utils.for_every_customer_create_default_landscape",
			"async": false,
			"callback": function(response) {
				if (response.message) {
					frappe.msgprint(response.message);
				} 
			}
		});
	}
});
