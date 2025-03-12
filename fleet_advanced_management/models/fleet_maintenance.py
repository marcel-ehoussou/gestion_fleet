from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class FleetMaintenance(models.Model):
    _name = 'fleet.vehicle.maintenance'
    _description = 'Maintenance du véhicule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Référence', required=True, copy=False,
                      readonly=True, default=lambda self: _('Nouveau'))
    vehicle_id = fields.Many2one('fleet.vehicle', string='Véhicule', required=True)
    date = fields.Date(string='Date de maintenance', required=True, default=fields.Date.context_today)
    
    maintenance_type = fields.Selection([
        ('preventive', 'Préventive'),
        ('corrective', 'Corrective'),
        ('predictive', 'Prédictive'),
        ('diagnostic', 'Diagnostique'),
    ], string='Type de maintenance', required=True)
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('scheduled', 'Planifiée'),
        ('in_progress', 'En cours'),
        ('done', 'Terminée'),
        ('cancelled', 'Annulée'),
    ], string='Statut', default='draft', tracking=True)
    
    # Détails du service
    service_items = fields.One2many('fleet.maintenance.service.item', 
                                   'maintenance_id', string='Éléments de service')
    total_parts_cost = fields.Float(string='Coût des pièces', compute='_compute_costs')
    labor_cost = fields.Float(string='Coût de la main-d\'œuvre')
    total_cost = fields.Float(string='Coût total', compute='_compute_costs')
    
    # Fournisseur de service
    vendor_id = fields.Many2one('res.partner', string='Fournisseur de service')
    technician = fields.Char(string='Nom du technicien')
    workshop_address = fields.Text(string='Adresse de l\'atelier')
    
    # Planification
    scheduled_date = fields.Datetime(string='Date planifiée')
    completion_date = fields.Datetime(string='Date de fin')
    duration = fields.Float(string='Durée (heures)')
    
    # Statut du véhicule
    odometer = fields.Float(string='Lecture du compteur kilométrique')
    next_service_odometer = fields.Float(string='Prochain service à l\'odomètre')
    next_service_date = fields.Date(string='Date du prochain service')
    
    # Documentation
    diagnosis = fields.Text(string='Diagnostic/Constatations')
    operations_performed = fields.Text(string='Opérations effectuées')
    recommendations = fields.Text(string='Recommandations')
    attachment_ids = fields.Many2many('ir.attachment', string='Pièces jointes')
    
    # Informations connexes
    expense_id = fields.Many2one('fleet.expense', string='Dépense associée')
    warranty_claim = fields.Boolean(string='Réclamation de garantie')
    warranty_details = fields.Text(string='Détails de la garantie')

    @api.model
    def create(self, vals):
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.maintenance') or _('Nouveau')
        return super(FleetMaintenance, self).create(vals)

    @api.depends('service_items.cost', 'labor_cost')
    def _compute_costs(self):
        for record in self:
            record.total_parts_cost = sum(record.service_items.mapped('cost'))
            record.total_cost = record.total_parts_cost + record.labor_cost

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        if self.vehicle_id:
            self.odometer = self.vehicle_id.odometer

    def action_schedule(self):
        if not self.scheduled_date:
            raise UserError(_('Veuillez d\'abord définir une date planifiée.'))
        self.state = 'scheduled'

    def action_start(self):
        self.state = 'in_progress'

    def action_complete(self):
        self.state = 'done'
        self.completion_date = fields.Datetime.now()
        self._create_expense_record()

    def action_cancel(self):
        self.state = 'cancelled'

    def _create_expense_record(self):
        # Créer un enregistrement de dépense associé
        if not self.expense_id and self.total_cost > 0:
            expense_vals = {
                'vehicle_id': self.vehicle_id.id,
                'date': fields.Date.today(),
                'amount': self.total_cost,
                'expense_type': 'maintenance',
                'description': f'Maintenance : {self.name}',
                'vendor_id': self.vendor_id.id,
            }
            self.expense_id = self.env['fleet.expense'].create(expense_vals)

    def action_print_report(self):
        # Générer un rapport de maintenance
        pass

    def action_send_reminder(self):
        # Envoyer un rappel à la personne responsable
        pass

class FleetMaintenanceServiceItem(models.Model):
    _name = 'fleet.maintenance.service.item'
    _description = 'Élément de service de maintenance'

    maintenance_id = fields.Many2one('fleet.vehicle.maintenance', 
                                    string='Enregistrement de maintenance')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Véhicule',
                                related='maintenance_id.vehicle_id',
                                store=True)
    name = fields.Char(string='Élément de service', required=True)
    product_id = fields.Many2one('product.product', string='Pièce')
    quantity = fields.Float(string='Quantité', default=1.0)
    unit_cost = fields.Float(string='Coût unitaire')
    cost = fields.Float(string='Coût total', compute='_compute_cost')
    state = fields.Selection([
        ('planned', 'Planifié'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé')
    ], string='Statut', default='planned')

    @api.depends('quantity', 'unit_cost')
    def _compute_cost(self):
        for record in self:
            record.cost = record.quantity * record.unit_cost
