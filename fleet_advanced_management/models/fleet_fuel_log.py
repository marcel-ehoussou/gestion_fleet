from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class FleetVehicleFuelLog(models.Model):
    _name = 'fleet.vehicle.fuel.log'
    _description = 'Vehicle Fuel Log'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Reference', required=True, copy=False,
                      readonly=True, default=lambda self: _('New'))
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    
    # Fuel Details
    fuel_type = fields.Selection([
        ('diesel', 'Diesel'),
        ('gasoline', 'Gasoline'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('lpg', 'LPG'),
        ('cng', 'CNG'),
        ('other', 'Other'),
    ], string='Fuel Type', required=True)
    
    liters = fields.Float(string='Liters')
    price_per_liter = fields.Float(string='Price per Liter')
    total_amount = fields.Float(string='Total Amount', compute='_compute_amount', store=True)
    
    # Odometer
    odometer = fields.Float(string='Odometer Reading', required=True)
    previous_odometer = fields.Float(string='Previous Odometer', compute='_compute_previous_odometer')
    distance = fields.Float(string='Distance', compute='_compute_distance', store=True)
    
    # Location and Vendor
    location = fields.Char(string='Fill-up Location')
    vendor_id = fields.Many2one('res.partner', string='Vendor/Station')
    invoice_reference = fields.Char(string='Invoice Reference')
    
    # Additional Info
    notes = fields.Text(string='Notes')
    full_tank = fields.Boolean(string='Full Tank')
    consumption = fields.Float(string='Consumption (L/100km)', compute='_compute_consumption')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.fuel.log') or _('New')
        return super(FleetVehicleFuelLog, self).create(vals)

    @api.depends('liters', 'price_per_liter')
    def _compute_amount(self):
        for record in self:
            record.total_amount = record.liters * record.price_per_liter

    @api.depends('vehicle_id', 'date')
    def _compute_previous_odometer(self):
        for record in self:
            previous_log = self.env['fleet.vehicle.fuel.log'].search([
                ('vehicle_id', '=', record.vehicle_id.id),
                ('date', '<', record.date),
                ('odometer', '!=', 0)
            ], order='date desc, odometer desc', limit=1)
            record.previous_odometer = previous_log.odometer if previous_log else 0.0

    @api.depends('odometer', 'previous_odometer')
    def _compute_distance(self):
        for record in self:
            record.distance = record.odometer - record.previous_odometer if record.previous_odometer > 0 else 0.0

    @api.depends('liters', 'distance')
    def _compute_consumption(self):
        for record in self:
            record.consumption = (record.liters * 100 / record.distance) if record.distance > 0 else 0.0

    def action_create_expense(self):
        """Create an expense record from fuel log"""
        self.ensure_one()
        expense_vals = {
            'vehicle_id': self.vehicle_id.id,
            'date': self.date,
            'amount': self.total_amount,
            'expense_type': 'fuel',
            'description': f'Fuel: {self.name}',
            'vendor_id': self.vendor_id.id,
        }
        expense = self.env['fleet.expense'].create(expense_vals)
        return {
            'name': _('Expense'),
            'view_mode': 'form',
            'res_model': 'fleet.expense',
            'res_id': expense.id,
            'type': 'ir.actions.act_window',
        }
