from frappe import _

doctype_list = [
	"Purchase Receipt",
	"Purchase Invoice",
	"Quotation",
	"Sales Order",
	"Delivery Note",
	"Sales Invoice",
]


def get_message(doctype):
<<<<<<< HEAD
	return _("{0} has been submitted successfully").format(_(doctype))


def get_first_success_message(doctype):
=======
	# Properly format the string with translated doctype
	return _("{0} has been submitted successfully").format(doctype)


def get_first_success_message(doctype):
	# Reuse the get_message function for consistency
>>>>>>> 125a352bc2 (fix: allow all dispatch address for drop ship invoice)
	return get_message(doctype)


def get_default_success_action():
<<<<<<< HEAD
=======
	# Loop through each doctype in the list and return formatted actions
>>>>>>> 125a352bc2 (fix: allow all dispatch address for drop ship invoice)
	return [
		{
			"doctype": "Success Action",
			"ref_doctype": doctype,
			"message": get_message(doctype),
			"first_success_message": get_first_success_message(doctype),
			"next_actions": "new\nprint\nemail",
		}
		for doctype in doctype_list
	]
