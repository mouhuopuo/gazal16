from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CompanyDis(models.Model):
    _name = "companies.disturubition"  # name of Table
    _inherit = 'mail.thread'

    company_id = fields.Many2one(
        'res.company',
        'Company',
        default=lambda self: self.env['res.company']._company_default_get('companies.disturubition'), tracking=True)

    ref = fields.Char(string="Reference", tracking=True)
    account = fields.Many2one('account.account', string='Account', domain="[('company_id', '=', company_id)]",
                              tracking=True, required=True)
    date = fields.Date(string='Date', tracking=True, required=True)
    journal = fields.Many2one('account.journal', string='Journal',
                              domain="[('company_id', '=', company_id),('type','=','general')]", tracking=True,
                              required=True)
    frequency = fields.Selection([('monthly', 'Monthly'), ('quarterly ', 'Quarterly'), ('yearly', 'Yearly')],
                                 string='Frequency', default='monthly', tracking=True, required=True)
    conter_account = fields.Many2one('account.account', string='Counter Account',
                                     domain="[('company_id', '=', company_id)]", tracking=True, required=True)
    company_ids = fields.One2many('company.lines', 'company_id', string="Companies", tracking=True, required=True)

    account_current_balance = fields.Float(
        related='account.current_balance',
        string='Account Current Balance',
        readonly=True, tracking=True, required=True
    )
    account_type = fields.Selection(
        related='account.account_type',
        string='Account Current Type',
        readonly=True, tracking=True
    )
    total_rate = fields.Float(compute='_compute_total_rate', string='Total Rate', store=True, tracking=True)
    or_date = fields.Date(
        string='Original Date',


    )

    # def _get_inserted_date(self):
    #     return self.date

    # @api.depends('date')
    # def _compute_date(self):
    #     for rec in self:
    #
    #         if rec.date:
    #
    #             rec.or_date = rec.date
    #         else:
    #             rec.or_date = ''

    @api.depends('company_ids.rate')
    def _compute_total_rate(self):
        for record in self:
            total_tax = sum(record.company_ids.mapped('rate'))
            record.total_rate = total_tax

    @api.constrains('total_rate')
    def _check_total_rate(self):
        for record in self:
            if record.total_rate > 1.00:
                raise ValidationError("The sum of Rate values in Companies cannot exceed 100% ")
            if record.total_rate < 1.00:
                raise ValidationError("The sum of Rate values in Companies cannot be less than 100%.")

    def perform_operations(self, date):
        print("fun")
        current_date = date
        records = self.search([('date', '=', current_date)])
        if records:
            print('rec', records)
            for record in records:
                main_account = self.env['account.account'].search([('id', '=', record.account.id)])
                # counter_account = self.env['account.account'].search([('id', '=', record.conter_account.id)])
                x = self.env['account.move'].create({
                    'date': record.date,
                    'journal_id': record.journal.id,
                    'ref': 'Transfer from original company (cron) ',
                })

                print("record ", x)
                is_credit = False
                if main_account.internal_group in ('asset', 'expense'):
                    self.env['account.move.line'].create({
                        # 'account_id': vals['company_ids'][0][2]['destination_account'],
                        'account_id': record.account.id,
                        'move_id': x.id,
                        'credit': main_account.current_balance,
                    })
                    print('got here 1')
                    is_credit = True
                elif main_account.internal_group in ('income', 'liability', 'equity'):
                    self.env['account.move.line'].create({
                        # 'account_id': vals['company_ids'][0][2]['destination_account'],
                        'account_id': record.account.id,
                        'move_id': x.id,
                        'debit': main_account.current_balance,
                    })
                    print('got here 2')
                    is_credit = False

                if is_credit:
                    self.env['account.move.line'].create({
                        # 'account_id': vals['company_ids'][0][2]['destination_account'],
                        'account_id': record.conter_account.id,
                        'move_id': x.id,
                        'debit': main_account.current_balance,
                    })
                    print('got here 3')
                else:
                    self.env['account.move.line'].create({
                        # 'account_id': vals['company_ids'][0][2]['destination_account'],
                        'account_id': record.conter_account.id,
                        'move_id': x.id,
                        'credit': main_account.current_balance,
                    })
                    print('got here 4')
                x.action_post()
                for line in record.company_ids:
                    destination_company_name = line.company.name
                    print("line", line)
                    # parent = self.env['companies.disturubition'].search([('id', '=',line.company_id.id)])
                    main_account_line = self.env['account.account'].search([('id', '=', line.destination_account.id)])
                    x = self.env['account.move'].create({
                        'journal_id': line.journal.id,
                        'date': record.date,
                        'ref': 'Transfer to other companies cron ',
                    })
                    is_credit = False
                    if main_account_line.internal_group in ('income', 'liability', 'equity'):
                        self.env['account.move.line'].create({
                            'account_id': line.destination_account.id,
                            'move_id': x.id,
                            'credit': record.account_current_balance * line.rate,
                        })
                        # print('got  here 11')
                        # print('tax',main_account_line.current_balance)
                        is_credit = True
                    elif main_account_line.internal_group in ('asset', 'expense'):
                        self.env['account.move.line'].create({
                            # 'account_id': vals['company_ids'][0][2]['destination_account'],
                            'account_id': line.destination_account.id,
                            'move_id': x.id,
                            'debit': record.account_current_balance * line.rate,
                        })
                        # print('got here 22')
                        # print('tax', main_account_line.current_balance)
                        is_credit = False

                    if is_credit:
                        self.env['account.move.line'].create({
                            'account_id': line.counter_account.id,
                            'move_id': x.id,
                            'debit': record.account_current_balance * line.rate,
                        })
                        # print('got here 33')
                        # print('tax', counter_account_line.current_balance)
                    else:
                        self.env['account.move.line'].create({
                            # 'account_id': vals['company_ids'][0][2]['destination_account'],
                            'account_id': line.counter_account.id,
                            'move_id': x.id,
                            'credit': record.account_current_balance * line.rate,
                        })
                    x.action_post()

    @api.model
    def schedule_cron_job(self):
        # Get the current date
        current_date = datetime.now().date()

        records = self.search([('date', '=', current_date)])

        for rec in records:
            print("records", len(rec.frequency), len('yearly'))
            if rec.frequency == 'monthly':
                self.perform_operations(rec.date)
                rec.date = rec.date + relativedelta(months=1)
                print('monthly', rec.date)

            elif rec.frequency == 'yearly':
                print('yearly')
                self.perform_operations(rec.date)
                rec.date = rec.date + relativedelta(years=1)
                print('yearly', rec.date)
            else:
                print('quarterly')
                self.perform_operations(rec.date)
                rec.date = rec.date + relativedelta(months=3)
                print('next quarterly', rec.date)

    def name_get(self):
        print("name get")
        print('def', 'context')
        res = []
        for rec in self:
            name = rec.ref
            res.append((rec.id, name))
        return res

    def cr_move_for_original(self, vals,date):
        x = self.env['account.move'].create({
            'date': date,
            'journal_id': vals['journal'],
            'ref': 'Transfer from company ',
        })

        main_account = self.env['account.account'].search([('id', '=', vals['account'])])
        is_credit = False
        if main_account.internal_group in ('asset', 'expense'):
            self.env['account.move.line'].create({
                'account_id': vals['account'],
                'move_id': x.id,
                'credit': main_account.current_balance,
            })
            is_credit = True
        elif main_account.internal_group in ('income', 'liability', 'equity'):
            self.env['account.move.line'].create({
                'account_id': vals['account'],
                'move_id': x.id,
                'debit': main_account.current_balance,
            })
            is_credit = False

        if is_credit:
            self.env['account.move.line'].create({
                'account_id': vals['conter_account'],
                'move_id': x.id,
                'debit': main_account.current_balance,
            })
        else:
            self.env['account.move.line'].create({
                'account_id': vals['conter_account'],
                'move_id': x.id,
                'credit': main_account.current_balance,
            })
        x.action_post()

        # if vals['frequency'] == 'monthly':



    # @api.model_create_multi
    # def create(self, vals_list):
    #     print(vals_list)
    #     for val in vals_list:
    #         val['ref'] = self.env['ir.sequence'].next_by_code('companies.disturubition')  # return next code of sequence
    #         print("created")
    #     return super(CompanyDis, self).create(vals_list)

    @api.model
    def create(self, vals):
        # vals['inserted_date'] = vals.get('date', False)
        original_date = vals.get('date', False)
        vals['or_date'] = vals.get('date', False)

        print('monthly',vals['frequency'])
        # print('inserted date ', vals['inserted_date'])

        if vals['frequency'] == 'monthly':
            date = datetime.strptime(original_date, '%Y-%m-%d')
            vals['date'] = (date + relativedelta(months=1)).strftime('%Y-%m-%d')


        elif vals['frequency'] == 'yearly':
            print('yearly')
            date = datetime.strptime(original_date, '%Y-%m-%d')
            vals['date'] = (date + relativedelta(years=1)).strftime('%Y-%m-%d')
            # print('yearly', rec.date)
        else:
            print('quarterly')
            date = datetime.strptime(original_date, '%Y-%m-%d')
            vals['date'] = (date + relativedelta(months=3)).strftime('%Y-%m-%d')
            # print('next quarterly', rec.date)

        # Increment the date by 1 month
        # if original_date:
        #     date = datetime.strptime(original_date, '%Y-%m-%d')
        #     vals['date'] = (date + relativedelta(months=1)).strftime('%Y-%m-%d')

        print("date is ", vals['date'])
        print("original is ", original_date)


        res = super(CompanyDis, self).create(vals)
        current_date = datetime.now().date()

        # TODO:: fetch the lines with their type
        # TODO:: you need to compute the value of the debit or the credit from the detched account we acces
        # TODO:: the current_balance value
        # then create the move from the processed values
        # after that you need to divide the value of the move on the specified companies in the lines
        # based on their rate
        # BUT before all of this you need to link the moves of the inter companies with their parent move

        if str(current_date) == str(original_date):
            # print("date is ", vals['date'])
            res.cr_move_for_original(vals,original_date)
            print("frequency is ", vals['frequency'])
            # print("date create ", vals['date'])
            # vals['date'] = vals['date'] + str(relativedelta(months=1))
            # vals['date'] = (datetime.strptime(vals['date'], '%Y-%m-%d') + relativedelta(months=1)).strftime('%Y-%m-%d')
            # print("increment date ", vals['date'])

        return res


