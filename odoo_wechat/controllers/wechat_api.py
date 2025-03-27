# -*- coding: utf-8 -*-
import base64
from werkzeug.exceptions import NotFound
from odoo.http import request, route, Controller


class WechatApi(Controller):

    @route('/<string:filename>.txt', type='http', auth="public", methods=['GET'])
    def wechat_verify_jsdk_file_content(self, filename=None, **kw):
        """
        读取js_sdk校验文件内容，进行企业微信验证
        :return: wechat_js_sdk_file的文件内容
        """
        wechat_id = request.env['wechat.setting'].sudo().search([('wechat_js_sdk_file_name', '=', f'{filename}.txt')], limit=1)
        if not wechat_id:
            raise NotFound()
        return base64.b64decode(wechat_id.wechat_js_sdk_file.decode('utf-8'))

