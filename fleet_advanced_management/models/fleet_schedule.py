from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class FleetDriverSchedule(models.Model):
    _name = 'fleet.driver.schedule'
    _description = 'Planning de travail du conducteur'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_datetime desc'

    name = fields.Char(string='Référence', required=True, copy=False,
                      readonly=True, default=lambda self: _('Nouveau'))
    driver_id = fields.Many2one('fleet.driver', string='Conducteur', required=True)
    
    # Période de planification
    start_datetime = fields.Datetime(string='Heure de début', required=True)
    end_datetime = fields.Datetime(string='Heure de fin', required=True)
    duration = fields.Float(string='Durée (heures)', compute='_compute_duration')
    
    # Type de planification
    schedule_type = fields.Selection([
        ('regular', 'Service régulier'),
        ('overtime', 'Heures supplémentaires'),
        ('on_call', 'Sur appel'),
        ('standby', 'En attente'),
        ('leave', 'Congé'),
    ], string='Type de planification', required=True, default='regular')
    
    # Statut
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string='Statut', default='draft', tracking=True)
    
    # Détails de l'affectation
    vehicle_id = fields.Many2one('fleet.vehicle', string='Véhicule assigné')
    location = fields.Char(string='Lieu de travail')
    description = fields.Text(string='Description')
    
    # Suivi du temps
    check_in = fields.Datetime(string='Heure d\'arrivée')
    check_out = fields.Datetime(string='Heure de départ')
    actual_hours = fields.Float(string='Heures réelles', compute='_compute_actual_hours')
    
    # Informations supplémentaires
    notes = fields.Text(string='Notes')
    attachment_ids = fields.Many2many('ir.attachment', string='Pièces jointes')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.driver.schedule') or _('Nouveau')
        return super(FleetDriverSchedule, self).create(vals)

    @api.depends('start_datetime', 'end_datetime')
    def _compute_duration(self):
        for record in self:
            if record.start_datetime and record.end_datetime:
                duration = fields.Datetime.from_string(record.end_datetime) - \
                          fields.Datetime.from_string(record.start_datetime)
                record.duration = duration.total_seconds() / 3600
            else:
                record.duration = 0.0

    @api.depends('check_in', 'check_out')
    def _compute_actual_hours(self):
        for record in self:
            if record.check_in and record.check_out:
                duration = fields.Datetime.from_string(record.check_out) - \
                          fields.Datetime.from_string(record.check_in)
                record.actual_hours = duration.total_seconds() / 3600
            else:
                record.actual_hours = 0.0

    @api.constrains('start_datetime', 'end_datetime')
    def _check_dates(self):
        for record in self:
            if record.start_datetime and record.end_datetime:
                if record.start_datetime > record.end_datetime:
                    raise ValidationError(_('L\'heure de fin ne peut pas être avant l\'heure de début'))
                
                # Vérifier les plannings qui se chevauchent
                domain = [
                    ('driver_id', '=', record.driver_id.id),
                    ('id', '!=', record.id),
                    ('state', 'not in', ['cancelled', 'completed']),
                    '|',
                    '&', ('start_datetime', '<=', record.start_datetime),
                         ('end_datetime', '>=', record.start_datetime),
                    '&', ('start_datetime', '<=', record.end_datetime),
                         ('end_datetime', '>=', record.end_datetime),
                ]
                if self.search_count(domain):
                    raise ValidationError(_('Le conducteur a déjà un planning pour cette période'))

    def action_confirm(self):
        self.ensure_one()
        self.state = 'confirmed'

    def action_start(self):
        self.ensure_one()
        self.state = 'in_progress'
        self.check_in = fields.Datetime.now()

    def action_complete(self):
        self.ensure_one()
        if not self.check_in:
            raise ValidationError(_('Impossible de terminer le planning sans heure d\'arrivée'))
        self.state = 'completed'
        self.check_out = fields.Datetime.now()

    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'

    def action_reset_to_draft(self):
        self.ensure_one()
        self.state = 'draft'
        self.check_in = False
        self.check_out = False

    def action_print_schedule(self):
        """Imprimer les détails du planning"""
        pass

    def action_send_notification(self):
        """Envoyer une notification de planning au conducteur"""
        pass
