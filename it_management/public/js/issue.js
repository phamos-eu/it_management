// Copyright (c) 2019, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

cur_frm.dashboard.add_transactions([
    {
        'items': [
            'Timesheet',
			'Purchase Order',
			'Delivery Note',
			'IT Service Report'
        ],
        'label': 'Activity'
    }
]);

frappe.ui.form.on('Issue', {
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
		/* frm.set_query('task', function () {
			// restrict tasks to project
			if (frm.doc.project) {
				return {
					'filters': {
						'project': frm.doc.project,
					}
				};
			}
		}); */
	},
	refresh: function (frm) {
		if (!frm.is_new()) {
			frm.add_custom_button('Add Activity', function () { frm.trigger('add_activity') });
			frm.add_custom_button('Purchase Order', function () { frm.trigger('make_purchase_order') }, __("Make"));
			frm.add_custom_button('Delivery Note', function () { frm.trigger('make_delivery_note') }, __("Make"));
			frm.add_custom_button('IT Service Report', function () { frm.trigger('make_it_service_report') }, __("Make"));
			frm.add_custom_button('Sales Invoice', function () { frm.trigger('make_sales_invoice') }, __("Make"));
		}
		//frm.trigger('render_contact');
	},
	contact: function (frm) {
        //frm.trigger('render_contact');
    },
	render_contact: function (frm) {
		if (frm.doc.contact && frm.doc.hasOwnProperty('__onload')) {
			frappe.contacts.render_address_and_contact(frm);
			// hide "New Contact" Button
			$('.btn-contact').hide();
		} else {
			cur_frm.fields_dict.contact_html.html();
		}
	},
	add_activity: function (frm) {
		activity_dialog(frm);
	},
	make_purchase_order: function (frm) {
		frappe.new_doc("Purchase Order", {
			"issue": frm.doc.name
		});
	},
	make_delivery_note: function (frm) {
		frappe.new_doc("Delivery Note", {
			"customer": frm.doc.customer,
			"project" : frm.doc.project,
			"issue": frm.doc.name
		});
	},
	make_it_service_report: function (frm) {
		frappe.new_doc("IT Service Report", {
			"issue": frm.doc.name,
			"project": frm.doc.project/*,
			"task": frm.doc.task*/
		});
	},
	make_sales_invoice: function (frm) {
		let dialog = new frappe.ui.Dialog({
			title: __("Select Item (optional)"),
			fields: [
				{"fieldtype": "Link", "label": __("Item Code"), "fieldname": "item_code", "options":"Item"},
				{"fieldtype": "Link", "label": __("Customer"), "fieldname": "customer", "options":"Customer", "default": frm.doc.customer}
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
		frm.timeline.insert_comment('Comment', dialog.note);
		const hours = moment(dialog.to_time).diff(moment(dialog.from_time), "seconds") / 3600;

		let timesheet = {
			doctype: 'Timesheet',
			issue: frm.doc.name,
			note: dialog.note,
			time_logs: [
				{
					activity_type: dialog.activity_type,
					from_time: dialog.from_time,
					to_time: dialog.to_time,
					// to_time: (new moment(dialog.from_time)).add(dialog.hours, 'hours').format('YYYY-MM-DD HH:mm:ss'),
					hours: hours,
					project: frm.doc.project,
					/* task: frm.doc.task, */
					billable: 1,
					billing_hours: hours,
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


/* frappe.ui.form.on('Issue', {
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
		if (frm.doc.status !== "Closed" && !cur_frm.custom_buttons["IT Ticket"]) {
			cur_frm.add_custom_button('IT Ticket', function () { frm.trigger('make_ticket') }, 'Make');
		}
	},
	make_ticket: function (frm) {
		var d = new frappe.ui.Dialog({
			title: __('IT Ticket Details'),
			fields: [
				{'fieldname': 'project', 'label': 'Project', 'fieldtype': 'Link', 'options': 'Project', 'default': frm.get_field('project').get_value()},
				{'fieldname': 'customer', 'label': 'Customer', 'fieldtype': 'Link', 'options': 'Customer', 'default': frm.get_field('customer').get_value()},
				{'fieldname': 'contact', 'label': 'Contact', 'fieldtype': 'Link', 'options': 'Contact', 'default': frm.get_field('contact').get_value()},
				{'fieldname': 'assignee', 'label': 'Assignee', 'fieldtype': 'Link', 'options': 'User'},
				{'fieldname': 'comment', 'label': 'Comment', 'fieldtype': 'Small Text'},
				{'fieldname': 'due_date', 'label': 'Complete By', 'fieldtype': 'Date', 'default': frappe.datetime.nowdate()},
				{'fieldname': 'notify', 'label': 'Notify by Email', 'fieldtype': 'Check'}
			],
			primary_action: function(){
				d.hide();
				
				let options = {
					'doctype': 'IT Ticket',
					'subject': frm.get_field('subject').get_value(),
					'description': frm.get_field('description').get_value(),
					'project': d.get_values().project,
					'priority': frm.get_field('priority').get_value(),
					'customer': d.get_values().customer,
					'contact': d.get_values().contact,
					'it_management_table':  frm.get_field('it_management_table').get_value()
				};

				frappe.db.insert(options).then((it_ticket) => {
					
					frappe.call({
						method: "it_management.it_management.doctype.it_ticket.it_ticket.relink_email",
						args: {
							"doctype": "Issue",
							"name": frm.doc.name,
							"it_ticket": it_ticket.name,
						}
					}).then(() => frm.refresh());

					frappe.show_alert({
						indicator: 'green',
						message: __(`IT Ticket ${it_ticket.name} created.`), 
					}).click(() => {
						frappe.set_route('Form', 'IT Ticket', it_ticket.name)
					});

					cur_frm.timeline.insert_comment(`${it_ticket.doctype} <a href="${
						frappe.utils.get_form_link(it_ticket.doctype, it_ticket.name)}">${it_ticket.name}</a> created.`).then(() => {
							frm.set_value("status", "Closed");
							frm.save().then(() => frm.save());
						});
						
					frappe.call({
						method: "it_management.it_management.doctype.it_ticket.it_ticket.add_created_from_issue_comment",
						args: {
							"issue": frm.doc.name,
							"ticket": it_ticket.name
						}
					})
					
					if (d.get_values().assignee) {
						frappe.call({
							"method": "frappe.desk.form.assign_to.add",
							"args": {
								"assign_to": d.get_values().assignee,
								"doctype": "IT Ticket",
								"name": it_ticket.name,
								"description": d.get_values().comment,
								"date": d.get_values().due_date,
								"notify": d.get_values().notify
							}
						});
					}
				});
			},
			primary_action_label: __('Create IT Ticket')
		});
		d.show();
	}
}); */