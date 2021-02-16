cur_frm.dashboard.add_transactions([
    {
		'items': [
			'Issue'
		],
		'label': 'Support'
	},
    {
        'items': [
            'Material Request'
        ],
        'label': 'Material'
	},
	{
		'items': [
			'Trip'
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
		//cur_frm.add_custom_button('IT Service Report', function () { frm.trigger('make_it_service_report') }, __("Make"));
		cur_frm.add_custom_button('Sales Invoice', function () { frm.trigger('make_sales_invoice') }, __("Make"));
		cur_frm.add_custom_button('Opportunity', function () { frm.trigger('make_opportunity') }, __("Make"));
		frm.add_custom_button('IT Checklist', function () { frm.trigger('get_it_checklist') }, __("Get Items from"));
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
	/*
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
	*/
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
	},
	make_opportunity: function (frm) {
		let op = frappe.new_doc("Opportunity", {
			"task" : frm.doc.name
		});
	},
	get_it_checklist: function (frm) {
		var d = new frappe.ui.Dialog({
			'fields': [
				{'fieldname': 'customer', 'fieldtype': 'Link', 'options': 'Customer', 'label': 'Customer', 'default': cur_frm.doc.customer},
				{'fieldname': 'cb_1', 'fieldtype': 'Column Break'},
				{'fieldname': 'type', 'fieldtype': 'Link', 'options': 'IT Checklist Type', 'label': 'Type'},
				{'fieldname': 'cb_2', 'fieldtype': 'Column Break'},
				{'fieldname': 'status', 'fieldtype': 'Select', 'options': [__('Implementing'), __('Running'), __('Issue'), __('Obsolet')].join('\n'), 'label': 'Status'},
				{'fieldname': 'sb_1', 'fieldtype': 'Section Break'},
				{'fieldname': 'result', 'fieldtype': 'HTML'}
			]
		});
		var $wrapper;
		var $results;
		var $placeholder;
		
		d.fields_dict["customer"].df.onchange = () => {
			var method = "it_management.utils.get_it_management_table";
			var args = {
				customer: d.fields_dict.customer.input.value,
				type: d.fields_dict.type.input.value,
				status: d.fields_dict.status.input.value
			};
			var columns = (["Link Name", "Customer", "Type", "Status"]);
			get_it_management_tables(frm, $results, $placeholder, method, args, columns);
		}
		d.fields_dict["type"].df.onchange = () => {
			var method = "it_management.utils.get_it_management_table";
			var args = {
				customer: d.fields_dict.customer.input.value,
				type: d.fields_dict.type.input.value,
				status: d.fields_dict.status.input.value
			};
			var columns = (["Link Name", "Customer", "Type", "Status"]);
			get_it_management_tables(frm, $results, $placeholder, method, args, columns);
		}
		d.fields_dict["status"].df.onchange = () => {
			var method = "it_management.utils.get_it_management_table";
			var args = {
				customer: d.fields_dict.customer.input.value,
				type: d.fields_dict.type.input.value,
				status: d.fields_dict.status.input.value
			};
			var columns = (["Link Name", "Customer", "Type", "Status"]);
			get_it_management_tables(frm, $results, $placeholder, method, args, columns);
		}
		
		//console.log(d.fields_dict.result)
		$wrapper = d.fields_dict.result.$wrapper.append(`<div class="results"
			style="border: 1px solid #d1d8dd; border-radius: 3px; height: 300px; overflow: auto;"></div>`);
		$results = $wrapper.find('.results');
		$placeholder = $(`<div class="multiselect-empty-state">
					<span class="text-center" style="margin-top: -40px;">
						<i class="fa fa-2x fa-table text-extra-muted"></i>
						<p class="text-extra-muted">No IT Managementtable found</p>
					</span>
				</div>`);
		$results.on('click', '.list-item--head :checkbox', (e) => {
			$results.find('.list-item-container .list-row-check')
				.prop("checked", ($(e.target).is(':checked')));
		});
		$results.empty();
		$results.append($placeholder);
		set_primary_action(frm, d, $results);
		var method = "it_management.utils.get_it_management_table";
		var args = {
			customer: d.fields_dict.customer.input.value,
			type: d.fields_dict.type.input.value,
			status: d.fields_dict.status.input.value
		};
		var columns = (["Link Name", "Customer", "Type", "Status"]);
		get_it_management_tables(frm, $results, $placeholder, method, args, columns);
		d.show();
		//console.log(d.fields_dict.result.$wrapper["0"].children["0"].children[1])
	}
});

var set_primary_action= function(frm, dialog, $results) {
	var me = this;
	dialog.set_primary_action(__('Get IT Managementtable'), function() {
		let checked_values = get_checked_values($results);
		if(checked_values.length > 0){
			frm.set_value("it_management_table", []);
			add_to_item_line(frm, checked_values);
			dialog.hide();
		}
		else{
			frappe.msgprint(__("Please select IT Management Table to fetch"));
		}
	});
};


var get_it_management_tables = function(frm, $results, $placeholder, method, args, columns) {
	var me = this;
	$results.empty();
	frappe.call({
		method: method,
		args: args,
		callback: function(data) {
			if(data.message){
				$results.append(make_list_row(columns));
				for(let i=0; i<data.message.length; i++){
					$results.append(make_list_row(columns, data.message[i]));
				}
			}else {
				$results.append($placeholder);
			}
		}
	});
}

var make_list_row= function(columns, result={}) {
	var me = this;
	// Make a head row by default (if result not passed)
	let head = Object.keys(result).length === 0;
	let contents = ``;
	columns.forEach(function(column) {
		console.log(column)

		//For all columns
		if(column != "Link Name"){
			var column_value = '-';
			if (result[column]) {
				column_value = result[column];
			}
			contents += `<div class="list-item__content ellipsis">
				${
					head ? `<span class="ellipsis">${__(frappe.model.unscrub(column))}</span>`

					:(column !== "name" ? `<span class="ellipsis">${__(column_value)}</span>`
						: `<a class="list-id ellipsis">
							${__(result[column])}</a>`)
				}
			</div>`;
		}else{
			//For case Link Name
			var column_value = '-';
			if (result[column]) {
				column_value = result[column];
			}
			contents += `<div class="list-item__content ellipsis" style="flex-grow: 2">
				${
					head ? `<span class="ellipsis">${__(frappe.model.unscrub(column))}</span>`

					:(column !== "name" ? `<span class="ellipsis">${__(column_value)}</span>`
						: `<a class="list-id ellipsis">
							${__(result[column])}</a>`)
				}
			</div>`;
		}
	})

	let $row = $(`<div class="list-item">
		<div class="list-item__content" style="flex: 0 0 10px;">
			<input type="checkbox" class="list-row-check" ${result.checked ? 'checked' : ''}>
		</div>
		${contents}
	</div>`);

	$row = list_row_data_items(head, $row, result);
	return $row;
};

var list_row_data_items = function(head, $row, result) {
	head ? $row.addClass('list-item--head')
		: $row = $(`<div class="list-item-container"
			data-reference= "${result.reference}"
			data-qty = ${result.quantity}
			data-description = "${result.description}">
			</div>`).append($row);
	return $row
};

var get_checked_values= function($results) {
	return $results.find('.list-item-container').map(function() {
		let checked_values = {};
		if ($(this).find('.list-row-check:checkbox:checked').length > 0 ) {
			checked_values['reference'] = $(this).attr('data-reference');
			return checked_values
		}
	}).get();
};

var add_to_item_line = function(frm, checked_values){
	for(let i=0; i<checked_values.length; i++){
		frappe.call({
			method: "it_management.utils.get_it_management_table_from_source",
			args: {
				'reference': checked_values[i].reference
			},
			callback: function(data) {
				if(data.message){
					for(let y=0; y<data.message.length; y++){
						var row_to_add_from_reference = data.message[y];
						var child = cur_frm.add_child('it_management_table');
						frappe.model.set_value(child.doctype, child.name, 'dynamic_type', row_to_add_from_reference.dynamic_type);
						frappe.model.set_value(child.doctype, child.name, 'dynamic_name', row_to_add_from_reference.dynamic_name);
						frappe.model.set_value(child.doctype, child.name, 'note', row_to_add_from_reference.note);
						frappe.model.set_value(child.doctype, child.name, 'checked', row_to_add_from_reference.checked);
						cur_frm.refresh_field('it_management_table');
					}
				}
			}
		});
	}
	frm.refresh_fields();
};