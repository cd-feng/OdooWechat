# -*- coding: utf-8 -*-
{
    'name': "Odoo-企业微信集成",
    'summary': """本模块用于集成企业微信提供的相关API""",
    'description': """ """,
    'author': "XueFeng.Su",
    'website': "https://github.com/cd-feng",
    'category': 'Wechat/基础',
    'version': '18.0.0.1',
    'depends': ['hr'],
    "license": "AGPL-3",
    'installable': True,
    'application': True,
    'auto_install': False,
    'external_dependencies': {
        'python': ['wechatpy']
    },
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',

        'data/default_ir_cron.xml',

        'views/menu.xml',
        'views/wechat_setting.xml',
        'views/hr_department.xml',
        'views/hr_employee.xml',
        'views/res_users.xml',

        'wizard/hr_department_wizard.xml',
        'wizard/hr_employee_wizard.xml',
    ],
}
