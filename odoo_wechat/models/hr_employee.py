# -*- coding: utf-8 -*-
import logging
import base64
import requests
from wechatpy.enterprise import WeChatClient
from odoo import api, fields, models
_logger = logging.getLogger(__name__)

def get_emp_avatar(avatar_url, timeout=5):
    """
    下载员工的头像(API不支持返回头像了)
    """
    try:
        return base64.b64encode(requests.get(avatar_url, timeout=timeout).content)
    except Exception:
        return False

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    wechat_id = fields.Char(string='企业微信Id', index=True)
    wechat_department_ids = fields.Many2many('hr.department', 'hr_employee_and_wechat_department_rel', string='所属部门')
    wechat_avatar = fields.Html('微信头像', compute='_compute_wechat_avatar', store=True)
    wechat_avatar_url = fields.Char('微信头像链接')
    wechat_status = fields.Selection(string='激活状态', selection=[('1', '已激活'), ('2', '已禁用'), ('4', '未激活'), ('5', '退出企业')])
    wechat_ex_alias = fields.Char(string='别名')

    @api.depends('wechat_avatar_url')
    def _compute_wechat_avatar(self):
        for res in self:
            if res.wechat_avatar_url:
                res.wechat_avatar = """<img src="{}" style="width:100px; height=100px;">""".format(res.wechat_avatar_url)
            else:
                res.wechat_avatar = False

    @api.model
    def request_wechat_employee_data(self, company_id, department_id=1, fetch_child=True):
        """
        从企业微信中同步获取所有员工数据
        """
        corp_id, secret = self.env['wechat.setting'].get_wechat_client_corp_secret(company_id)
        try:
            client = WeChatClient(corp_id, secret)
            return client.user.list(department_id=department_id, fetch_child=fetch_child)
        except Exception as e:
            raise e

    def update_department_emp_list(self, employee_list, company_id):
        """
        更新部门下的所有员工
        """
        if not employee_list:
            _logger.warning("未收到任何员工数据，跳过同步")
            return
        employee_model, department_model = self.env['hr.employee'], self.env['hr.department']
        # 预加载 Odoo 现有的员工
        employee_dict = dict(employee_model.search([('company_id', '=', company_id)]).mapped(lambda e: (e.wechat_id, e.id)))
        # 预加载 Odoo 现有的部门
        department_dict = dict(department_model.search([('company_id', '=', company_id)]).mapped(lambda d: (d.wechat_id, d.id)))
        new_emp_values, updated_emp_ids = [], []
        gender_mapping = {"1": "male", "2": "female"}
        # 处理员工数据（新增/更新）
        for data in employee_list:
            _logger.info(f"同步员工数据：{data}")
            wechat_id, name, position = data['userid'], data['name'], data.get('position', '')
            # 提取 extattr 里的工号
            job_number = next((attr.get('value') for attr in data.get('extattr', {}).get('attrs', []) if attr.get('name') == '工号'), None)
            # 处理部门（默认取 `main_department`）
            department_id = department_dict.get(data.get('main_department')) if data.get('main_department') else False
            values = {
                'company_id': company_id,
                'name': name,
                'wechat_id': wechat_id,
                'job_title': position,
                'job_number': job_number,
                'department_id': department_id,
                'wechat_avatar_url': data.get('avatar'),
                'wechat_status': str(data.get('status')),
                'wechat_ex_alias': data.get('alias'),
                'work_phone': data.get('mobile'),
                'work_email': data.get('email'),
                'gender': gender_mapping.get(str(data.get('gender')), "other"),
            }
            if wechat_id in employee_dict:      # 需要更新的员工
                updated_emp_ids.append((employee_dict[wechat_id], values))
            else:                               # 需要批量创建的新员工
                new_emp_values.append(values)
        # 批量更新已有员工（避免循环 `write()`）
        if updated_emp_ids:
            for emp_id, values in updated_emp_ids:
                employee_model.browse(emp_id).write(values)
        # 批量创建新员工
        if new_emp_values:
            employee_model.create(new_emp_values)
        self.env.cr.commit()
        _logger.info(f"企业微信员工同步完成，共更新 {len(updated_emp_ids)} 条，新增 {len(new_emp_values)} 条")

    @api.model
    def create_res_users(self, company_id, default_password):
        """
        为指定公司(company_id)下的所有员工创建 Odoo 登录用户。
        规则：
        1. 只为 `user_id` 为空的员工创建用户
        2. 使用 `wechat_id` 作为 `login`
        3. 设定默认密码
        4. 绑定 `employee_id`
        """
        res_user, hr_employee = self.env['res.users'], self.env['hr.employee']
        # 获取默认密码
        default_passwd = 'QWERasdf123123!' if not default_password else default_password
        # 获取所有没有创建用户的员工
        employees = hr_employee.search([('company_id', '=', company_id), ('user_id', '=', False), ('wechat_id', '!=', False)])
        if not employees:
            _logger.info(f"没有需要创建用户的员工")
            return
        _logger.info(f"发现{len(employees)}名员工需要创建用户")
        # 预加载所有已有用户，防止 `wechat_id` 冲突
        existing_users = res_user.search_read([], ['id', 'login'])
        existing_logins = {user['login'] for user in existing_users}
        new_users = []
        for emp in employees:
            if emp.wechat_id in existing_logins:
                _logger.warning(f"用户 {emp.wechat_id} 已存在，跳过")
                continue  # 避免创建重复的用户
            new_users.append({
                'name': emp.name,
                'login': emp.wechat_id,
                'wx_ent_user_id': emp.wechat_id,
                'password': default_passwd,
                'company_id': emp.company_id.id,
                'employee_id': emp.id,  # 绑定 employee_id
                'employee_ids': [(6, 0, [emp.id])],  # 反向绑定 employees
                'groups_id': [(6, 0, [self.env.ref('base.group_user').id])]  # 赋予普通用户权限
            })
        if new_users:
            created_users = res_user.create(new_users)
            # 绑定 user_id 到员工表
            # for emp, user in zip(employees, created_users):
            #     emp.user_id = user.id
            _logger.info(f"成功创建 {len(created_users)} 名新用户")

    @api.model
    def get_emp_by_wechat_id(self, wechat_id, company_id=None):
        """
        根据企业微信Id返回员工实例对象
        """
        domain = [('wechat_id', '=', wechat_id)]
        if company_id:
            domain.append(('company_id', '=', company_id))
        return self.search(domain, limit=1)

