frappe.ui.form.on('Project', {
	refresh: function (frm) {
		cur_frm.add_custom_button('Purchase Order', function () { frm.trigger('make_purchase_order') }, __("Make"));
		cur_frm.add_custom_button('Delivery Note', function () { frm.trigger('make_delivery_note') }, __("Make"));
		cur_frm.add_custom_button('Sales Invoice', function () { frm.trigger('make_sales_invoice') }, __("Make"));
	},
	add_activity: function (frm) {
		activity_dialog(frm);
	},
	make_purchase_order: function (frm) {
		if (frm.is_new()) {
			show_alert(__('Save the document first.'));
			return;
		} else {
			frappe.new_doc("Purchase Order", {
				"project": frm.doc.name
			});
		}
	},
	make_delivery_note: function (frm) {
		if (frm.is_new()) {
			show_alert(__('Save the document first.'));
			return;
		} else {
			frappe.new_doc("Delivery Note", {
				"project" : frm.doc.name
			});
		}
	},
	make_sales_invoice: function (frm) {
		let dialog = new frappe.ui.Dialog({
			title: __("Select Item (optional)"),
			fields: [
				{"fieldtype": "Link", "label": __("Customer"), "fieldname": "customer", "options":"Customer", "default": cur_frm.doc.customer}
			]
		});

		dialog.set_primary_action(__("Make Sales Invoice"), () => {
			var args = dialog.get_values();
			if(!args) return;
			dialog.hide();
			frappe.new_doc("Sales Invoice", {
				"project": frm.doc.name,
				"customer": args.customer
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
			//issue: frm.doc.issue,
			note: dialog.note,
			time_logs: [
				{
					activity_type: dialog.activity_type,
					from_time: dialog.from_time,
					to_time: dialog.to_time,
					// to_time: (new moment(dialog.from_time)).add(dialog.hours, 'hours').format('YYYY-MM-DD HH:mm:ss'),
					hours: hours,
					project: frm.doc.name,
					//task: frm.doc.name,
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
