# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ITMSocket(Document):
	def validate(self):
		self._validate_room_location()
		self._sync_landscape_from_location()
		self._validate_endpoint()

	def on_update(self):
		self._sync_endpoint_pair()

	def after_insert(self):
		self._sync_endpoint_pair()

	def on_trash(self):
		if self.endpoint_socket and frappe.db.exists("ITM Socket", self.endpoint_socket):
			other = frappe.db.get_value("ITM Socket", self.endpoint_socket, "endpoint_socket")
			if other == self.name:
				frappe.db.set_value(
					"ITM Socket",
					self.endpoint_socket,
					{"endpoint_socket": None, "endpoint_location": None},
					update_modified=False,
				)

	def _validate_room_location(self):
		if not self.itm_location:
			frappe.throw(_("Location (Room) is required."), title=_("Missing Location"))
		location_type = frappe.db.get_value("ITM Location", self.itm_location, "location_type")
		if location_type != "Room":
			frappe.throw(
				_("ITM Socket location must be a Room (got {0}).").format(_(location_type or "none")),
				title=_("Invalid Location"),
			)

	def _sync_landscape_from_location(self):
		self.itm_landscape = frappe.db.get_value(
			"ITM Location", self.itm_location, "itm_landscape"
		)

	def _validate_endpoint(self):
		if not self.endpoint_socket:
			self.endpoint_location = None
			return
		if self.endpoint_socket == self.name:
			frappe.throw(
				_("A socket cannot be its own endpoint."),
				title=_("Invalid Endpoint"),
			)
		self.endpoint_location = frappe.db.get_value(
			"ITM Socket", self.endpoint_socket, "itm_location"
		)

	def _sync_endpoint_pair(self):
		"""Keep endpoint_socket bidirectional; clear the previous partner when changed."""
		before = self.get_doc_before_save()
		old_endpoint = before.endpoint_socket if before else None
		new_endpoint = self.endpoint_socket

		if old_endpoint and old_endpoint != new_endpoint and frappe.db.exists("ITM Socket", old_endpoint):
			if frappe.db.get_value("ITM Socket", old_endpoint, "endpoint_socket") == self.name:
				frappe.db.set_value(
					"ITM Socket",
					old_endpoint,
					{"endpoint_socket": None, "endpoint_location": None},
					update_modified=False,
				)

		if not new_endpoint or not frappe.db.exists("ITM Socket", new_endpoint):
			return

		other_endpoint = frappe.db.get_value("ITM Socket", new_endpoint, "endpoint_socket")
		if other_endpoint == self.name:
			return

		# If B was paired with C, clear C first
		if other_endpoint and other_endpoint != self.name and frappe.db.exists("ITM Socket", other_endpoint):
			if frappe.db.get_value("ITM Socket", other_endpoint, "endpoint_socket") == new_endpoint:
				frappe.db.set_value(
					"ITM Socket",
					other_endpoint,
					{"endpoint_socket": None, "endpoint_location": None},
					update_modified=False,
				)

		frappe.db.set_value(
			"ITM Socket",
			new_endpoint,
			{"endpoint_socket": self.name, "endpoint_location": self.itm_location},
			update_modified=False,
		)
