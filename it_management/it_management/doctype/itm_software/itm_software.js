// Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

frappe.ui.form.on('ITM Software', {
	// refresh: function(frm) {

	// }
	status: function(frm) {
		if (frm.doc.status == "Active"){
			frm.set_value("disabled", false);
		}
		if (frm.doc.end_of_life){
			frm.set_value("value_holder",frm.doc.end_of_life);
		}
		
	}
});
