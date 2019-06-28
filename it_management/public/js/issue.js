frappe.ui.form.on('Issue', {
	refresh: function (frm) {
		cur_frm.add_custom_button('IT Ticket', function () { frm.trigger('make_ticket') }, 'Make');
	},
	make_ticket: function (frm) {
		let options = {
			'doctype': 'IT Ticket',
			'subject': frm.get_field('subject').get_value(),
			'description': frm.get_field('description').get_value(),
			'project': frm.get_field('project').get_value(),
			'priority': frm.get_field('priority').get_value(),
			'customer': frm.get_field('customer').get_value(),
			'contact': frm.get_field('contact').get_value(),
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

			frm.timeline.insert_comment('Comment', `${it_ticket.doctype} <a href="${
				frappe.utils.get_form_link(it_ticket.doctype, it_ticket.name)}">${it_ticket.name}</a> created.`);
		});
	}
});
