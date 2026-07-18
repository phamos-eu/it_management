// Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

frappe.ui.form.on('ITM Network Interface Controller', {
	setup(frm) {
		frm.set_query('itm_socket', () => ({
			filters: {},
		}));
	},
	itm_ip_address(frm) {
		if (!frm.doc.itm_ip_address) return;
		frappe.db.get_value('ITM IP Address', frm.doc.itm_ip_address, 'itm_subnet', (r) => {
			if (r && r.itm_subnet) {
				frm.set_value('itm_subnet', r.itm_subnet);
			}
		});
	},
});
