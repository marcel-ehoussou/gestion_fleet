from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class FleetVehicleRevenue(models.Model):
    _name = 'fleet.vehicle.revenue'
    _description = 'Vehicle Revenue'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Reference', required=True, copy=False,
                      readonly=True, default=lambda self: _('New'))
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    
    # Revenue Source
    revenue_type = fields.Selection([
        ('rental', 'Vehicle Rental'),
        ('service', 'Service Revenue'),
        ('sale', 'Vehicle Sale'),
        ('insurance', 'Insurance Claim'),
        ('other', 'Other'),
    ], string='Revenue Type', required=True)
    
    # Financial Information
    amount = fields.Float(string='Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                 default=lambda self: self.env.company.currency_id)
    tax_amount = fields.Float(string='Tax Amount')
    total_amount = fields.Float(string='Total Amount', compute='_compute_total')
    
    # Customer Information
    partner_id = fields.Many2one('res.partner', string='Customer')
    invoice_reference = fields.Char(string='Invoice Reference')
    payment_status = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], string='Payment Status', default='draft', tracking=True)
    
    # Related Information
    reservation_id = fields.Many2one('fleet.vehicle.reservation', string='Related Reservation')
    maintenance_id = fields.Many2one('fleet.vehicle.maintenance', string='Related Maintenance')
    description = fields.Text(string='Description')
    notes = fields.Text(string='Notes')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.revenue') or _('New')
        return super(FleetVehicleRevenue, self).create(vals)

    @api.depends('amount', 'tax_amount')
    def _compute_total(self):
        for record in self:
            record.total_amount = record.amount + record.tax_amount

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError(_('Amount must be positive'))

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
        """Create customer invoice"""
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
            'name': _('Invoice'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'type': 'ir.actions.act_window',
        }

    def action_send_to_accounting(self):
        """Send revenue record to accounting module"""
        # Integration with accounting module
        pass

    def action_generate_report(self):
        """Generate revenue report"""
        # Report generation logic
        pass
