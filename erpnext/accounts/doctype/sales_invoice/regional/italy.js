<<<<<<< HEAD
{% include "erpnext/regional/italy/sales_invoice.js" %}

erpnext.setup_e_invoice_button('Sales Invoice')
=======
frappe.ui.form.on("Sales Invoice", {
	refresh: (frm) => {
		if (frm.doc.docstatus == 1) {
			frm.add_custom_button(__("Generate E-Invoice"), () => {
				frm.call({
					method: "erpnext.regional.italy.utils.generate_single_invoice",
					args: {
						docname: frm.doc.name,
					},
					callback: function (r) {
						frm.reload_doc();
						if (r.message) {
							open_url_post(frappe.request.url, {
								cmd: "frappe.core.doctype.file.file.download_file",
								file_url: r.message,
							});
						}
					},
				});
			});
		}
	},
});
>>>>>>> 125a352bc2 (fix: allow all dispatch address for drop ship invoice)
