from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class FleetExpense(models.Model):
    _name = 'fleet.expense'
    _description = 'Dépense de flotte'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Référence', required=True, copy=False, 
                      readonly=True, default=lambda self: _('Nouveau'))
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Véhicule', required=True)
    driver_id = fields.Many2one('fleet.driver', string='Conducteur')
    expense_type = fields.Selection([
        ('fuel', 'Carburant'),
        ('repair', 'Réparation'),
        ('maintenance', 'Maintenance'),
        ('insurance', 'Assurance'),
        ('tax', 'Taxe'),
        ('other', 'Autre'),
    ], string='Type', required=True)
    
    amount = fields.Float(string='Montant', required=True)
    description = fields.Text(string='Description')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('submitted', 'Soumis'),
        ('approved', 'Approuvé'),
        ('paid', 'Payé'),
        ('cancelled', 'Annulé'),
    ], string='Statut', default='draft', tracking=True)
    
    # Champs spécifiques au carburant
    liters = fields.Float(string='Litres')
    price_per_liter = fields.Float(string='Prix par litre')
    odometer = fields.Float(string='Lecture du compteur kilométrique')
    fuel_type = fields.Selection([
        ('diesel', 'Diesel'),
        ('gasoline', 'Essence'),
        ('electric', 'Électrique'),
        ('hybrid', 'Hybride'),
    ], string='Type de carburant')
    
    # Champs spécifiques à la réparation/maintenance
    service_type_id = fields.Many2one('fleet.service.type', string='Type de service')
    vendor_id = fields.Many2one('res.partner', string='Fournisseur')
    invoice_ref = fields.Char(string='Référence de la facture')
    next_service_date = fields.Date(string='Date du prochain service')
    
    # Champs spécifiques à l'assurance/taxe
    start_date = fields.Date(string='Date de début')
    end_date = fields.Date(string='Date de fin')
    policy_number = fields.Char(string='Numéro de police/document')
    
    # Champs comptables
    analytic_account_id = fields.Many2one('account.analytic.account', 
                                         string='Compte analytique')
    company_id = fields.Many2one('res.company', string='Société', 
                                default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Devise',
                                 related='company_id.currency_id')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.expense') or _('Nouveau')
        return super(FleetExpense, self).create(vals)
    
    @api.onchange('expense_type')
    def _onchange_expense_type(self):
        # Réinitialiser les champs spécifiques lorsque le type de dépense change
        if self.expense_type != 'fuel':
            self.liters = 0.0
            self.price_per_liter = 0.0
            self.fuel_type = False
        
    @api.onchange('liters', 'price_per_liter')
    def _onchange_fuel_calculation(self):
        if self.expense_type == 'fuel':
            self.amount = self.liters * self.price_per_liter
            
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.start_date > record.end_date:
                raise ValidationError(_('La date de fin ne peut pas être antérieure à la date de début.'))
                
    def action_submit(self):
        self.state = 'submitted'
        
    def action_approve(self):
        self.state = 'approved'
        
    def action_pay(self):
        self.state = 'paid'
        
    def action_cancel(self):
        self.state = 'cancelled'
        
    def action_draft(self):
        self.state = 'draft'
        
    def action_create_vendor_bill(self):
        # Logique pour créer une facture fournisseur en comptabilité
        pass
        
    def action_view_analytics(self):
        # Logique pour voir les analyses des dépenses
        pass
