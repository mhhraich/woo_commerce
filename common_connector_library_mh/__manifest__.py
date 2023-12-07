# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Common Connector Library',
    'version': '15.0.1.0.1',
    'license': 'AGPL-3',
    'category': 'Sales',
    'author': 'MMH.',
    'maintainer': 'MMH COMPANY',
    'summary': """Create a versatile approach to handle various operations and establish
    an automated workflow system to efficiently manage the order processing automatically.""",
    'depends': ['delivery', 'sale_stock', 'sale_management','account'],
    "images": ["static/description/banner.png"],
    'data': ['security/ir.model.access.csv',
             'data/ir_sequence.xml',
             'data/ir_cron.xml',
             'views/stock_quant_package_view.xml',
             'views/common_log_book_view.xml',
             'views/account_fiscal_position.xml',
             'views/common_product_image_ept.xml',
             'views/product_view.xml',
             'views/product_template.xml',
             'views/sale_order_view.xml',
             'views/sale_workflow_process_view.xml',
             'data/automatic_workflow_data.xml',
             'views/common_log_lines_ept.xml',
             ],
    'installable': True,
    'price': 50.00,
    'currency': 'USD',
    'cloc_exclude': ['**/*.xml', ],
    'assets': {
        'web.assets_backend': [
            '/common_connector_library/static/src/scss/graph_widget_ept.scss',
            '/common_connector_library/static/src/scss/on_boarding_wizards.css',
            '/common_connector_library/static/src/scss/queue_line_dashboard.scss',
            '/common_connector_library/static/src/js/graph_widget_ept.js',
            '/common_connector_library/static/src/js/queue_line_dashboard.js'
        ],
        'web.assets_qweb': [
            '/common_connector_library/static/src/xml/dashboard_widget.xml',
            '/common_connector_library/static/src/xml/queue_line_dashboard.xml'
        ]
    },
}
