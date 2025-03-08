# Fleet Dashboard Module

## Overview
The Fleet Dashboard module provides advanced analytics and real-time monitoring capabilities for the Fleet Management system. It offers interactive dashboards, KPI tracking, and comprehensive reporting tools.

## Features

### Main Dashboard
- **Vehicle Status Overview**
  - Total fleet count
  - Available vehicles
  - Vehicles in maintenance
  - Reserved vehicles
  - Interactive status charts

- **Financial Analytics**
  - Revenue tracking (MTD/YTD)
  - Cost analysis
  - Profit margins
  - Trend visualization

- **Maintenance Metrics**
  - Pending maintenance
  - Ongoing services
  - Cost tracking
  - Service history charts

- **Fuel Analytics**
  - Consumption trends
  - Cost analysis
  - Efficiency metrics
  - Comparative charts

### KPI Dashboard
- **Customizable KPIs**
  - Define custom metrics
  - Set targets
  - Configure thresholds
  - Track trends

- **Performance Categories**
  - Vehicle metrics
  - Driver performance
  - Maintenance efficiency
  - Financial indicators
  - Operational metrics

- **Visualization Options**
  - Line charts
  - Bar graphs
  - Pie charts
  - Trend indicators
  - Status badges

## Technical Details

### Dependencies
- base
- web
- fleet_advanced_management
- board

### Installation
1. Ensure you have cloned the complete gestion_fleet project:
   ```bash
   cd /path/to/odoo/addons
   git clone https://github.com/your-repository/gestion_fleet.git
   ```

2. Update your Odoo configuration:
   ```
   addons_path = /path/to/odoo/addons,/path/to/odoo/addons/gestion_fleet
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Restart Odoo server:
   ```bash
   service odoo restart
   ```

5. Install the modules through Odoo's interface:
   - First install `fleet_advanced_management`
   - Then install this module (`fleet_dashboard`)

### Configuration

#### Security Groups
- **Fleet Dashboard User**
  - View dashboards
  - Access reports
  - View KPIs

- **Fleet Dashboard Manager**
  - Configure dashboards
  - Manage KPIs
  - Set targets
  - Define thresholds

#### KPI Setup
1. Go to `Fleet Dashboard > KPI Dashboard`
2. Click "Create" to add new KPIs
3. Configure:
   - Metric name
   - Calculation method
   - Target values
   - Warning thresholds
   - Display options

### Module Structure
```
gestion_fleet/                  # Project root directory
└── fleet_dashboard/            # Dashboard module
    ├── README.md               # Module documentation
    ├── __init__.py             # Module entry point
    ├── __manifest__.py          # Module descriptor
    ├── models/                 # Data models
    │   ├── __init__.py
    │   ├── fleet_dashboard.py    # Main dashboard logic
    │   └── fleet_kpi.py         # KPI configuration
    ├── views/                  # UI definitions
    │   ├── dashboard_views.xml   # Dashboard layouts
    │   └── kpi_dashboard_views.xml  # KPI interfaces
    ├── static/                 # Static assets
    │   └── src/
    │       ├── js/                # JavaScript files
    │       │   ├── dashboard_action.js  # Dashboard logic
    │       │   └── kpi_dashboard.js     # KPI handling
    │       ├── css/              # Stylesheets
    │       │   └── dashboard.css        # Custom styles
    │       └── xml/              # QWeb templates
    │           └── dashboard_templates.xml
    └── security/               # Access control
        ├── dashboard_security.xml  # Security rules
        └── ir.model.access.csv    # Access rights
```

### Development Notes

#### Adding New KPIs
1. Define the KPI model in `fleet_kpi.py`
2. Add computation methods
3. Create corresponding views
4. Update security settings

#### Customizing Dashboards
1. Modify QWeb templates in `dashboard_templates.xml`
2. Update JavaScript handlers in `dashboard_action.js`
3. Adjust styling in `dashboard.css`

#### Best Practices
- Use proper Odoo inheritance
- Follow SOLID principles
- Maintain security configurations
- Document code changes
- Write unit tests

## Usage Guide

### Accessing Dashboards
1. Navigate to `Fleet Dashboard > Dashboards`
2. Select desired dashboard view
3. Use filters to refine data
4. Export reports as needed

### Managing KPIs
1. Go to `Fleet Dashboard > KPI Dashboard`
2. Create or modify KPIs
3. Set targets and thresholds
4. Monitor performance

### Customizing Views
1. Access dashboard configuration
2. Arrange widgets as needed
3. Select relevant metrics
4. Save layout preferences

## Troubleshooting

### Common Issues
1. **Dashboard Not Loading**
   - Check browser console
   - Verify JavaScript loading
   - Clear browser cache

2. **KPI Calculation Errors**
   - Verify data sources
   - Check computation methods
   - Review error logs

3. **Performance Issues**
   - Optimize database queries
   - Check server resources
   - Review client-side rendering

## Support
For technical support:
- Create issue in repository
- Contact development team
- Check documentation

## Contributing
1. Review coding standards
2. Test thoroughly
3. Document changes
4. Submit pull request

## License
LGPL-3
