from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class FleetDriver(models.Model):
    _name = 'fleet.driver'
    _description = 'Fleet Driver'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Related Employee')
    license_number = fields.Char(string='License Number', required=True, tracking=True)
    license_type = fields.Selection([
        ('a', 'Type A'),
        ('b', 'Type B'),
        ('c', 'Type C'),
        ('d', 'Type D'),
    ], string='License Type', required=True)
    license_expiry = fields.Date(string='License Expiry Date', required=True)
    
    # Contact Information
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    address = fields.Text(string='Address')
    
    # Status and Availability
    state = fields.Selection([
        ('available', 'Available'),
        ('driving', 'On Drive'),
        ('off_duty', 'Off Duty'),
        ('leave', 'On Leave'),
    ], string='Status', default='available', tracking=True)
    
    # Assignments and Schedule
    current_vehicle_id = fields.Many2one('fleet.vehicle', string='Current Vehicle',
                                       compute='_compute_current_vehicle')
    reservation_ids = fields.One2many('fleet.vehicle.reservation', 'driver_id',
                                    string='Vehicle Reservations')
    schedule_ids = fields.One2many('fleet.driver.schedule', 'driver_id',
                                 string='Work Schedule')
    
    # Performance Metrics
    total_distance = fields.Float(string='Total Distance Driven',
                                compute='_compute_total_distance')
    fuel_efficiency_rating = fields.Float(string='Fuel Efficiency Rating',
                                        compute='_compute_efficiency_rating')
    accident_count = fields.Integer(string='Number of Accidents',
                                  compute='_compute_accident_count')
    
    # Documents
    document_ids = fields.One2many('fleet.driver.document', 'driver_id',
                                 string='Documents')
    
    # Analytics
    revenue_generated = fields.Float(string='Total Revenue Generated',
                                   compute='_compute_revenue')
    performance_score = fields.Float(string='Performance Score',
                                   compute='_compute_performance_score')

    @api.depends('reservation_ids')
    def _compute_current_vehicle(self):
        for driver in self:
            current_reservation = driver.reservation_ids.filtered(
                lambda r: r.state == 'ongoing'
            )
            driver.current_vehicle_id = current_reservation.vehicle_id if current_reservation else False

    @api.depends('reservation_ids')
    def _compute_total_distance(self):
        for driver in self:
            # Calculate total distance driven from reservations and odometer logs
            pass

    @api.depends('reservation_ids')
    def _compute_efficiency_rating(self):
        for driver in self:
            # Calculate efficiency based on fuel consumption and driving patterns
            pass

    @api.depends('performance_score', 'fuel_efficiency_rating')
    def _compute_performance_score(self):
        for driver in self:
            # Calculate overall performance score
            pass

    @api.constrains('license_expiry')
    def _check_license_validity(self):
        for driver in self:
            if driver.license_expiry and driver.license_expiry < fields.Date.today():
                raise UserError(_('Driver license has expired!'))

    def action_set_available(self):
        self.ensure_one()
        self.state = 'available'

    def action_set_off_duty(self):
        self.ensure_one()
        self.state = 'off_duty'

    def action_view_schedule(self):
        # Action to view driver's schedule
        pass

    def action_view_performance_report(self):
        # Action to view detailed performance report
        pass

    def action_send_reminder(self):
        # Action to send reminder about license renewal or other important dates
        pass
