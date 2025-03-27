# -*- coding: utf-8 -*-
import logging
from wechatpy.enterprise import WeChatClient
from odoo import fields, models, api
_logger = logging.getLogger(__name__)


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    wechat_id = fields.Integer(string='企业微信部门ID', index=True)
    wechat_department_leader = fields.Char(string='部门负责人的UserID')
    wechat_parent_id = fields.Integer(string='父部门ID', index=True)
    wechat_order = fields.Char(string='父部门中的次序值')

    @api.model
    def request_wechat_department_data(self, company_id):
        """
        从企业微信中同步获取所有部门数据
        """
        corp_id, secret = self.env['wechat.setting'].get_wechat_client_corp_secret(company_id)
        try:
            client = WeChatClient(corp_id, secret)
            return client.department.get()
        except Exception as e:
            raise e

    @api.model
    def update_odoo_department_data(self, department_list, company_id):
        """
        更新微信部门数据
        """
        if not department_list:
            _logger.warning("未收到任何企业微信部门数据，跳过更新...")
            return
        model = self.env['hr.department'].sudo()
        # 预加载已有的部门数据（减少数据库查询）
        existing_departments = model.search_read([('company_id', '=', company_id)], ['id', 'wechat_id', 'parent_id'])
        department_dict = {dept['wechat_id']: dept['id'] for dept in existing_departments if dept.get('wechat_id')}
        new_dept_values, updated_dept_ids = [], []
        # 处理部门数据（新增/更新）
        for data in department_list:
            wechat_id, name = data['id'], data['name']
            values = {
                'company_id': company_id,
                'name': name,
                'wechat_id': wechat_id,
                'wechat_department_leader': data.get('department_leader'),
                'wechat_parent_id': data.get('parentid'),
                'wechat_order': data.get('order'),
            }
            if wechat_id in department_dict:
                updated_dept_ids.append((department_dict[wechat_id], values))
            else:
                new_dept_values.append(values)
        # 批量更新已有部门
        if updated_dept_ids:
            for dept_id, values in updated_dept_ids:
                model.browse(dept_id).write(values)
        # 批量创建新部门
        if new_dept_values:
            new_departments = model.create(new_dept_values)
            department_dict.update({dept.wechat_id: dept.id for dept in new_departments})
        self.env.cr.commit()  # 提交事务，提高稳定性
        # 处理上级部门（避免重复搜索）
        for data in department_list:
            wechat_id, parentid = data.get('id'), data.get('parentid')
            if parentid and parentid in department_dict and wechat_id in department_dict:
                model.browse(department_dict[wechat_id]).write({'parent_id': department_dict[parentid]})
        return len(updated_dept_ids), len(new_dept_values)

