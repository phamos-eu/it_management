// Copyright (c) 2019, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

frappe.ui.form.on('Incident', {
	onload: function(frm){
		// restrict Dynamic Links to IT Mnagement
		frm.set_query("dynamic_type", "it_management_table", function() {
			return {
				"filters": {
					"module": "IT Management",
					"istable": 0,
				}
			};
		});
	},
	refresh: function (frm) {
		frm.add_custom_button('Add Activity', function () { frm.trigger('add_activity') });
	},
	add_activity: function (frm) {
		incident_activity_dialog(frm);
	},
});

function incident_activity_dialog(frm) {
	const activity = new frappe.ui.Dialog({
		title: __('New Activity'),
		fields: [
			{
				fieldtype: 'Datetime',
				label: __("From Time"),
				fieldname: 'from_time',
				default: frappe.datetime.now_datetime()
			},
			{
				fieldtype: 'Column Break',
				fieldname: 'cb_1',
			},
			{
				fieldtype: 'Float',
				fieldname: 'hours',
				label: __("Hours"),
				default: 0.25
			},
			{
				fieldtype: 'Check',
				fieldname: 'billable',
				label: __("Bill"),
				default: 1
			},
			{
				fieldtype: 'Section Break',
				fieldname: 'sb_1',
			},
			{
				fieldtype: 'Text Editor',
				fieldname: 'note',
			},
		],
	})

	activity.set_primary_action(__("Save"), (dialog) => {
		frm.timeline.insert_comment("Comment", dialog.note);

		let timesheet = {
			doctype: "Timesheet",
			note: dialog.note,
			time_logs: [
				{
					from_time: dialog.from_time,
					hours: dialog.hours,
					project: frm.project,
					billable: dialog.billable,
				}
			]
		};

		// Get employee for logged user
		const options = { user_id: frappe.session.user };
		const fields = ['name', 'company'];

		frappe.db.get_value('Employee', options, fields)
			.then(({ message: employee }) => {
				if (employee) {
					timesheet["employee"] = employee.name;
					timesheet["company"] = employee.company;
				}
			})
			.then(() => {
				frappe.db.insert(timesheet);
			})
			.then(() => {
				activity.hide();
				activity.clear();
			});
	})

	activity.show();
}
