# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
import logging
import time

from odoo import models, fields

_logger = logging.getLogger("WooCommerce")


class WooCouponDataQueueLineEpt(models.Model):
    _name = "woo.coupon.data.queue.line.ept"
    _description = "WooCommerce Coupon Data Queue Line"
    _rec_name = "number"

    coupon_data_queue_id = fields.Many2one("woo.coupon.data.queue.ept", ondelete="cascade")
    instance_id = fields.Many2one(related="coupon_data_queue_id.woo_instance_id", copy=False,
                                  help="Coupon imported from this Woocommerce Instance.")
    state = fields.Selection([("draft", "Draft"), ("failed", "Failed"), ("cancel", "Cancelled"), ("done", "Done")],
                             default="draft", copy=False)
    woo_coupon = fields.Char(string="Woo Coupon Id", help="Id of imported coupon.", copy=False)
    coupon_id = fields.Many2one("woo.coupons.ept", copy=False, help="coupon created in Odoo.")
    coupon_data = fields.Text(help="Data imported from Woocommerce of current coupon.", copy=False)
    processed_at = fields.Datetime(help="Shows Date and Time, When the data is processed.", copy=False)
    common_log_lines_ids = fields.One2many("common.log.lines.ept", "woo_coupon_data_queue_line_id",
                                           help="Log lines created against which line.", string="Log Message")
    number = fields.Char(string='Coupon Name')

    def process_coupon_queue_line(self):
        common_log_book_obj = self.env["common.log.book.ept"]
        coupon_obj = self.env["woo.coupons.ept"]
        start = time.time()
        self.env.cr.execute(
            """update woo_coupon_data_queue_ept set is_process_queue = False where is_process_queue = True""")
        self._cr.commit()
        queue_id = self.coupon_data_queue_id
        if queue_id.common_log_book_id:
            common_log_book_id = queue_id.common_log_book_id
        else:
            common_log_book_id = common_log_book_obj.create({"type": "import",
                                                             "module": "woocommerce_ept",
                                                             "woo_instance_id": queue_id.woo_instance_id.id,
                                                             "active": True})

        coupon_obj.create_or_write_coupon(self, common_log_book_id)
        if not common_log_book_id.log_lines:
            common_log_book_id.unlink()
        else:
            queue_id.common_log_book_id = common_log_book_id
        end = time.time()
        _logger.info("Processed %s Coupons in %s seconds.", str(len(self)), str(end - start))

    def auto_coupon_queue_lines_process(self):
        coupon_data_queue_obj = self.env["woo.coupon.data.queue.ept"]
        query = """SELECT coupon_data_queue_id FROM woo_coupon_data_queue_line_ept WHERE state = 'draft' ORDER BY
        "create_date" ASC limit 1;"""
        self._cr.execute(query)
        coupon_queue_data = self._cr.fetchone()
        coupon_queue_id = coupon_data_queue_obj.browse(coupon_queue_data)
        coupon_queue_lines = coupon_queue_id and coupon_queue_id.coupon_data_queue_line_ids.filtered(
            lambda x: x.state == "draft")
        if coupon_queue_lines:
            coupon_queue_lines.process_coupon_queue_line()
        return True
