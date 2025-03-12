from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class FleetDriver(models.Model):
    _name = 'fleet.driver'
    _description = 'Conducteur de flotte'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nom', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employé associé')
    license_number = fields.Char(string='Numéro de permis', required=True, tracking=True)
    license_type = fields.Selection([
        ('a', 'Type A'),
        ('b', 'Type B'),
        ('c', 'Type C'),
        ('d', 'Type D'),
    ], string='Type de permis', required=True)
    license_expiry = fields.Date(string='Date d\'expiration du permis', required=True)
    
    # Informations de contact
    phone = fields.Char(string='Téléphone')
    email = fields.Char(string='Email')
    address = fields.Text(string='Adresse')
    
    # Statut et disponibilité
    state = fields.Selection([
        ('available', 'Disponible'),
        ('driving', 'En conduite'),
        ('off_duty', 'Hors service'),
        ('leave', 'En congé'),
    ], string='Statut', default='available', tracking=True)
    
    # Affectations et planning
    current_vehicle_id = fields.Many2one('fleet.vehicle', string='Véhicule actuel',
                                       compute='_compute_current_vehicle')
    reservation_ids = fields.One2many('fleet.vehicle.reservation', 'driver_id',
                                    string='Réservations de véhicules')
    schedule_ids = fields.One2many('fleet.driver.schedule', 'driver_id',
                                 string='Planning de travail')
    
    # Indicateurs de performance
    total_distance = fields.Float(string='Distance totale parcourue',
                                compute='_compute_total_distance')
    fuel_efficiency_rating = fields.Float(string='Efficacité énergétique',
                                        compute='_compute_efficiency_rating')
    accident_count = fields.Integer(string='Nombre d\'accidents',
                                  compute='_compute_accident_count')
    
    # Documents
    document_ids = fields.One2many('fleet.driver.document', 'driver_id',
                                 string='Documents')
    
    # Analyses
    revenue_generated = fields.Float(string='Revenu total généré',
                                   compute='_compute_revenue')
    performance_score = fields.Float(string='Score de performance',
                                   compute='_compute_performance_score')

    @api.depends('reservation_ids')
    def _compute_current_vehicle(self):
        for driver in self:
            current_reservation = driver.reservation_ids.filtered(
                lambda r: r.state == 'ongoing'
            )
            # S'il y a plusieurs réservations, on peut choisir la première ou ajuster la logique
            driver.current_vehicle_id = current_reservation and current_reservation[0].vehicle_id or False

    @api.depends('reservation_ids')
    def _compute_total_distance(self):
        for driver in self:
            total = 0.0
            # Supposons que chaque réservation a un champ 'distance'
            for reservation in driver.reservation_ids:
                total += getattr(reservation, 'distance', 0.0)
            driver.total_distance = total

    @api.depends('reservation_ids')
    def _compute_efficiency_rating(self):
        for driver in self:
            # Logique à définir : ici on assigne simplement 0.0 par défaut
            driver.fuel_efficiency_rating = 0.0

    @api.depends('performance_score', 'fuel_efficiency_rating')
    def _compute_performance_score(self):
        for driver in self:
            # Logique à définir : ici on assigne simplement 0.0 par défaut
            driver.performance_score = 0.0

    @api.depends('document_ids')
    def _compute_accident_count(self):
        for driver in self:
            # Logique à définir pour compter le nombre d'accidents
            driver.accident_count = 0

    @api.depends('reservation_ids')
    def _compute_revenue(self):
        for driver in self:
            # Logique à définir pour calculer le revenu généré
            driver.revenue_generated = 0.0

    @api.constrains('license_expiry')
    def _check_license_validity(self):
        for driver in self:
            if driver.license_expiry and driver.license_expiry < fields.Date.today():
                raise UserError(_('Le permis de conduire a expiré !'))

    def action_set_available(self):
        self.ensure_one()
        self.state = 'available'

    def action_set_off_duty(self):
        self.ensure_one()
        self.state = 'off_duty'

    def action_view_schedule(self):
        # Action pour voir le planning du conducteur
        pass

    def action_view_performance_report(self):
        # Action pour voir le rapport de performance détaillé
        pass

    def action_send_reminder(self):
        # Action pour envoyer un rappel concernant le renouvellement du permis ou d'autres dates importantes
        pass
