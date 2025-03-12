from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class FleetVehicleFuelLog(models.Model):
    _name = 'fleet.vehicle.fuel.log'
    _description = 'Journal de carburant du véhicule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Référence', required=True, copy=False,
                      readonly=True, default=lambda self: _('Nouveau'))
    vehicle_id = fields.Many2one('fleet.vehicle', string='Véhicule', required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    
    # Détails du carburant
    fuel_type = fields.Selection([
        ('diesel', 'Diesel'),
        ('gasoline', 'Essence'),
        ('electric', 'Électrique'),
        ('hybrid', 'Hybride'),
        ('lpg', 'GPL'),
        ('cng', 'GNC'),
        ('other', 'Autre'),
    ], string='Type de carburant', required=True)
    
    liters = fields.Float(string='Litres')
    price_per_liter = fields.Float(string='Prix par litre')
    total_amount = fields.Float(string='Montant total', compute='_compute_amount', store=True)
    
    # Compteur kilométrique
    odometer = fields.Float(string='Lecture du compteur kilométrique', required=True)
    previous_odometer = fields.Float(string='Compteur kilométrique précédent', compute='_compute_previous_odometer')
    distance = fields.Float(string='Distance', compute='_compute_distance', store=True)
    
    # Localisation et fournisseur
    location = fields.Char(string='Lieu de remplissage')
    vendor_id = fields.Many2one('res.partner', string='Fournisseur/Station')
    invoice_reference = fields.Char(string='Référence de la facture')
    
    # Informations supplémentaires
    notes = fields.Text(string='Notes')
    full_tank = fields.Boolean(string='Plein complet')
    consumption = fields.Float(string='Consommation (L/100km)', compute='_compute_consumption')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.fuel.log') or _('Nouveau')
        return super(FleetVehicleFuelLog, self).create(vals)

    @api.depends('liters', 'price_per_liter')
    def _compute_amount(self):
        for record in self:
            record.total_amount = record.liters * record.price_per_liter

    @api.depends('vehicle_id', 'date')
    def _compute_previous_odometer(self):
        for record in self:
            previous_log = self.env['fleet.vehicle.fuel.log'].search([
                ('vehicle_id', '=', record.vehicle_id.id),
                ('date', '<', record.date),
                ('odometer', '!=', 0)
            ], order='date desc, odometer desc', limit=1)
            record.previous_odometer = previous_log.odometer if previous_log else 0.0

    @api.depends('odometer', 'previous_odometer')
    def _compute_distance(self):
        for record in self:
            record.distance = record.odometer - record.previous_odometer if record.previous_odometer > 0 else 0.0

    @api.depends('liters', 'distance')
    def _compute_consumption(self):
        for record in self:
            record.consumption = (record.liters * 100 / record.distance) if record.distance > 0 else 0.0

    def action_create_expense(self):
        """Créer un enregistrement de dépense à partir du journal de carburant"""
        self.ensure_one()
        expense_vals = {
            'vehicle_id': self.vehicle_id.id,
            'date': self.date,
            'amount': self.total_amount,
            'expense_type': 'fuel',
            'description': f'Carburant : {self.name}',
            'vendor_id': self.vendor_id.id,
        }
        expense = self.env['fleet.expense'].create(expense_vals)
        return {
            'name': _('Dépense'),
            'view_mode': 'form',
            'res_model': 'fleet.expense',
            'res_id': expense.id,
            'type': 'ir.actions.act_window',
        }
