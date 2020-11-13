frappe.ui.form.on('Sales Invoice Timesheet', {
	onload(frm){
        /** 
        frm.set_query("time_sheet", function() {  
            //Get Sales Invoice
            sales_invoice = frappe.get_doc("Sales Invoice",frm.doc.)
            
			if (frm.doc.location) {   // Wenn das Feld location ausgefüllt ist
				return {
					'filters': {
						"location" : frm.doc.location, // Filter 1
						"floor" : frm.doc.floor // Filter 2
					}
				};
            }
            
        });
        */
    }
});