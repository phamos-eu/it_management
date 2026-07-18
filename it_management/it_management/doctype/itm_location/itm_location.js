// Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

frappe.ui.form.on('ITM Location', {
	setup(frm) {
		frm.set_query('itm_parent_location', () => {
			const expected = {
				Building: 'Site',
				Floor: 'Building',
				Room: 'Floor',
			}[frm.doc.location_type];

			if (!expected) {
				return {};
			}

			return {
				filters: {
					location_type: expected,
					disabled: 0,
				},
			};
		});
	},

	refresh(frm) {
		frm.trigger('toggle_location_fields');
	},

	location_type(frm) {
		frm.trigger('toggle_location_fields');
		if (frm.doc.location_type === 'Site') {
			frm.set_value('itm_parent_location', null);
		}
	},

	itm_parent_location(frm) {
		if (frm.doc.location_type === 'Site' || !frm.doc.itm_parent_location) {
			return;
		}
		frappe.db.get_value(
			'ITM Location',
			frm.doc.itm_parent_location,
			'itm_landscape',
			(r) => {
				if (r) {
					frm.set_value('itm_landscape', r.itm_landscape || null);
				}
			}
		);
	},

	toggle_location_fields(frm) {
		const is_site = frm.doc.location_type === 'Site';
		const show_address =
			frm.doc.location_type === 'Site' || frm.doc.location_type === 'Building';

		frm.set_df_property('itm_landscape', 'read_only', is_site ? 0 : 1);
		frm.set_df_property('itm_location_address', 'hidden', show_address ? 0 : 1);
		frm.set_df_property('itm_parent_location', 'hidden', is_site ? 1 : 0);
		frm.set_df_property('itm_parent_location', 'reqd', is_site ? 0 : 1);
	},
});
