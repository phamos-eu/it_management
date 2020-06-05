cur_frm.dashboard.add_transactions([
    {
        'items': [
            'Material Request'
        ],
        'label': 'Activity'
    }
]);

frappe.ui.form.on('Task', {
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
	},
	refresh: function (frm) {
		cur_frm.add_custom_button('Issue', function () { frm.trigger('make_ticket') }, 'Make');
		cur_frm.add_custom_button('Timesheet', function () { frm.trigger('add_activity') }, __("Make"));
		cur_frm.add_custom_button('Purchase Order', function () { frm.trigger('make_purchase_order') }, __("Make"));
		cur_frm.add_custom_button('Delivery Note', function () { frm.trigger('make_delivery_note') }, __("Make"));
		cur_frm.add_custom_button('IT Service Report', function () { frm.trigger('make_it_service_report') }, __("Make"));
		cur_frm.add_custom_button('Sales Invoice', function () { frm.trigger('make_sales_invoice') }, __("Make"));
	},
	make_ticket: function (frm) {
		let options = {
			'doctype': 'Issue',
			'subject': frm.get_field('subject').get_value(),
			'description': frm.get_field('description').get_value(),
			//'priority': "Mittel",
			'task': frm.doc.name,
			'project': frm.get_field('project').get_value(),
			'customer': frm.get_field('customer').get_value()
		};

		frappe.db.insert(options).then((issue) => {
			frappe.call({
				method: "it_management.utils.relink_email",
				args: {
					"doctype": "Task",
					"name": frm.doc.name,
					"issue": issue.name,
				}
			}).then(() => frm.refresh());

			frappe.show_alert({
				indicator: 'green',
				message: __("Issue ${issue.name} created."), 
			}).click(() => {
				frappe.set_route('Form', 'Issue', issue.name)
			});

			frm.timeline.insert_comment(`${issue.doctype} <a href="${frappe.utils.get_form_link(issue.doctype, issue.name)}">${issue.name}</a> created.`);
		});
	},
	add_activity: function (frm) {
		activity_dialog(frm);
	},
	make_purchase_order: function (frm) {
		if (frm.is_new()) {
			show_alert(__('Save the document first.'));
			return;
		}
		if (frm.doc.issue) {
			frappe.new_doc("Purchase Order", {
				"issue": frm.doc.issue
			});
		} else {
			show_alert(__('Create/Link an Issue first.'));
			return;
		}
	},
	make_delivery_note: function (frm) {
		if (frm.is_new()) {
			show_alert(__('Save the document first.'));
			return;
		}
		if (frm.doc.project) {
			frappe.new_doc("Delivery Note", {
				//"customer": frm.doc.customer,
				"project" : frm.doc.project,
				"issue": frm.doc.name
			});
		} else {
			show_alert(__('Create/Link a Project first.'));
			return;
		}
	},
	make_it_service_report: function (frm) {
		if (frm.is_new()) {
			show_alert(__('Save the document first.'));
			return;
		}
		if (frm.doc.project) {
			frappe.new_doc("IT Service Report", {
				"issue": frm.doc.issue,
				"project": frm.doc.project,
				"task": frm.doc.name
			});
		} else {
			show_alert(__('Create/Link a Project first.'));
			return;
		}
	},
	make_sales_invoice: function (frm) {
		let dialog = new frappe.ui.Dialog({
			title: __("Select Item (optional)"),
			fields: [
				{"fieldtype": "Link", "label": __("Item Code"), "fieldname": "item_code", "options":"Item"},
				{"fieldtype": "Link", "label": __("Customer"), "fieldname": "customer", "options":"Customer"}
			]
		});

		dialog.set_primary_action(__("Make Sales Invoice"), () => {
			var args = dialog.get_values();
			if(!args) return;
			dialog.hide();
			return frappe.call({
				type: "GET",
				method: "it_management.utils.make_sales_invoice",
				args: {
					"source_name": frm.doc.name,
					"item_code": args.item_code,
					"customer": args.customer
				},
				freeze: true,
				callback: function(r) {
					if(!r.exc) {
						frappe.model.sync(r.message);
						frappe.set_route("Form", r.message.doctype, r.message.name);
					}
				}
			});
		});
		dialog.show();
	}
});

function activity_dialog(frm) {
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
				fieldtype: 'Datetime',
				fieldname: 'to_time',
				label: __('To Time'),
				default: frappe.datetime.now_datetime(),
			},
			// {
			// 	fieldtype: 'Float',
			// 	fieldname: 'hours',
			// 	label: __('Hours'),
			// 	default: 0.25
			// },
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
		const hours = moment(dialog.to_time).diff(moment(dialog.from_time), "seconds") / 3600;

		let timesheet = {
			doctype: 'Timesheet',
			issue: frm.doc.issue,
			note: dialog.note,
			time_logs: [
				{
					activity_type: dialog.activity_type,
					from_time: dialog.from_time,
					to_time: dialog.to_time,
					// to_time: (new moment(dialog.from_time)).add(dialog.hours, 'hours').format('YYYY-MM-DD HH:mm:ss'),
					hours: hours,
					project: frm.doc.project,
					task: frm.doc.name,
					billable: 1,
					billing_hours: hours,
				}
			],
			docstatus: 1
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
				if (dialog.note!="<div><br></div>") {
					frm.timeline.insert_comment(dialog.note);
				} else {
					frm.timeline.insert_comment(__("Timesheet created"));
				}
			});
	})

	activity.show();
}
