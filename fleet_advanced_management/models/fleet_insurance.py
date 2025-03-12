from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class FleetVehicleInsurance(models.Model):
    _name = 'fleet.vehicle.insurance'
    _description = 'Assurance du véhicule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc'

    name = fields.Char(string='Numéro de police', required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Véhicule', required=True)
    
    # Détails de l'assurance
    insurance_type = fields.Selection([
        ('liability', 'Responsabilité civile'),
        ('comprehensive', 'Tous risques'),
        ('third_party', 'Tiers'),
        ('other', 'Autre')
    ], string='Type d\'assurance', required=True)
    
    insurer_id = fields.Many2one('res.partner', string='Compagnie d\'assurance', required=True)
    agent_id = fields.Many2one('res.partner', string='Agent d\'assurance')
    
    # Période de couverture
    start_date = fields.Date(string='Date de début', required=True)
    end_date = fields.Date(string='Date de fin', required=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('cancelled', 'Annulé')
    ], string='Statut', compute='_compute_state', store=True)
    
    # Informations financières
    premium_amount = fields.Float(string='Montant de la prime')
    deductible = fields.Float(string='Montant de la franchise')
    coverage_amount = fields.Float(string='Montant de la couverture')
    payment_frequency = fields.Selection([
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('semi_annual', 'Semestriel'),
        ('annual', 'Annuel')
    ], string='Fréquence de paiement')
    
    # Détails de la couverture
    coverage_details = fields.Text(string='Détails de la couverture')
    exclusions = fields.Text(string='Exclusions')
    notes = fields.Text(string='Notes')
    
    # Documents
    attachment_ids = fields.Many2many('ir.attachment', string='Documents')
    
    @api.depends('start_date', 'end_date')
    def _compute_state(self):
        today = fields.Date.today()
        for record in self:
            if not record.start_date or not record.end_date:
                record.state = 'draft'
            elif record.end_date < today:
                record.state = 'expired'
            elif record.start_date <= today <= record.end_date:
                record.state = 'active'
            else:
                record.state = 'draft'

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date > record.end_date:
                    raise UserError(_('La date de fin doit être après la date de début'))

    def action_renew_policy(self):
        """Créer un nouvel enregistrement d'assurance basé sur l'actuel"""
        self.ensure_one()
        return {
            'name': _('Renouveler la police d\'assurance'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle.insurance',
            'view_mode': 'form',
            'context': {
                'default_vehicle_id': self.vehicle_id.id,
                'default_insurance_type': self.insurance_type,
                'default_insurer_id': self.insurer_id.id,
                'default_agent_id': self.agent_id.id,
                'default_premium_amount': self.premium_amount,
                'default_deductible': self.deductible,
                'default_coverage_amount': self.coverage_amount,
                'default_payment_frequency': self.payment_frequency,
                'default_coverage_details': self.coverage_details,
                'default_exclusions': self.exclusions,
            }
        }

    def action_send_expiry_reminder(self):
        """Envoyer un rappel d'expiration à la personne responsable"""
        # Logique du modèle ici
        pass

    def action_create_expense(self):
        """Créer un enregistrement de dépense pour la prime d'assurance"""
        self.ensure_one()
        expense_vals = {
            'vehicle_id': self.vehicle_id.id,
            'date': fields.Date.today(),
            'amount': self.premium_amount,
            'expense_type': 'insurance',
            'description': f'Prime d\'assurance : {self.name}',
            'vendor_id': self.insurer_id.id,
        }
        expense = self.env['fleet.expense'].create(expense_vals)
        return {
            'name': _('Dépense'),
            'view_mode': 'form',
            'res_model': 'fleet.expense',
            'res_id': expense.id,
            'type': 'ir.actions.act_window',
        }
