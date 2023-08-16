{
    'name': 'Employee Info',
    'author': 'Odoo mates',
    'sequence': -1000,
    'website': 'www.odoomates.tech',
    'summary': 'Odoo 16 Developer',
    'depends': [
        'account_accountant',
        'hr_contract_salary',
        'hr_payroll',
        'report_xlsx', 'web', ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/create_excel_wizard.xml',
        'views/employee_info.xml',
        'views/emp_inherit.xml',
        'views/payslip_inherit.xml',
        'report/report.xml',

    ],
    'license': 'LGPL-3',
}
