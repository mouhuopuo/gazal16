from odoo import models
import base64
import io
import logging
_LOGGER = logging.getLogger(__name__)


class ExcelPayrollXlsx(models.AbstractModel):
    _name = 'report.employee.info.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    # def write_emp_info_records(self, sheet, start_row, emp_info_records, border_format,data):
    #     emp_info_id = data.get('emp_info_id', False)
    #     row = start_row
    #     col = 0
    #
    #     for emp_info_record in emp_info_records:
    #         emp_info = self.env['employee.info'].browse(emp_info_record)
    #         if emp_info_id and emp_info_id != emp_info_record['id']:
    #             continue
    #
    #         row_data = [
    #             emp_info.type,
    #             emp_info.name,
    #             emp_info.agreement_code,
    #             emp_info.finance_account,
    #             emp_info.num_of_section,
    #             emp_info.num_of_facilityin_in_office,
    #             emp_info.num_of_facilityin_in_commerce,
    #             emp_info.bank_code,
    #             emp_info.currency.name,
    #             emp_info.file_reference,
    #         ]
    #
    #         sheet.write_row(row, col, row_data, border_format)
    #         row += 1
    #
    #     # Now you can call the function like this within your main method

    def generate_xlsx_report(self, workbook, data, emp):
        emp_info_id = data.get('emp_info_id', False)
        batch_num = data.get('batch_num', False)


        processed_temp = data.get('temp', [])

        fields_to_include = ['type', 'name', 'agreement_code', 'finance_account', 'num_of_section',
                             'num_of_facilityin_in_office', 'num_of_facilityin_in_commerce', 'bank_code', 'currency',
                             'file_reference']
        fields_to_capitalize = ['type', 'اسم العميل', 'رمز الاتفاقية', 'حساب التمويل', 'رقم الفرع','تاريخ الأستحقاق ',
                                ' رقم المنشأة في مكتب العمل  ',
                                'رقم المنشأة في الغرفة التجارية', 'رمز البنك', 'العملة','رقم الدفعة', 'مرجع الملف']
        fields_to_include_third_row = ['SN','هوية المستفيد/ المرجع'
            , 'المستفيد/اسم الموظف', 'رقم الحساب', 'رمز البنك', 'إجمالي المبلغ', 'الراتب الأساسي', 'بدل السكن',
                                       'دخل آخر', 'الخصومات', 'العنوان', 'العملة', 'الحالة', 'وصف الدفع', 'مرجع الدفع']
        #
        # print("emp", data['rec'])
        # print("emp info", emp_info_id)
        # print("sadsd", data.get('x', []))

        sheet = workbook.add_worksheet('Excel ')
        bold = workbook.add_format({'bold': True})
        format_1 = workbook.add_format(
            {'bold': True, 'bg_color': '#038d71', 'font_color': 'white', 'border': 1})
        border_format = workbook.add_format({'border': 1})
        header_height = 30  # Adjust the height value as needed
        sheet.set_row(0, header_height)  # Adjust the height value as needed

        for col, field_name in enumerate(fields_to_capitalize):
            sheet.write(0, col, field_name.capitalize(), format_1)


        for col, field_name in enumerate(fields_to_include):
            sheet.set_column(col, col, len(field_name)+2)

        _LOGGER.info(" row data ")
        _LOGGER.info(data['rec1'])
        row = 1
        due_date = data.get('due_date', False)
        # print("date ", type(due_date))
        # print("date ", type(due_date))
        # formatted_due_date = datetime.strptime(due_date, '%Y-%M-%d')
        # print("time", formatted_due_date)
        # formatted_due_date.strftime(formatted_due_date[0],'%d%m%y')
        # print("time",formatted_due_date)




        for emp_info_record in data['rec1']:
            emp_info = self.env['employee.info'].browse(emp_info_record)
            if emp_info_id and emp_info_id != emp_info_record['id']:
                continue
            col = 0
            row_data = [
                emp_info.type,
                emp_info.name,
                emp_info.agreement_code,
                emp_info.finance_account,
                emp_info.num_of_section,
                due_date,
                emp_info.num_of_facilityin_in_office,
                emp_info.num_of_facilityin_in_commerce,
                emp_info.bank_code,
                emp_info.currency.name,
                batch_num,
                # curency[0],
            ]
            # for field_name in bank_info_record:
            sheet.write_row(row, col, row_data, border_format)
            row += 1


        for col, field_name in enumerate(fields_to_include_third_row):
            sheet.write(2, col, field_name.capitalize(), format_1)



        for col, field_name in enumerate(fields_to_include_third_row):
            sheet.set_column(col, col, len(field_name)+6)


        aggregated_data = {}

        # Iterate through each record
        print('data ', data)
        for employee_id in data['rec']:
            emp = self.env['hr.employee'].browse(employee_id)
            if not aggregated_data.get(emp.id):
                aggregated_data[emp.id] = {
                    'employee_id': emp,
                    'net_wage': 0.0,
                    'basic_wage': 0.0,
                    'house_wage': 0.0,
                    'allowances': 0.0,
                    'deductions': 0.0,
                    'state': 'inactive',
                    'empty':''
                }
        print('agg ', aggregated_data)
        for (payslip_rec) in data['temp']:
            print('payslip : ', payslip_rec)
            payslip = self.env['hr.payslip'].browse(payslip_rec['id'])
            employee_id = payslip.employee_id.id
            print('employee : ', employee_id, payslip.employee_id.name)

            if employee_id not in aggregated_data:
                # Initialize the dictionary for the employee
                aggregated_data[employee_id] = {
                    'employee_id': payslip.employee_id,
                    'net_wage': payslip.net_wage,
                    'basic_wage': payslip.basic_wage,
                    'house_wage': payslip.house_wage,
                    'allowances': payslip.allowances,
                    'deductions': payslip.deductions,
                }
            else:
                aggregated_data[employee_id]['net_wage'] += payslip.net_wage
                aggregated_data[employee_id]['basic_wage'] += payslip.basic_wage
                aggregated_data[employee_id]['house_wage'] += payslip.house_wage
                aggregated_data[employee_id]['allowances'] += payslip.allowances
                aggregated_data[employee_id]['deductions'] += payslip.deductions
                aggregated_data[employee_id]['state'] = 'active'
                aggregated_data[employee_id]['empty'] = ''
        print("aggregated", aggregated_data)

        # Write aggregated data to the Excel sheet
        sequence = 0o001
        row = 3
        for employee_id, emp_data in aggregated_data.items():
            col = 0
            row_data = [
                sequence,
                emp_data['employee_id'].identification_id,
                emp_data['employee_id'].name,
                emp_data['employee_id'].bank_account_id.acc_number,
                emp_data['employee_id'].bank_account_id.bank_id.bic,
                emp_data['net_wage'],
                emp_data['basic_wage'],
                emp_data['house_wage'],
                emp_data['allowances'],
                emp_data['deductions'],
                emp_data['empty'],
                emp_info['currency'].name,
                emp_data['state'],
            ]
            sheet.write_row(row, col, row_data, border_format)
            row += 1
            sequence += 1

        sheet.merge_range('L1:O1', '')
        sheet.merge_range('L2:O2', '')

        sheet.freeze_panes(1, 0)
        for worksheet in workbook.worksheets():
            worksheet.set_paper(9)  # 9 corresponds to A4
