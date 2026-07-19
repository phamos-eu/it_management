// Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

const ITM_SUBNET_ADDRESS_DEBOUNCE_MS = 650;

function itm_subnet_is_complete_ipv4(value) {
	if (!value) {
		return false;
	}
	return /^\s*\d+\.\d+\.\d+\.\d+\s*$/.test(String(value));
}

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

	network_address(frm) {
		frm.trigger('schedule_address_design');
	},

	prefix_length(frm) {
		frm.trigger('schedule_address_design');
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

	schedule_address_design(frm) {
		if (frm._itm_subnet_design_timer) {
			clearTimeout(frm._itm_subnet_design_timer);
			frm._itm_subnet_design_timer = null;
		}

		const address = frm.doc.network_address;
		// While typing an incomplete address, do not validate or call the server
		if (address && !itm_subnet_is_complete_ipv4(address)) {
			return;
		}

		frm._itm_subnet_design_timer = setTimeout(() => {
			frm._itm_subnet_design_timer = null;
			frm.trigger('recalculate_address_design');
		}, ITM_SUBNET_ADDRESS_DEBOUNCE_MS);
	},

	recalculate_address_design(frm) {
		if (
			!frm.doc.network_address ||
			frm.doc.prefix_length === undefined ||
			frm.doc.prefix_length === null ||
			frm.doc.prefix_length === ''
		) {
			return;
		}

		if (!itm_subnet_is_complete_ipv4(frm.doc.network_address)) {
			return;
		}

		if (frm._itm_subnet_design_busy) {
			return;
		}
		frm._itm_subnet_design_busy = true;

		frappe.call({
			method: 'it_management.it_management.doctype.itm_subnet.itm_subnet.calculate_address_design',
			args: {
				network_address: frm.doc.network_address,
				prefix_length: frm.doc.prefix_length,
			},
			freeze: false,
			callback(r) {
				frm._itm_subnet_design_busy = false;
				const d = r.message;
				if (!d) {
					return;
				}
				if (d.ok === false) {
					// Soft feedback after a complete address was entered — not while typing
					frappe.show_alert(
						{
							message: d.error || __('Invalid IPv4 network address'),
							indicator: 'orange',
						},
						8
					);
					return;
				}
				// Update model directly for normalized network to avoid event loops
				frm.doc.network_address = d.network_address;
				frm.doc.prefix_length = d.prefix_length;
				frm.doc.subnet_mask = d.subnet_mask;
				frm.doc.cidr = d.cidr;
				frm.doc.first_usable = d.first_usable;
				frm.doc.last_usable = d.last_usable;
				frm.doc.broadcast = d.broadcast;
				frm.doc.usable_hosts = d.usable_hosts;
				[
					'network_address',
					'prefix_length',
					'subnet_mask',
					'cidr',
					'first_usable',
					'last_usable',
					'broadcast',
					'usable_hosts',
				].forEach((field) => frm.refresh_field(field));
			},
			error() {
				frm._itm_subnet_design_busy = false;
			},
		});
	},
});
