from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class FleetVehicleInspection(models.Model):
    _name = 'fleet.vehicle.inspection'
    _description = 'Vehicle Technical Inspection'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Reference', required=True, copy=False,
                      readonly=True, default=lambda self: _('New'))
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True)
    date = fields.Date(string='Inspection Date', required=True, default=fields.Date.context_today)
    
    # Inspection Details
    inspection_type = fields.Selection([
        ('periodic', 'Periodic Technical Inspection'),
        ('pre_purchase', 'Pre-Purchase Inspection'),
        ('damage', 'Damage Assessment'),
        ('warranty', 'Warranty Inspection'),
        ('other', 'Other')
    ], string='Inspection Type', required=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    # Inspector Information
    inspector_id = fields.Many2one('res.partner', string='Inspector/Company')
    inspector_name = fields.Char(string='Inspector Name')
    location = fields.Char(string='Inspection Location')
    
    # Vehicle Information at Time of Inspection
    odometer = fields.Float(string='Odometer Reading')
    next_inspection_date = fields.Date(string='Next Inspection Due')
    next_inspection_odometer = fields.Float(string='Next Inspection Odometer')
    
    # Inspection Areas
    brake_system = fields.Selection([
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('na', 'N/A')
    ], string='Brake System')
    
    suspension = fields.Selection([
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('na', 'N/A')
    ], string='Suspension')
    
    steering = fields.Selection([
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('na', 'N/A')
    ], string='Steering')
    
    engine = fields.Selection([
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('na', 'N/A')
    ], string='Engine')
    
    transmission = fields.Selection([
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('na', 'N/A')
    ], string='Transmission')
    
    exhaust = fields.Selection([
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('na', 'N/A')
    ], string='Exhaust System')
    
    # Results and Documentation
    passed_all = fields.Boolean(string='Passed All Checks', compute='_compute_passed_all')
    notes = fields.Text(string='Notes')
    recommendations = fields.Text(string='Recommendations')
    attachment_ids = fields.Many2many('ir.attachment', string='Documents')
    
    # Costs
    cost = fields.Float(string='Inspection Cost')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                 default=lambda self: self.env.company.currency_id)
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.inspection') or _('New')
        return super(FleetVehicleInspection, self).create(vals)

    @api.depends('brake_system', 'suspension', 'steering', 'engine', 'transmission', 'exhaust')
    def _compute_passed_all(self):
        for record in self:
            checks = [record.brake_system, record.suspension, record.steering,
                     record.engine, record.transmission, record.exhaust]
            record.passed_all = all(check in ['good', 'fair', 'na'] for check in checks if check)

    def action_start_inspection(self):
        self.state = 'in_progress'

    def action_mark_passed(self):
        if not self.passed_all:
            raise UserError(_('Cannot mark as passed. Some checks have failed.'))
        self.state = 'passed'

    def action_mark_failed(self):
        self.state = 'failed'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_create_expense(self):
        """Create expense record for inspection cost"""
        self.ensure_one()
        if not self.cost:
            raise UserError(_('Please set the inspection cost first.'))
            
        expense_vals = {
            'vehicle_id': self.vehicle_id.id,
            'date': self.date,
            'amount': self.cost,
            'expense_type': 'inspection',
            'description': f'Technical Inspection: {self.name}',
            'vendor_id': self.inspector_id.id,
        }
        expense = self.env['fleet.expense'].create(expense_vals)
        return {
            'name': _('Expense'),
            'view_mode': 'form',
            'res_model': 'fleet.expense',
            'res_id': expense.id,
            'type': 'ir.actions.act_window',
        }

    def action_schedule_maintenance(self):
        """Schedule maintenance based on inspection results"""
        self.ensure_one()
        return {
            'name': _('Schedule Maintenance'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle.maintenance',
            'view_mode': 'form',
            'context': {
                'default_vehicle_id': self.vehicle_id.id,
                'default_maintenance_type': 'corrective',
                'default_notes': self.notes,
            },
        }
