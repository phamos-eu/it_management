frappe.ui.form.on('Sales Invoice', {
	refresh: function (frm) {
		cur_frm.add_custom_button('Issue', function () { frm.trigger('get_issue_ts') }, __("Get items from"));
		cur_frm.add_custom_button('IT Service Report', function () { frm.trigger('get_it_service_report_ts') }, __("Get items from"));
		cur_frm.add_custom_button('Task', function () { frm.trigger('get_task_ts') }, __("Get items from"));
		cur_frm.add_custom_button('Project', function () { frm.trigger('get_project_ts') }, __("Get items from"));
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