class CompanyLines(models.Model):
    _name = "company.lines"

    company = fields.Many2one('res.company', string="Company")

    destination_account = fields.Many2one('account.account', string="Destination account",
                                          domain="[('company_id', '=', company)]")
    counter_account = fields.Many2one('account.account', string="Counter account",
                                      domain="[('company_id', '=', company)]")
    company_id = fields.Many2one('companies.disturubition', string="Companies")
    journal = fields.Many2one('account.journal', string='Journal',
                              domain="[('company_id', '=', company),('type','=','general')]")
    rate = fields.Float('Rate')  # Float because we add 0.1 to avoid zero Frequency issue

    account_type = fields.Char(

        string='Account Type',
    )

    @api.onchange('company')
    def compute_destination_account_domain(self):
        account_type = False
        company = self.company
        if self.company_id.account:
            account_type = self.company_id.account.internal_group
        else:
            return {'domain': {'destination_account': [('company_id', '=', company.name)]}}

        domain = [('company_id', '=', company.name)]
        if account_type in ('expense', 'asset'):
            domain += [('internal_group', 'in', ('expense', 'asset'))]
        elif account_type in ('income', 'liability', 'equity'):
            domain += [('internal_group', 'in', ('income', 'liability', 'equity'))]

        return {'domain': {'destination_account': domain}}

    def cr_move_line_for_other(self, vals, parent):

        x = self.env['account.move'].create({
            'journal_id': vals['journal'],
            'date': parent.or_date,
            'ref': 'Transfer to other companies '
        })

        main_account_line = self.env['account.account'].search([('id', '=', vals['destination_account'])])
        is_credit = False
        if main_account_line.internal_group in ('income', 'liability', 'equity'):
            self.env['account.move.line'].create({
                'account_id': vals['destination_account'],
                'move_id': x.id,
                'credit': parent.account_current_balance * vals['rate'],
            })
            is_credit = True
        elif main_account_line.internal_group in ('asset', 'expense'):
            self.env['account.move.line'].create({
                'account_id': vals['destination_account'],
                'move_id': x.id,
                'debit': parent.account_current_balance * vals['rate'],
            })
            is_credit = False

        if is_credit:
            self.env['account.move.line'].create({
                'account_id': vals['counter_account'],
                'move_id': x.id,
                'debit': parent.account_current_balance * vals['rate'],
            })
        else:
            self.env['account.move.line'].create({
                'account_id': vals['counter_account'],
                'move_id': x.id,
                'credit': parent.account_current_balance * vals['rate'],
            })
        x.action_post()

    @api.model
    def create(self, vals):
        # original_date = False
        #
        # # Get the frequency value from the parent CompanyDis record
        # if 'company_id' in vals:
        #     company_dis = self.env['companies.disturubition'].browse(vals['company_id'])
        #     original_date = company_dis.date
        #     frequency = company_dis.frequency

        # print('orginal date in lines', original_date)

        res = super(CompanyLines, self).create(vals)
        current_date = datetime.now().date()
        parent = res.company_id
        # original_date = parent.vals.get('date', False)
        print("parent is ", parent.account.current_balance)
        # print("date in line   is ",original_date)
        if current_date == parent.or_date :
            res.cr_move_line_for_other(vals, parent)
        return res

    @api.model
    def default_get(self, fields):  # when creat is clicked
        res = super(CompanyLines, self).default_get(fields)
        if 'company_id' in fields and 'active_id' in self.env.context:
            # print("fields", fields)
            res['company_id'] = self.env['companies.disturubition'].browse(self.env.context['active_id'])

        # print("fields", fields)
        return res

    @api.constrains('rate')
    def _check_rate(self):
        for record in self:
            if record.rate > 1.00:
                raise ValidationError("The rate in Companies cannot exceed 100 %.")
            elif record.rate < 0.00:
                raise ValidationError("The rate in Companies cannot be negative .")
            elif record.rate == 0.00:
                raise ValidationError("The rate in Companies must be greater than zero ")
