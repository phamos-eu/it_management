// Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

const ITM_IP_VALIDATE_DEBOUNCE_MS = 450;

function itm_ip_is_complete_ipv4(value) {
	if (!value) {
		return false;
	}
	return /^\s*\d+\.\d+\.\d+\.\d+\s*$/.test(String(value));
}

frappe.ui.form.on('ITM IP Address', {
	refresh(frm) {
		frm.trigger('check_ip_against_subnet');
	},

	ip_address(frm) {
		frm.trigger('schedule_ip_check');
	},

	itm_subnet(frm) {
		frm.trigger('schedule_ip_check');
	},

	schedule_ip_check(frm) {
		if (frm._itm_ip_check_timer) {
			clearTimeout(frm._itm_ip_check_timer);
			frm._itm_ip_check_timer = null;
		}

		const ip = frm.doc.ip_address;
		if (ip && !itm_ip_is_complete_ipv4(ip)) {
			frm.set_df_property('ip_address', 'description', '');
			return;
		}

		frm._itm_ip_check_timer = setTimeout(() => {
			frm._itm_ip_check_timer = null;
			frm.trigger('check_ip_against_subnet');
		}, ITM_IP_VALIDATE_DEBOUNCE_MS);
	},

	check_ip_against_subnet(frm) {
		if (!frm.doc.ip_address || !itm_ip_is_complete_ipv4(frm.doc.ip_address)) {
			frm.set_df_property('ip_address', 'description', '');
			return;
		}

		frappe.call({
			method: 'it_management.it_management.doctype.itm_ip_address.itm_ip_address.validate_ip_for_subnet',
			args: {
				ip_address: frm.doc.ip_address,
				itm_subnet: frm.doc.itm_subnet,
			},
			callback(r) {
				const result = r.message || {};
				const message = result.message || '';
				frm.set_df_property('ip_address', 'description', message);

				if (!result.ok && frm.doc.itm_subnet && message) {
					frm.dashboard.clear_headline();
					frm.dashboard.set_headline_alert(message, 'red');
				} else if (result.ok) {
					frm.dashboard.clear_headline();
					frm.dashboard.set_headline_alert(message, 'green');
				} else {
					frm.dashboard.clear_headline();
				}
			},
		});
	},
});
