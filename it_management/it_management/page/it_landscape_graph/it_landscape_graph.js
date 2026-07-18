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

	// App script/CSS only — Cytoscape is resolved via AMD capture in ensure_cytoscape().
	const assets = [
		"/assets/it_management/js/it_landscape_graph.js",
		"/assets/it_management/css/it_landscape_graph.css",
	];

	frappe.require(assets, () => {
		if (
			!(
				window.it_management &&
				it_management.landscape_graph &&
				it_management.landscape_graph.ITLandscapeGraph
			)
		) {
			frappe.msgprint({
				title: __("Missing library"),
				message: __("IT Landscape Graph script did not load."),
				indicator: "red",
			});
			return;
		}

		const graph = new it_management.landscape_graph.ITLandscapeGraph({
			wrapper: $(wrapper).find(".it-landscape-graph-mount").get(0),
		});
		graph.init();
		page.graph = graph;
	});
};
