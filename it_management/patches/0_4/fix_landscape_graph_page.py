# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Repair IT Landscape Graph Page after earlier patch revisions created a Page
without on-disk Desk page assets (causing FileNotFoundError in load_assets).

Page assets now ship with the app under:
it_management/page/it_landscape_graph/
"""

import frappe


def execute():
	# Re-run ensure logic for sites that already executed the older patch.
	frappe.get_attr("it_management.patches.0_4.add_landscape_graph_link.execute")()
