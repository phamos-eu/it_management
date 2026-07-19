// Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

frappe.provide("it_management.networking");

it_management.networking.NetworkingOverview = class NetworkingOverview {
	constructor({ wrapper, page }) {
		this.$wrapper = $(wrapper);
		this.page = page;
		this.landscape = null;
		this.profiles = [];
	}

	init() {
		this.render_shell();
		this.bind_actions();
		this.load_profiles();
	}

	render_shell() {
		this.$wrapper.html(`
			<div class="itm-net">
				<div class="itm-net__hero">
					<p class="itm-net__brand">${__("Networking")}</p>
					<p class="itm-net__lede">${__(
						"Sites, LANs, subnets, and IP space — plan new networks and see what is still free."
					)}</p>
				</div>
				<div class="itm-net__toolbar">
					<div class="itm-net__landscape-field"></div>
					<button class="btn btn-primary btn-sm itm-net__plan-btn" type="button">
						${__("Plan new subnet")}
					</button>
				</div>
				<div class="itm-net__body">
					<div class="itm-net__empty text-muted">${__("Select a Landscape to load LANs and subnets.")}</div>
				</div>
			</div>
		`);

		this.landscape_control = frappe.ui.form.make_control({
			parent: this.$wrapper.find(".itm-net__landscape-field"),
			df: {
				fieldtype: "Link",
				options: "ITM Landscape",
				label: __("Landscape"),
				fieldname: "itm_landscape",
				reqd: 1,
				change: () => {
					this.landscape = this.landscape_control.get_value();
					this.refresh_overview();
				},
			},
			render_input: true,
		});
	}

	bind_actions() {
		this.$wrapper.on("click", ".itm-net__plan-btn", () => {
			if (!this.landscape) {
				frappe.msgprint(__("Select a Landscape first."));
				return;
			}
			new it_management.networking.PlanSubnetWizard({
				landscape: this.landscape,
				profiles: this.profiles,
				on_created: () => this.refresh_overview(),
			}).show();
		});
	}

	load_profiles() {
		frappe.call({
			method: "it_management.it_management.utils.networking.get_purpose_profiles",
			callback: (r) => {
				this.profiles = r.message || [];
			},
		});
	}

	refresh_overview() {
		const $body = this.$wrapper.find(".itm-net__body");
		if (!this.landscape) {
			$body.html(
				`<div class="itm-net__empty">${__("Select a Landscape to load LANs and subnets.")}</div>`
			);
			return;
		}

		$body.html(`<div class="text-muted">${__("Loading…")}</div>`);
		frappe.call({
			method: "it_management.it_management.utils.networking.get_networking_overview",
			args: { itm_landscape: this.landscape },
			callback: (r) => {
				const lans = (r.message && r.message.lans) || [];
				if (!lans.length) {
					$body.html(
						`<div class="itm-net__empty">${__(
							"No Local Area Networks in this Landscape yet. Create a LAN, then plan a subnet."
						)}</div>`
					);
					return;
				}
				$body.html(lans.map((lan) => this.render_lan(lan)).join(""));
			},
		});
	}

	render_lan(lan) {
		const subnets = lan.subnets || [];
		const subnet_html = subnets.length
			? subnets.map((s) => this.render_subnet(s)).join("")
			: `<div class="itm-net__empty">${__("No subnets on this LAN yet.")}</div>`;

		return `
			<section class="itm-net__lan">
				<div class="itm-net__lan-title">
					<h3>
						<a href="/app/itm-local-area-network/${encodeURIComponent(lan.name)}">${frappe.utils.escape_html(
							lan.title
						)}</a>
					</h3>
					<span class="itm-net__lan-meta">${
						lan.itm_location
							? frappe.utils.escape_html(lan.itm_location)
							: __("No location")
					} · ${__(
						subnets.length === 1 ? "{0} subnet" : "{0} subnets",
						[subnets.length]
					)}</span>
				</div>
				${subnet_html}
			</section>
		`;
	}

	render_subnet(s) {
		const usable = s.usable || 0;
		const used = s.used || 0;
		const free = s.free || 0;
		const used_pct = usable ? Math.min(100, Math.round((used / usable) * 100)) : 0;
		const free_pct = Math.max(0, 100 - used_pct);
		return `
			<div class="itm-net__subnet">
				<div class="itm-net__subnet-head">
					<span>
						<a href="/app/itm-subnet/${encodeURIComponent(s.name)}">${frappe.utils.escape_html(
							s.cidr || s.name
						)}</a>
						<span class="itm-net__status">${frappe.utils.escape_html(s.lifecycle_status || "")}</span>
						${
							s.vlan_tag != null && s.vlan_tag !== ""
								? `<span class="itm-net__status">VLAN ${frappe.utils.escape_html(
										String(s.vlan_tag)
								  )}</span>`
								: ""
						}
					</span>
				</div>
				<div class="itm-net__bar" title="${used} used / ${free} free">
					<div class="itm-net__bar-used" style="width:${used_pct}%"></div>
					<div class="itm-net__bar-free" style="width:${free_pct}%"></div>
				</div>
				<div class="itm-net__counts">${__("{0} used · {1} free · {2} usable", [
					used,
					free,
					usable,
				])}</div>
			</div>
		`;
	}
};

