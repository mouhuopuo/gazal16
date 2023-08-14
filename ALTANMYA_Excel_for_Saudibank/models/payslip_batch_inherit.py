from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError



class HrPayslip(models.Model):
    _inherit = "hr.payslip"


    house_wage=fields.Monetary(compute='_compute_net')
    allowances=fields.Monetary(compute='_compute_net')
    deductions =fields.Monetary(compute='_compute_net')

    @api.depends('line_ids')
    def _compute_net(self):
        sum_allowance = 0.0
        sum_deductions = 0.0
        sum_house = 0.0
        for payslip in self:
            for line in payslip.line_ids:
                if line.category_id.name == 'Allowance':
                    sum_allowance+=line.total
                elif line.category_id.name == 'Deduction':
                    sum_deductions += line.total
                elif line.category_id.name == 'House':
                    sum_house += line.total
            payslip.allowances = sum_allowance
            payslip.deductions = sum_deductions
            payslip.house_wage = sum_house
            # print("pyyyyyy", sum)




        # sum=0
        # for line in s:
        #     print("line")
        #     if line.category_id == 'House':
        #         sum+=line.total
        # self.house_wage=sum





