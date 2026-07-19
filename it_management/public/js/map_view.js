// Copyright (c) 2026, IT Management contributors
// For license information, please see license.txt

/**
 * Enable Frappe Map View for DocTypes that link to Address.
 *
 * Frappe already ships Map View (Leaflet + OpenStreetMap). It appears in the
 * view switcher when listview_settings.get_coords_method is set, or when the
 * DocType has latitude/longitude / Geolocation fields.
 *
 * Markers are auto-framed with padding so two hits in Germany stay framed
 * tightly, while hits in Paris + London expand the viewport with a border.
 */

frappe.provide("frappe.listview_settings");
frappe.provide("it_management.map_view");

it_management.map_view.ADDRESS_LINK_DOCTYPES = [
	"ITM Location",
	"Location",
	"ITM Trip",
	"Trip",
	"IT Service Report",
];

it_management.map_view.COORDS_METHOD =
	"it_management.it_management.utils.map_view.get_coords";

it_management.map_view.FIT_BOUNDS_OPTIONS = {
	padding: [48, 48],
	maxZoom: 16,
};

(function register_address_map_views() {
	it_management.map_view.ADDRESS_LINK_DOCTYPES.forEach((doctype) => {
		const existing = frappe.listview_settings[doctype] || {};
		frappe.listview_settings[doctype] = Object.assign({}, existing, {
			get_coords_method: it_management.map_view.COORDS_METHOD,
		});
	});
})();

/** Fit map frame to markers with a small border around the hit area. */
it_management.map_view.fit_marker_bounds = function (map, marker_layer) {
	if (!map || !marker_layer) {
		return;
	}
	const bounds = marker_layer.getBounds();
	if (!bounds || !bounds.isValid()) {
		return;
	}
	map.fitBounds(bounds, it_management.map_view.FIT_BOUNDS_OPTIONS);
};

/** Patch core MapView once it is available so all map views get padded bounds. */
it_management.map_view.patch_fit_bounds = function () {
	if (!frappe.views || !frappe.views.MapView) {
		return;
	}
	if (frappe.views.MapView.prototype.__itm_fit_bounds_patched) {
		return;
	}

	const original = frappe.views.MapView.prototype.render_map_data;
	frappe.views.MapView.prototype.render_map_data = function () {
		if (this.markerLayer) {
			this.map.removeLayer(this.markerLayer);
		}

		if (!(this.coords && this.coords.features && this.coords.features.length)) {
			return;
		}

		this.markerLayer = L.featureGroup();

		this.coords.features.forEach((feature) => {
			const label =
				(feature.properties &&
					(feature.properties.title || feature.properties.name)) ||
				"";
			const popup = frappe.utils.get_form_link(
				this.doctype,
				feature.properties.name,
				true,
				label
			);
			const marker = L.geoJSON(feature).bindPopup(popup);
			this.markerLayer.addLayer(marker);
		});

		this.markerLayer.addTo(this.map);
		it_management.map_view.fit_marker_bounds(this.map, this.markerLayer);
	};

	// Keep a reference in case callers expect the original
	frappe.views.MapView.prototype.__itm_original_render_map_data = original;
	frappe.views.MapView.prototype.__itm_fit_bounds_patched = true;
};

it_management.map_view.schedule_patch = function () {
	it_management.map_view.patch_fit_bounds();
	if (frappe.views && frappe.views.MapView && frappe.views.MapView.prototype.__itm_fit_bounds_patched) {
		return;
	}
	// list.bundle (MapView) may load after app_include_js
	setTimeout(it_management.map_view.schedule_patch, 400);
};

$(document).on("app_ready", () => {
	it_management.map_view.schedule_patch();
});

if (frappe.router && frappe.router.on) {
	frappe.router.on("change", () => {
		it_management.map_view.patch_fit_bounds();
	});
}

it_management.map_view.schedule_patch();
