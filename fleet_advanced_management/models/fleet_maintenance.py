from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class FleetMaintenance(models.Model):
    _name = 'fleet.vehicle.maintenance'
    _description = 'Vehicle Maintenance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Reference', required=True, copy=False,
                      readonly=True, default=lambda self: _('New'))
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True)
    date = fields.Date(string='Maintenance Date', required=True, default=fields.Date.context_today)
    
    maintenance_type = fields.Selection([
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
        ('predictive', 'Predictive'),
        ('diagnostic', 'Diagnostic'),
    ], string='Maintenance Type', required=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('done', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    # Service Details
    service_items = fields.One2many('fleet.maintenance.service.item', 
                                   'maintenance_id', string='Service Items')
    total_parts_cost = fields.Float(string='Parts Cost', compute='_compute_costs')
    labor_cost = fields.Float(string='Labor Cost')
    total_cost = fields.Float(string='Total Cost', compute='_compute_costs')
    
    # Service Provider
    vendor_id = fields.Many2one('res.partner', string='Service Provider')
    technician = fields.Char(string='Technician Name')
    workshop_address = fields.Text(string='Workshop Address')
    
    # Scheduling
    scheduled_date = fields.Datetime(string='Scheduled Date')
    completion_date = fields.Datetime(string='Completion Date')
    duration = fields.Float(string='Duration (Hours)')
    
    # Vehicle Status
    odometer = fields.Float(string='Odometer Reading')
    next_service_odometer = fields.Float(string='Next Service at Odometer')
    next_service_date = fields.Date(string='Next Service Date')
    
    # Documentation
    diagnosis = fields.Text(string='Diagnosis/Findings')
    operations_performed = fields.Text(string='Operations Performed')
    recommendations = fields.Text(string='Recommendations')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    # Related Info
    expense_id = fields.Many2one('fleet.expense', string='Related Expense')
    warranty_claim = fields.Boolean(string='Warranty Claim')
    warranty_details = fields.Text(string='Warranty Details')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.maintenance') or _('New')
        return super(FleetMaintenance, self).create(vals)

    @api.depends('service_items.cost', 'labor_cost')
    def _compute_costs(self):
        for record in self:
            record.total_parts_cost = sum(record.service_items.mapped('cost'))
            record.total_cost = record.total_parts_cost + record.labor_cost

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        if self.vehicle_id:
            self.odometer = self.vehicle_id.odometer

    def action_schedule(self):
        if not self.scheduled_date:
            raise UserError(_('Please set a scheduled date first.'))
        self.state = 'scheduled'

    def action_start(self):
        self.state = 'in_progress'

    def action_complete(self):
        self.state = 'done'
        self.completion_date = fields.Datetime.now()
        self._create_expense_record()

    def action_cancel(self):
        self.state = 'cancelled'

    def _create_expense_record(self):
        # Create related expense record
        if not self.expense_id and self.total_cost > 0:
            expense_vals = {
                'vehicle_id': self.vehicle_id.id,
                'date': fields.Date.today(),
                'amount': self.total_cost,
                'expense_type': 'maintenance',
                'description': f'Maintenance: {self.name}',
                'vendor_id': self.vendor_id.id,
            }
            self.expense_id = self.env['fleet.expense'].create(expense_vals)

    def action_print_report(self):
        # Generate maintenance report
        pass

    def action_send_reminder(self):
        # Send reminder to responsible person
        pass

class FleetMaintenanceServiceItem(models.Model):
    _name = 'fleet.maintenance.service.item'
    _description = 'Maintenance Service Item'

    maintenance_id = fields.Many2one('fleet.vehicle.maintenance', 
                                    string='Maintenance Record')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle',
                                related='maintenance_id.vehicle_id',
                                store=True)
    name = fields.Char(string='Service Item', required=True)
    product_id = fields.Many2one('product.product', string='Part')
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_cost = fields.Float(string='Unit Cost')
    cost = fields.Float(string='Total Cost', compute='_compute_cost')
    state = fields.Selection([
        ('planned', 'Planned'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='planned')

    @api.depends('quantity', 'unit_cost')
    def _compute_cost(self):
        for record in self:
            record.cost = record.quantity * record.unit_cost
