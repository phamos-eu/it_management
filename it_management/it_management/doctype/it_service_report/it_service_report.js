// Copyright (c) 2019, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

frappe.ui.form.on('IT Service Report', {
	refresh: function(frm) {
		// check if entry already saved
		if (frm.doc.__islocal) {
			// get and set current loggedin employee
			var user = frappe.user_info().email;

			frappe.call({
				method:"frappe.client.get_list",
				args:{
				doctype:"Employee",
				filters: [
					["user_id","=", user]
				],
				fields: ["name"]
				},
				callback: function(r) {
					if (r.message[0]) {
						cur_frm.set_value('employee', r.message[0].name);
					}
					
					//Obsolet:
					/* //get and set copy of it management table of it ticket
					frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype:"IT Management Table",
							filters: [
								["parent","=", cur_frm.doc.issue],
								["checked","=", 0]
							],
							fields: ["name", "dynamic_name", "dynamic_type", "note"],
							parent: "IT Ticket",
						},
						callback: function(r) {
							if (r.message) {
								console.log(r.message);
								var i;
								for (i=0; i<r.message.length; i++) {
									var child = cur_frm.add_child('table_13');
									frappe.model.set_value(child.doctype, child.name, 'dynamic_type', r.message[i].dynamic_type);
									frappe.model.set_value(child.doctype, child.name, 'dynamic_name', r.message[i].dynamic_name);
									frappe.model.set_value(child.doctype, child.name, 'note', r.message[i].note);
									frappe.model.set_value(child.doctype, child.name, 'identifier', r.message[i].name);
									cur_frm.refresh_field('table_13');
								}
							}
						}
					}); */
					//get and set copy of it management table of issue
					if (cur_frm.doc.issue) {
						/* frappe.call({
							"method": "frappe.client.get_list",
							"args": {
								"doctype":"IT Management Table",
								"filters": [
									["parent","=", cur_frm.doc.issue],
									["checked","=", 0]
								],
								"fields": ["name", "dynamic_name", "dynamic_type", "note"],
								"parent": "Issue"
							},
							"callback": function(r) {
								if (r.message) {
									console.log(r.message);
									var i;
									for (i=0; i<r.message.length; i++) {
										var child = cur_frm.add_child('table_13');
										frappe.model.set_value(child.doctype, child.name, 'dynamic_type', r.message[i].dynamic_type);
										frappe.model.set_value(child.doctype, child.name, 'dynamic_name', r.message[i].dynamic_name);
										frappe.model.set_value(child.doctype, child.name, 'note', r.message[i].note);
										frappe.model.set_value(child.doctype, child.name, 'identifier', r.message[i].name);
										cur_frm.refresh_field('table_13');
									}
								}
							}
						}); */
						frappe.call({
							"method": "it_management.it_management.doctype.it_service_report.it_service_report.fetch_it_management_table_of_issue",
							"args": {
								"issue": cur_frm.doc.issue
							},
							"callback": function(r) {
								if (r.message) {
									console.log(r.message);
									var i;
									for (i=0; i<r.message.length; i++) {
										var child = cur_frm.add_child('table_13');
										frappe.model.set_value(child.doctype, child.name, 'dynamic_type', r.message[i].dynamic_type);
										frappe.model.set_value(child.doctype, child.name, 'dynamic_name', r.message[i].dynamic_name);
										frappe.model.set_value(child.doctype, child.name, 'note', r.message[i].note);
										frappe.model.set_value(child.doctype, child.name, 'identifier', r.message[i].name);
										cur_frm.refresh_field('table_13');
									}
								}
							}
						});
					}
				}
			}); 
			
			// set date to today
			cur_frm.set_value('date', frappe.datetime.now_date());
		}
		if (cur_frm.doc.docstatus == 1) {
			// Custom BTN "Make Sales Invoice"
			frm.add_custom_button('Sales Invoice', function () { frm.trigger('make_sales_invoice') }, __("Make"));
		} else {
			if (!cur_frm.doc.table_13) {
				// Custom BTN "Get IT Checklist"
				frm.add_custom_button('IT Checklist', function () { frm.trigger('get_it_checklist') }, __("Get IT Managementtable from"));
			}
		}
	},
	before_save: function(frm) {
		// calculate and set time diff in hours as float
		var time_diff = (moment(frappe.datetime.now_date() + " " + cur_frm.doc.end).diff(moment(frappe.datetime.now_date() + " " + cur_frm.doc.start),"seconds")) / 3600;
		cur_frm.set_value('time_total', time_diff);
		
		// if billing_total == 0, set billing_total = time_total
		if (!cur_frm.doc.billing_time) {
			cur_frm.set_value('billing_time', time_diff);
		}
	},
	make_sales_invoice: function (frm) {
		var customer = '';
		frappe.call({
            "method": "frappe.client.get",
            "args": {
                "doctype": "Issue",
                "name": frm.doc.issue
            },
            "callback": function(response) {
                var issue = response.message;

                if (issue) {
                    customer = issue.customer;
                }
				let dialog = new frappe.ui.Dialog({
					title: __("Select Item (optional)"),
					fields: [
						{"fieldtype": "Link", "label": __("Item Code"), "fieldname": "item_code", "options":"Item"},
						{"fieldtype": "Link", "label": __("Customer"), "fieldname": "customer", "options":"Customer", "default": customer}
					]
				});

				dialog.set_primary_action(__("Make Sales Invoice"), () => {
					var args = dialog.get_values();
					if(!args) return;
					dialog.hide();
					return frappe.call({
						type: "GET",
						method: "it_management.it_management.doctype.it_service_report.it_service_report.make_sales_invoice",
						args: {
							"source_name": frm.doc.timesheet,
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
	},
	get_it_checklist: function (frm) {
		var d = new frappe.ui.Dialog({
			'fields': [
				{'fieldname': 'customer', 'fieldtype': 'Link', 'options': 'Customer', 'label': 'Customer'},
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
	}
});

var set_primary_action= function(frm, dialog, $results) {
	var me = this;
	dialog.set_primary_action(__('Get IT Managementtable'), function() {
		let checked_values = get_checked_values($results);
		if(checked_values.length > 0){
			frm.set_value("table_13", []);
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
						var child = cur_frm.add_child('table_13');
						frappe.model.set_value(child.doctype, child.name, 'dynamic_type', row_to_add_from_reference.dynamic_type);
						frappe.model.set_value(child.doctype, child.name, 'dynamic_name', row_to_add_from_reference.dynamic_name);
						frappe.model.set_value(child.doctype, child.name, 'note', row_to_add_from_reference.note);
						frappe.model.set_value(child.doctype, child.name, 'checked', row_to_add_from_reference.checked);
						cur_frm.refresh_field('table_13');
					}
				}
			}
		});
	}
	frm.refresh_fields();
};
