from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class FleetVehicleInsurance(models.Model):
    _name = 'fleet.vehicle.insurance'
    _description = 'Vehicle Insurance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc'

    name = fields.Char(string='Policy Number', required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True)
    
    # Insurance Details
    insurance_type = fields.Selection([
        ('liability', 'Liability'),
        ('comprehensive', 'Comprehensive'),
        ('third_party', 'Third Party'),
        ('other', 'Other')
    ], string='Insurance Type', required=True)
    
    insurer_id = fields.Many2one('res.partner', string='Insurance Company', required=True)
    agent_id = fields.Many2one('res.partner', string='Insurance Agent')
    
    # Coverage Period
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string='Status', compute='_compute_state', store=True)
    
    # Financial Information
    premium_amount = fields.Float(string='Premium Amount')
    deductible = fields.Float(string='Deductible Amount')
    coverage_amount = fields.Float(string='Coverage Amount')
    payment_frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual'),
        ('annual', 'Annual')
    ], string='Payment Frequency')
    
    # Coverage Details
    coverage_details = fields.Text(string='Coverage Details')
    exclusions = fields.Text(string='Exclusions')
    notes = fields.Text(string='Notes')
    
    # Documents
    attachment_ids = fields.Many2many('ir.attachment', string='Documents')
    
    @api.depends('start_date', 'end_date')
    def _compute_state(self):
        today = fields.Date.today()
        for record in self:
            if not record.start_date or not record.end_date:
                record.state = 'draft'
            elif record.end_date < today:
                record.state = 'expired'
            elif record.start_date <= today <= record.end_date:
                record.state = 'active'
            else:
                record.state = 'draft'

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date > record.end_date:
                    raise UserError(_('End date must be after start date'))

    def action_renew_policy(self):
        """Create a new insurance record based on current one"""
        self.ensure_one()
        return {
            'name': _('Renew Insurance Policy'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle.insurance',
            'view_mode': 'form',
            'context': {
                'default_vehicle_id': self.vehicle_id.id,
                'default_insurance_type': self.insurance_type,
                'default_insurer_id': self.insurer_id.id,
                'default_agent_id': self.agent_id.id,
                'default_premium_amount': self.premium_amount,
                'default_deductible': self.deductible,
                'default_coverage_amount': self.coverage_amount,
                'default_payment_frequency': self.payment_frequency,
                'default_coverage_details': self.coverage_details,
                'default_exclusions': self.exclusions,
            }
        }

    def action_send_expiry_reminder(self):
        """Send expiry reminder to responsible person"""
        # Template logic here
        pass

    def action_create_expense(self):
        """Create expense record for insurance premium"""
        self.ensure_one()
        expense_vals = {
            'vehicle_id': self.vehicle_id.id,
            'date': fields.Date.today(),
            'amount': self.premium_amount,
            'expense_type': 'insurance',
            'description': f'Insurance Premium: {self.name}',
            'vendor_id': self.insurer_id.id,
        }
        expense = self.env['fleet.expense'].create(expense_vals)
        return {
            'name': _('Expense'),
            'view_mode': 'form',
            'res_model': 'fleet.expense',
            'res_id': expense.id,
            'type': 'ir.actions.act_window',
        }
