{
    'name': 'Company Distrubution',
    'author': 'Odoo mates',
    'sequence': -1000,
    'website': 'www.odoomates.tech',
    'summary': 'Odoo 16 Developer',
    'depends': ['account_accountant'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/cron_action.xml',
        'views/Accounting_menu.xml',

    ]
}