it_management.networking.PlanSubnetWizard = class PlanSubnetWizard {
	constructor({ landscape, profiles, on_created }) {
		this.landscape = landscape;
		this.profiles = profiles || [];
		this.on_created = on_created;
		this.step = 0;
		this.steps = [
			__("Purpose"),
			__("Size"),
			__("Address"),
			__("Infrastructure"),
			__("Review"),
		];
		this.lan_count = null;
		this.state = {
			purpose_profile: "Corporate",
			expected_clients: 50,
			prefix_length: null,
			lan_mode: "existing",
			itm_local_area_network: null,
			lan_title: "",
			itm_location: null,
			lan_created_in_wizard: false,
			vlan_tag: null,
			network_address: null,
			design: null,
			conflicts: [],
			profile_notes: "",
			gateway: null,
			dhcp: null,
			dns_1: null,
			dns_2: null,
			ntp_1: null,
			ntp_2: null,
			note: "",
		};
	}

	async show() {
		this.dialog = new frappe.ui.Dialog({
			title: __("Plan a subnet"),
			size: "large",
			fields: [{ fieldtype: "HTML", fieldname: "body" }],
			primary_action_label: __("Next"),
			primary_action: () => this.next(),
			secondary_action_label: __("Back"),
			secondary_action: () => this.back(),
		});
		this.dialog.$wrapper.addClass("itm-net-wizard");
		this.dialog.show();
		this.dialog.fields_dict.body.$wrapper.html(
			`<p class="text-muted">${__("Loading…")}</p>`
		);
		await this.load_lan_context();
		this.render_step();
	}

	async load_lan_context() {
		const r = await frappe.call({
			method: "it_management.it_management.utils.networking.get_lan_options",
			args: { itm_landscape: this.landscape },
		});
		const msg = r.message || {};
		this.lan_count = msg.count || 0;
		if (this.lan_count === 0) {
			this.state.lan_mode = "new";
		} else if (!this.state.lan_mode) {
			this.state.lan_mode = "existing";
		}
	}

	set_footer() {
		const $primary = this.dialog.get_primary_btn();
		if (this.step === this.steps.length - 1) {
			$primary.text(__("Create as Implementing"));
		} else {
			$primary.text(__("Next"));
		}
		const $secondary =
			(this.dialog.get_secondary_btn && this.dialog.get_secondary_btn()) ||
			this.dialog.$wrapper.find(".btn-modal-secondary");
		if (!$secondary || !$secondary.length) {
			return;
		}
		if (this.step === 0) {
			$secondary.hide();
		} else {
			$secondary.show().text(__("Back"));
		}
	}

	back() {
		if (this.step > 0) {
			this.step -= 1;
			this.render_step();
		}
	}

	async next() {
		const ok = await this.collect_step();
		if (!ok) {
			return;
		}
		if (this.step < this.steps.length - 1) {
			this.step += 1;
			if (this.step === 2) {
				await this.load_suggestion();
			}
			this.render_step();
			return;
		}
		await this.create();
	}

	async collect_step() {
		const $body = $(this.dialog.fields_dict.body.wrapper);
		if (this.step === 0) {
			const purpose = $body.find("[name=purpose_profile]:checked").val();
			if (!purpose) {
				frappe.msgprint(__("Choose a purpose profile."));
				return false;
			}
			this.state.purpose_profile = purpose;

			const lan_mode =
				this.lan_count === 0
					? "new"
					: $body.find("[name=lan_mode]:checked").val() || this.state.lan_mode;
			this.state.lan_mode = lan_mode;

			if (lan_mode === "existing") {
				const lan = this.lan_control && this.lan_control.get_value();
				if (!lan) {
					frappe.msgprint(__("Select a Local Area Network."));
					return false;
				}
				this.state.itm_local_area_network = lan;
				this.state.lan_created_in_wizard = false;
				return true;
			}

			const title = (this.lan_title_control && this.lan_title_control.get_value()) || "";
			if (!title.trim()) {
				frappe.msgprint(__("Enter a title for the new Local Area Network."));
				return false;
			}
			this.state.lan_title = title.trim();
			this.state.itm_location =
				(this.lan_location_control && this.lan_location_control.get_value()) || null;

			const r = await frappe.call({
				method: "it_management.it_management.utils.networking.quick_create_lan",
				args: {
					title: this.state.lan_title,
					itm_landscape: this.landscape,
					itm_location: this.state.itm_location,
					name: this.state.lan_created_in_wizard
						? this.state.itm_local_area_network
						: null,
				},
				freeze: true,
				freeze_message: __("Saving Local Area Network…"),
			});
			if (!r.message || !r.message.name) {
				return false;
			}
			this.state.itm_local_area_network = r.message.name;
			this.state.lan_title = r.message.title || this.state.lan_title;
			this.state.lan_created_in_wizard = true;
			this.lan_count = Math.max(this.lan_count || 0, 1);
			return true;
		}
		if (this.step === 1) {
			const clients = cint($body.find("[name=expected_clients]").val());
			if (!clients || clients < 1) {
				frappe.msgprint(__("Enter expected clients."));
				return false;
			}
			this.state.expected_clients = clients;
			const prefix = $body.find("[name=prefix_length]").val();
			this.state.prefix_length = prefix === "" ? null : cint(prefix);
			return true;
		}
		if (this.step === 2) {
			const network = ($body.find("[name=network_address]").val() || "").trim();
			const prefix = cint($body.find("[name=prefix_length]").val());
			const vlan = $body.find("[name=vlan_tag]").val();
			if (!network || !prefix) {
				frappe.msgprint(__("Network address and prefix are required."));
				return false;
			}
			this.state.network_address = network;
			this.state.prefix_length = prefix;
			this.state.vlan_tag = vlan === "" ? null : cint(vlan);
			await this.recalculate_design();
			return !!this.state.design;
		}
		if (this.step === 3) {
			["gateway", "dhcp", "dns_1", "dns_2", "ntp_1", "ntp_2"].forEach((field) => {
				const ctrl = this.role_controls && this.role_controls[field];
				this.state[field] = ctrl ? ctrl.get_value() : null;
			});
			return true;
		}
		return true;
	}

	async load_suggestion() {
		const r = await frappe.call({
			method: "it_management.it_management.utils.networking.suggest_subnet_design",
			args: {
				itm_landscape: this.landscape,
				purpose_profile: this.state.purpose_profile,
				expected_clients: this.state.expected_clients,
				prefix_length: this.state.prefix_length,
			},
		});
		const msg = r.message || {};
		this.state.design = msg.design;
		this.state.conflicts = msg.conflicts || [];
		this.state.profile_notes = msg.profile_notes || "";
		this.state.vlan_tag = this.state.vlan_tag != null ? this.state.vlan_tag : msg.vlan_hint;
		if (msg.design) {
			this.state.network_address = msg.design.network_address;
			this.state.prefix_length = msg.design.prefix_length;
		}
	}

	async recalculate_design() {
		try {
			const r = await frappe.call({
				method:
					"it_management.it_management.doctype.itm_subnet.itm_subnet.calculate_address_design",
				args: {
					network_address: this.state.network_address,
					prefix_length: this.state.prefix_length,
				},
			});
			const d = r.message;
			if (!d || d.ok === false) {
				this.state.design = null;
				if (d && d.error) {
					frappe.show_alert({ message: d.error, indicator: "orange" }, 8);
				}
				return;
			}
			this.state.design = d;
			this.state.network_address = d.network_address;
			this.state.prefix_length = d.prefix_length;
		} catch (e) {
			this.state.design = null;
		}
	}

	render_step() {
		this.set_footer();
		const steps_html = this.steps
			.map(
				(label, idx) => `
			<span class="itm-net-wizard__step ${idx === this.step ? "is-active" : ""} ${
					idx < this.step ? "is-done" : ""
				}">${idx + 1}. ${label}</span>`
			)
			.join("");

		let content = "";
		if (this.step === 0) {
			content = this.html_purpose();
		} else if (this.step === 1) {
			content = this.html_size();
		} else if (this.step === 2) {
			content = this.html_address();
		} else if (this.step === 3) {
			content = this.html_infra();
		} else {
			content = this.html_review();
		}

		this.dialog.fields_dict.body.$wrapper.html(`
			<div class="itm-net-wizard__steps">${steps_html}</div>
			${content}
		`);

		if (this.step === 0) {
			this.bind_lan_mode_ui();
		}

		if (this.step === 3) {
			this.role_controls = {};
			["gateway", "dhcp", "dns_1", "dns_2", "ntp_1", "ntp_2"].forEach((field) => {
				const label = {
					gateway: __("Gateway"),
					dhcp: __("DHCP"),
					dns_1: __("DNS 1"),
					dns_2: __("DNS 2"),
					ntp_1: __("NTP 1"),
					ntp_2: __("NTP 2"),
				}[field];
				const $row = this.dialog.fields_dict.body.$wrapper.find(
					`.itm-net-wizard__role[data-role="${field}"]`
				);
				const ctrl = frappe.ui.form.make_control({
					parent: $row.find(".itm-net-wizard__role-link")[0],
					df: {
						fieldtype: "Link",
						options: "ITM Host Item",
						label,
						fieldname: field,
						get_query: () => ({
							filters: { itm_landscape: this.landscape },
						}),
					},
					render_input: true,
				});
				if (this.state[field]) {
					ctrl.set_value(this.state[field]);
				}
				this.role_controls[field] = ctrl;
				$row.find(".itm-net-wizard__role-create").on("click", () => {
					this.quick_create_host(field, ctrl);
				});
			});
		}
	}

	html_purpose() {
		const options = (this.profiles.length
			? this.profiles
			: [{ name: "Corporate", label: __("Corporate"), description: "" }]
		)
			.map(
				(p) => `
			<label style="display:block;margin:0.35rem 0;">
				<input type="radio" name="purpose_profile" value="${frappe.utils.escape_html(p.name)}" ${
					p.name === this.state.purpose_profile ? "checked" : ""
				}/>
				<strong>${frappe.utils.escape_html(p.label || p.name)}</strong>
				<span class="text-muted"> — ${frappe.utils.escape_html(p.description || "")}</span>
			</label>`
			)
			.join("");

		const force_new = this.lan_count === 0;
		const mode = force_new ? "new" : this.state.lan_mode || "existing";
		const mode_picker = force_new
			? `<p class="itm-net-wizard__hint">${__(
					"No Local Area Network exists in this Landscape yet. Enter a title (and optional location) below — the LAN is created here so you stay in the wizard."
			  )}</p>`
			: `
			<p class="itm-net-wizard__hint" style="margin-top:1rem;">${__(
				"Which Local Area Network should own this subnet? Pick an existing LAN or create a new one without leaving the wizard."
			)}</p>
			<label style="margin-right:1rem;">
				<input type="radio" name="lan_mode" value="existing" ${
					mode === "existing" ? "checked" : ""
				}/> ${__("Existing")}
			</label>
			<label>
				<input type="radio" name="lan_mode" value="new" ${
					mode === "new" ? "checked" : ""
				}/> ${__("New")}
			</label>`;

		return `
			<div class="itm-net-wizard__help">
				<strong>${__("Step 1 — Purpose")}</strong>
				${__(
					"Pick the kind of network you are designing. Each profile suggests a typical size, private address range, and VLAN hint. You can change every value in later steps."
				)}
				<br/><br/>
				${__(
					"Example: choose Guest Wi-Fi for visitor access; the next steps will lean toward a larger subnet (more clients) and an isolated VLAN."
				)}
			</div>
			<p class="itm-net-wizard__hint">${__("Network purpose")}</p>
			${options}
			<div class="itm-net-wizard__lan-section" style="margin-top:1rem;">
				${mode_picker}
				<div class="itm-net-wizard__lan-existing" style="margin-top:0.75rem;"></div>
				<div class="itm-net-wizard__lan-new" style="margin-top:0.75rem;"></div>
			</div>
		`;
	}

	bind_lan_mode_ui() {
		const $wrap = this.dialog.fields_dict.body.$wrapper;
		const force_new = this.lan_count === 0;
		const apply_mode = (mode) => {
			this.state.lan_mode = mode;
			const $existing = $wrap.find(".itm-net-wizard__lan-existing");
			const $new = $wrap.find(".itm-net-wizard__lan-new");
			if (mode === "existing") {
				$existing.show();
				$new.hide();
				this.mount_existing_lan_control($existing);
			} else {
				$existing.hide();
				$new.show();
				this.mount_new_lan_controls($new);
			}
		};

		if (!force_new) {
			$wrap.find("[name=lan_mode]").on("change", (e) => {
				apply_mode(e.target.value);
			});
		}
		apply_mode(force_new ? "new" : this.state.lan_mode || "existing");
	}

	mount_existing_lan_control($parent) {
		$parent.empty();
		this.lan_control = frappe.ui.form.make_control({
			parent: $parent.get(0),
			df: {
				fieldtype: "Link",
				options: "ITM Local Area Network",
				label: __("Local Area Network"),
				fieldname: "itm_local_area_network",
				reqd: 1,
				get_query: () => ({
					filters: { itm_landscape: this.landscape },
				}),
			},
			render_input: true,
		});
		if (this.state.itm_local_area_network && !this.state.lan_created_in_wizard) {
			this.lan_control.set_value(this.state.itm_local_area_network);
		}
	}

	mount_new_lan_controls($parent) {
		$parent.empty();
		this.lan_title_control = frappe.ui.form.make_control({
			parent: $parent.get(0),
			df: {
				fieldtype: "Data",
				label: __("LAN Title"),
				fieldname: "lan_title",
				reqd: 1,
				default: this.state.lan_title || "",
			},
			render_input: true,
		});
		if (this.state.lan_title) {
			this.lan_title_control.set_value(this.state.lan_title);
		}

		const $loc = $('<div style="margin-top:0.5rem;"></div>').appendTo($parent);
		this.lan_location_control = frappe.ui.form.make_control({
			parent: $loc.get(0),
			df: {
				fieldtype: "Link",
				options: "ITM Location",
				label: __("Location"),
				fieldname: "itm_location",
				get_query: () => ({
					filters: {
						location_type: ["in", ["Site", "Building"]],
						disabled: 0,
					},
				}),
			},
			render_input: true,
		});
		if (this.state.itm_location) {
			this.lan_location_control.set_value(this.state.itm_location);
		}
	}

	html_size() {
		return `
			<div class="itm-net-wizard__help">
				<strong>${__("Step 2 — Size")}</strong>
				${__(
					"Tell us how many devices (clients) need addresses. We use that to suggest a subnet size, with some room to grow."
				)}
				<br/><br/>
				<strong>${__("What is Prefix length?")}</strong>
				${__(
					"In CIDR notation the prefix is the number after the slash (e.g. /24 in 192.168.1.0/24). A smaller number means a larger network (more addresses)."
				)}
				<br/><br/>
				${__("Common examples:")}
				<ul style="margin:0.35rem 0 0;padding-left:1.2rem;">
					<li><code>/24</code> — ${__("about 254 usable addresses (typical office VLAN)")}</li>
					<li><code>/23</code> — ${__("about 510 usable addresses (busy guest Wi-Fi)")}</li>
					<li><code>/16</code> — ${__("about 65,534 usable addresses (very large site)")}</li>
				</ul>
				<br/>
				${__(
					"Leave Prefix length empty to let us choose from expected clients. Only set it if you already know the size you want."
				)}
			</div>
			<div class="form-group">
				<label>${__("Expected clients")}</label>
				<input class="form-control" type="number" min="1" name="expected_clients" value="${
					this.state.expected_clients || 50
				}"/>
				<span class="itm-net-wizard__field-help">${__(
					"Example: 40 PCs and printers → enter 40 (or a bit more for growth)."
				)}</span>
			</div>
			<div class="form-group">
				<label>${__("Prefix length (optional override)")}</label>
				<input class="form-control" type="number" min="8" max="32" name="prefix_length" value="${
					this.state.prefix_length != null ? this.state.prefix_length : ""
				}" placeholder="${__("Auto")}"/>
				<span class="itm-net-wizard__field-help">${__(
					"Optional. Example: enter 24 for a classic /24. Leave blank for automatic sizing."
				)}</span>
			</div>
		`;
	}

	html_address() {
		const d = this.state.design || {};
		const conflicts = (this.state.conflicts || [])
			.map(
				(c) =>
					`${frappe.utils.escape_html(c.cidr)} (${frappe.utils.escape_html(
						c.lifecycle_status || ""
					)})`
			)
			.join(", ");
		return `
			<div class="itm-net-wizard__help">
				<strong>${__("Step 3 — Address")}</strong>
				${__(
					"We suggest a free IPv4 block in this Landscape. Network address + prefix together form the CIDR (e.g. 10.40.0.0 + 23 → 10.40.0.0/23). Mask and usable range are calculated for you."
				)}
				<br/><br/>
				${__(
					"Example: network 192.168.10.0 with prefix 24 means addresses 192.168.10.1–192.168.10.254 for hosts."
				)}
			</div>
			${
				this.state.profile_notes
					? `<p class="itm-net-wizard__hint">${frappe.utils.escape_html(
							this.state.profile_notes
					  )}</p>`
					: ""
			}
			${
				conflicts
					? `<div class="itm-net-wizard__warn">${__(
							"Possible conflicts in this landscape"
					  )}: ${conflicts}. ${__("Save will warn but not block.")}</div>`
					: ""
			}
			<div class="form-group">
				<label>${__("Network address")}</label>
				<input class="form-control" name="network_address" value="${frappe.utils.escape_html(
					this.state.network_address || d.network_address || ""
				)}"/>
				<span class="itm-net-wizard__field-help">${__(
					"First address of the block. Each part must be 0–255. Example: 10.40.0.0"
				)}</span>
			</div>
			<div class="form-group">
				<label>${__("Prefix length")}</label>
				<input class="form-control" type="number" min="0" max="32" name="prefix_length" value="${
					this.state.prefix_length != null ? this.state.prefix_length : d.prefix_length || 24
				}"/>
				<span class="itm-net-wizard__field-help">${__(
					"Same meaning as on the Size step (the /xx in CIDR). Example: 24"
				)}</span>
			</div>
			<div class="form-group">
				<label>${__("VLAN tag")}</label>
				<input class="form-control" type="number" name="vlan_tag" value="${
					this.state.vlan_tag != null ? this.state.vlan_tag : ""
				}"/>
				<span class="itm-net-wizard__field-help">${__(
					"Optional switch/VLAN id for this subnet. Example: 40 for guest Wi-Fi."
				)}</span>
			</div>
			<pre class="itm-net-wizard__design">${__("Mask")}: ${frappe.utils.escape_html(
				d.subnet_mask || "—"
			)}
${__("CIDR")}: ${frappe.utils.escape_html(d.cidr || "—")}
${__("Usable")}: ${frappe.utils.escape_html(String(d.first_usable || "—"))} – ${frappe.utils.escape_html(
				String(d.last_usable || "—")
			)} (${d.usable_hosts != null ? d.usable_hosts : "—"})</pre>
		`;
	}

	html_infra() {
		const roles = ["gateway", "dhcp", "dns_1", "dns_2", "ntp_1", "ntp_2"];
		const rows = roles
			.map(
				(role) => `
			<div class="itm-net-wizard__role-row itm-net-wizard__role" data-role="${role}">
				<div class="itm-net-wizard__role-link"></div>
				<button type="button" class="btn btn-default btn-sm itm-net-wizard__role-create">${__(
					"New host"
				)}</button>
			</div>`
			)
			.join("");
		return `
			<div class="itm-net-wizard__help">
				<strong>${__("Step 4 — Infrastructure")}</strong>
				${__(
					"Optionally link the Host Items that will provide network services for this subnet. All fields are optional — you can finish planning and assign hosts later."
				)}
				<br/><br/>
				${__("Typical roles:")}
				<ul style="margin:0.35rem 0 0;padding-left:1.2rem;">
					<li><strong>${__("Gateway")}</strong> — ${__("router / default gateway for clients")}</li>
					<li><strong>${__("DHCP")}</strong> — ${__("hands out IP addresses automatically")}</li>
					<li><strong>${__("DNS")}</strong> — ${__("name resolution (primary / secondary)")}</li>
					<li><strong>${__("NTP")}</strong> — ${__("time sync (primary / secondary)")}</li>
				</ul>
				<br/>
				${__(
					"Example: pick your firewall as Gateway, and an existing domain controller as DNS 1. Use “New host” only when the device is not in ITM yet."
				)}
			</div>
			${rows}
		`;
	}

	html_review() {
		const d = this.state.design || {};
		const lan_label = this.state.lan_title || this.state.itm_local_area_network || "";
		return `
			<div class="itm-net-wizard__help">
				<strong>${__("Step 5 — Review")}</strong>
				${__(
					"Check the summary, then create the subnet with lifecycle Implementing. Address or VLAN overlaps only warn — you can still create the record for planning."
				)}
			</div>
			<pre class="itm-net-wizard__design">${__("Purpose")}: ${frappe.utils.escape_html(
				this.state.purpose_profile
			)}
${__("LAN")}: ${frappe.utils.escape_html(lan_label)}
${__("CIDR")}: ${frappe.utils.escape_html(d.cidr || "")}
${__("VLAN")}: ${this.state.vlan_tag != null ? this.state.vlan_tag : "—"}
${__("Gateway")}: ${frappe.utils.escape_html(this.state.gateway || "—")}
${__("DHCP")}: ${frappe.utils.escape_html(this.state.dhcp || "—")}
${__("DNS")}: ${frappe.utils.escape_html(this.state.dns_1 || "—")} / ${frappe.utils.escape_html(
				this.state.dns_2 || "—"
			)}
${__("NTP")}: ${frappe.utils.escape_html(this.state.ntp_1 || "—")} / ${frappe.utils.escape_html(
				this.state.ntp_2 || "—"
			)}</pre>
		`;
	}

	quick_create_host(field, ctrl) {
		const d = new frappe.ui.Dialog({
			title: __("New Host Item"),
			fields: [
				{
					fieldtype: "Data",
					fieldname: "title",
					label: __("Title"),
					reqd: 1,
				},
			],
			primary_action_label: __("Create"),
			primary_action: (values) => {
				frappe.call({
					method: "it_management.it_management.utils.networking.quick_create_host_item",
					args: {
						title: values.title,
						itm_landscape: this.landscape,
					},
					freeze: true,
					callback: (r) => {
						if (r.message && r.message.name) {
							ctrl.set_value(r.message.name);
							d.hide();
						}
					},
				});
			},
		});
		d.show();
	}

	async create() {
		const r = await frappe.call({
			method: "it_management.it_management.utils.networking.create_subnet_from_wizard",
			args: {
				values: {
					itm_local_area_network: this.state.itm_local_area_network,
					network_address: this.state.network_address,
					prefix_length: this.state.prefix_length,
					vlan_tag: this.state.vlan_tag,
					gateway: this.state.gateway,
					dhcp: this.state.dhcp,
					dns_1: this.state.dns_1,
					dns_2: this.state.dns_2,
					ntp_1: this.state.ntp_1,
					ntp_2: this.state.ntp_2,
					lifecycle_status: "Implementing",
					note: __("Created via Plan subnet wizard ({0})", [this.state.purpose_profile]),
				},
			},
			freeze: true,
			freeze_message: __("Creating subnet…"),
		});
		if (!r.message) {
			return;
		}
		this.dialog.hide();
		frappe.show_alert({
			message: __("Created subnet {0}", [r.message.cidr || r.message.name]),
			indicator: "green",
		});
		if (this.on_created) {
			this.on_created(r.message);
		}
		frappe.set_route("Form", "ITM Subnet", r.message.name);
	}
};
