// Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

frappe.pages["it-networking-overview"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Networking"),
		single_column: true,
	});

	$(wrapper).find(".layout-main-section").empty().append(`
		<div class="itm-networking-overview-mount"></div>
	`);

	const assets = [
		"/assets/it_management/js/it_networking_overview.js",
		"/assets/it_management/css/it_networking_overview.css",
	];

	frappe.require(assets, () => {
		if (
			!(
				window.it_management &&
				it_management.networking &&
				it_management.networking.NetworkingOverview
			)
		) {
			frappe.msgprint({
				title: __("Missing library"),
				message: __("Networking Overview script did not load."),
				indicator: "red",
			});
			return;
		}

		const view = new it_management.networking.NetworkingOverview({
			wrapper: $(wrapper).find(".itm-networking-overview-mount").get(0),
			page,
		});
		view.init();
	});
};
