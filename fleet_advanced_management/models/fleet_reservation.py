from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class FleetReservation(models.Model):
    _name = 'fleet.vehicle.reservation'
    _description = 'Réservation de véhicule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc'

    name = fields.Char(string='Référence', required=True, copy=False,
                      readonly=True, default=lambda self: _('Nouveau'))
    vehicle_id = fields.Many2one('fleet.vehicle', string='Véhicule', required=True)
    driver_id = fields.Many2one('fleet.driver', string='Conducteur', required=True)
    
    # Période de réservation
    start_date = fields.Datetime(string='Date de début', required=True)
    end_date = fields.Datetime(string='Date de fin', required=True)
    duration = fields.Float(string='Durée (heures)', compute='_compute_duration')
    
    # Objet et itinéraire
    purpose = fields.Selection([
        ('business', 'Voyage d\'affaires'),
        ('delivery', 'Livraison'),
        ('maintenance', 'Maintenance'),
        ('other', 'Autre'),
    ], string='Objet', required=True)
    description = fields.Text(string='Description')
    start_location = fields.Char(string='Lieu de départ')
    end_location = fields.Char(string='Lieu d\'arrivée')
    estimated_distance = fields.Float(string='Distance estimée (km)')
    
    # Statut
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('ongoing', 'En cours'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string='Statut', default='draft', tracking=True)
    
    # Lectures du compteur kilométrique
    initial_odometer = fields.Float(string='Compteur kilométrique initial')
    final_odometer = fields.Float(string='Compteur kilométrique final')
    actual_distance = fields.Float(string='Distance réelle', 
                                 compute='_compute_actual_distance')
    
    # Coûts et revenus
    estimated_fuel_cost = fields.Float(string='Coût estimé du carburant',
                                     compute='_compute_estimated_costs')
    actual_fuel_cost = fields.Float(string='Coût réel du carburant')
    additional_costs = fields.Float(string='Coûts supplémentaires')
    total_cost = fields.Float(string='Coût total', compute='_compute_total_cost')
    revenue = fields.Float(string='Revenu')
    profit = fields.Float(string='Profit', compute='_compute_profit')
    
    # Documents associés
    document_ids = fields.Many2many('fleet.vehicle.document', 
                                  string='Documents associés')
    note = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.reservation') or _('Nouveau')
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
                # Calculer le coût estimé du carburant en fonction de l'efficacité énergétique du véhicule
                fuel_efficiency = record.vehicle_id.fuel_efficiency or 10  # L/100km
                avg_fuel_price = 1.5  # Prix moyen du carburant par litre
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
                    raise ValidationError(_('La date de fin ne peut pas être antérieure à la date de début'))
                # Vérifier les réservations qui se chevauchent
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
                    raise ValidationError(_('Le véhicule est déjà réservé pour cette période'))

    def action_confirm(self):
        self.state = 'confirmed'

    def action_start(self):
        self.ensure_one()
        if not self.initial_odometer:
            raise ValidationError(_('Veuillez définir la lecture initiale du compteur kilométrique'))
        self.state = 'ongoing'

    def action_complete(self):
        self.ensure_one()
        if not self.final_odometer:
            raise ValidationError(_('Veuillez définir la lecture finale du compteur kilométrique'))
        self.state = 'completed'
        self._create_expense_records()

    def action_cancel(self):
        self.state = 'cancelled'

    def _create_expense_records(self):
        # Créer des enregistrements de dépenses pour le carburant et les coûts supplémentaires
        if self.actual_fuel_cost > 0:
            self.env['fleet.expense'].create({
                'vehicle_id': self.vehicle_id.id,
                'driver_id': self.driver_id.id,
                'date': fields.Date.today(),
                'expense_type': 'fuel',
                'amount': self.actual_fuel_cost,
                'description': f'Coût du carburant pour la réservation {self.name}',
            })
        if self.additional_costs > 0:
            self.env['fleet.expense'].create({
                'vehicle_id': self.vehicle_id.id,
                'driver_id': self.driver_id.id,
                'date': fields.Date.today(),
                'expense_type': 'other',
                'amount': self.additional_costs,
                'description': f'Coûts supplémentaires pour la réservation {self.name}',
            })

    def action_print_trip_sheet(self):
        # Générer le rapport de feuille de route
        pass

    def action_send_confirmation(self):
        # Envoyer un email de confirmation au conducteur
        pass
