# -*- coding: utf-8 -*-
import logging
import threading
from odoo import models, api, fields, exceptions

_logger = logging.getLogger(__name__)
SYNCHRONOUS_WECHAT_EMP_STATUS = False


class MdiasWechatEmployee(models.TransientModel):
    _name = 'wechat.employee.synchronous'
    _description = "企业微信员工同步向导"

    company_id = fields.Many2one('res.company', string="公司", required=True, default=lambda self: self.env.company)

    def on_synchronous(self):
        """
        立即同步按钮
        :return:
        """
        global SYNCHRONOUS_WECHAT_EMP_STATUS
        if SYNCHRONOUS_WECHAT_EMP_STATUS:
            raise exceptions.UserError("正在后台同步数据，请稍后在人员档案中查看数据.")
        SYNCHRONOUS_WECHAT_EMP_STATUS = True
        threading.Thread(target=self.synchronous_department_emp, args=[self.env.user.id, self.company_id.id]).start()
        return {
            'type': 'ir.actions.client', 'tag': 'display_notification',
            'params': {
                'type': 'success', 'title': '企业微信同步通知',
                'message': f"系统正在后台同步员工数据，请耐心等待执行完成.",
                'sticky': False, 'next': {'type': 'ir.actions.act_window_close'}
            }
        }

    @api.model
    def synchronous_department_emp(self, uid, company_id):
        """
        执行同步操作
        """
        global SYNCHRONOUS_WECHAT_EMP_STATUS    # 同步的状态，同步完成或者出现任何问题是都要设置为False
        with self.pool.cursor() as new_cr:
            self = self.with_env(self.env(cr=new_cr, su=True))
            employee_model = self.env['hr.employee'].sudo()
            try:
                user_list = employee_model.request_wechat_employee_data(company_id)
                employee_model.update_department_emp_list(user_list, company_id)
            except Exception as e:
                raise exceptions.ValidationError(f"同步企业微信员工数据失败：{e}")
            finally:
                SYNCHRONOUS_WECHAT_EMP_STATUS = False
            # 创建系统用户并与员工关联
            try:
                state, default_password = self.env['wechat.setting'].get_wechat_is_create_wechat_user(company_id)
                if state:
                    employee_model.create_res_users(company_id, default_password)
            except Exception as e:
                raise exceptions.ValidationError(f"创建系统用户并与员工关联时出现了错误：{e}")
            finally:
                SYNCHRONOUS_WECHAT_EMP_STATUS = False

