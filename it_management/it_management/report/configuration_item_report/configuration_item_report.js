// Copyright (c) 2016, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Configuration Item Report"] = {
    "filters": [
        {
            "fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"default": ""
        },
    ]
}
