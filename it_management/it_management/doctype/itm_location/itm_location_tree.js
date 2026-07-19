// Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

frappe.treeview_settings["ITM Location"] = {
	breadcrumb: "IT Management",
	title: __("ITM Location"),
	get_tree_nodes: "frappe.desk.treeview.get_children",
	add_tree_node: "frappe.desk.treeview.add_node",
	filters: [
		{
			fieldname: "itm_landscape",
			fieldtype: "Link",
			options: "ITM Landscape",
			label: __("Landscape"),
		},
	],
	fields: [
		{
			fieldtype: "Data",
			fieldname: "itm_location_name",
			label: __("Location Name"),
			reqd: true,
		},
		{
			fieldtype: "Select",
			fieldname: "location_type",
			label: __("Location Type"),
			options: "Site\nBuilding\nFloor\nRoom",
			reqd: true,
			default: "Site",
		},
		{
			fieldtype: "Link",
			fieldname: "itm_landscape",
			label: __("Landscape"),
			options: "ITM Landscape",
			description: __("Set on Site only; inherited by child locations."),
		},
		{
			fieldtype: "Check",
			fieldname: "is_group",
			label: __("Is Location Group"),
			description: __("Set automatically from Location Type."),
			default: 1,
			hidden: 1,
		},
		{
			fieldtype: "Link",
			fieldname: "parent_itm_location",
			label: __("Parent Location"),
			options: "ITM Location",
			hidden: 1,
		},
	],
	ignore_fields: ["parent_itm_location"],
};
