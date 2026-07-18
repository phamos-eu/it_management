// Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

frappe.pages["it-landscape-graph"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("IT Landscape Graph"),
		single_column: true,
	});

	$(wrapper).find(".layout-main-section").empty().append(`
		<div class="it-landscape-graph-mount"></div>
	`);

	const assets = [
		"/assets/it_management/js/cytoscape.min.js",
		"/assets/it_management/js/it_landscape_graph.js",
		"/assets/it_management/css/it_landscape_graph.css",
	];

	frappe.require(assets, () => {
		const mount = $(wrapper).find(".it-landscape-graph-mount").get(0);
		const start = () => {
			const graph = new it_management.landscape_graph.ITLandscapeGraph({
				wrapper: mount,
			});
			graph.init();
			page.graph = graph;
		};

		// Patched Cytoscape sets window.cytoscape; ensure_cytoscape covers fallbacks.
		if (
			window.it_management &&
			it_management.landscape_graph &&
			it_management.landscape_graph.ensure_cytoscape
		) {
			start();
		} else {
			frappe.msgprint({
				title: __("Missing library"),
				message: __("IT Landscape Graph script did not load."),
				indicator: "red",
			});
		}
	});
};
