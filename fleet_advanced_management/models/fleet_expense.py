from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class FleetExpense(models.Model):
    _name = 'fleet.expense'
    _description = 'Fleet Expense'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Reference', required=True, copy=False, 
                      readonly=True, default=lambda self: _('New'))
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True)
    driver_id = fields.Many2one('fleet.driver', string='Driver')
    expense_type = fields.Selection([
        ('fuel', 'Fuel'),
        ('repair', 'Repair'),
        ('maintenance', 'Maintenance'),
        ('insurance', 'Insurance'),
        ('tax', 'Tax'),
        ('other', 'Other'),
    ], string='Type', required=True)
    
    amount = fields.Float(string='Amount', required=True)
    description = fields.Text(string='Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    # Fuel specific fields
    liters = fields.Float(string='Liters')
    price_per_liter = fields.Float(string='Price per Liter')
    odometer = fields.Float(string='Odometer Reading')
    fuel_type = fields.Selection([
        ('diesel', 'Diesel'),
        ('gasoline', 'Gasoline'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
    ], string='Fuel Type')
    
    # Repair/Maintenance specific fields
    service_type_id = fields.Many2one('fleet.service.type', string='Service Type')
    vendor_id = fields.Many2one('res.partner', string='Vendor/Supplier')
    invoice_ref = fields.Char(string='Invoice Reference')
    next_service_date = fields.Date(string='Next Service Date')
    
    # Insurance/Tax specific fields
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    policy_number = fields.Char(string='Policy/Document Number')
    
    # Accounting fields
    analytic_account_id = fields.Many2one('account.analytic.account', 
                                         string='Analytic Account')
    company_id = fields.Many2one('res.company', string='Company', 
                                default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                 related='company_id.currency_id')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.expense') or _('New')
        return super(FleetExpense, self).create(vals)
    
    @api.onchange('expense_type')
    def _onchange_expense_type(self):
        # Reset specific fields when expense type changes
        if self.expense_type != 'fuel':
            self.liters = 0.0
            self.price_per_liter = 0.0
            self.fuel_type = False
        
    @api.onchange('liters', 'price_per_liter')
    def _onchange_fuel_calculation(self):
        if self.expense_type == 'fuel':
            self.amount = self.liters * self.price_per_liter
            
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.start_date > record.end_date:
                raise ValidationError(_('End date cannot be before start date.'))
                
    def action_submit(self):
        self.state = 'submitted'
        
    def action_approve(self):
        self.state = 'approved'
        
    def action_pay(self):
        self.state = 'paid'
        
    def action_cancel(self):
        self.state = 'cancelled'
        
    def action_draft(self):
        self.state = 'draft'
        
    def action_create_vendor_bill(self):
        # Logic to create vendor bill in accounting
        pass
        
    def action_view_analytics(self):
        # Logic to view expense analytics
        pass
