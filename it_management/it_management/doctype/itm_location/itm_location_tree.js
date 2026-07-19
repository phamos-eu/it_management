// Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

frappe.provide("frappe.treeview_settings");

const ITM_LOCATION_CHILD_TYPE = {
	Site: "Building",
	Building: "Floor",
	Floor: "Room",
};

frappe.treeview_settings["ITM Location"] = {
	breadcrumb: "IT Management",
	title: __("ITM Location"),
	get_tree_nodes: "frappe.desk.treeview.get_children",
	add_tree_node: "it_management.it_management.doctype.itm_location.itm_location.add_node",
	filters: [
		{
			fieldname: "itm_landscape",
			fieldtype: "Link",
			options: "ITM Landscape",
			label: __("Landscape"),
		},
	],
	// parent_itm_location is set by Tree View / add_node — do not put it in the dialog
	ignore_fields: ["parent_itm_location"],
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
			read_only: 1,
		},
		{
			fieldtype: "Link",
			fieldname: "itm_landscape",
			label: __("Landscape"),
			options: "ITM Landscape",
			description: __("Set on Site only; inherited by child locations."),
		},
	],
	onload(treeview) {
		frappe.treeview_settings["ITM Location"].treeview = treeview;
		const original_new_node = treeview.new_node.bind(treeview);

		treeview.new_node = function () {
			const node = treeview.tree.get_selected_node();
			if (!(node && node.expandable)) {
				frappe.msgprint(__("Select a group {0} first.", [__("ITM Location")]));
				return;
			}

			const open_dialog = (child_type) => {
				treeview.opts.fields = [
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
						options: child_type,
						reqd: true,
						default: child_type,
						read_only: 1,
					},
					{
						fieldtype: "Link",
						fieldname: "itm_landscape",
						label: __("Landscape"),
						options: "ITM Landscape",
						description: __("Set on Site only; inherited by child locations."),
						hidden: child_type === "Site" ? 0 : 1,
					},
				];
				original_new_node();
			};

			if (node.is_root) {
				open_dialog("Site");
				return;
			}

			const parent_name = node.data && node.data.value ? node.data.value : node.label;
			frappe.db.get_value("ITM Location", parent_name, "location_type", (r) => {
				const parent_type = r && r.location_type;
				const child_type = ITM_LOCATION_CHILD_TYPE[parent_type];
				if (!child_type) {
					frappe.msgprint(
						__("Cannot add a child under a {0}.", [__(parent_type || _("location"))])
					);
					return;
				}
				open_dialog(child_type);
			});
		};
	},
};
