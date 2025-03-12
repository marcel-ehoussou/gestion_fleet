from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class FleetVehicleOdometerLog(models.Model):
    _name = 'fleet.vehicle.odometer.log'
    _description = 'Journal du compteur kilométrique du véhicule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Référence', required=True, copy=False,
                      readonly=True, default=lambda self: _('Nouveau'))
    vehicle_id = fields.Many2one('fleet.vehicle', string='Véhicule', required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    
    # Informations du compteur kilométrique
    value = fields.Float(string='Valeur du compteur kilométrique', required=True)
    unit = fields.Selection([
        ('kilometers', 'Kilomètres'),
        ('miles', 'Miles')
    ], string='Unité', required=True, default='kilometers')
    previous_odometer = fields.Float(string='Compteur kilométrique précédent', compute='_compute_previous_odometer')
    distance = fields.Float(string='Distance', compute='_compute_distance', store=True)
    
    # Informations supplémentaires
    driver_id = fields.Many2one('fleet.driver', string='Conducteur')
    reason = fields.Selection([
        ('start_day', 'Début de journée'),
        ('end_day', 'Fin de journée'),
        ('trip', 'Voyage'),
        ('maintenance', 'Maintenance'),
        ('fuel', 'Remplissage de carburant'),
        ('other', 'Autre')
    ], string='Raison')
    
    location = fields.Char(string='Lieu')
    notes = fields.Text(string='Notes')
    attachment_ids = fields.Many2many('ir.attachment', string='Pièces jointes')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.odometer.log') or _('Nouveau')
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
                raise UserError(_('La valeur du compteur kilométrique ne peut pas être inférieure à la lecture précédente.'))

    def action_create_trip_record(self):
        """Créer un enregistrement de voyage basé sur le journal du compteur kilométrique"""
        self.ensure_one()
        return {
            'name': _('Créer un enregistrement de voyage'),
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
        """Mettre à jour la lecture actuelle du compteur kilométrique du véhicule"""
        self.ensure_one()
        self.vehicle_id.write({
            'odometer': self.value,
            'odometer_unit': self.unit,
        })
