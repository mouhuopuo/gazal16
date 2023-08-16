from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class EmpInfo(models.Model):
    _name = "employee.info"  # name of Table

    type = fields.Char(string="Type")
    name = fields.Char(string="Name")
    agreement_code = fields.Char(string="Agreement Code", tracking=True)
    finance_account = fields.Char(string="Finance account", tracking=True)
    num_of_section = fields.Char(string="Number of ٍSection", tracking=True)
    num_of_facilityin_in_office = fields.Char(string="Number of Facility (office)", tracking=True)
    num_of_facilityin_in_commerce = fields.Char(string="Number of Facility (commerce)", tracking=True)
    bank_code = fields.Char(string="Bank Code", tracking=True)
    currency = fields.Many2one('res.currency', string='Currency', selection_add=[('3', 'SAR')])
    file_reference = fields.Char(string='File Reference')

    # hr_employee=fields.Many2one('hr.employee', string='Employee')
    # employee_name = fields.Char(string='Employee Name', compute='_compute_employee_data', store=True)
    # identification_id = fields.Char(string='Identification ID', compute='_compute_employee_data', store=True)
    # bank_account_id = fields.Char(string='Bank Account ID', compute='_compute_employee_data', store=True)
    #

    # Your other fields for the employee.info model

    @api.depends('name')
    def _compute_employee_data(self):
        # records= self.env['hr.employee'].search([('emp_Info','=',self.id)])
        # print("records",records)
        name = []
        for rec in self:
            employee = rec.env['hr.employee'].search([('emp_Info', '=', rec.id)], limit=1)
            if employee:
                rec.employee_name = employee.name
                rec.identification_id = employee.identification_id
                rec.bank_account_id = employee.bank_account_id
            # rec.bank_account_id
            # # data=[
            # #     rec.identification_id,
            # #     rec.name,
            # #     rec.bank_account_id,
            # # ]
            # name=rec.bank_account_id
            # self.employee_name = name
        print("name", name)

    def name_get(self):
        print("name get")
        res = []
        for rec in self:
            name = f'{rec.name} - {rec.num_of_facilityin_in_office}'
            res.append((rec.id, name))
        return res
