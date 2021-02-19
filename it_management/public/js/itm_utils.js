
function activity_dialog(frm) {
	if (frm.is_new()) {
		show_alert(__('Save the document first.'));
		return;
	}

	let referenced_task = ""
	if(frm.doc.doctype == "Task"){
		referenced_task = frm.doc.name;
	}else if(frm.doc.doctype == "Issue"){
		referenced_task = frm.doc.task;
	}else if(frm.doc.doctype == "Maintenance Visit"){
		referenced_task = frm.doc.task;
	}

	const activity = new frappe.ui.Dialog({
		title: __('New Activity'),
		fields: [
			{
				fieldtype: 'Link',
				label: __('Activity Type'),
				fieldname: 'activity_type',
				options: 'Activity Type',
				reqd: 1
			},
			{
				fieldtype: 'Column Break',
				fieldname: 'cb_1',
			},
			{
				fieldtype: 'Link',
				label: __('Project'),
				fieldname: 'project',
				options: 'Project',
				default: frm.doc.project,
				reqd: 1
			},
			{
				fieldtype: 'Link',
				label: __('Task'),
				fieldname: 'task',
				options: 'Task',
				default: referenced_task
			},
			// {
			// 	fieldtype: 'Float',
			// 	fieldname: 'hours',
			// 	label: __('Hours'),
			// 	default: 0.25
			// },
			{
				fieldtype: 'Section Break',
				fieldname: 'sb_2'
			},
			{
				fieldtype: 'Text Editor',
				fieldname: 'note',
			},
			{
				fieldtype: 'Section Break',
				fieldname: 'sb_1',
			},

			{
				fieldtype: 'Datetime',
				label: __('From Time'),
				fieldname: 'from_time',
				default: frappe.datetime.now_datetime()
			},

			{
				fieldtype: 'Int',
				fieldname: 'pause',
				label: __('Pause'),
				default: "0" 
			},
			{
				fieldtype: 'Column Break',
				fieldname: 'cb_2',
			},
			{
				fieldtype: 'Datetime',
				fieldname: 'to_time',
				label: __('To Time'),
				default: frappe.datetime.now_datetime(),
			}

		],
	})

	activity.set_primary_action(__('Save'), (dialog) => {
		//frm.timeline.insert_comment('Comment', dialog.note);
		let break_hours = dialog.pause / 60;
		const hours = (moment(dialog.to_time).diff(moment(dialog.from_time), "seconds") / 3600) - break_hours ;

		/*
		let referenced_task = ""
		if(frm.doc.doctype == "Task"){
			referenced_task = frm.doc.name;
		}else if(frm.doc.doctype == "Issue"){
			referenced_task = frm.doc.task;
		}else if(frm.doc.doctype == "Maintenance Visit"){
			referenced_task = frm.doc.task;
		}
		*/

		let timesheet = {
			doctype: 'Timesheet',
			issue: (frm.doc.doctype == "Issue") ? frm.doc.name : "",
			maintenance_visit: (frm.doc.doctype == "Maintenance Visit") ? frm.doc.name : "",
			note: dialog.note,
			time_logs: [
				{
					activity_type: dialog.activity_type,
					from_time: dialog.from_time,
					to_time: dialog.to_time,
					// to_time: (new moment(dialog.from_time)).add(dialog.hours, 'hours').format('YYYY-MM-DD HH:mm:ss'),
					hours: hours,
					task: dialog.task, 
					billable: 1,
					billing_hours: hours,
					project: dialog.project
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
		frm.refresh();
	})

	activity.show();
	/** 
	console.log(Object.getOwnPropertyNames(activity.fields_dict.to_time))
	console.log(activity.fields_dict.to_time.$wrapper)
	console.log(activity.fields_dict.to_time.$input)
	console.log(activity.fields_dict.from_time.disp_area.textContent)
	
	activity.fields_dict.from_time.$input.on("click", function(event){
		activity.fields_dict.to_time.disp_area.textContent = activity.fields_dict.from_time.disp_area.textContent; //This doesnt work
		//activity.fields_dict.to_time.refresh()
	});
	activity.fields_dict.to_time.$input.on("click", function(event){
		//activity.fields_dict.from_time = activity.fields_dict.to_time;
	});
	*/
	
}


function add_it_management_table_items(frm, source_doctype) {
	let dialog = new frappe.ui.form.MultiSelectDialog({

		// Read carefully and adjust parameters
		doctype: source_doctype, // Doctype that needs to be selected in the dialog (e.g. "IT Checklist")
		target: frm,
		setters: {
			// Dropdown Filterfields
			customer: frm.doc.customer,
		},
		date_field: "modified", // "modified", "creation", ...
		get_query() {
			// Filter for shown documents
			return {
				filters: {  }
			}
		},
		action(selections) {
			frappe.call({
				method: "it_management.utils.get_items_from_childtable",
				args : { 'data' : {
					// Configure these two Parameters
				   "childdoctypename" : "IT Management Table", // What is the childtable doctype that contains the wanted items?
				   "parentselections" : selections,
				   "fields" : ["dynamic_type", "dynamic_name", "note"] // Fields that we need to pull from the childtable doctype
				   }
				},
				callback: function(json){

					// Do something with the items (e.g. add them to the childtable within the current document)
					json.message.forEach(item => {
						let row = frm.add_child('it_management_table', {
							dynamic_type: item.dynamic_type,
							dynamic_name: item.dynamic_name,
							note: item.note
						});
					});
					frm.refresh_field('it_management_table');
					frappe.msgprint(__('Items') + ' ' + __('from') + ' ' + source_doctype + ' ' + __('imported.'));

				}
			});
		}
	});
}