# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from datetime import date

import frappe
from frappe import _, bold
from frappe.core.doctype.role.role import get_users
from frappe.model.document import Document
<<<<<<< HEAD
=======
from frappe.query_builder.functions import Sum
>>>>>>> 125a352bc2 (fix: allow all dispatch address for drop ship invoice)
from frappe.utils import add_days, cint, flt, formatdate, get_datetime, getdate

from erpnext.accounts.utils import get_fiscal_year
from erpnext.controllers.item_variant import ItemTemplateCannotHaveStock
from erpnext.stock.doctype.inventory_dimension.inventory_dimension import get_inventory_dimensions
<<<<<<< HEAD
=======
from erpnext.stock.serial_batch_bundle import SerialBatchBundle
>>>>>>> 125a352bc2 (fix: allow all dispatch address for drop ship invoice)
from erpnext.stock.stock_ledger import get_previous_sle


class StockFreezeError(frappe.ValidationError):
	pass


class BackDatedStockTransaction(frappe.ValidationError):
	pass


<<<<<<< HEAD
=======
class InventoryDimensionNegativeStockError(frappe.ValidationError):
	pass


>>>>>>> 125a352bc2 (fix: allow all dispatch address for drop ship invoice)
exclude_from_linked_with = True


class StockLedgerEntry(Document):
<<<<<<< HEAD
=======
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		actual_qty: DF.Float
		auto_created_serial_and_batch_bundle: DF.Check
		batch_no: DF.Data | None
		company: DF.Link | None
		dependant_sle_voucher_detail_no: DF.Data | None
		fiscal_year: DF.Data | None
		has_batch_no: DF.Check
		has_serial_no: DF.Check
		incoming_rate: DF.Currency
		is_adjustment_entry: DF.Check
		is_cancelled: DF.Check
		item_code: DF.Link | None
		outgoing_rate: DF.Currency
		posting_date: DF.Date | None
		posting_datetime: DF.Datetime | None
		posting_time: DF.Time | None
		project: DF.Link | None
		qty_after_transaction: DF.Float
		recalculate_rate: DF.Check
		serial_and_batch_bundle: DF.Link | None
		serial_no: DF.LongText | None
		stock_queue: DF.LongText | None
		stock_uom: DF.Link | None
		stock_value: DF.Currency
		stock_value_difference: DF.Currency
		to_rename: DF.Check
		valuation_rate: DF.Currency
		voucher_detail_no: DF.Data | None
		voucher_no: DF.DynamicLink | None
		voucher_type: DF.Link | None
		warehouse: DF.Link | None
	# end: auto-generated types

>>>>>>> 125a352bc2 (fix: allow all dispatch address for drop ship invoice)
	def autoname(self):
		"""
		Temporarily name doc for fast insertion
		name will be changed using autoname options (in a scheduled job)
		"""
		self.name = frappe.generate_hash(txt="", length=10)
		if self.meta.autoname == "hash":
			self.to_rename = 0

	def validate(self):
		self.flags.ignore_submit_comment = True
		from erpnext.stock.utils import validate_disabled_warehouse, validate_warehouse_company

		self.validate_mandatory()
<<<<<<< HEAD
		self.validate_item()
=======
>>>>>>> 125a352bc2 (fix: allow all dispatch address for drop ship invoice)
		self.validate_batch()
		validate_disabled_warehouse(self.warehouse)
		validate_warehouse_company(self.warehouse, self.company)
		self.scrub_posting_time()
		self.validate_and_set_fiscal_year()
		self.block_transactions_against_group_warehouse()
		self.validate_with_last_transaction_posting_time()
		self.validate_inventory_dimension_negative_stock()

<<<<<<< HEAD
	def set_posting_datetime(self):
		from erpnext.stock.utils import get_combine_datetime

		self.posting_datetime = get_combine_datetime(self.posting_date, self.posting_time)
		self.db_set("posting_datetime", self.posting_datetime)

	def validate_inventory_dimension_negative_stock(self):
		if self.is_cancelled:
			return

		extra_cond = ""
		kwargs = {}

=======
	def set_posting_datetime(self, save=False):
		from erpnext.stock.utils import get_combine_datetime

		if save:
			posting_datetime = get_combine_datetime(self.posting_date, self.posting_time)
			if not self.posting_datetime or self.posting_datetime != posting_datetime:
				self.db_set("posting_datetime", posting_datetime)
		else:
			self.posting_datetime = get_combine_datetime(self.posting_date, self.posting_time)

	def validate_inventory_dimension_negative_stock(self):
		if self.is_cancelled or self.actual_qty >= 0:
			return

