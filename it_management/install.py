# Copyright (c) 2026, IT Management contributors
# For license information, please see license.txt

from __future__ import unicode_literals


def after_install():
	_ensure_map_view_setup()


def after_migrate():
	_ensure_map_view_setup()


def _ensure_map_view_setup():
	from it_management.it_management.utils.address_geo_fields import ensure_address_geo_fields

	ensure_address_geo_fields()
