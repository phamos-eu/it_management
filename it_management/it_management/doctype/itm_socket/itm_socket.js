// Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

frappe.ui.form.on('ITM Socket', {
	setup(frm) {
		frm.set_query('itm_location', () => ({
			filters: { location_type: 'Room', disabled: 0 },
		}));
		frm.set_query('endpoint_socket', () => {
			const filters = { name: ['!=', frm.doc.name || ''] };
			return { filters };
		});
	},
});
