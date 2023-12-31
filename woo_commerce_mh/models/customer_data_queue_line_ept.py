# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import json
import logging
import time

from datetime import datetime

from odoo import models, fields

_logger = logging.getLogger("WooCommerce")


class WooCustomerDataQueueLineEpt(models.Model):
    _name = "woo.customer.data.queue.line.ept"
    _description = 'WooCommerce Customer Data Queue Line'
    _rec_name = "woo_synced_data_id"

    woo_instance_id = fields.Many2one('woo.instance.ept', string='Instance',
                                      help="Determines that queue line associated with particular instance")
    state = fields.Selection([('draft', 'Draft'), ('failed', 'Failed'), ("cancel", "Cancelled"), ('done', 'Done')],
                             default='draft')
    last_process_date = fields.Datetime(readonly=True)
    woo_synced_data = fields.Char(string='WooCommerce Synced Data')
    woo_synced_data_id = fields.Char(string='Woo Customer Id')
    queue_id = fields.Many2one('woo.customer.data.queue.ept')
    common_log_lines_ids = fields.One2many("common.log.lines.ept", "woo_customer_data_queue_line_id",
                                           help="Log lines created against which line.")
    name = fields.Char(string="Customer", help="Customer Name of Woo Commerce")

    def process_woo_customer_queue_lines(self):
        common_log_line_obj = self.env["common.log.lines.ept"]
        model_id = common_log_line_obj.get_model_id("res.partner")
        partner_obj = self.env['res.partner']

        log_lines = []
        commit_count = 0
        parent_partner = False

        for customer_queue_line in self:
            commit_count += 1
            if commit_count == 10:
                customer_queue_line.queue_id.is_process_queue = True
                self._cr.commit()
                commit_count = 0
            instance = customer_queue_line.woo_instance_id
            customer_val = json.loads(customer_queue_line.woo_synced_data)
            _logger.info("Start processing Woo customer Id %s for instance %s.", customer_val.get('id', False),
                         instance.name)

            if customer_val:
                parent_partner = partner_obj.woo_create_contact_customer(customer_val, instance)
            if parent_partner:
                partner_obj.woo_create_or_update_customer(customer_val.get('billing'), instance,
                                                          parent_partner, 'invoice')
                partner_obj.woo_create_or_update_customer(customer_val.get('shipping'), instance, parent_partner,
                                                          'delivery')
                customer_queue_line.write({'state': 'done', 'last_process_date': datetime.now()})
            else:
                customer_queue_line.write({'state': 'failed', 'last_process_date': datetime.now()})
                log_line_id = common_log_line_obj.create({
                    'model_id': model_id,
                    'message': "Please check customer name or addresses in WooCommerce.",
                    'woo_customer_data_queue_line_id': customer_queue_line.id
                })
                log_lines.append(log_line_id.id)
            customer_queue_line.queue_id.is_process_queue = False
            _logger.info("End processing Woo customer Id %s for instance %s.", customer_val.get('id', False),
                         instance.name)
        return True

    def woo_customer_data_queue_to_odoo(self):
        customer_queue_ids = []
        woo_customer_data_queue_obj = self.env["woo.customer.data.queue.ept"]
        common_log_obj = self.env["common.log.book.ept"]
        ir_model_obj = self.env['ir.model']
        start = time.time()

        self.env.cr.execute(
            """update woo_customer_data_queue_ept set is_process_queue = False where is_process_queue = True""")
        self._cr.commit()
        query = """select queue.id from woo_customer_data_queue_line_ept as queue_line
                    inner join woo_customer_data_queue_ept as queue on queue_line.queue_id = queue.id
                    where queue_line.state='draft' and queue.is_action_require = 'False'
                    ORDER BY queue_line.create_date ASC"""
        self._cr.execute(query)
        customer_queue_list = self._cr.fetchall()

        for result in customer_queue_list:
            customer_queue_ids.append(result[0])

        if not customer_queue_ids:
            return False
        customer_queues = woo_customer_data_queue_obj.browse(list(set(customer_queue_ids)))

        customer_queue_process_cron_time = customer_queues.woo_instance_id.get_woo_cron_execution_time(
            "woo_commerce_mh.process_woo_customer_data")
        for customer_queue in customer_queues:
            customer_queue.queue_process_count += 1
            if customer_queue.queue_process_count > 3:
                customer_queue.is_action_require = True
                note = "<p>Attention %s queue is processed 3 times you need to process it manually.</p>" % (
                    customer_queue.name)
                customer_queue.message_post(body=note)
                if customer_queue.woo_instance_id.is_create_schedule_activity:
                    model = ir_model_obj.search([('model', '=', 'woo.customer.data.queue.ept')])
                    common_log_obj.create_woo_schedule_activity(customer_queue, model, True)
                continue
            queue_lines = customer_queue.queue_line_ids.filtered(lambda x: x.state == "draft")
            self._cr.commit()
            if not queue_lines:
                continue

            queue_lines.process_woo_customer_queue_lines_directly()
            if time.time() - start > customer_queue_process_cron_time - 60:
                return True
        return True

    def process_woo_customer_queue_lines_directly(self):
        self.process_woo_customer_queue_lines()
        queues = self.queue_id
        self.set_log_line_with_queue_line(queues)
        return True

    def set_log_line_with_queue_line(self, queues):
        common_log_obj = self.env["common.log.book.ept"]
        common_log_line_obj = self.env["common.log.lines.ept"]
        for queue in queues:
            log_lines = common_log_line_obj.search([('woo_customer_data_queue_line_id', 'in', queue.queue_line_ids.ids),
                                                    ('log_book_id', '=', False)])
            if log_lines:
                if queue.common_log_book_id:
                    queue.common_log_book_id.write({'log_lines': [(6, 0, log_lines.ids)]})
                else:
                    common_log_id = common_log_obj.create({
                        'type': 'import', 'module': 'woocommerce_ept',
                        'woo_instance_id': queue.woo_instance_id.id,
                        'log_lines': [(6, 0, log_lines.ids)]
                    })
                    queue.write({'common_log_book_id': common_log_id.id})
        return True
