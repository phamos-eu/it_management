// Copyright (c) 2026, IT Management contributors
// For license information, please see license.txt

frappe.ui.form.on("Address", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		frm.add_custom_button(__("Geocode Address"), () => {
			frappe.call({
				method: "it_management.it_management.utils.geocoding.geocode_address",
				args: {
					name: frm.doc.name,
					force: 1,
				},
				freeze: true,
				freeze_message: __("Looking up coordinates…"),
				callback(r) {
					if (!r.message) {
						return;
					}
					frm.reload_doc();
					frappe.show_alert({
						message: __("Coordinates updated"),
						indicator: "green",
					});
				},
			});
		});
	},

	itm_manual_coordinates(frm) {
		if (frm.doc.itm_manual_coordinates) {
			frappe.show_alert({
				message: __("Auto-geocoding disabled for this address"),
				indicator: "orange",
			});
		}
	},
});
