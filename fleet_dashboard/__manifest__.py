{
    'name': 'Fleet Dashboard',
    'version': '1.0',
    'category': 'Operations/Fleet',
    'summary': 'Advanced dashboards for fleet management',
    'description': """
        Fleet Management Dashboard Module including:
        * Vehicle Status Overview
        * Maintenance Analytics
        * Fuel Consumption Analysis
        * Cost Analysis Dashboard
        * Driver Performance Metrics
        * Reservation Calendar
        * Document Expiry Tracking
        * Interactive KPI Dashboard
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'web',
        'fleet_advanced_management',
        'board',
    ],
    'data': [
        'security/dashboard_security.xml',
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
        'views/fleet_dashboard_views.xml',
        'views/kpi_dashboard_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'fleet_dashboard/static/src/js/dashboard_action.js',
            'fleet_dashboard/static/src/js/kpi_dashboard.js',
            'fleet_dashboard/static/src/xml/dashboard_templates.xml',
            'fleet_dashboard/static/src/css/dashboard.css',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