#################################################################################################
    # def setup_formats(slef,workbook):
    #     print("hhhhhhhhh")
    #
    #     bold = workbook.add_format({'bold': True})
    #     format_1 = workbook.add_format(
    #         {'bold': True, 'bg_color': '#038d71', 'font_color': 'white', 'border': 1})
    #     border_format = workbook.add_format({'border': 1})
    #     return bold, format_1, border_format
    #
    # def write_header(self,sheet, fields_to_capitalize, format_1):
    #     for col, field_name in enumerate(fields_to_capitalize):
    #         sheet.write(0, col, field_name.capitalize(), format_1)
    #
    # def set_column_widths(self,sheet, fields_to_include):
    #     for col, field_name in enumerate(fields_to_include):
    #         sheet.set_column(col, col, len(field_name) + 2)
    #
    # def write_employee_data(self, sheet, emp_info_records, emp_info_id, border_format):
    #     row = 1
    #     for emp_info_record in emp_info_records:
    #         emp_info = self.env['employee.info'].browse(emp_info_record)
    #         if emp_info_id and emp_info_id != emp_info_record['id']:
    #             continue
    #         col = 0
    #         row_data = [
    #             emp_info.type,
    #             emp_info.name,
    #             emp_info.agreement_code,
    #             emp_info.finance_account,
    #             emp_info.num_of_section,
    #             emp_info.num_of_facilityin_in_office,
    #             emp_info.num_of_facilityin_in_commerce,
    #             emp_info.bank_code,
    #             emp_info.currency.name,
    #             emp_info.file_reference,
    #             # curency[0],
    #         ]
    #         sheet.write_row(row, col, row_data, border_format)
    #         row += 1
    #
    # def write_third_row_header(self,sheet, fields_to_include_third_row, format_1):
    #     for col, field_name in enumerate(fields_to_include_third_row):
    #         sheet.write(2, col, field_name.capitalize(), format_1)
    #
    # def set_third_row_column_widths(self,sheet, fields_to_include_third_row):
    #     for col, field_name in enumerate(fields_to_include_third_row):
    #         sheet.set_column(col, col, len(field_name) + 6)
    #
    # def process_payslip_data(self, payslip_records, emp_info_records):
    #     aggregated_data = {}
    #
    #     # Iterate through each record
    #     for employee_id in emp_info_records:
    #         emp = self.env['hr.employee'].browse(employee_id)
    #         if not aggregated_data.get(emp.id):
    #             aggregated_data[emp.id] = {
    #                 'employee_id': emp,
    #                 'net_wage': 0.0,
    #                 'basic_wage': 0.0,
    #                 'house_wage': 0.0,
    #                 'allowances': 0.0,
    #                 'deductions': 0.0,
    #                 'state': 'inactive'
    #             }
    #     for payslip_rec in payslip_records:
    #         payslip = self.env['hr.payslip'].browse(payslip_rec['id'])
    #         employee_id = payslip.employee_id.id
    #
    #         if employee_id not in aggregated_data:
    #             # Initialize the dictionary for the employee
    #             aggregated_data[employee_id] = {
    #                 'employee_id': payslip.employee_id,
    #                 'net_wage': payslip.net_wage,
    #                 'basic_wage': payslip.basic_wage,
    #                 'house_wage': payslip.house_wage,
    #                 'allowances': payslip.allowances,
    #                 'deductions': payslip.deductions,
    #             }
    #         else:
    #             aggregated_data[employee_id]['net_wage'] += payslip.net_wage
    #             aggregated_data[employee_id]['basic_wage'] += payslip.basic_wage
    #             aggregated_data[employee_id]['house_wage'] += payslip.house_wage
    #             aggregated_data[employee_id]['allowances'] += payslip.allowances
    #             aggregated_data[employee_id]['deductions'] += payslip.deductions
    #             aggregated_data[employee_id]['state'] = 'active'
    #     return aggregated_data
    #
    # def write_aggregated_data(self,sheet, aggregated_data, fields_to_include_third_row, border_format):
    #     sequence = 0o001
    #     row = 3
    #     for employee_id, emp_data in aggregated_data.items():
    #         col = 0
    #         row_data = [
    #             sequence,
    #             emp_data['employee_id'].id,
    #             emp_data['employee_id'].name,
    #             emp_data['employee_id'].bank_account_id.acc_number,
    #             emp_data['employee_id'].bank_account_id.bank_id.bic,
    #             emp_data['net_wage'],
    #             emp_data['basic_wage'],
    #             emp_data['house_wage'],
    #             emp_data['allowances'],
    #             emp_data['deductions'],
    #             emp_data['house_wage'],
    #             # emp_info['currency'].name,
    #             # emp_data['state'],
    #         ]
    #         sheet.write_row(row, col, row_data, border_format)
    #         row += 1
    #         sequence += 1
    #
    # def generate_xlsx_report(self, workbook, data, emp):
    #     sheet = workbook.add_worksheet('Excel ')
    #
    #     # bold = self.setup_formats(workbook).bold
    #     format_1 = self.setup_formats(workbook)
    #     print("hhhhhhhhh")
    #
    #     border_format = self.setup_formats(workbook)
    #
    #     fields_to_include = ['type', 'name', 'agreement_code', 'finance_account', 'num_of_section',
    #                          'num_of_facilityin_in_office', 'num_of_facilityin_in_commerce', 'bank_code', 'currency',
    #                          'file_reference']
    #     fields_to_capitalize = ['type', 'اسم العميل', 'رمز الاتفاقية', 'حساب التمويل', 'رقم الفرع',
    #                             ' رقم المنشأة في مكتب العمل  ',
    #                             'رقم المنشأة في الغرفة التجارية', 'رمز البنك', 'العملة', 'مرجع الملف']
    #
    #     fields_to_include_third_row = ['SN', 'هوية المستفيد/ المرجع'
    #         , 'المستفيد/اسم الموظف', 'رقم الحساب', 'رمز البنك', 'إجمالي المبلغ', 'الراتب الأساسي', 'بدل السكن',
    #                                    'دخل آخر', 'الخصومات', 'العنوان', 'العملة', 'الحالة', 'وصف الدفع', 'مرجع الدفع']
    #
    #     header_height = 30
    #     sheet.set_row(0, header_height)
    #
    #     self.write_header(sheet, fields_to_capitalize, format_1)
    #     self.set_column_widths(sheet, fields_to_include)
    #     self.write_third_row_header(sheet, fields_to_include_third_row, format_1)
    #     self.set_third_row_column_widths(sheet, fields_to_include_third_row)
    #
    #     # emp_info_records = data['rec1']
    #     # emp_info_id = data.get('emp_info_id', False)
    #     # self.write_employee_data(sheet, emp_info_records, emp_info_id, border_format)
    #     #
    #     #
    #     # payslip_records = data['temp']
    #     # aggregated_data = self.process_payslip_data(payslip_records, emp_info_records)
    #     # self.write_aggregated_data(sheet, aggregated_data, fields_to_include_third_row, border_format)
    #
    #     sheet.merge_range('K1:O1', '', format_1)
    #     sheet.freeze_panes(1, 0)
    #
    #     for worksheet in workbook.worksheets():
    #         worksheet.set_paper(9)  # 9 corresponds to A4
    #
    #
