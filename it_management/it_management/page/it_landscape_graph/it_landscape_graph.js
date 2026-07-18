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
		"/assets/it_management/js/lib/cytoscape.min.js",
		"/assets/it_management/js/it_landscape_graph.js",
		"/assets/it_management/css/it_landscape_graph.css",
	];

	frappe.require(assets, () => {
		const graph = new it_management.landscape_graph.ITLandscapeGraph({
			wrapper: $(wrapper).find(".it-landscape-graph-mount").get(0),
		});
		graph.init();
		page.graph = graph;
	});
};
