// Copyright (c) 2019, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

frappe.ui.form.on('Location', {
	address: function(frm) {
		erpnext.utils.get_address_display(frm, 'address');
	}
});
