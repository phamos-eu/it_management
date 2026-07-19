// Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

frappe.ui.form.on('ITM Subnet', {
	setup(frm) {
		frm.set_query('itm_local_area_network', () => {
			const filters = {};
			if (frm.doc.itm_landscape) {
				filters.itm_landscape = frm.doc.itm_landscape;
			}
			return { filters };
		});
		frm.set_query('itm_location', () => ({
			filters: {
				location_type: ['in', ['Site', 'Building']],
				disabled: 0,
			},
		}));
	},

	itm_local_area_network(frm) {
		if (!frm.doc.itm_local_area_network) {
			return;
		}
		frappe.db.get_value(
			'ITM Local Area Network',
			frm.doc.itm_local_area_network,
			['itm_landscape', 'itm_location'],
			(r) => {
				if (!r) {
					return;
				}
				frm.set_value('itm_landscape', r.itm_landscape || null);
				if (!frm.doc.itm_location && r.itm_location) {
					frm.set_value('itm_location', r.itm_location);
				}
			}
		);
	},
});
