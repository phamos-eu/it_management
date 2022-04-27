import frappe

def execute():
    """
    Code to effect `Configuration Item Table` renamed to `Host Item`
    Change will take effect when latest is run could also run script from your `bench console`
    """
    if frappe.db.table_exists(
        "Configuration Item") and not frappe.db.table_exists(
            "Host Item"):
        frappe.rename_doc("DocType", "Configuration Item","Host Item", force=True )
        frappe.reload_doc("it_management", "doctype", "host_item")