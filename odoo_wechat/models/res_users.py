# -*- coding: utf-8 -*-
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    wx_ent_user_id = fields.Char(string='企业微信UserId', index=True)
