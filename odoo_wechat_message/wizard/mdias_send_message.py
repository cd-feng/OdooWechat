# -*- coding: utf-8 -*-
import logging
from odoo import models, fields
_logger = logging.getLogger(__name__)


class MdiasWechatSendMessage(models.TransientModel):
    _name = 'mdias.wechat.send.message'
    _description = "测试发送应用消息"

    employee_ids = fields.Many2many("hr.employee", "mdias_employee_and_wechat_message_rel",
                                    string="接收消息员工", required=True, domain="[('wechat_id', '!=', False)]")
    content = fields.Text(string="消息内容", default='MDIAS消息通知. \n 在 <a href="http://xxx.com:8060/mdias/wechat/auto_oauth"> MDIAS </a> 系统中向您推送了一条消息。')

    def on_send_message(self):
        """
        发送消息
        """
        self.employee_ids.send_wechat_message(self.content)
        return {'type': 'ir.actions.act_window_close'}
