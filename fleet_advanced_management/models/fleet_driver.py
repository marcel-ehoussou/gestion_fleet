from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import base64

class FleetDriver(models.Model):
    _name = 'fleet.driver'
    _description = 'Fleet Driver'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Related Employee')
    
    # Image fields
    image_1920 = fields.Binary(string='Image', attachment=True)
    image_128 = fields.Binary("Image 128", compute='_compute_image_128', store=True)
    
    @api.model
    def _get_image_128(self, image_1920):
        """Resize the image to 128x128px"""
        return tools.image_process(image_1920, size=(128, 128))
    
    @api.depends('image_1920')
    def _compute_image_128(self):
        for record in self:
            record.image_128 = self._get_image_128(record.image_1920) if record.image_1920 else False
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

    @api.depends('reservation_ids.state', 'reservation_ids.end_odometer', 'reservation_ids.start_odometer')
    def _compute_total_distance(self):
        for driver in self:
            total = 0.0
            # Calculer la distance totale à partir des réservations terminées
            completed_reservations = driver.reservation_ids.filtered(lambda r: r.state == 'done')
            for reservation in completed_reservations:
                if reservation.end_odometer and reservation.start_odometer:
                    total += (reservation.end_odometer - reservation.start_odometer)
            driver.total_distance = total

    @api.depends('reservation_ids.state', 'reservation_ids.fuel_consumption', 'reservation_ids.distance_driven')
    def _compute_efficiency_rating(self):
        for driver in self:
            total_consumption = 0.0
            total_distance = 0.0
            completed_reservations = driver.reservation_ids.filtered(lambda r: r.state == 'done')
            
            for reservation in completed_reservations:
                if reservation.fuel_consumption and reservation.distance_driven:
                    total_consumption += reservation.fuel_consumption
                    total_distance += reservation.distance_driven
            
            # Calculer l'efficacité en km/L
            driver.fuel_efficiency_rating = (total_distance / total_consumption) if total_consumption else 0.0
            
    @api.depends('reservation_ids.state', 'reservation_ids.accident_count')
    def _compute_accident_count(self):
        for driver in self:
            total_accidents = 0
            completed_reservations = driver.reservation_ids.filtered(lambda r: r.state == 'done')
            for reservation in completed_reservations:
                if reservation.accident_count:
                    total_accidents += reservation.accident_count
            driver.accident_count = total_accidents
            
    @api.depends('reservation_ids.state', 'reservation_ids.total_cost')
    def _compute_revenue(self):
        for driver in self:
            total_revenue = 0.0
            completed_reservations = driver.reservation_ids.filtered(lambda r: r.state == 'done')
            for reservation in completed_reservations:
                if reservation.total_cost:
                    total_revenue += reservation.total_cost
            driver.revenue_generated = total_revenue

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
