from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class FleetDocument(models.Model):
    _name = 'fleet.vehicle.document'
    _description = 'Document du véhicule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'expiry_date'

    name = fields.Char(string='Nom du document', required=True)
    reference = fields.Char(string='Numéro de référence', required=True)
    
    document_type = fields.Selection([
        ('registration', 'Immatriculation du véhicule'),
        ('insurance', 'Assurance'),
        ('permit', 'Permis'),
        ('tax', 'Taxe routière'),
        ('inspection', 'Inspection technique'),
        ('maintenance', 'Enregistrement de maintenance'),
        ('other', 'Autre'),
    ], string='Type de document', required=True)
    
    # Détails du document
    vehicle_id = fields.Many2one('fleet.vehicle', string='Véhicule')
    driver_id = fields.Many2one('fleet.driver', string='Conducteur')
    issuing_authority = fields.Char(string='Autorité émettrice')
    issue_date = fields.Date(string='Date d\'émission', required=True)
    expiry_date = fields.Date(string='Date d\'expiration')
    
    # Statut du document
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('valid', 'Valide'),
        ('expired', 'Expiré'),
        ('cancelled', 'Annulé'),
    ], string='Statut', compute='_compute_state', store=True)
    
    active = fields.Boolean(default=True)
    
    # Stockage du document
    attachment_ids = fields.Many2many('ir.attachment', string='Pièces jointes')
    document_url = fields.Char(string='URL du document')
    notes = fields.Text(string='Notes')
    
    # Configuration des rappels
    reminder_ids = fields.One2many('fleet.document.reminder', 'document_id',
                                  string='Rappels')
    
    # Informations de renouvellement
    renewal_cost = fields.Float(string='Coût de renouvellement')
    last_renewal_date = fields.Date(string='Date du dernier renouvellement')
    next_renewal_date = fields.Date(string='Date du prochain renouvellement')
    
    @api.depends('expiry_date')
    def _compute_state(self):
        today = fields.Date.today()
        for record in self:
            if not record.expiry_date:
                record.state = 'valid'
            elif record.expiry_date < today:
                record.state = 'expired'
            else:
                record.state = 'valid'

    @api.constrains('issue_date', 'expiry_date')
    def _check_dates(self):
        for record in self:
            if record.issue_date and record.expiry_date:
                if record.expiry_date < record.issue_date:
                    raise ValidationError(_('La date d\'expiration ne peut pas être antérieure à la date d\'émission'))

    def action_set_draft(self):
        self.ensure_one()
        self.state = 'draft'

    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'

    def action_renew(self):
        self.ensure_one()
        return {
            'name': _('Renouveler le document'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.document.renewal.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_document_id': self.id},
        }

    def action_send_reminder(self):
        # Envoyer un rappel par email concernant l'expiration du document
        pass

    def action_archive(self):
        self.ensure_one()
        self.active = False

    @api.model
    def run_document_check(self):
        # Action planifiée pour vérifier la validité des documents et envoyer des notifications
        soon_to_expire = self.search([
            ('expiry_date', '!=', False),
            ('expiry_date', '>', fields.Date.today()),
            ('expiry_date', '<=', fields.Date.today() + timedelta(days=30)),
            ('state', '=', 'valide'),
        ])
        for document in soon_to_expire:
            document.action_send_reminder()

class FleetDriverDocument(models.Model):
    _name = 'fleet.driver.document'
    _description = 'Driver Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'expiry_date'

    name = fields.Char(string='Document Name', required=True, tracking=True)
    description = fields.Text(string='Description')
    
    # Document Details
    driver_id = fields.Many2one('fleet.driver', string='Driver', required=True)
    document_type = fields.Selection([
        ('license', 'Driver License'),
        ('permit', 'Special Permit'),
        ('certification', 'Certification'),
        ('training', 'Training Certificate'),
        ('medical', 'Medical Certificate'),
        ('other', 'Other'),
    ], string='Document Type', required=True, tracking=True)
    
    issue_date = fields.Date(string='Issue Date', required=True, tracking=True)
    expiry_date = fields.Date(string='Expiry Date', tracking=True)
    
    # Document Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('valid', 'Valid'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', compute='_compute_state', store=True, tracking=True)
    
    active = fields.Boolean(default=True)
    
    # Document Storage
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    notes = fields.Text(string='Notes')
    
    @api.depends('expiry_date')
    def _compute_state(self):
        today = fields.Date.today()
        for record in self:
            if not record.expiry_date:
                record.state = 'valid'
            elif record.expiry_date < today:
                record.state = 'expired'
            else:
                record.state = 'valid'

    @api.constrains('issue_date', 'expiry_date')
    def _check_dates(self):
        for record in self:
            if record.issue_date and record.expiry_date:
                if record.expiry_date < record.issue_date:
                    raise ValidationError(_('Expiry date cannot be before issue date'))

    def action_set_draft(self):
        self.ensure_one()
        self.state = 'draft'

    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'

    def action_archive(self):
        self.ensure_one()
        self.active = False

class FleetDocumentReminder(models.Model):
    _name = 'fleet.document.reminder'
    _description = 'Rappel de document'

    document_id = fields.Many2one('fleet.vehicle.document', string='Document',
                                 required=True)
    reminder_type = fields.Selection([
        ('days', 'Jours avant'),
        ('weeks', 'Semaines avant'),
        ('months', 'Mois avant'),
    ], string='Type de rappel', required=True)
    
    value = fields.Integer(string='Valeur', required=True)
    notification_type = fields.Selection([
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('both', 'Les deux'),
    ], string='Type de notification', required=True)
    
    recipient_ids = fields.Many2many('res.partner', string='Destinataires')
    message_template = fields.Text(string='Modèle de message')
    active = fields.Boolean(default=True)

    def action_send_notification(self):
        # Envoyer une notification basée sur la configuration du rappel
        pass
