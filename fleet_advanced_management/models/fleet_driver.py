from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class FleetDriver(models.Model):
    _name = 'fleet.driver'
    _description = 'Fleet Driver'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Related Employee')
    
    # Image
    image_1920 = fields.Image(string='Image')
    image_128 = fields.Image(string='Image 128', related='image_1920', max_width=128, max_height=128, store=True)
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
    schedule_count = fields.Integer(string='Schedule Count',
                                  compute='_compute_schedule_count')
    
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

    @api.depends('total_distance', 'fuel_efficiency_rating', 'accident_count', 'revenue_generated')
    def _compute_performance_score(self):
        for driver in self:
            # Base score starts at 100
            score = 100.0
            
            # Reduce score based on accidents (each accident reduces 10 points)
            score -= driver.accident_count * 10
            
            # Add points for fuel efficiency (0-20 points)
            if driver.fuel_efficiency_rating:
                score += min(driver.fuel_efficiency_rating * 2, 20)
            
            # Add points for experience/distance driven (0-20 points)
            if driver.total_distance:
                score += min(driver.total_distance / 1000, 20)  # 1 point per 1000 km, max 20 points
            
            # Add points for revenue generation (0-20 points)
            if driver.revenue_generated:
                score += min(driver.revenue_generated / 1000, 20)  # 1 point per 1000 currency units, max 20 points
            
            # Ensure score stays between 0 and 100
            driver.performance_score = max(min(score, 100), 0)

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

    @api.depends('schedule_ids')
    def _compute_schedule_count(self):
        for driver in self:
            driver.schedule_count = len(driver.schedule_ids)

    def action_view_schedule(self):
        self.ensure_one()
        return {
            'name': _('Work Schedule'),
            'res_model': 'fleet.driver.schedule',
            'view_mode': 'tree,form',
            'domain': [('driver_id', '=', self.id)],
            'context': {'default_driver_id': self.id},
            'type': 'ir.actions.act_window',
        }

    def action_view_performance_report(self):
        self.ensure_one()
        return {
            'name': _('Performance Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.driver.performance.report',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_driver_id': self.id,
                'default_performance_score': self.performance_score,
                'default_total_distance': self.total_distance,
                'default_fuel_efficiency': self.fuel_efficiency_rating,
                'default_accident_count': self.accident_count,
                'default_revenue': self.revenue_generated,
            }
        }

    def action_send_reminder(self):
        # Action to send reminder about license renewal or other important dates
        pass
