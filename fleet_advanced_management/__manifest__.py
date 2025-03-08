{
    'name': 'Fleet Advanced Management',
    'version': '1.0',
    'category': 'Operations/Fleet',
    'summary': 'Advanced fleet management system with fuel tracking, maintenance, and driver management',
    'description': """
        Advanced Fleet Management System including:
        * Fuel expense tracking and analysis
        * Repair and maintenance management
        * Other expenses tracking (insurance, technical control, etc.)
        * Driver and vehicle reservation management
        * Mileage tracking
        * Deadline monitoring
        * Revenue tracking
        * Document management
        * Custom alerts and reminders
        * Advanced reporting and dashboard
        * Driver schedule management
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'fleet',
        'hr',
        'account',
        'mail',
    ],
    'data': [
        'security/fleet_security.xml',
        'security/ir.model.access.csv',
        'views/fleet_vehicle_views.xml',
        'views/fleet_driver_views.xml',
        'views/fleet_driver_performance_views.xml',
        'views/fleet_expense_views.xml',
        'views/fleet_maintenance_views.xml',
        'views/fleet_reservation_views.xml',
        'views/fleet_document_views.xml',
        'views/fleet_dashboard_views.xml',
        'views/menu_views.xml',
        'data/fleet_data.xml',
    ],
    'demo': [
        'data/fleet_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
