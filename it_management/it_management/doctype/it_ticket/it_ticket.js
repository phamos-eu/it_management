// Copyright (c) 2019, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

frappe.ui.form.on('IT Ticket', {
	onload: function (frm) {
		// restrict Dynamic Links to IT Mnagement
		frm.set_query('dynamic_type', 'it_management_table', function () {
			return {
				'filters': {
					'module': 'IT Management',
					'istable': 0,
				}
			};
		});
		frm.set_query('contact', function () {
			// restrict contact to customer
			if (frm.doc.customer) {
				return {
					filters: {
						link_doctype: 'Customer',
						link_name: frm.doc.customer,
					}
				};
			}
		});
		frm.set_query('project', function () {
			// restrict project to customer
			if (frm.doc.customer) {
				return {
					'filters': {
						'customer': frm.doc.customer,
					}
				};
			}
		});
		frm.set_query('task', function () {
			// restrict tasks to project
			if (frm.doc.project) {
				return {
					'filters': {
						'project': frm.doc.project,
					}
				};
			}
		});
	},
	refresh: function (frm) {
		if (!frm.is_new()) {
			frm.add_custom_button('Add Activity', function () { frm.trigger('add_activity') });
			frappe.contacts.render_address_and_contact(frm);
			// hide "New Contact" Button
			$('.btn-contact').hide();
		}
	},
	add_activity: function (frm) {
		it_ticket_activity_dialog(frm);
	},
});

function it_ticket_activity_dialog(frm) {
	if (frm.is_new()) {
		show_alert(__('Save the document first.'));
		return;
	}
	const activity = new frappe.ui.Dialog({
		title: __('New Activity'),
		fields: [
			{
				fieldtype: 'Datetime',
				label: __('From Time'),
				fieldname: 'from_time',
				default: frappe.datetime.now_datetime()
			},
			{
				fieldtype: 'Link',
				label: __('Activity Type'),
				fieldname: 'activity_type',
				options: 'Activity Type',
			},
			{
				fieldtype: 'Column Break',
				fieldname: 'cb_1',
			},
			{
				fieldtype: 'Float',
				fieldname: 'hours',
				label: __('Hours'),
				default: 0.25
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

	activity.set_primary_action(__('Save'), (dialog) => {
		frm.timeline.insert_comment('Comment', dialog.note);

		let timesheet = {
			doctype: 'Timesheet',
			it_ticket: frm.doc.name,
			note: dialog.note,
			time_logs: [
				{
					activity_type: dialog.activity_type,
					from_time: dialog.from_time,
					to_time: (new moment(dialog.from_time)).add(dialog.hours, 'hours').format('YYYY-MM-DD HH:mm:ss'),
					hours: dialog.hours,
					project: frm.doc.project,
					task: frm.doc.task,
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
					timesheet['employee'] = employee.name;
					timesheet['company'] = employee.company;
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
