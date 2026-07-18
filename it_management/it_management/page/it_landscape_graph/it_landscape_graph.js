// Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

frappe.pages["it-landscape-graph"].on_page_load = function (wrapper) {
	// Graph UI lives as a website page under www/; open it from Desk.
	window.location.href = "/it_landscape_graph";
};
