# -*- coding: utf-8 -*-
{
    'name': "Odoo-企业微信登录插件",
    'summary': """本插件支持企业微信内免密登录到Odoo系统""",
    'description': """ """,
    'author': "XueFeng.Su",
    'website': "https://github.com/cd-feng",
    'category': 'Wechat/登录',
    'version': '18.0.0.1',
    'depends': ['odoo_wechat', 'auth_oauth'],
    "license": "AGPL-3",
    'installable': True,
    'application': False,
    'auto_install': False,
    'data': [
        'data/auth_oauth_data.xml',

        'views/wechat_login_template.xml',
    ],
    'images': [
        'static/description/login.png'
    ],
}
