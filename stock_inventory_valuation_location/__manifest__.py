# Copyright 2020 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': 'Stock Inventory Valuation by Location',
    'version': '12.0.1.0.0',
    "author": "Vauxoo",
    'summary': 'Introduces an estimation of the value by location in fifo.',
    'depends': ['stock', 'account'],
    'category': 'Inventory',
    "website": "http://vauxoo.com",
    "license": "LGPL-3",
    'data': [
        'views/stock_quant_views.xml',
    ],
    'test': [
    ],
    'installable': True,
    'application': False,
}
