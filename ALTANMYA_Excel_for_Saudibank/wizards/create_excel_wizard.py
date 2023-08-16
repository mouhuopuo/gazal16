from odoo import api, fields, models


class Createexcelwizard(models.TransientModel):
    _name = "create.excel.wizard"  # name of Table
    _description = "Create Excel Wizard"

    emp_info_id = fields.Many2one('employee.info', string='Employee Info', required=True)
    payslips_batch_id = fields.Many2one('hr.payslip.run', string='Payslips Batches', required=True)
    due_date = fields.Date(string='Due Date', required=True)
    batch_num = fields.Char(string='Batch Number', required=True)

    def print_payroll_excel(self):
        print("payrol")
        # emp_info_id = self.emp_info_id.id
        # if emp_info_id:
        #     query = """
        #             SELECT *
        #             FROM employee_info
        #             WHERE id = %s
        #         """
        #     self.env.cr.execute(query, [emp_info_id])
        #     rec = self.env.cr.dictfetchall()
        # else:
        #     rec = []
        #
        # print("records", rec)
        # data = {
        #     'rec': rec,
        #     'form_data': self.read()[0],
        # }
        # report = self.env.ref('ALTANMYA_Excel_for_Saudibank.report_payroll_card_xls')
        # return report.report_action(self, data=data)

        # rec=self.env['employee.info'].search_read([('id', '=', emp_info_id)])

        if not self.emp_info_id:
            raise ValueError("Please select Employee Info.")

        if not self.payslips_batch_id:
            raise ValueError("Please select Payslips Batches.")

        domain1 = []
        domain2 = []
        emp_info_id = self.emp_info_id
        # payslips_batch_id=self.payslips_batch_id
        if emp_info_id:
            # domain1=[('name', '=', emp_info_id.employee_name)]
            domain2 = [('id', '=', emp_info_id.id)]
            domain3 = [('emp_Info', '=', emp_info_id.id)]

        # payslips_batch_id = self.paayslips_batch_id
        recc1 = self.env['hr.employee'].search(domain2)
        recc = self.env['hr.employee'].search(domain3)
        forpayslips = self.env['hr.employee'].search(domain3)
        print("forpayslips", forpayslips)
        x = self.env['hr.payslip']
        for rec in forpayslips:
            x += self.payslips_batch_id.slip_ids.filtered(lambda l: l.employee_id.id == rec['id'])
        temp = self.env['hr.payslip'].search_read([('id', 'in', x.ids)])
        print("rec", recc, temp)
        print("datttttee", self.due_date)
        date = str(self.due_date.day) + '-' + str(self.due_date.month) + '-' + str(self.due_date.year)
        data = {
            'rec': [emp.id for emp in recc],
            'rec1': [emp.id for emp in recc1],
            'form_data': self.read()[0],
            'temp': temp,
            'due_date': date,
            'batch_num': self.batch_num,
        }

        report = self.env.ref('ALTANMYA_Excel_for_Saudibank.report_payroll_card_xls')
        return report.report_action(self, data=data)
