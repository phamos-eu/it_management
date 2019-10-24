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
});