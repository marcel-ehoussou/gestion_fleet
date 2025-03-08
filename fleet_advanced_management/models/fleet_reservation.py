from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class FleetReservation(models.Model):
    _name = 'fleet.vehicle.reservation'
    _description = 'Vehicle Reservation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc'

    name = fields.Char(string='Reference', required=True, copy=False,
                      readonly=True, default=lambda self: _('New'))
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True)
    driver_id = fields.Many2one('fleet.driver', string='Driver', required=True)
    
    # Reservation Period
    start_date = fields.Datetime(string='Start Date', required=True)
    end_date = fields.Datetime(string='End Date', required=True)
    duration = fields.Float(string='Duration (Hours)', compute='_compute_duration')
    
    # Purpose and Route
    purpose = fields.Selection([
        ('business', 'Business Trip'),
        ('delivery', 'Delivery'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    ], string='Purpose', required=True)
    description = fields.Text(string='Description')
    start_location = fields.Char(string='Start Location')
    end_location = fields.Char(string='End Location')
    estimated_distance = fields.Float(string='Estimated Distance (km)')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    # Odometer Readings
    initial_odometer = fields.Float(string='Initial Odometer')
    final_odometer = fields.Float(string='Final Odometer')
    actual_distance = fields.Float(string='Actual Distance', 
                                 compute='_compute_actual_distance')
    
    # Costs and Revenue
    estimated_fuel_cost = fields.Float(string='Estimated Fuel Cost',
                                     compute='_compute_estimated_costs')
    actual_fuel_cost = fields.Float(string='Actual Fuel Cost')
    additional_costs = fields.Float(string='Additional Costs')
    total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost')
    revenue = fields.Float(string='Revenue')
    profit = fields.Float(string='Profit', compute='_compute_profit')
    
    # Related Documents
    document_ids = fields.Many2many('fleet.vehicle.document', 
                                  string='Related Documents')
    note = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.reservation') or _('New')
        return super(FleetReservation, self).create(vals)

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for record in self:
            if record.start_date and record.end_date:
                duration = fields.Datetime.from_string(record.end_date) - \
                          fields.Datetime.from_string(record.start_date)
                record.duration = duration.total_seconds() / 3600
            else:
                record.duration = 0.0

    @api.depends('initial_odometer', 'final_odometer')
    def _compute_actual_distance(self):
        for record in self:
            if record.final_odometer and record.initial_odometer:
                record.actual_distance = record.final_odometer - record.initial_odometer
            else:
                record.actual_distance = 0.0

    @api.depends('estimated_distance', 'vehicle_id')
    def _compute_estimated_costs(self):
        for record in self:
            if record.vehicle_id and record.estimated_distance:
                # Calculate estimated fuel cost based on vehicle's fuel efficiency
                fuel_efficiency = record.vehicle_id.fuel_efficiency or 10  # L/100km
                avg_fuel_price = 1.5  # Average fuel price per liter
                estimated_fuel = (record.estimated_distance / 100) * fuel_efficiency
                record.estimated_fuel_cost = estimated_fuel * avg_fuel_price
            else:
                record.estimated_fuel_cost = 0.0

    @api.depends('actual_fuel_cost', 'additional_costs')
    def _compute_total_cost(self):
        for record in self:
            record.total_cost = record.actual_fuel_cost + record.additional_costs

    @api.depends('revenue', 'total_cost')
    def _compute_profit(self):
        for record in self:
            record.profit = record.revenue - record.total_cost

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date > record.end_date:
                    raise ValidationError(_('End date cannot be before start date'))
                # Check for overlapping reservations
                domain = [
                    ('vehicle_id', '=', record.vehicle_id.id),
                    ('id', '!=', record.id),
                    ('state', 'not in', ['cancelled', 'completed']),
                    '|',
                    '&', ('start_date', '<=', record.start_date),
                         ('end_date', '>=', record.start_date),
                    '&', ('start_date', '<=', record.end_date),
                         ('end_date', '>=', record.end_date),
                ]
                if self.search_count(domain):
                    raise ValidationError(_('Vehicle is already reserved for this period'))

    def action_confirm(self):
        self.state = 'confirmed'

    def action_start(self):
        self.ensure_one()
        if not self.initial_odometer:
            raise ValidationError(_('Please set initial odometer reading'))
        self.state = 'ongoing'

    def action_complete(self):
        self.ensure_one()
        if not self.final_odometer:
            raise ValidationError(_('Please set final odometer reading'))
        self.state = 'completed'
        self._create_expense_records()

    def action_cancel(self):
        self.state = 'cancelled'

    def _create_expense_records(self):
        # Create expense records for fuel and additional costs
        if self.actual_fuel_cost > 0:
            self.env['fleet.expense'].create({
                'vehicle_id': self.vehicle_id.id,
                'driver_id': self.driver_id.id,
                'date': fields.Date.today(),
                'expense_type': 'fuel',
                'amount': self.actual_fuel_cost,
                'description': f'Fuel cost for reservation {self.name}',
            })
        if self.additional_costs > 0:
            self.env['fleet.expense'].create({
                'vehicle_id': self.vehicle_id.id,
                'driver_id': self.driver_id.id,
                'date': fields.Date.today(),
                'expense_type': 'other',
                'amount': self.additional_costs,
                'description': f'Additional costs for reservation {self.name}',
            })

    def action_print_trip_sheet(self):
        # Generate trip sheet report
        pass

    def action_send_confirmation(self):
        # Send confirmation email to driver
        pass
