from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError



class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"


    emp_Info=fields.Many2one('employee.info', string='Bank Excel Sheet')
