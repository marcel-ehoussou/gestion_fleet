from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class FleetDriverSchedule(models.Model):
    _name = 'fleet.driver.schedule'
    _description = 'Driver Work Schedule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_datetime desc'

    name = fields.Char(string='Reference', required=True, copy=False,
                      readonly=True, default=lambda self: _('New'))
    driver_id = fields.Many2one('fleet.driver', string='Driver', required=True)
    
    # Schedule Period
    date = fields.Date(string='Date', required=True)
    start_time = fields.Float(string='Start Time', required=True)
    end_time = fields.Float(string='End Time', required=True)
    start_datetime = fields.Datetime(string='Start DateTime', compute='_compute_datetime', store=True)
    end_datetime = fields.Datetime(string='End DateTime', compute='_compute_datetime', store=True)
    duration = fields.Float(string='Duration (Hours)', compute='_compute_duration')
    
    # Schedule Type
    assignment_type = fields.Selection([
        ('regular', 'Regular Shift'),
        ('overtime', 'Overtime'),
        ('on_call', 'On Call'),
        ('standby', 'Standby'),
        ('leave', 'Leave'),
    ], string='Schedule Type', required=True, default='regular')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    # Assignment Details
    vehicle_id = fields.Many2one('fleet.vehicle', string='Assigned Vehicle')
    location = fields.Char(string='Work Location')
    description = fields.Text(string='Description')
    
    # Time Tracking
    check_in = fields.Datetime(string='Check In Time')
    check_out = fields.Datetime(string='Check Out Time')
    actual_hours = fields.Float(string='Actual Hours', compute='_compute_actual_hours')
    
    # Additional Information
    notes = fields.Text(string='Notes')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.driver.schedule') or _('New')
        return super(FleetDriverSchedule, self).create(vals)

    @api.depends('date', 'start_time', 'end_time')
    def _compute_datetime(self):
        for record in self:
            if record.date:
                # Convert float time to hours and minutes
                start_hour = int(record.start_time)
                start_minute = int((record.start_time % 1) * 60)
                end_hour = int(record.end_time)
                end_minute = int((record.end_time % 1) * 60)
                
                # Create datetime objects
                record.start_datetime = fields.Datetime.to_string(
                    datetime.combine(record.date,
                                    datetime.min.time().replace(hour=start_hour,
                                                               minute=start_minute)))
                record.end_datetime = fields.Datetime.to_string(
                    datetime.combine(record.date,
                                    datetime.min.time().replace(hour=end_hour,
                                                               minute=end_minute)))

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for record in self:
            if record.start_time is not False and record.end_time is not False:
                record.duration = record.end_time - record.start_time
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
                    raise ValidationError(_('End time cannot be before start time'))
                
                # Check for overlapping schedules
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
                    raise ValidationError(_('Driver already has a schedule for this period'))

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
            raise ValidationError(_('Cannot complete schedule without check-in time'))
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
        """Print schedule details"""
        pass

    def action_send_notification(self):
        """Send schedule notification to driver"""
        pass
