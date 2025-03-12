from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class FleetVehicleRevenue(models.Model):
    _name = 'fleet.vehicle.revenue'
    _description = 'Revenu du véhicule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Référence', required=True, copy=False,
                      readonly=True, default=lambda self: _('Nouveau'))
    vehicle_id = fields.Many2one('fleet.vehicle', string='Véhicule', required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    
    # Source de revenu
    revenue_type = fields.Selection([
        ('rental', 'Location de véhicule'),
        ('service', 'Revenu de service'),
        ('sale', 'Vente de véhicule'),
        ('insurance', 'Réclamation d\'assurance'),
        ('other', 'Autre'),
    ], string='Type de revenu', required=True)
    
    # Informations financières
    amount = fields.Float(string='Montant', required=True)
    currency_id = fields.Many2one('res.currency', string='Devise',
                                 default=lambda self: self.env.company.currency_id)
    tax_amount = fields.Float(string='Montant de la taxe')
    total_amount = fields.Float(string='Montant total', compute='_compute_total')
    
    # Informations sur le client
    partner_id = fields.Many2one('res.partner', string='Client')
    invoice_reference = fields.Char(string='Référence de la facture')
    payment_status = fields.Selection([
        ('draft', 'Brouillon'),
        ('pending', 'En attente'),
        ('paid', 'Payé'),
        ('cancelled', 'Annulé'),
    ], string='Statut de paiement', default='draft', tracking=True)
    
    # Informations connexes
    reservation_id = fields.Many2one('fleet.vehicle.reservation', string='Réservation associée')
    maintenance_id = fields.Many2one('fleet.vehicle.maintenance', string='Maintenance associée')
    description = fields.Text(string='Description')
    notes = fields.Text(string='Notes')
    attachment_ids = fields.Many2many('ir.attachment', string='Pièces jointes')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.revenue') or _('Nouveau')
        return super(FleetVehicleRevenue, self).create(vals)

    @api.depends('amount', 'tax_amount')
    def _compute_total(self):
        for record in self:
            record.total_amount = record.amount + record.tax_amount

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError(_('Le montant doit être positif'))

    def action_mark_as_paid(self):
        self.ensure_one()
        self.payment_status = 'paid'

    def action_mark_as_pending(self):
        self.ensure_one()
        self.payment_status = 'pending'

    def action_cancel(self):
        self.ensure_one()
        self.payment_status = 'cancelled'

    def action_create_invoice(self):
        """Créer une facture client"""
        self.ensure_one()
        invoice_vals = {
            'partner_id': self.partner_id.id,
            'invoice_date': self.date,
            'invoice_line_ids': [(0, 0, {
                'name': f'{self.revenue_type} - {self.vehicle_id.name}',
                'quantity': 1,
                'price_unit': self.amount,
            })],
        }
        invoice = self.env['account.move'].create(invoice_vals)
        return {
            'name': _('Facture'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'type': 'ir.actions.act_window',
        }

    def action_send_to_accounting(self):
        """Envoyer l'enregistrement de revenu au module de comptabilité"""
        # Intégration avec le module de comptabilité
        pass

    def action_generate_report(self):
        """Générer un rapport de revenu"""
        # Logique de génération de rapport
        pass
