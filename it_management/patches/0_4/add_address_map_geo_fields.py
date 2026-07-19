# Copyright (c) 2026, IT Management contributors
# For license information, please see license.txt

from __future__ import unicode_literals


def execute():
	"""Add latitude/longitude custom fields on Address for Map View."""
	from it_management.it_management.utils.address_geo_fields import ensure_address_geo_fields

	ensure_address_geo_fields()
