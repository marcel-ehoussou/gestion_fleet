from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class FleetDocument(models.Model):
    _name = 'fleet.vehicle.document'
    _description = 'Vehicle Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'expiry_date'

    name = fields.Char(string='Document Name', required=True)
    reference = fields.Char(string='Reference Number', required=True)
    
    document_type = fields.Selection([
        ('registration', 'Vehicle Registration'),
        ('insurance', 'Insurance'),
        ('permit', 'Permit'),
        ('tax', 'Road Tax'),
        ('inspection', 'Technical Inspection'),
        ('maintenance', 'Maintenance Record'),
        ('other', 'Other'),
    ], string='Document Type', required=True)
    
    # Document Details
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    driver_id = fields.Many2one('fleet.driver', string='Driver')
    issuing_authority = fields.Char(string='Issuing Authority')
    issue_date = fields.Date(string='Issue Date', required=True)
    expiry_date = fields.Date(string='Expiry Date')
    
    # Document Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('valid', 'Valid'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', compute='_compute_state', store=True)
    
    active = fields.Boolean(default=True)
    
    # Document Storage
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    document_url = fields.Char(string='Document URL')
    notes = fields.Text(string='Notes')
    
    # Reminder Configuration
    reminder_ids = fields.One2many('fleet.document.reminder', 'document_id',
                                  string='Reminders')
    
    # Renewal Information
    renewal_cost = fields.Float(string='Renewal Cost')
    last_renewal_date = fields.Date(string='Last Renewal Date')
    next_renewal_date = fields.Date(string='Next Renewal Date')
    
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

    def action_renew(self):
        self.ensure_one()
        return {
            'name': _('Renew Document'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.document.renewal.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_document_id': self.id},
        }

    def action_send_reminder(self):
        # Send reminder email about document expiration
        pass

    def action_archive(self):
        self.ensure_one()
        self.active = False

    @api.model
    def run_document_check(self):
        # Scheduled action to check document validity and send notifications
        soon_to_expire = self.search([
            ('expiry_date', '!=', False),
            ('expiry_date', '>', fields.Date.today()),
            ('expiry_date', '<=', fields.Date.today() + timedelta(days=30)),
            ('state', '=', 'valid'),
        ])
        for document in soon_to_expire:
            document.action_send_reminder()

class FleetDocumentReminder(models.Model):
    _name = 'fleet.document.reminder'
    _description = 'Document Reminder'

    document_id = fields.Many2one('fleet.vehicle.document', string='Document',
                                 required=True)
    reminder_type = fields.Selection([
        ('days', 'Days Before'),
        ('weeks', 'Weeks Before'),
        ('months', 'Months Before'),
    ], string='Reminder Type', required=True)
    
    value = fields.Integer(string='Value', required=True)
    notification_type = fields.Selection([
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('both', 'Both'),
    ], string='Notification Type', required=True)
    
    recipient_ids = fields.Many2many('res.partner', string='Recipients')
    message_template = fields.Text(string='Message Template')
    active = fields.Boolean(default=True)

    def action_send_notification(self):
        # Send notification based on reminder configuration
        pass
