# -*- coding: utf-8 -*-
import logging
from odoo import models, api
_logger = logging.getLogger(__name__)


class HrWechatCorn(models.AbstractModel):
    _name = 'hr.wechat.cron'
    _description = "企业微信自动同步任务"

    @api.model
    def _hr_sync_cron(self):
        """
        自动同步任务
        """
        department_model, employee_model = self.env['hr.department'].sudo(), self.env['hr.employee'].sudo()
        for company_id in self.env['res.company'].sudo().search([]):
            # 同步部门数据
            try:
                department_data = department_model.request_wechat_department_data()
                department_model.update_odoo_department_data(department_data, company_id.id)
            except Exception as e:
                _logger.error(f"同步企业微信部门数据失败：{e}")
            # 同步员工数据
            try:
                user_list = employee_model.request_wechat_employee_data()
                employee_model.update_department_emp_list(user_list, company_id.id)
            except Exception as e:
                _logger.error(f"同步企业微信员工数据失败：{e}")
            # 创建系统用户并与员工关联
            try:
                state, default_password = self.env['wechat.setting'].get_wechat_is_create_wechat_user(company_id)
                if state:
                    employee_model.create_res_users(company_id.id, default_password)
            except Exception as e:
                _logger.error(f"创建系统用户并与员工关联失败：{e}")
