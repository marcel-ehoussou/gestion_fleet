from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    # Fuel Management
    fuel_log_ids = fields.One2many('fleet.vehicle.fuel.log', 'vehicle_id', string='Fuel Logs')
    fuel_efficiency = fields.Float(string='Fuel Efficiency (L/100km)', compute='_compute_fuel_efficiency')
    last_fuel_cost = fields.Float(string='Last Fuel Cost', compute='_compute_last_fuel_cost')
    
    # Maintenance and Repairs
    maintenance_log_ids = fields.One2many('fleet.vehicle.maintenance', 'vehicle_id', string='Maintenance Logs')
    next_maintenance_date = fields.Date(string='Next Maintenance Date', compute='_compute_next_maintenance', store=True)
    maintenance_cost_total = fields.Float(string='Total Maintenance Cost', compute='_compute_maintenance_cost')
    service_count = fields.Integer(string='Services', compute='_compute_service_count')
    service_activity = fields.Selection([
        ('overdue', 'Overdue'),
        ('today', 'Today'),
        ('planned', 'Planned'),
        ('none', 'None'),
    ], string='Service Activity', compute='_compute_service_activity')
    
    # Other Expenses
    insurance_ids = fields.One2many('fleet.vehicle.insurance', 'vehicle_id', string='Insurance Records')
    technical_inspection_ids = fields.One2many('fleet.vehicle.inspection', 'vehicle_id', string='Technical Inspections')
    current_insurance_id = fields.Many2one('fleet.vehicle.insurance', string='Current Insurance',
                                         compute='_compute_current_insurance')
    
    # Mileage Tracking
    odometer_log_ids = fields.One2many('fleet.vehicle.odometer.log', 'vehicle_id', string='Odometer Logs')
    last_odometer = fields.Float(string='Last Odometer Reading', compute='_compute_last_odometer')
    daily_usage = fields.Float(string='Average Daily Usage (km)', compute='_compute_daily_usage')
    
    # Documents
    document_ids = fields.One2many('fleet.vehicle.document', 'vehicle_id', string='Documents')
    document_count = fields.Integer(string='Document Count', compute='_compute_document_count')
    
    # Reservations
    reservation_ids = fields.One2many('fleet.vehicle.reservation', 'vehicle_id', string='Reservations')
    is_available = fields.Boolean(string='Available', compute='_compute_availability', store=True)
    current_driver_id = fields.Many2one('fleet.driver', string='Current Driver',
                                      compute='_compute_current_driver')
    
    # Revenue Tracking
    revenue_ids = fields.One2many('fleet.vehicle.revenue', 'vehicle_id', string='Revenue Records')
    total_revenue = fields.Float(string='Total Revenue', compute='_compute_total_revenue')
    profitability = fields.Float(string='Profitability (%)', compute='_compute_profitability', store=True)
    
    @api.depends('fuel_log_ids', 'odometer_log_ids')
    def _compute_fuel_efficiency(self):
        for vehicle in self:
            if len(vehicle.odometer_log_ids) >= 2:
                sorted_logs = vehicle.odometer_log_ids.sorted('date')
                distance = sorted_logs[-1].value - sorted_logs[0].value
                total_fuel = sum(vehicle.fuel_log_ids.mapped('liters'))
                if distance > 0 and total_fuel > 0:
                    vehicle.fuel_efficiency = (total_fuel * 100) / distance
                else:
                    vehicle.fuel_efficiency = 0
            else:
                vehicle.fuel_efficiency = 0
            
    @api.depends('maintenance_log_ids', 'maintenance_log_ids.state', 'maintenance_log_ids.date')
    def _compute_next_maintenance(self):
        for vehicle in self:
            upcoming_maintenances = vehicle.maintenance_log_ids.filtered(
                lambda m: m.state == 'scheduled' and m.date > fields.Date.today()
            ).sorted('date')
            vehicle.next_maintenance_date = upcoming_maintenances[0].date if upcoming_maintenances else False

    @api.depends('maintenance_log_ids.total_cost')
    def _compute_maintenance_cost(self):
        for vehicle in self:
            vehicle.maintenance_cost_total = sum(vehicle.maintenance_log_ids.mapped('total_cost'))
            
    @api.depends('insurance_ids')
    def _compute_current_insurance(self):
        today = fields.Date.today()
        for vehicle in self:
            current_insurance = vehicle.insurance_ids.filtered(
                lambda i: i.state == 'valid' and 
                          i.start_date <= today and 
                          (not i.end_date or i.end_date >= today)
            )
            vehicle.current_insurance_id = current_insurance[0] if current_insurance else False
            
    @api.depends('reservation_ids', 'reservation_ids.state', 'reservation_ids.start_date', 'reservation_ids.end_date')
    def _compute_availability(self):
        now = fields.Datetime.now()
        for vehicle in self:
            current_reservation = vehicle.reservation_ids.filtered(
                lambda r: r.state == 'confirmed' and 
                          r.start_date <= now and 
                          r.end_date >= now
            )
            vehicle.is_available = not bool(current_reservation)
            if current_reservation:
                vehicle.current_driver_id = current_reservation[0].driver_id
            else:
                vehicle.current_driver_id = False
            
    @api.depends('revenue_ids', 'revenue_ids.amount', 'maintenance_cost_total', 'fuel_log_ids', 'fuel_log_ids.total_amount')
    def _compute_profitability(self):
        for vehicle in self:
            total_revenue = sum(vehicle.revenue_ids.mapped('amount'))
            total_cost = vehicle.maintenance_cost_total + \
                        sum(vehicle.fuel_log_ids.mapped('total_amount'))
            if total_cost > 0:
                vehicle.profitability = (total_revenue - total_cost) / total_cost * 100
            else:
                vehicle.profitability = 0
            
    def action_schedule_maintenance(self):
        # Action to schedule maintenance
        pass
        
    def action_create_reservation(self):
        # Action to create new reservation
        pass
        
    def action_view_documents(self):
        # Action to view related documents
        pass
        
    def action_report_analytics(self):
        # Action to generate analytics report
        pass

    @api.depends('maintenance_log_ids')
    def _compute_service_count(self):
        for vehicle in self:
            vehicle.service_count = len(vehicle.maintenance_log_ids)

    @api.depends('maintenance_log_ids', 'next_maintenance_date')
    def _compute_service_activity(self):
        today = fields.Date.today()
        for vehicle in self:
            if not vehicle.next_maintenance_date:
                vehicle.service_activity = 'none'
                continue

            if vehicle.next_maintenance_date < today:
                vehicle.service_activity = 'overdue'
            elif vehicle.next_maintenance_date == today:
                vehicle.service_activity = 'today'
            else:
                vehicle.service_activity = 'planned'

    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        xml_id = self._context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window']._for_xml_id('fleet_advanced_management.' + xml_id)
            res.update(context=dict(self.env.context, default_vehicle_id=self.id, group_by=False))
            return res
        return False
