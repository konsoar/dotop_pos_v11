# -*- coding: utf-8 -*-
# Part of dotop. See LICENSE file for full copyright and licensing details.

{
    'name': 'Base Kanban',
    'category': 'Hidden',
    'description': """
网页看板视图
========================

""",
    'version': '1.0',
    'depends': ['web'],
    'data' : [
        'views/web_kanban_templates.xml',
    ],
    'qweb' : [
        'static/src/xml/*.xml',
    ],
    'auto_install': True
}
