# -*- coding: utf-8 -*-
import logging
import base64
import requests
from wechatpy.enterprise import WeChatClient
from odoo import api, fields, models
_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # def send_wechat_message(self, message):
    #     """
    #     发送应用消息
    #     https://qyapi.weixin.qq.com/cgi-bin/message/
    #     """
    #     message_data = {
    #         'touser': "|".join(x.wechat_id for x in self),
    #         'msgtype': 'text',
    #         'agentid': int(wechat_agent_id),
    #         'text': {'content': message},
    #         'safe': 0,
    #     }



