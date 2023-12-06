# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class DeliveryCarrier(models.Model):

    _inherit = "delivery.carrier"

    woo_code = fields.Char(help="WooCommerce Delivery Code")
