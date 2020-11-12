var it_management_sales_invoice_reload_after_save_tmp = false

frappe.ui.form.on('Sales Invoice', {
	save_and_reload(frm){
		it_management_sales_invoice_reload_after_save_tmp = true
		frm.save();
	},
	after_save(frm){
		pull_timesheets_on_save(frm)
	},
	refresh: function (frm) {
		//cur_frm.add_custom_button('Issue', function () { frm.trigger('get_issue_ts') }, __("Get items from"));
		//cur_frm.add_custom_button('IT Service Report', function () { frm.trigger('get_it_service_report_ts') }, __("Get items from"));
		//cur_frm.add_custom_button('Task', function () { frm.trigger('get_task_ts') }, __("Get items from"));
		//cur_frm.add_custom_button('Project', function () { frm.trigger('get_project_ts') }, __("Get items from"));
	},
	onload: function(frm) {
		filter_tasks(frm);
	},
	project: function(frm) {
		filter_tasks(frm);
	},
	get_issue_ts: function (frm) {
		get_ts_dialog(frm, 'Issue');
	},
	get_it_service_report_ts: function (frm) {
		get_ts_dialog(frm, 'IT Service Report');
	},
	get_task_ts: function (frm) {
		get_ts_dialog(frm, 'Task');
	},
	get_project_ts: function (frm) {
		get_ts_dialog(frm, 'Project');
	}
});

function pull_timesheets_on_save(frm){
	//Create an array of timesheet names already in the childtable
	var timesheet_items = frm.doc.timesheets
	var existing_ts = []
	var existing_sales_invoice_ts = []
	for (let i = 0; i < timesheet_items.length; i++) {
		const element = timesheet_items[i]["time_sheet"];
		const sales_invoice_ts = timesheet_items[i]["name"];
		existing_ts.push(element);
		existing_sales_invoice_ts.push(sales_invoice_ts);
	}

	//Go through all Tasks in Multiselect
	frappe.call({
		method: "it_management.utils.add_sales_invoice_timesheets",
		args : { 'data' : {
			"tasks" : frm.doc.tasks,
			"existing_ts" : existing_ts,
			"existing_sales_invoice_ts" : existing_sales_invoice_ts,
			"sales invoice" : frm.doc.name,
			"pull_timesheets_on_save" : frm.doc.pull_timesheets_on_save
			}
		},
		callback: function(r) {
			if (r.message) {
				console.log(r.message);
			}
			if(it_management_sales_invoice_reload_after_save_tmp){
				frm.reload_doc();
				location.reload();
				it_management_sales_invoice_reload_after_save_tmp = false
			}
			
		}
	});
}

function filter_tasks(frm){
	frm.set_query("tasks", function() {  
		if (frm.doc.project) {   
			return {
				'filters': {
					"project" : frm.doc.project
				}
			};
		}
	});
}

function get_ts_dialog(frm, source) {
	var source_ref = '';
	var fields = [];
	if (source == 'Issue') {
		source_ref = 'issue';
		fields = [
			{
				fieldtype: 'Link',
				label: __('Issue'),
				fieldname: 'issue',
				options: 'Issue',
				reqd: 1
			}
		]
	}
	if (source == 'IT Service Report') {
		source_ref = 'it_service_report';
		fields = [
			{
				fieldtype: 'Link',
				label: __('IT Service Report'),
				fieldname: 'it_service_report',
				options: 'IT Service Report',
				reqd: 1
			}
		]
	}
	if (source == 'Task') {
		source_ref = 'task';
		fields = [
			{
				fieldtype: 'Link',
				label: __('Task'),
				fieldname: 'task',
				options: 'Task',
				reqd: 1
			}
		]
	}
	if (source == 'Project') {
		source_ref = 'project';
		fields = [
			{
				fieldtype: 'Link',
				label: __('Project'),
				fieldname: 'project',
				options: 'Project',
				reqd: 1
			}
		]
	}
	const dialog = new frappe.ui.Dialog({
		title: __('Timesheets of'),
		fields: fields
	})

	dialog.set_primary_action(__('Get Timesheets'), (d) => {
		frappe.call({
			method: "it_management.utils.get_timesheets_from_source",
			args: {
				"source": source,
				"source_ref": d[source_ref]
			},
			callback: function(r) {
				if (r.message) {
					var timesheets = r.message;
					var i;
					for (i=0; i<timesheets.length; i++) {
						console.log(timesheets[i]);
					
						var child = cur_frm.add_child('timesheets');
						frappe.model.set_value(child.doctype, child.name, 'time_sheet', timesheets[i].parent);
						frappe.model.set_value(child.doctype, child.name, 'billing_hours', timesheets[i].billing_hours);
						frappe.model.set_value(child.doctype, child.name, 'billing_amount', timesheets[i].billing_amt);
						frappe.model.set_value(child.doctype, child.name, 'timesheet_detail', timesheets[i].name);
						
					}
					cur_frm.refresh_field('timesheets');
					dialog.hide();
				}
			}
		});
	})

	dialog.show();
}
