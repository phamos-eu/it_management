frappe.ui.form.on('Issue', {
	refresh: function (frm) {
		cur_frm.add_custom_button('IT Ticket', function () { frm.trigger('make_ticket') }, 'Make');
	},
	make_ticket: function (frm) {
		let options = {
			'doctype': 'IT Ticket',
			'subject': frm.doc.subject,
			'description': frm.doc.description,
		};

		if (frm.doc.project) {
			options['project'] = frm.doc.project;
		}
		if (frm.doc.contact) {
			options['contact'] = frm.doc.contact;
		}
		if (frm.doc.customer) {
			options['customer'] = frm.doc.customer;
		}
		if (frm.doc.priority) {
			options['priority'] = frm.doc.priority;
		}

		frappe.db.insert(options).then((doc) => {
			const filters = {
				'reference_doctype': frm.doc.doctype,
				'reference_name': frm.doc.name,
			};
			frappe.db.get_list('Communication', { filters: filters })
				.then((comm_list) => {
					comm_list.forEach(communication => {
						frappe.call({
							method: "frappe.email.relink",
							args: {
								"name": communication.name,
								"reference_doctype": doc.doctype,
								"reference_name": doc.name
							}
						});
					});
				})
				.then(() => frm.refresh());

			frappe.show_alert({
				indicator: 'green',
				message: __(`IT Ticket ${doc.name} created.`), 
			}).click(() => {
				frappe.set_route('Form', 'IT Ticket', doc.name)
			});

			frm.timeline.insert_comment('Comment', `IT Ticket ${doc.name} created.`);
		});
	}
});
