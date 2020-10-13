// Copyright (c) 2020, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

frappe.ui.form.on('Trip', {
	setup: function(frm){
	},
	onload: function(frm) {
		if(frm.is_new()){
		  frappe.model.get_value('User',user,["full_name"], function(full_name){
			frappe.model.get_value('Employee',{'employee_name':full_name.full_name},["name"],function(emp_name){
			  frm.set_value("employee",emp_name.name);
			});
		  });
		}
	  }
});
