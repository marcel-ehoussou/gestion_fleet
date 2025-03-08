from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class FleetVehicleOdometerLog(models.Model):
    _name = 'fleet.vehicle.odometer.log'
    _description = 'Vehicle Odometer Log'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Reference', required=True, copy=False,
                      readonly=True, default=lambda self: _('New'))
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    
    # Odometer Information
    value = fields.Float(string='Odometer Value', required=True)
    unit = fields.Selection([
        ('kilometers', 'Kilometers'),
        ('miles', 'Miles')
    ], string='Unit', required=True, default='kilometers')
    previous_odometer = fields.Float(string='Previous Odometer', compute='_compute_previous_odometer')
    distance = fields.Float(string='Distance', compute='_compute_distance', store=True)
    
    # Additional Information
    driver_id = fields.Many2one('fleet.driver', string='Driver')
    reason = fields.Selection([
        ('start_day', 'Start of Day'),
        ('end_day', 'End of Day'),
        ('trip', 'Trip'),
        ('maintenance', 'Maintenance'),
        ('fuel', 'Fuel Fill'),
        ('other', 'Other')
    ], string='Reason')
    
    location = fields.Char(string='Location')
    notes = fields.Text(string='Notes')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.odometer.log') or _('New')
        return super(FleetVehicleOdometerLog, self).create(vals)

    @api.depends('vehicle_id', 'date')
    def _compute_previous_odometer(self):
        for record in self:
            previous_log = self.env['fleet.vehicle.odometer.log'].search([
                ('vehicle_id', '=', record.vehicle_id.id),
                ('date', '<', record.date),
                ('value', '!=', 0)
            ], order='date desc, value desc', limit=1)
            record.previous_odometer = previous_log.value if previous_log else 0.0

    @api.depends('value', 'previous_odometer')
    def _compute_distance(self):
        for record in self:
            record.distance = record.value - record.previous_odometer if record.previous_odometer > 0 else 0.0

    @api.constrains('value', 'previous_odometer')
    def _check_odometer_value(self):
        for record in self:
            if record.previous_odometer > record.value:
                raise UserError(_('The odometer value cannot be less than the previous odometer reading.'))

    def action_create_trip_record(self):
        """Create a trip record based on odometer log"""
        self.ensure_one()
        return {
            'name': _('Create Trip Record'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle.trip',
            'view_mode': 'form',
            'context': {
                'default_vehicle_id': self.vehicle_id.id,
                'default_driver_id': self.driver_id.id,
                'default_start_odometer': self.previous_odometer,
                'default_end_odometer': self.value,
                'default_date': self.date,
            },
        }

    def action_update_vehicle_odometer(self):
        """Update vehicle's current odometer reading"""
        self.ensure_one()
        self.vehicle_id.write({
            'odometer': self.value,
            'odometer_unit': self.unit,
        })
