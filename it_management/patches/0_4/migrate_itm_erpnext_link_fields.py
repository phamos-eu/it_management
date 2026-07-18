# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Migrate all remaining ITM-* DocType ERPNext Link fields to Custom Fields.

Companion to remove_erpnext_fields_from_itm_host_item (Host Item + Solution).
This patch covers every other ITM DocType that linked to Customer / Item /
Supplier, and is also safe to re-run for Host Item / Solution (idempotent).

Needed because sites that already executed the Host-Item-only patch will not
re-run it after that file was extended to include ITM Solution.

Pre_model_sync: preserve valued columns as Data Custom Fields, then apply
IT Management Settings via sync_erpnext_custom_fields().

Compatible with Frappe v15 and v16.
"""

import frappe


def execute():
	from it_management.it_management.utils.erpnext_integration import (
		migrate_managed_erpnext_standard_fields,
		sync_erpnext_custom_fields,
	)

	# All managed ITM DocTypes (Host Item, Solution, Trip, User Account, …)
	for line in migrate_managed_erpnext_standard_fields():
		frappe.log("ITM ERPNext field migration: {0}".format(line))

	for line in sync_erpnext_custom_fields():
		frappe.log("ITM ERPNext custom field sync: {0}".format(line))

	frappe.db.commit()
