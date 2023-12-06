# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class ImportOrderStatusEpt(models.Model):

    _name = "import.order.status.ept"
    _description = "WooCommerce Order Status"

    name = fields.Char()
    status = fields.Char()
