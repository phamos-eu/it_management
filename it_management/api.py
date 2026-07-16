# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json


@frappe.whitelist()
def get_landscape_graph_data(landscape=None, solutions=None):
	"""
	Returns ITM Host Items and their Solution groups for GoJS visualization.
	
	Args:
	    landscape (str, optional): Filter by ITM Landscape name. Defaults to None (all landscapes).
	    solutions (str, optional): JSON string of list of ITM Solution names to filter by.
	                                Defaults to None (all solutions).
	
	Returns:
	    dict: {"nodes": [...], "groups": [...]}
	        - nodes: List of host items with their properties
        - groups: List of solution groups with their member hosts
	"""
	# Parse solutions parameter (comes as JSON string from frontend)
	selected_solutions = None
	if solutions:
		try:
			selected_solutions = json.loads(solutions)
		except (json.JSONDecodeError, TypeError):
			selected_solutions = None

	# Build filters for the query
	filters = {}
	if landscape:
		filters["itm_landscape"] = landscape

	# Fetch all ITM Host Items (with or without Solution)
	host_items = frappe.get_all(
		"ITM Host Item",
		fields=["name", "title", "status", "itm_solution", "itm_landscape"],
		filters=filters,
		order_by="title"
	)

	# Filter by solutions if specified
	if selected_solutions:
		host_items = [
			host for host in host_items 
			if host.get("itm_solution") in selected_solutions
		]

	# Build nodes list
	nodes = []
	for host in host_items:
		node = {
			"key": host["name"],
			"text": host["title"] or host["name"],
			"status": host.get("status", ""),
			"solution": host.get("itm_solution", ""),
			"landscape": host.get("itm_landscape", "")
		}
		nodes.append(node)

	# Build groups (Solutions) - only for hosts that have a solution
	solution_groups = {}
	for host in host_items:
		solution_name = host.get("itm_solution")
		if solution_name:
			if solution_name not in solution_groups:
				solution_groups[solution_name] = {
					"members": []
				}
			# Use the solution name as the key, but sanitize it for GoJS
			safe_key = f"SOL-{solution_name.replace(' ', '-').replace('_', '-')}"
			solution_groups[solution_name]["key"] = safe_key
			solution_groups[solution_name]["members"].append(host["name"])

	# Convert groups dict to list
	groups = []
	for solution_name, group_data in solution_groups.items():
		# Get the solution doc to fetch its title (name1 field)
		solution_doc = frappe.get_cached_doc("ITM Solution", solution_name)
		solution_title = solution_doc.get("name1", solution_name) if solution_doc else solution_name
		
		group = {
			"key": group_data["key"],
			"text": solution_title,
			"isGroup": True,
			"members": group_data["members"]
		}
		groups.append(group)

	return {
		"nodes": nodes,
		"groups": groups
	}
