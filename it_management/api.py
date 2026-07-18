# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

import json

import frappe
from frappe import _


def _parse_solutions(solutions):
	"""Parse solutions argument (JSON list or single name) into a list."""
	if not solutions:
		return None

	if isinstance(solutions, (list, tuple)):
		return [name for name in solutions if name]

	try:
		parsed = json.loads(solutions)
	except (json.JSONDecodeError, TypeError):
		return [solutions] if isinstance(solutions, str) else None

	if isinstance(parsed, list):
		return [name for name in parsed if name]
	if isinstance(parsed, str) and parsed:
		return [parsed]
	return None


def _solution_node_id(solution_name):
	return "SOL::{}".format(solution_name)


def _host_node_id(host_name):
	return "HOST::{}".format(host_name)


@frappe.whitelist()
def get_landscape_graph_data(landscape=None, solutions=None):
	"""
	Return Cytoscape elements for the IT Landscape Graph.

	Hosts are linked to Solutions via ITM Host Item Solution Table (M2M).
	Virtual hosts may also link to a parent host via hosted_on.

	Args:
	        landscape: Optional ITM Landscape name filter.
	        solutions: Optional JSON list of ITM Solution names.

	Returns:
	        dict with Cytoscape `elements` (nodes + edges).
	"""
	selected_solutions = _parse_solutions(solutions)

	filters = {}
	if landscape:
		filters["itm_landscape"] = landscape

	# Permission-aware read
	host_items = frappe.get_list(
		"ITM Host Item",
		fields=[
			"name",
			"title",
			"lifecycle_status",
			"health_status",
			"deployment",
			"hosted_on",
			"itm_landscape",
		],
		filters=filters,
		order_by="title",
		limit_page_length=10000,
	)

	host_solutions = {}
	if host_items:
		host_names = [host.name for host in host_items]
		for row in frappe.get_all(
			"ITM Host Item Solution Table",
			filters={
				"parent": ["in", host_names],
				"parenttype": "ITM Host Item",
			},
			fields=["parent", "itm_solution"],
		):
			if not row.itm_solution:
				continue
			host_solutions.setdefault(row.parent, []).append(row.itm_solution)

	if selected_solutions:
		selected = set(selected_solutions)
		host_items = [
			host
			for host in host_items
			if selected.intersection(host_solutions.get(host.name, []))
		]

	solution_names = set()
	for host in host_items:
		for solution_name in host_solutions.get(host.name, []):
			if not selected_solutions or solution_name in selected_solutions:
				solution_names.add(solution_name)

	solution_titles = {}
	if solution_names:
		for row in frappe.get_list(
			"ITM Solution",
			filters={"name": ["in", list(solution_names)]},
			fields=["name", "name1", "lifecycle_status", "health_status"],
			limit_page_length=10000,
		):
			solution_titles[row.name] = row

	elements = []
	host_ids = set()

	for solution_name in sorted(solution_names):
		meta = solution_titles.get(solution_name)
		elements.append(
			{
				"group": "nodes",
				"data": {
					"id": _solution_node_id(solution_name),
					"label": (meta.name1 if meta else None) or solution_name,
					"node_type": "solution",
					"doctype": "ITM Solution",
					"docname": solution_name,
					"lifecycle_status": (meta.lifecycle_status if meta else "") or "",
					"health_status": (meta.health_status if meta else "") or "",
				},
			}
		)

	for host in host_items:
		host_id = _host_node_id(host.name)
		host_ids.add(host_id)
		memberships = host_solutions.get(host.name, [])
		if selected_solutions:
			memberships = [s for s in memberships if s in selected_solutions]

		elements.append(
			{
				"group": "nodes",
				"data": {
					"id": host_id,
					"label": host.title or host.name,
					"node_type": "host",
					"doctype": "ITM Host Item",
					"docname": host.name,
					"lifecycle_status": host.lifecycle_status or "",
					"health_status": host.health_status or "",
					"deployment": host.deployment or "Physical",
					"landscape": host.itm_landscape or "",
					"solutions": memberships,
					"hosted_on": host.hosted_on or "",
				},
			}
		)

		for solution_name in memberships:
			elements.append(
				{
					"group": "edges",
					"data": {
						"id": "MEMBER::{}::{}".format(host.name, solution_name),
						"source": host_id,
						"target": _solution_node_id(solution_name),
						"edge_type": "member",
					},
				}
			)

	# Virtual hosting relationships (only when both endpoints are in the graph)
	for host in host_items:
		if not host.hosted_on:
			continue
		source_id = _host_node_id(host.name)
		target_id = _host_node_id(host.hosted_on)
		if source_id not in host_ids or target_id not in host_ids:
			continue
		elements.append(
			{
				"group": "edges",
				"data": {
					"id": "HOSTED::{}::{}".format(host.name, host.hosted_on),
					"source": source_id,
					"target": target_id,
					"edge_type": "hosted_on",
				},
			}
		)

	return {"elements": elements}
