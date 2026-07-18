// Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

frappe.provide("it_management.landscape_graph");

(function () {
	"use strict";

	const CYTOSCAPE_SRC = "/assets/it_management/js/lib/cytoscape.min.js";

	const HEALTH_COLORS = {
		Healthy: "#2e7d32",
		Warning: "#ef6c00",
		Critical: "#c62828",
		Unknown: "#757575",
	};

	const LIFECYCLE_COLORS = {
		Implementing: "#f9a825",
		Running: "#2e7d32",
		Storage: "#9e9e9e",
		Obsolete: "#546e7a",
	};

	/**
	 * Cytoscape's UMD build calls define() when RequireJS is present (Frappe Desk),
	 * which skips setting window.cytoscape. Load via a classic script tag with AMD
	 * temporarily disabled so the browser-global export runs.
	 */
	it_management.landscape_graph.ensure_cytoscape = function () {
		if (typeof window.cytoscape === "function") {
			return Promise.resolve(window.cytoscape);
		}

		if (it_management.landscape_graph._cytoscape_loading) {
			return it_management.landscape_graph._cytoscape_loading;
		}

		it_management.landscape_graph._cytoscape_loading = new Promise(
			(resolve, reject) => {
				const previous_define = window.define;
				const restore_define = () => {
					if (previous_define !== undefined) {
						window.define = previous_define;
					}
				};

				// Force the UMD browser branch: (global).cytoscape = factory()
				if (typeof window.define === "function" && window.define.amd) {
					window.define = undefined;
				}

				const script = document.createElement("script");
				script.src = CYTOSCAPE_SRC;
				script.async = true;
				script.onload = () => {
					restore_define();
					if (typeof window.cytoscape === "function") {
						resolve(window.cytoscape);
					} else {
						reject(new Error("Cytoscape loaded but global was not set"));
					}
				};
				script.onerror = () => {
					restore_define();
					reject(new Error("Failed to fetch " + CYTOSCAPE_SRC));
				};
				document.head.appendChild(script);
			}
		).finally(() => {
			it_management.landscape_graph._cytoscape_loading = null;
		});

		return it_management.landscape_graph._cytoscape_loading;
	};

	function escapeHtml(value) {
		return String(value == null ? "" : value)
			.replace(/&/g, "&amp;")
			.replace(/</g, "&lt;")
			.replace(/>/g, "&gt;")
			.replace(/"/g, "&quot;")
			.replace(/'/g, "&#39;");
	}

	function healthColor(status) {
		return HEALTH_COLORS[status] || HEALTH_COLORS.Unknown;
	}

	function lifecycleColor(status) {
		return LIFECYCLE_COLORS[status] || "#9e9e9e";
	}

	it_management.landscape_graph.ITLandscapeGraph = class ITLandscapeGraph {
		constructor(opts) {
			this.wrapper = opts.wrapper;
			this.cy = null;
			this.currentLandscape = null;
			this.currentSolutions = [];
			this.searchTerm = "";
			this.$tooltip = null;
		}

		init() {
			return it_management.landscape_graph
				.ensure_cytoscape()
				.then(() => {
					this.render_layout();
					this.bind_events();
					return this.load_filter_options().then(() => this.load_graph_data());
				})
				.catch((err) => {
					console.error(err);
					frappe.msgprint({
						title: __("Missing library"),
						message: __(
							"Cytoscape.js failed to load. Hard-refresh the page or run bench clear-cache / bench build if assets are missing."
						),
						indicator: "red",
					});
				});
		}

		render_layout() {
			$(this.wrapper).html(`
				<div class="it-landscape-graph-container">
					<div class="graph-controls">
						<div class="control-group">
							<label for="landscape-filter">${__("Filter by Landscape")}</label>
							<select id="landscape-filter" class="form-control">
								<option value="">${__("All Landscapes")}</option>
							</select>
						</div>
						<div class="control-group">
							<label for="solution-filter">${__("Filter by Solution")}</label>
							<select id="solution-filter" class="form-control" multiple></select>
						</div>
						<div class="control-group">
							<label for="search-box">${__("Search Hosts")}</label>
							<input type="text" id="search-box" class="form-control"
								placeholder="${__("Type to search...")}">
						</div>
						<div class="control-group control-actions">
							<button type="button" id="export-png" class="btn btn-primary btn-sm">
								${__("Export as PNG")}
							</button>
							<button type="button" id="reset-view" class="btn btn-default btn-sm">
								${__("Reset View")}
							</button>
						</div>
					</div>
					<div class="graph-legend">
						<strong>${__("Health")}:</strong>
						<span class="legend-item">
							<span class="legend-color" style="background:${HEALTH_COLORS.Healthy}"></span>
							${__("Healthy")}
						</span>
						<span class="legend-item">
							<span class="legend-color" style="background:${HEALTH_COLORS.Warning}"></span>
							${__("Warning")}
						</span>
						<span class="legend-item">
							<span class="legend-color" style="background:${HEALTH_COLORS.Critical}"></span>
							${__("Critical")}
						</span>
						<span class="legend-item">
							<span class="legend-color" style="background:${HEALTH_COLORS.Unknown}"></span>
							${__("Unknown")}
						</span>
						<span class="legend-sep">|</span>
						<strong>${__("Lifecycle")}:</strong>
						<span class="legend-item">
							<span class="legend-color legend-ring"
								style="border-color:${LIFECYCLE_COLORS.Implementing}"></span>
							${__("Implementing")}
						</span>
						<span class="legend-item">
							<span class="legend-color legend-ring"
								style="border-color:${LIFECYCLE_COLORS.Running}"></span>
							${__("Running")}
						</span>
						<span class="legend-item">
							<span class="legend-color legend-ring"
								style="border-color:${LIFECYCLE_COLORS.Storage}"></span>
							${__("Storage")}
						</span>
						<span class="legend-item">
							<span class="legend-color legend-ring"
								style="border-color:${LIFECYCLE_COLORS.Obsolete}"></span>
							${__("Obsolete")}
						</span>
						<span class="legend-sep">|</span>
						<span class="legend-item">
							<span class="legend-shape legend-ellipse"></span> ${__("Physical Host")}
						</span>
						<span class="legend-item">
							<span class="legend-shape legend-diamond"></span> ${__("Virtual Host")}
						</span>
						<span class="legend-item">
							<span class="legend-shape legend-roundrect"></span> ${__("Solution")}
						</span>
					</div>
					<div id="graph-container" class="graph-canvas"></div>
					<div id="node-tooltip" class="graph-tooltip" style="display:none;"></div>
				</div>
			`);
			this.$tooltip = $(this.wrapper).find("#node-tooltip");
		}

		bind_events() {
			const $w = $(this.wrapper);

			$w.find("#landscape-filter").on("change", (e) => {
				this.currentLandscape = e.target.value || null;
				this.load_graph_data();
			});

			$w.find("#solution-filter").on("change", (e) => {
				const selected = Array.from(e.target.selectedOptions)
					.map((opt) => opt.value)
					.filter(Boolean);
				this.currentSolutions = selected;
				this.load_graph_data();
			});

			const on_search = (e) => {
				this.searchTerm = (e.target.value || "").trim().toLowerCase();
				this.apply_search_filter();
			};
			const debounced_search =
				frappe.utils && frappe.utils.debounce
					? frappe.utils.debounce(on_search, 200)
					: on_search;
			$w.find("#search-box").on("input", debounced_search);

			$w.find("#export-png").on("click", () => this.export_png());
			$w.find("#reset-view").on("click", () => {
				if (this.cy) {
					this.cy.fit(undefined, 40);
				}
			});
		}

		load_filter_options() {
			const load_list = (doctype, fields, order_by) =>
				frappe
					.call({
						method: "frappe.client.get_list",
						args: {
							doctype: doctype,
							fields: fields,
							order_by: order_by,
							limit_page_length: 500,
						},
					})
					.then((r) => r.message || []);

			return Promise.all([
				load_list("ITM Landscape", ["name", "title"], "title asc"),
				load_list("ITM Solution", ["name", "name1"], "name1 asc"),
			]).then(([landscapes, solutions]) => {
				const $landscape = $(this.wrapper).find("#landscape-filter");
				(landscapes || []).forEach((row) => {
					$landscape.append(
						`<option value="${escapeHtml(row.name)}">${escapeHtml(
							row.title || row.name
						)}</option>`
					);
				});

				const $solution = $(this.wrapper).find("#solution-filter");
				(solutions || []).forEach((row) => {
					$solution.append(
						`<option value="${escapeHtml(row.name)}">${escapeHtml(
							row.name1 || row.name
						)}</option>`
					);
				});
			});
		}

		load_graph_data() {
			const $container = $(this.wrapper).find("#graph-container");
			$container.addClass("is-loading");

			return frappe
				.call({
					method: "it_management.api.get_landscape_graph_data",
					args: {
						landscape: this.currentLandscape || undefined,
						solutions:
							this.currentSolutions && this.currentSolutions.length
								? JSON.stringify(this.currentSolutions)
								: undefined,
					},
				})
				.then((r) => {
					const elements = (r.message && r.message.elements) || [];
					this.render_cytoscape(elements);
					this.apply_search_filter();
					if (!elements.length) {
						frappe.show_alert({
							message: __("No host items match the current filters"),
							indicator: "orange",
						});
					}
				})
				.catch(() => {
					frappe.show_alert({
						message: __("Error loading graph data"),
						indicator: "red",
					});
				})
				.then(() => {
					$container.removeClass("is-loading");
				});
		}

		render_cytoscape(elements) {
			const container = $(this.wrapper).find("#graph-container").get(0);
			if (this.cy) {
				this.cy.destroy();
				this.cy = null;
			}

			const self = this;
			this.cy = cytoscape({
				container: container,
				elements: elements,
				layout: {
					name: "cose",
					animate: false,
					padding: 40,
					nodeRepulsion: 8000,
					idealEdgeLength: 100,
					gravity: 0.25,
				},
				style: [
					{
						selector: "node[node_type = 'host']",
						style: {
							label: "data(label)",
							"text-valign": "bottom",
							"text-halign": "center",
							"font-size": 11,
							color: "#212121",
							"text-margin-y": 6,
							width: 36,
							height: 36,
							"background-color": (ele) =>
								healthColor(ele.data("health_status")),
							"border-width": 4,
							"border-color": (ele) =>
								lifecycleColor(ele.data("lifecycle_status")),
							shape: (ele) =>
								ele.data("deployment") === "Virtual" ? "diamond" : "ellipse",
						},
					},
					{
						selector: "node[node_type = 'solution']",
						style: {
							label: "data(label)",
							"text-valign": "center",
							"text-halign": "center",
							"font-size": 12,
							"font-weight": 600,
							color: "#0d47a1",
							"text-wrap": "wrap",
							"text-max-width": 120,
							width: 120,
							height: 52,
							shape: "round-rectangle",
							"background-color": "#e3f2fd",
							"border-width": 2,
							"border-color": (ele) =>
								healthColor(ele.data("health_status")),
						},
					},
					{
						selector: "edge[edge_type = 'member']",
						style: {
							width: 2,
							"line-color": "#90a4ae",
							"target-arrow-color": "#90a4ae",
							"target-arrow-shape": "triangle",
							"curve-style": "bezier",
						},
					},
					{
						selector: "edge[edge_type = 'hosted_on']",
						style: {
							width: 2,
							"line-color": "#7b1fa2",
							"line-style": "dashed",
							"target-arrow-color": "#7b1fa2",
							"target-arrow-shape": "chevron",
							"curve-style": "bezier",
							label: __("hosted on"),
							"font-size": 9,
							color: "#7b1fa2",
							"text-rotation": "autorotate",
						},
					},
					{
						selector: "node.dimmed, edge.dimmed",
						style: {
							opacity: 0.15,
						},
					},
					{
						selector: "node:selected",
						style: {
							"border-width": 5,
							"border-color": "#1565c0",
						},
					},
				],
				minZoom: 0.2,
				maxZoom: 3,
				wheelSensitivity: 0.3,
			});

			this.cy.on("tap", "node", (evt) => {
				const data = evt.target.data();
				if (data.doctype && data.docname) {
					frappe.set_route("Form", data.doctype, data.docname);
				}
			});

			this.cy.on("mouseover", "node", (evt) => {
				self.show_tooltip(evt.target, evt.originalEvent);
			});
			this.cy.on("mouseout", "node", () => self.hide_tooltip());
			this.cy.on("mousemove", "node", (evt) => {
				self.position_tooltip(evt.originalEvent);
			});

			this.cy.fit(undefined, 40);
		}

		apply_search_filter() {
			if (!this.cy) {
				return;
			}

			const term = this.searchTerm;
			if (!term) {
				this.cy.elements().removeClass("dimmed");
				return;
			}

			const matchedHosts = this.cy.nodes('[node_type = "host"]').filter((node) => {
				const label = (node.data("label") || "").toLowerCase();
				const name = (node.data("docname") || "").toLowerCase();
				return label.includes(term) || name.includes(term);
			});

			const keep = matchedHosts.closedNeighborhood().add(matchedHosts);
			this.cy.elements().addClass("dimmed");
			keep.removeClass("dimmed");
		}

		show_tooltip(node, domEvent) {
			const d = node.data();
			let html = `<div><strong>${escapeHtml(d.label || d.docname)}</strong></div>`;
			html += `<div>${escapeHtml(d.node_type === "solution" ? __("Solution") : __("Host Item"))}</div>`;

			if (d.lifecycle_status) {
				html += `<div>${__("Lifecycle")}: ${escapeHtml(d.lifecycle_status)}</div>`;
			}
			if (d.health_status) {
				html += `<div>${__("Health")}: ${escapeHtml(d.health_status)}</div>`;
			}
			if (d.deployment) {
				html += `<div>${__("Deployment")}: ${escapeHtml(d.deployment)}</div>`;
			}
			if (d.landscape) {
				html += `<div>${__("Landscape")}: ${escapeHtml(d.landscape)}</div>`;
			}
			if (d.solutions && d.solutions.length) {
				html += `<div>${__("Solutions")}: ${escapeHtml(d.solutions.join(", "))}</div>`;
			}
			if (d.hosted_on) {
				html += `<div>${__("Hosted On")}: ${escapeHtml(d.hosted_on)}</div>`;
			}

			this.$tooltip.html(html).show();
			this.position_tooltip(domEvent);
		}

		position_tooltip(domEvent) {
			if (!domEvent || !this.$tooltip) {
				return;
			}
			const offset = $(this.wrapper).offset() || { left: 0, top: 0 };
			this.$tooltip.css({
				left: domEvent.pageX - offset.left + 16,
				top: domEvent.pageY - offset.top + 16,
			});
		}

		hide_tooltip() {
			if (this.$tooltip) {
				this.$tooltip.hide();
			}
		}

		export_png() {
			if (!this.cy) {
				return;
			}
			const png = this.cy.png({
				full: true,
				scale: 2,
				bg: "#ffffff",
			});
			const link = document.createElement("a");
			link.download = "it-landscape-graph.png";
			link.href = png;
			link.click();
		}
	};

	// Website page bootstrap (DOMContentLoaded)
	it_management.landscape_graph.boot_website = function () {
		const root = document.querySelector(".it-landscape-graph-mount");
		if (!root) {
			return;
		}
		const graph = new it_management.landscape_graph.ITLandscapeGraph({
			wrapper: root,
		});
		return graph.init();
	};
})();
