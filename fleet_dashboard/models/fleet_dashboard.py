from odoo import models, fields, api, _
from datetime import datetime, timedelta

class FleetDashboard(models.Model):
    _name = 'fleet.dashboard'
    _description = 'Fleet Dashboard'

    name = fields.Char(string='Name', required=True)
    date = fields.Date(string='Date', default=fields.Date.context_today)
    
    # Vehicle Statistics
    total_vehicles = fields.Integer(string='Total Vehicles', compute='_compute_vehicle_stats')
    available_vehicles = fields.Integer(string='Available Vehicles', compute='_compute_vehicle_stats')
    in_maintenance_vehicles = fields.Integer(string='Vehicles in Maintenance', compute='_compute_vehicle_stats')
    reserved_vehicles = fields.Integer(string='Reserved Vehicles', compute='_compute_vehicle_stats')
    
    # Maintenance Statistics
    pending_maintenance = fields.Integer(string='Pending Maintenance', compute='_compute_maintenance_stats')
    ongoing_maintenance = fields.Integer(string='Ongoing Maintenance', compute='_compute_maintenance_stats')
    maintenance_cost_mtd = fields.Float(string='Maintenance Cost MTD', compute='_compute_maintenance_stats')
    maintenance_cost_ytd = fields.Float(string='Maintenance Cost YTD', compute='_compute_maintenance_stats')
    
    # Fuel Statistics
    fuel_consumption_mtd = fields.Float(string='Fuel Consumption MTD (L)', compute='_compute_fuel_stats')
    fuel_cost_mtd = fields.Float(string='Fuel Cost MTD', compute='_compute_fuel_stats')
    avg_fuel_efficiency = fields.Float(string='Average Fuel Efficiency (L/100km)', compute='_compute_fuel_stats')
    total_fuel_cost_ytd = fields.Float(string='Total Fuel Cost YTD', compute='_compute_fuel_stats')
    
    # Driver Statistics
    total_drivers = fields.Integer(string='Total Drivers', compute='_compute_driver_stats')
    available_drivers = fields.Integer(string='Available Drivers', compute='_compute_driver_stats')
    on_duty_drivers = fields.Integer(string='On Duty Drivers', compute='_compute_driver_stats')
    off_duty_drivers = fields.Integer(string='Off Duty Drivers', compute='_compute_driver_stats')
    
    # Reservation Statistics
    active_reservations = fields.Integer(string='Active Reservations', compute='_compute_reservation_stats')
    upcoming_reservations = fields.Integer(string='Upcoming Reservations', compute='_compute_reservation_stats')
    completed_reservations_mtd = fields.Integer(string='Completed Reservations MTD', compute='_compute_reservation_stats')
    reservation_revenue_mtd = fields.Float(string='Reservation Revenue MTD', compute='_compute_reservation_stats')
    
    # Document Statistics
    expiring_documents = fields.Integer(string='Expiring Documents', compute='_compute_document_stats')
    expired_documents = fields.Integer(string='Expired Documents', compute='_compute_document_stats')
    documents_expiring_soon = fields.Integer(string='Documents Expiring Soon', compute='_compute_document_stats')
    
    # Financial Statistics
    total_revenue_mtd = fields.Float(string='Total Revenue MTD', compute='_compute_financial_stats')
    total_expenses_mtd = fields.Float(string='Total Expenses MTD', compute='_compute_financial_stats')
    profit_mtd = fields.Float(string='Profit MTD', compute='_compute_financial_stats')
    profit_margin = fields.Float(string='Profit Margin (%)', compute='_compute_financial_stats')

    @api.depends('date')
    def _compute_vehicle_stats(self):
        for record in self:
            vehicles = self.env['fleet.vehicle'].search([])
            record.total_vehicles = len(vehicles)
            record.available_vehicles = len(vehicles.filtered(lambda v: v.is_available))
            record.in_maintenance_vehicles = len(vehicles.filtered(lambda v: not v.is_available and v.maintenance_log_ids.filtered(lambda m: m.state == 'in_progress')))
            record.reserved_vehicles = len(vehicles.filtered(lambda v: not v.is_available and v.reservation_ids.filtered(lambda r: r.state in ['confirmed', 'ongoing'])))

    @api.depends('date')
    def _compute_maintenance_stats(self):
        for record in self:
            start_of_month = record.date.replace(day=1)
            start_of_year = record.date.replace(month=1, day=1)
            
            maintenances = self.env['fleet.vehicle.maintenance'].search([])
            record.pending_maintenance = len(maintenances.filtered(lambda m: m.state == 'draft'))
            record.ongoing_maintenance = len(maintenances.filtered(lambda m: m.state == 'in_progress'))
            
            mtd_maintenances = maintenances.filtered(lambda m: m.date >= start_of_month and m.state == 'done')
            ytd_maintenances = maintenances.filtered(lambda m: m.date >= start_of_year and m.state == 'done')
            
            record.maintenance_cost_mtd = sum(mtd_maintenances.mapped('total_cost'))
            record.maintenance_cost_ytd = sum(ytd_maintenances.mapped('total_cost'))

    @api.depends('date')
    def _compute_fuel_stats(self):
        for record in self:
            start_of_month = record.date.replace(day=1)
            start_of_year = record.date.replace(month=1, day=1)
            
            fuel_logs = self.env['fleet.expense'].search([
                ('expense_type', '=', 'fuel'),
                ('date', '>=', start_of_month)
            ])
            
            record.fuel_consumption_mtd = sum(fuel_logs.mapped('liters'))
            record.fuel_cost_mtd = sum(fuel_logs.mapped('amount'))
            
            if record.fuel_consumption_mtd > 0:
                total_distance = sum(fuel_logs.mapped('vehicle_id.odometer_log_ids').filtered(lambda o: o.date >= start_of_month).mapped('distance'))
                record.avg_fuel_efficiency = (record.fuel_consumption_mtd / total_distance * 100) if total_distance else 0
            
            ytd_fuel_logs = self.env['fleet.expense'].search([
                ('expense_type', '=', 'fuel'),
                ('date', '>=', start_of_year)
            ])
            record.total_fuel_cost_ytd = sum(ytd_fuel_logs.mapped('amount'))

    @api.depends('date')
    def _compute_driver_stats(self):
        for record in self:
            drivers = self.env['fleet.driver'].search([])
            record.total_drivers = len(drivers)
            record.available_drivers = len(drivers.filtered(lambda d: d.state == 'available'))
            record.on_duty_drivers = len(drivers.filtered(lambda d: d.state == 'driving'))
            record.off_duty_drivers = len(drivers.filtered(lambda d: d.state in ['off_duty', 'leave']))

    @api.depends('date')
    def _compute_reservation_stats(self):
        for record in self:
            start_of_month = record.date.replace(day=1)
            reservations = self.env['fleet.vehicle.reservation'].search([])
            
            record.active_reservations = len(reservations.filtered(lambda r: r.state == 'ongoing'))
            record.upcoming_reservations = len(reservations.filtered(lambda r: r.state == 'confirmed' and r.start_date > fields.Datetime.now()))
            
            completed_reservations = reservations.filtered(lambda r: r.state == 'completed' and r.end_date >= start_of_month)
            record.completed_reservations_mtd = len(completed_reservations)
            record.reservation_revenue_mtd = sum(completed_reservations.mapped('revenue'))

    @api.depends('date')
    def _compute_document_stats(self):
        for record in self:
            today = fields.Date.today()
            next_month = today + timedelta(days=30)
            
            documents = self.env['fleet.vehicle.document'].search([])
            record.expired_documents = len(documents.filtered(lambda d: d.state == 'expired'))
            record.documents_expiring_soon = len(documents.filtered(lambda d: d.state == 'valid' and d.expiry_date and d.expiry_date <= next_month))
            record.expiring_documents = record.expired_documents + record.documents_expiring_soon

    @api.depends('date')
    def _compute_financial_stats(self):
        for record in self:
            start_of_month = record.date.replace(day=1)
            
            expenses = self.env['fleet.expense'].search([('date', '>=', start_of_month)])
            reservations = self.env['fleet.vehicle.reservation'].search([
                ('state', '=', 'completed'),
                ('end_date', '>=', start_of_month)
            ])
            
            record.total_expenses_mtd = sum(expenses.mapped('amount'))
            record.total_revenue_mtd = sum(reservations.mapped('revenue'))
            record.profit_mtd = record.total_revenue_mtd - record.total_expenses_mtd
            record.profit_margin = (record.profit_mtd / record.total_revenue_mtd * 100) if record.total_revenue_mtd else 0

    def action_view_vehicles(self):
        return {
            'name': _('Vehicles'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle',
            'view_mode': 'kanban,tree,form',
            'context': {'search_default_available': True},
        }

    def action_view_maintenance(self):
        return {
            'name': _('Maintenance'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle.maintenance',
            'view_mode': 'tree,form,calendar',
            'context': {'search_default_ongoing': True},
        }

    def action_view_reservations(self):
        return {
            'name': _('Reservations'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle.reservation',
            'view_mode': 'calendar,tree,form',
            'context': {'search_default_upcoming': True},
        }

    def action_view_documents(self):
        return {
            'name': _('Documents'),
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle.document',
            'view_mode': 'tree,form',
            'context': {'search_default_expiring_soon': True},
        }
