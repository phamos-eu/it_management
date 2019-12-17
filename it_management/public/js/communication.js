frappe.ui.form.on('Communication', {
	refresh: function (frm) {
		cur_frm.add_custom_button('IT Ticket', function () { frm.trigger('make_ticket') }, 'Make');
	},
	make_ticket: function (frm) {
		let options = {
			'doctype': 'IT Ticket',
			'subject': frm.doc.subject,
			'description': frm.doc.content,
		};
		if ((frm.doc.reference_doctype) && (frm.doc.reference_name)) {
			if (frm.doc.reference_doctype === 'Customer') {
				options['customer'] = frm.get_field('reference_name').get_value();
			}
			if (frm.doc.reference_doctype === 'Project') {
				options['project'] = frm.get_field('reference_name').get_value();
			}
			if (frm.doc.reference_doctype === 'Task') {
				options['task'] = frm.get_field('reference_name').get_value();
			}
		}

		//obsolet:
		/* frappe.db.insert(options).then((it_ticket) => {
			frappe.call({
				method: 'frappe.email.relink',
				args: {
					'name': frm.doc.name,
					'reference_doctype': 'IT Ticket',
					'reference_name': it_ticket.name
				},
				callback: function () {
					frm.refresh();
				}
			});

			frm.timeline.insert_comment('Comment', `${it_ticket.doctype} <a href="${
				frappe.utils.get_form_link(it_ticket.doctype, it_ticket.name)}">${it_ticket.name}</a> created.`);
		}); */
		frappe.db.insert(options).then((issue) => {
			frappe.call({
				method: 'frappe.email.relink',
				args: {
					'name': frm.doc.name,
					'reference_doctype': 'Issue',
					'reference_name': issue.name
				},
				callback: function () {
					frm.refresh();
				}
			});

			frm.timeline.insert_comment('Comment', `${issue.doctype} <a href="${
				frappe.utils.get_form_link(issue.doctype, issue.name)}">${issue.name}</a> created.`);
		});
	}
});
