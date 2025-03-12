from odoo import models, fields, api, _

class FleetDriverPerformanceReport(models.TransientModel):
    _name = 'fleet.driver.performance.report'
    _description = 'Driver Performance Report'

    driver_id = fields.Many2one('fleet.driver', string='Driver', required=True)
    date = fields.Date(string='Report Date', default=fields.Date.today)
    
    # Performance Metrics
    performance_score = fields.Float(string='Overall Performance Score')
    total_distance = fields.Float(string='Total Distance Driven (km)')
    fuel_efficiency = fields.Float(string='Fuel Efficiency Rating')
    accident_count = fields.Integer(string='Number of Accidents')
    revenue = fields.Float(string='Revenue Generated')
    
    # Detailed Analysis
    strengths = fields.Text(string='Strengths', compute='_compute_analysis')
    areas_for_improvement = fields.Text(string='Areas for Improvement', compute='_compute_analysis')
    recommendations = fields.Text(string='Recommendations', compute='_compute_analysis')
    
    @api.depends('performance_score', 'total_distance', 'fuel_efficiency', 'accident_count', 'revenue')
    def _compute_analysis(self):
        for report in self:
            # Initialize lists for analysis
            strengths = []
            improvements = []
            recommendations = []
            
            # Analyze performance score
            if report.performance_score >= 90:
                strengths.append(_('Exceptional overall performance'))
            elif report.performance_score >= 80:
                strengths.append(_('Very good overall performance'))
            elif report.performance_score < 60:
                improvements.append(_('Overall performance needs improvement'))
                recommendations.append(_('Schedule performance review meeting'))
            
            # Analyze fuel efficiency
            if report.fuel_efficiency >= 8:
                strengths.append(_('Excellent fuel efficiency'))
            elif report.fuel_efficiency < 5:
                improvements.append(_('Fuel efficiency could be improved'))
                recommendations.append(_('Provide eco-driving training'))
            
            # Analyze accidents
            if report.accident_count == 0:
                strengths.append(_('Perfect safety record'))
            elif report.accident_count > 2:
                improvements.append(_('Safety record needs attention'))
                recommendations.append(_('Mandatory safety training required'))
            
            # Analyze revenue
            if report.revenue > 10000:
                strengths.append(_('Strong revenue generation'))
            elif report.revenue < 5000:
                improvements.append(_('Revenue generation below target'))
                recommendations.append(_('Review route optimization'))
            
            # Format the analysis texts
            report.strengths = '\n'.join(['• ' + s for s in strengths]) if strengths else _('No notable strengths identified')
            report.areas_for_improvement = '\n'.join(['• ' + i for i in improvements]) if improvements else _('No major areas requiring improvement')
            report.recommendations = '\n'.join(['• ' + r for r in recommendations]) if recommendations else _('No specific recommendations at this time')
    
    def action_print_report(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.report',
            'report_name': 'fleet_advanced_management.driver_performance_report',
            'report_type': 'qweb-pdf',
            'data': {
                'doc_ids': self.ids,
                'doc_model': 'fleet.driver.performance.report',
            }
        }
