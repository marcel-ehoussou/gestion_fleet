from odoo import models, fields, api, _
from datetime import datetime, timedelta

class FleetKPI(models.Model):
    _name = 'fleet.kpi'
    _description = 'Fleet KPI Metrics'
    _order = 'sequence, id'

    name = fields.Char(string='KPI Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    category = fields.Selection([
        ('vehicle', 'Vehicle'),
        ('maintenance', 'Maintenance'),
        ('fuel', 'Fuel'),
        ('driver', 'Driver'),
        ('reservation', 'Reservation'),
        ('financial', 'Financial'),
    ], string='Category', required=True)
    
    calculation_type = fields.Selection([
        ('count', 'Count'),
        ('sum', 'Sum'),
        ('average', 'Average'),
        ('percentage', 'Percentage'),
    ], string='Calculation Type', required=True)
    
    model_id = fields.Many2one('ir.model', string='Model')
    field_id = fields.Many2one('ir.model.fields', string='Field')
    domain = fields.Char(string='Domain')
    
    value_type = fields.Selection([
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('monetary', 'Monetary'),
        ('percentage', 'Percentage'),
    ], string='Value Type', required=True)
    
    target_value = fields.Float(string='Target Value')
    warning_threshold = fields.Float(string='Warning Threshold (%)')
    critical_threshold = fields.Float(string='Critical Threshold (%)')
    
    current_value = fields.Float(string='Current Value', compute='_compute_current_value')
    previous_value = fields.Float(string='Previous Value', compute='_compute_current_value')
    trend = fields.Float(string='Trend (%)', compute='_compute_current_value')
    status = fields.Selection([
        ('good', 'Good'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ], string='Status', compute='_compute_current_value')
    
    time_range = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ], string='Time Range', required=True, default='monthly')
    
    display_graph = fields.Boolean(string='Display Graph', default=True)
    graph_type = fields.Selection([
        ('line', 'Line'),
        ('bar', 'Bar'),
        ('pie', 'Pie'),
    ], string='Graph Type', default='line')
    
    color = fields.Char(string='Color', default='#2196F3')
    icon = fields.Char(string='Icon', default='fa fa-chart-line')
    
    @api.depends('model_id', 'field_id', 'domain', 'calculation_type', 'time_range', 'target_value')
    def _compute_current_value(self):
        for kpi in self:
            current_value = 0.0
            previous_value = 0.0
            
            if kpi.model_id and kpi.field_id:
                Model = self.env[kpi.model_id.model]
                field_name = kpi.field_id.name
                domain = eval(kpi.domain) if kpi.domain else []
                
                # Calculate date ranges
                today = fields.Date.today()
                if kpi.time_range == 'daily':
                    current_start = today
                    previous_start = today - timedelta(days=1)
                elif kpi.time_range == 'weekly':
                    current_start = today - timedelta(days=today.weekday())
                    previous_start = current_start - timedelta(weeks=1)
                elif kpi.time_range == 'monthly':
                    current_start = today.replace(day=1)
                    previous_start = (current_start - timedelta(days=1)).replace(day=1)
                else:  # yearly
                    current_start = today.replace(month=1, day=1)
                    previous_start = current_start.replace(year=current_start.year-1)
                
                # Current period calculation
                current_domain = domain + [('create_date', '>=', current_start)]
                current_records = Model.search(current_domain)
                
                if kpi.calculation_type == 'count':
                    current_value = len(current_records)
                elif kpi.calculation_type == 'sum':
                    current_value = sum(current_records.mapped(field_name))
                elif kpi.calculation_type == 'average':
                    values = current_records.mapped(field_name)
                    current_value = sum(values) / len(values) if values else 0
                elif kpi.calculation_type == 'percentage':
                    total_records = len(Model.search(domain))
                    current_value = (len(current_records) / total_records * 100) if total_records else 0
                
                # Previous period calculation
                previous_domain = domain + [
                    ('create_date', '>=', previous_start),
                    ('create_date', '<', current_start)
                ]
                previous_records = Model.search(previous_domain)
                
                if kpi.calculation_type == 'count':
                    previous_value = len(previous_records)
                elif kpi.calculation_type == 'sum':
                    previous_value = sum(previous_records.mapped(field_name))
                elif kpi.calculation_type == 'average':
                    values = previous_records.mapped(field_name)
                    previous_value = sum(values) / len(values) if values else 0
                elif kpi.calculation_type == 'percentage':
                    total_records = len(Model.search(domain))
                    previous_value = (len(previous_records) / total_records * 100) if total_records else 0
            
            kpi.current_value = current_value
            kpi.previous_value = previous_value
            
            # Calculate trend
            if previous_value:
                kpi.trend = ((current_value - previous_value) / previous_value) * 100
            else:
                kpi.trend = 0
            
            # Calculate status
            if kpi.target_value:
                achievement = (current_value / kpi.target_value) * 100
                if achievement >= kpi.critical_threshold:
                    kpi.status = 'critical'
                elif achievement >= kpi.warning_threshold:
                    kpi.status = 'warning'
                else:
                    kpi.status = 'good'
            else:
                kpi.status = 'good'

    def action_view_details(self):
        self.ensure_one()
        return {
            'name': _('KPI Details'),
            'type': 'ir.actions.act_window',
            'res_model': self.model_id.model,
            'view_mode': 'graph,pivot,tree',
            'domain': self.domain,
            'context': {
                'group_by': 'create_date:' + self.time_range,
            },
        }
