from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class FleetVehicleInspection(models.Model):
    _name = 'fleet.vehicle.inspection'
    _description = 'Inspection technique du véhicule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Référence', required=True, copy=False,
                      readonly=True, default=lambda self: _('Nouveau'))
    vehicle_id = fields.Many2one('fleet.vehicle', string='Véhicule', required=True)
    date = fields.Date(string='Date d\'inspection', required=True, default=fields.Date.context_today)
    
    # Détails de l'inspection
    inspection_type = fields.Selection([
        ('periodic', 'Inspection technique périodique'),
        ('pre_purchase', 'Inspection avant achat'),
        ('damage', 'Évaluation des dommages'),
        ('warranty', 'Inspection de garantie'),
        ('other', 'Autre')
    ], string='Type d\'inspection', required=True)
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('in_progress', 'En cours'),
        ('passed', 'Réussi'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé')
    ], string='Statut', default='draft', tracking=True)
    
    # Informations sur l'inspecteur
    inspector_id = fields.Many2one('res.partner', string='Inspecteur/Entreprise')
    inspector_name = fields.Char(string='Nom de l\'inspecteur')
    location = fields.Char(string='Lieu de l\'inspection')
    
    # Informations sur le véhicule au moment de l'inspection
    odometer = fields.Float(string='Lecture du compteur kilométrique')
    next_inspection_date = fields.Date(string='Prochaine inspection due')
    next_inspection_odometer = fields.Float(string='Prochain compteur kilométrique d\'inspection')
    
    # Zones d'inspection
    brake_system = fields.Selection([
        ('good', 'Bon'),
        ('fair', 'Moyen'),
        ('poor', 'Mauvais'),
        ('na', 'N/A')
    ], string='Système de freinage')
    
    suspension = fields.Selection([
        ('good', 'Bon'),
        ('fair', 'Moyen'),
        ('poor', 'Mauvais'),
        ('na', 'N/A')
    ], string='Suspension')
    
    steering = fields.Selection([
        ('good', 'Bon'),
        ('fair', 'Moyen'),
        ('poor', 'Mauvais'),
        ('na', 'N/A')
    ], string='Direction')
    
    engine = fields.Selection([
        ('good', 'Bon'),
        ('fair', 'Moyen'),
        ('poor', 'Mauvais'),
        ('na', 'N/A')
    ], string='Moteur')
    
    transmission = fields.Selection([
        ('good', 'Bon'),
        ('fair', 'Moyen'),
        ('poor', 'Mauvais'),
        ('na', 'N/A')
    ], string='Transmission')
    
    exhaust = fields.Selection([
        ('good', 'Bon'),
        ('fair', 'Moyen'),
        ('poor', 'Mauvais'),
        ('na', 'N/A')
    ], string='Système d\'échappement')
    
    # Résultats et documentation
    passed_all = fields.Boolean(string='Tous les contrôles réussis', compute='_compute_passed_all')
    notes = fields.Text(string='Notes')
    recommendations = fields.Text(string='Recommandations')
    attachment_ids = fields.Many2many('ir.attachment', string='Documents')
    
    # Coûts
    cost = fields.Float(string='Coût de l\'inspection')
    currency_id = fields.Many2one('res.currency', string='Devise',
                                 default=lambda self: self.env.company.currency_id)
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.inspection') or _('Nouveau')
        return super(FleetVehicleInspection, self).create(vals)

    @api.depends('brake_system', 'suspension', 'steering', 'engine', 'transmission', 'exhaust')
    def _compute_passed_all(self):
        for record in self:
            checks = [record.brake_system, record.suspension, record.steering,
                     record.engine, record.transmission, record.exhaust]
            record.passed_all = all(check in ['good', 'fair', 'na'] for check in checks if check)

    def action_start_inspection(self):
        self.state = 'in_progress'

    def action_mark_passed(self):
        if not self.passed_all:
            raise UserError(_('Impossible de marquer comme réussi. Certains contrôles ont échoué.'))
        self.state = 'passed'

    def action_mark_failed(self):
        self.state = 'failed'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_create_expense(self):
        """Créer un enregistrement de dépense pour le coût de l'inspection"""
        self.ensure_one()
        if not self.cost:
            raise UserError(_('Veuillez d\'abord définir le coût de l\'inspection.'))
            
        expense_vals = {
            'vehicle_id': self.vehicle_id.id,
            'date': self.date,
            'amount': self.cost,
            'expense_type': 'inspection',
            'description': f'Inspection technique : {self.name}',
            'vendor_id': self.inspector_id.id,
        }
        expense = self.env['fleet.expense'].create(expense_vals)
        return {
            'name': _('Dépense'),
            'view_mode': 'form',
            'res_model': 'fleet.expense',
            'res_id': expense.id,
            'type': 'ir.actions.act_window',
        }

    def action_schedule_maintenance(self):
        """Planifier la maintenance en fonction des résultats de l'inspection"""
        self.ensure_one()
        return {
            'name': _('Planifier la maintenance'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle.maintenance',
            'view_mode': 'form',
            'context': {
                'default_vehicle_id': self.vehicle_id.id,
                'default_maintenance_type': 'corrective',
                'default_notes': self.notes,
            },
        }
