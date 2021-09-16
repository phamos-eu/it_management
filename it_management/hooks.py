# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "it_management"
app_title = "IT Management"
app_publisher = "IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups,"
app_description = "Management von IT-Bausteinen. Hierzu gehören"
app_icon = "octicon octicon-checklist"
app_color = "blue"
app_email = "Dienstleistungsverträge, Accounts und Internetleistungen.info@tueit.de"
app_license = "GPL"

# Includes in <head>
# ------------------

# Custom Error Handling for Custom Error
fixtures = [‘Property Setter’]

# include js, css files in header of desk.html
# app_include_css = "/assets/it_management/css/it_management.css"
app_include_js = ["/assets/it_management/js/itm_utils.js"]

# include js, css files in header of web template
# web_include_css = "/assets/it_management/css/it_management.css"
# web_include_js = "/assets/it_management/js/it_management.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Communication" : "public/js/communication.js",
    "Issue" : "public/js/issue.js",
    "Task" : "public/js/task.js",
    "Project" : "public/js/project.js",
    "Sales Invoice" : "public/js/sales_invoice.js",
    "Sales Invoice Timesheet" : "public/js/sales_invoice_timesheets.js",
    "Maintenance Visit" : "public/js/maintenance_visit.js",
    "Event" : "public/js/event.js",
    "Item" : "public/js/item.js",
    "Customer" : "public/js/customer.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "it_management.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "it_management.install.before_install"
# after_install = "it_management.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "it_management.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"it_management.tasks.all"
# 	],
# 	"daily": [
# 		"it_management.tasks.daily"
# 	],
# 	"hourly": [
# 		"it_management.tasks.hourly"
# 	],
# 	"weekly": [
# 		"it_management.tasks.weekly"
# 	]
# 	"monthly": [
# 		"it_management.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "it_management.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "it_management.event.get_events"
# }

override_doctype_dashboards = {
    "Event": "it_management.event.get_dashboard_data",
    "Contact": "it_management.contact.get_dashboard_data"
}
