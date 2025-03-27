# -*- coding: utf-8 -*-
import logging
from wechatpy.enterprise import WeChatClient
from odoo.addons.web.controllers.main import ensure_db
from odoo.http import request, route, Controller
from odoo.exceptions import AccessError
from odoo.service import security

_logger = logging.getLogger(__name__)


class WeChatApi(Controller):

    @route('/wechat/auto_oauth', type='http', auth='none', methods=['GET'])
    def wechat_auto_oauth(self, **kw):
        """
        企业微信内免密登录接口（企业微信内自动授权）
        """
        ensure_db()
        if request.uid and request.session.uid and request.session.session_token:
            return request.redirect('/web')
        wechat_company_data = request.env['wechat.setting'].sudo().get_all_company_wechat_corp()
        if not wechat_company_data:
            return request.redirect('/web')
        return request.render('odoo_wechat_login.oauth_login_template', {
            'wechat_company_data': wechat_company_data,
        })

    @route('/wechat/login', type='http', auth='none', methods=['GET'])
    def wechat_login(self, **kw):
        """
        构造企业微信网页授权链接(需要网页上手动授权)
        """
        ensure_db()
        if request.uid and request.session.uid and request.session.session_token:
            return request.redirect('/web')
        wechat_company_data = request.env['wechat.setting'].sudo().get_all_company_wechat_corp()
        if not wechat_company_data:
            return request.redirect('/web')
        return request.render('odoo_wechat_login.login_template', {'wechat_company_data': wechat_company_data})

    @route('/wechat/oauth/login', type='http', auth='none', methods=['GET'])
    def wechat_oauth_login(self, **kw):
        """
        根据企业微信的用户身份在PC端做免登认证处理，认证成功即可登录MDIAS系统
        """
        _logger.info('企业微信正在调用免登身份认证，携带参数为:{}'.format(kw))
        code, corp_id = kw.get('code', None), kw.get('state', None)
        if not code or not corp_id:
            return f"登录失败，回调参数不正确. code: {code}, wechat_corp_id: {corp_id}"
        setting_id = request.env['wechat.setting'].sudo().search([('wechat_corp_id', '=', corp_id)], limit=1)
        if not setting_id:
            return f"登录失败，无可用的wechat_corp_id: {corp_id}"
        try:
            client = WeChatClient(setting_id.wechat_corp_id, setting_id.wechat_secret)
            user_data = client.get('auth/getuserinfo', params={'code': code})
            # user_data = client.user.get_info(setting_id.wechat_agent_id, code)
            wechat_uid = user_data['userid']
            emp_id = request.env['hr.employee'].sudo().get_emp_by_wechat_id(wechat_uid, setting_id.company_id.id)
        except Exception as e:
            return f"获取企业微信用户信息失败：{e}"
        if not emp_id.user_id:
            return f"<h1>系统未授予{emp_id.name}用户的登录权限，请联系管理员处理..</h1>"
        try:
            request.uid = emp_id.user_id.id
            request.session.uid = emp_id.user_id.id
            request.session.session_token = security.compute_session_token(request.session, request.env)
        except AccessError as e:
            return "尝试登录系统失败：{}".format(e)
        except Exception as e:
            raise e
        return request.redirect('/web')
