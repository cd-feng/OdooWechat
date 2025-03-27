# -*- coding: utf-8 -*-
import logging
from odoo import models, exceptions, fields
_logger = logging.getLogger(__name__)


class WechatDepartment(models.TransientModel):
    _name = 'wechat.department.synchronous'
    _description = "企业微信部门同步向导"
    
    company_id = fields.Many2one('res.company', string="公司", required=True, default=lambda self: self.env.company)
    
    def on_synchronous(self):
        """
        立即同步所有的部门数据
        :return:
        """
        try:
            department_data = self.env['hr.department'].request_wechat_department_data(self.company_id.id)
        except Exception as e:
            raise exceptions.ValidationError(f"同步部门数据失败：{e}")
        updated_dept_ids, new_dept_values = self.env['hr.department'].update_odoo_department_data(department_data, self.company_id.id)
        return {
            'type': 'ir.actions.client', 'tag': 'display_notification',
            'params': {
                'type': 'success', 'title': '同步数据结果',
                'message': f"企业微信部门同步完成，共更新 {updated_dept_ids} 条，新增 {new_dept_values} 条!",
                'sticky': False, 'next': {'type': 'ir.actions.act_window_close'}
            }
        }