>>>>>>> 125a352bc2 (fix: allow all dispatch address for drop ship invoice)
		dimensions = self._get_inventory_dimensions()
		if not dimensions:
			return

<<<<<<< HEAD
		for dimension, values in dimensions.items():
			kwargs[dimension] = values.get("value")
			extra_cond += f" and {dimension} = %({dimension})s"

		kwargs.update(
			{
				"item_code": self.item_code,
				"warehouse": self.warehouse,
				"posting_date": self.posting_date,
				"posting_time": self.posting_time,
				"company": self.company,
				"sle": self.name,
			}
		)

		sle = get_previous_sle(kwargs, extra_cond=extra_cond)
		qty_after_transaction = 0.0
		flt_precision = cint(frappe.db.get_default("float_precision")) or 2
		if sle:
			qty_after_transaction = sle.qty_after_transaction

		diff = qty_after_transaction + flt(self.actual_qty)
		diff = flt(diff, flt_precision)
		if diff < 0 and abs(diff) > 0.0001:
			self.throw_validation_error(diff, dimensions)

	def throw_validation_error(self, diff, dimensions):
		dimension_msg = _(", with the inventory {0}: {1}").format(
			"dimensions" if len(dimensions) > 1 else "dimension",
			", ".join(f"{bold(d.doctype)} ({d.value})" for k, d in dimensions.items()),
		)

		msg = _(
			"{0} units of {1} are required in {2}{3}, on {4} {5} for {6} to complete the transaction."
=======
		flt_precision = cint(frappe.db.get_default("float_precision")) or 2
		for dimension, values in dimensions.items():
			dimension_value = values.get("value")
			available_qty = self.get_available_qty_after_prev_transaction(dimension, dimension_value)

			diff = flt(available_qty + flt(self.actual_qty), flt_precision)  # qty after current transaction
			if diff < 0 and abs(diff) > 0.0001:
				self.throw_validation_error(diff, dimension, dimension_value)

	def get_available_qty_after_prev_transaction(self, dimension, dimension_value):
		sle = frappe.qb.DocType("Stock Ledger Entry")
		available_qty = (
			frappe.qb.from_(sle)
			.select(Sum(sle.actual_qty))
			.where(
				(sle.item_code == self.item_code)
				& (sle.warehouse == self.warehouse)
				& (sle.posting_datetime < self.posting_datetime)
				& (sle.company == self.company)
				& (sle.is_cancelled == 0)
				& (sle[dimension] == dimension_value)
			)
		).run()

		return available_qty[0][0] or 0

	def throw_validation_error(self, diff, dimension, dimension_value):
		msg = _(
			"{0} units of {1} are required in {2} with the inventory dimension: {3} ({4}) on {5} {6} for {7} to complete the transaction."
>>>>>>> 125a352bc2 (fix: allow all dispatch address for drop ship invoice)
		).format(
			abs(diff),
			frappe.get_desk_link("Item", self.item_code),
			frappe.get_desk_link("Warehouse", self.warehouse),
<<<<<<< HEAD
			dimension_msg,
=======
			frappe.bold(dimension),
			frappe.bold(dimension_value),
>>>>>>> 125a352bc2 (fix: allow all dispatch address for drop ship invoice)
			self.posting_date,
			self.posting_time,
			frappe.get_desk_link(self.voucher_type, self.voucher_no),
		)

<<<<<<< HEAD
		frappe.throw(msg, title=_("Inventory Dimension Negative Stock"))
=======
		frappe.throw(
			msg, title=_("Inventory Dimension Negative Stock"), exc=InventoryDimensionNegativeStockError
		)
>>>>>>> 125a352bc2 (fix: allow all dispatch address for drop ship invoice)

	def _get_inventory_dimensions(self):
		inv_dimensions = get_inventory_dimensions()
		inv_dimension_dict = {}
		for dimension in inv_dimensions:
			if not dimension.get("validate_negative_stock") or not self.get(dimension.fieldname):
				continue

			dimension["value"] = self.get(dimension.fieldname)
			inv_dimension_dict.setdefault(dimension.fieldname, dimension)

		return inv_dimension_dict

	def on_submit(self):
<<<<<<< HEAD
		self.set_posting_datetime()
		self.check_stock_frozen_date()
		self.calculate_batch_qty()

		if not self.get("via_landed_cost_voucher"):
			from erpnext.stock.doctype.serial_no.serial_no import process_serial_no

			process_serial_no(self)

	def calculate_batch_qty(self):
		if self.batch_no:
			batch_qty = (
				frappe.db.get_value(
					"Stock Ledger Entry",
					{"docstatus": 1, "batch_no": self.batch_no, "is_cancelled": 0},
					"sum(actual_qty)",
				)
				or 0
			)
			frappe.db.set_value("Batch", self.batch_no, "batch_qty", batch_qty)
=======
		self.set_posting_datetime(save=True)
		self.check_stock_frozen_date()

		# Added to handle few test cases where serial_and_batch_bundles are not required
		if frappe.flags.in_test and frappe.flags.ignore_serial_batch_bundle_validation:
			return

		if not self.get("via_landed_cost_voucher"):
			SerialBatchBundle(
				sle=self,
				item_code=self.item_code,
				warehouse=self.warehouse,
				company=self.company,
			)

		self.validate_serial_batch_no_bundle()
>>>>>>> 125a352bc2 (fix: allow all dispatch address for drop ship invoice)

	def validate_mandatory(self):
		mandatory = ["warehouse", "posting_date", "voucher_type", "voucher_no", "company"]
		for k in mandatory:
			if not self.get(k):
				frappe.throw(_("{0} is required").format(self.meta.get_label(k)))

		if self.voucher_type != "Stock Reconciliation" and not self.actual_qty:
			frappe.throw(_("Actual Qty is mandatory"))

<<<<<<< HEAD
	def validate_item(self):
		item_det = frappe.db.sql(
			"""select name, item_name, has_batch_no, docstatus,
			is_stock_item, has_variants, stock_uom, create_new_batch
			from tabItem where name=%s""",
			self.item_code,
			as_dict=True,
		)

		if not item_det:
			frappe.throw(_("Item {0} not found").format(self.item_code))

		item_det = item_det[0]

		if item_det.is_stock_item != 1:
			frappe.throw(_("Item {0} must be a stock Item").format(self.item_code))

		# check if batch number is valid
		if item_det.has_batch_no == 1:
			batch_item = (
				self.item_code
				if self.item_code == item_det.item_name
				else self.item_code + ":" + item_det.item_name
			)
			if not self.batch_no:
				frappe.throw(_("Batch number is mandatory for Item {0}").format(batch_item))
			elif not frappe.db.get_value("Batch", {"item": self.item_code, "name": self.batch_no}):
				frappe.throw(
					_("{0} is not a valid Batch Number for Item {1}").format(self.batch_no, batch_item)
				)

		elif item_det.has_batch_no == 0 and self.batch_no and self.is_cancelled == 0:
			frappe.throw(_("The Item {0} cannot have Batch").format(self.item_code))

		if item_det.has_variants:
			frappe.throw(
				_("Stock cannot exist for Item {0} since has variants").format(self.item_code),
				ItemTemplateCannotHaveStock,
			)

		self.stock_uom = item_det.stock_uom
=======
	def validate_serial_batch_no_bundle(self):
		if self.is_cancelled == 1:
			return

		item_detail = frappe.get_cached_value(
			"Item",
			self.item_code,
			["has_serial_no", "has_batch_no", "is_stock_item", "has_variants", "stock_uom"],
			as_dict=1,
		)

		values_to_be_change = {}
		if self.has_batch_no != item_detail.has_batch_no:
			values_to_be_change["has_batch_no"] = item_detail.has_batch_no

		if self.has_serial_no != item_detail.has_serial_no:
			values_to_be_change["has_serial_no"] = item_detail.has_serial_no

		if values_to_be_change:
			self.db_set(values_to_be_change)

		if not item_detail:
			self.throw_error_message(f"Item {self.item_code} not found")

		if item_detail.has_variants:
			self.throw_error_message(
				f"Stock cannot exist for Item {self.item_code} since has variants",
				ItemTemplateCannotHaveStock,
			)

		if item_detail.is_stock_item != 1:
			self.throw_error_message("Item {0} must be a stock Item").format(self.item_code)

		if item_detail.has_serial_no or item_detail.has_batch_no:
			if not self.serial_and_batch_bundle:
				self.throw_error_message(f"Serial No / Batch No are mandatory for Item {self.item_code}")

		if self.serial_and_batch_bundle and not item_detail.has_serial_no and not item_detail.has_batch_no:
			self.throw_error_message(f"Serial No and Batch No are not allowed for Item {self.item_code}")

	def throw_error_message(self, message, exception=frappe.ValidationError):
		frappe.throw(_(message), exception)
>>>>>>> 125a352bc2 (fix: allow all dispatch address for drop ship invoice)

	def check_stock_frozen_date(self):
		stock_settings = frappe.get_cached_doc("Stock Settings")

		if stock_settings.stock_frozen_upto:
			if (
				getdate(self.posting_date) <= getdate(stock_settings.stock_frozen_upto)
				and stock_settings.stock_auth_role not in frappe.get_roles()
			):
				frappe.throw(
					_("Stock transactions before {0} are frozen").format(
						formatdate(stock_settings.stock_frozen_upto)
					),
					StockFreezeError,
				)

		stock_frozen_upto_days = cint(stock_settings.stock_frozen_upto_days)
		if stock_frozen_upto_days:
			older_than_x_days_ago = (
				add_days(getdate(self.posting_date), stock_frozen_upto_days) <= date.today()
			)
			if older_than_x_days_ago and stock_settings.stock_auth_role not in frappe.get_roles():
				frappe.throw(
					_("Not allowed to update stock transactions older than {0}").format(
						stock_frozen_upto_days
					),
					StockFreezeError,
				)

	def scrub_posting_time(self):
		if not self.posting_time or self.posting_time == "00:0":
			self.posting_time = "00:00"

	def validate_batch(self):
		if self.batch_no and self.voucher_type != "Stock Entry":
			if (self.voucher_type in ["Purchase Receipt", "Purchase Invoice"] and self.actual_qty < 0) or (
				self.voucher_type in ["Delivery Note", "Sales Invoice"] and self.actual_qty > 0
			):
				return

			expiry_date = frappe.db.get_value("Batch", self.batch_no, "expiry_date")
			if expiry_date:
				if getdate(self.posting_date) > getdate(expiry_date):
					frappe.throw(
						_("Batch {0} of Item {1} has expired.").format(self.batch_no, self.item_code)
					)

	def validate_and_set_fiscal_year(self):
		if not self.fiscal_year:
			self.fiscal_year = get_fiscal_year(self.posting_date, company=self.company)[0]
		else:
			from erpnext.accounts.utils import validate_fiscal_year

			validate_fiscal_year(
				self.posting_date, self.fiscal_year, self.company, self.meta.get_label("posting_date"), self
			)

	def block_transactions_against_group_warehouse(self):
		from erpnext.stock.utils import is_group_warehouse

		is_group_warehouse(self.warehouse)

	def validate_with_last_transaction_posting_time(self):
		authorized_role = frappe.db.get_single_value(
			"Stock Settings", "role_allowed_to_create_edit_back_dated_transactions"
		)
		if authorized_role:
			authorized_users = get_users(authorized_role)
			if authorized_users and frappe.session.user not in authorized_users:
				last_transaction_time = frappe.db.sql(
					"""
					select MAX(timestamp(posting_date, posting_time)) as posting_time
					from `tabStock Ledger Entry`
					where docstatus = 1 and is_cancelled = 0 and item_code = %s
					and warehouse = %s""",
					(self.item_code, self.warehouse),
				)[0][0]

				cur_doc_posting_datetime = "{} {}".format(
					self.posting_date,
					self.get("posting_time") or "00:00:00",
				)

				if last_transaction_time and get_datetime(cur_doc_posting_datetime) < get_datetime(
					last_transaction_time
				):
					msg = _("Last Stock Transaction for item {0} under warehouse {1} was on {2}.").format(
						frappe.bold(self.item_code),
						frappe.bold(self.warehouse),
						frappe.bold(last_transaction_time),
					)

					msg += "<br><br>" + _(
						"You are not authorized to make/edit Stock Transactions for Item {0} under warehouse {1} before this time."
					).format(frappe.bold(self.item_code), frappe.bold(self.warehouse))

					msg += "<br><br>" + _("Please contact any of the following users to {} this transaction.")
					msg += "<br>" + "<br>".join(authorized_users)
					frappe.throw(msg, BackDatedStockTransaction, title=_("Backdated Stock Entry"))

	def on_cancel(self):
		msg = _("Individual Stock Ledger Entry cannot be cancelled.")
		msg += "<br>" + _("Please cancel related transaction.")
		frappe.throw(msg)


def on_doctype_update():
	frappe.db.add_index("Stock Ledger Entry", ["voucher_no", "voucher_type"])
	frappe.db.add_index("Stock Ledger Entry", ["batch_no", "item_code", "warehouse"])
	frappe.db.add_index("Stock Ledger Entry", ["warehouse", "item_code"], "item_warehouse")
	frappe.db.add_index("Stock Ledger Entry", ["posting_datetime", "creation"])
