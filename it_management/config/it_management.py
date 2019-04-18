from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "label": _("Configuration Management"),
            # "icon": "fa fa-bank",
            "items": [
                {
                    "type": "doctype",
                    "name": "Configuration Item",
                    "label": _("Configuration Item"),
                    "description": _("Configuration Item")
                },
                {
                    "type": "doctype",
                    "name": "Solution",
                    "label": _("Solution"),
                    "description": _("Solution")
                },
                {
                    "type": "doctype",
                    "name": "Socket",
                    "label": _("Socket"),
                    "description": _("Socket")
                },
                {
                    "type": "doctype",
                    "name": "Network Jack",
                    "label": _("Network Jack"),
                    "description": _("Network Jack")
                },
            ]
        },
        {
            "label": _("Software"),
            # "icon": "fa fa-wrench",
            "items": [
                {
                    "type": "doctype",
                    "name": "Licence",
                    "label": _("Licence"),
                    "description": _("Licence")
                },
                {
                    "type": "doctype",
                    "name": "Software Instance",
                    "label": _("Software Instance"),
                    "description": _("Software Instance")
                },
                {
                    "type": "doctype",
                    "name": "User Account",
                    "label": _("User Account"),
                    "description": _("User Account")
                },
                {
                    "type": "doctype",
                    "name": "User Group",
                    "label": _("User Group"),
                    "description": _("User Group")
                },
                {
                    "type": "doctype",
                    "name": "Software Version",
                    "label": _("Software Version"),
                    "description": _("Software Version")
                }
            ]
        }
    ]
