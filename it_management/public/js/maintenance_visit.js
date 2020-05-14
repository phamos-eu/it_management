frappe.ui.form.on('Maintenance Visit', {
	refresh(frm) {
		if (!frm.is_new()){
                        frm.add_custom_button('Timesheet', function () { frm.trigger('add_activity') },__("Make"));
                        frm.add_custom_button('Issue', function() {frm.trigger('make_issue')},__('Make'));
        }
	},
	add_activity: function(frm){
	    activity_dialog(frm);
	},
	make_issue: function(frm){
	    frappe.new_doc("Issue",{
	       "customer": frm.doc.customer 
	    });
	}
})
