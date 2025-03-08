# Fleet Management System for Odoo

## Overview
This project consists of two complementary Odoo modules that provide a comprehensive fleet management solution:
1. `fleet_advanced_management`: Core fleet management functionality
2. `fleet_dashboard`: Advanced analytics and KPI tracking

## Modules

### Fleet Advanced Management
The core module provides comprehensive fleet management capabilities including:
- Vehicle Management
- Driver Management
- Fuel Expense Tracking
- Maintenance Planning
- Document Management
- Reservation System
- Cost Analysis

### Fleet Dashboard
The dashboard module extends the core functionality with:
- Real-time Analytics Dashboard
- KPI Tracking System
- Interactive Charts and Graphs
- Performance Metrics
- Document Expiry Tracking
- Financial Analysis Tools

## Installation

### Prerequisites
- Odoo 16.0 or later
- Python 3.8+
- PostgreSQL 12+

### Installation Steps
1. Clone this repository into your Odoo addons directory:
```bash
cd /path/to/odoo/addons
git clone https://github.com/your-repository/gestion_fleet.git
```

2. Update your Odoo configuration file (`odoo.conf`) to include the path to these modules:
```
addons_path = /path/to/odoo/addons,/path/to/odoo/addons/gestion_fleet
```

3. Restart your Odoo server:
```bash
service odoo restart
```

4. Install the modules through Odoo's interface:
   - Go to Apps
   - Remove the 'Apps' filter and search for:
     - "Fleet Advanced Management"
     - "Fleet Dashboard"
   - Install both modules

## Configuration

### Initial Setup
1. **Security Groups**
   - Fleet User: Basic access to fleet operations
   - Fleet Manager: Full access to all features
   - Fleet Dashboard User: Access to dashboards
   - Fleet Dashboard Manager: KPI configuration rights

2. **Master Data**
   - Configure vehicle types and categories
   - Set up driver profiles
   - Define maintenance schedules
   - Configure expense categories
   - Set up document types

3. **Dashboard Configuration**
   - Configure KPIs and targets
   - Customize dashboard layouts
   - Set up alert thresholds

## Features

### Vehicle Management
- Complete vehicle lifecycle management
- Maintenance scheduling and tracking
- Fuel consumption monitoring
- Cost tracking and analysis
- Document management

### Driver Management
- Driver profiles and documentation
- License tracking and renewal alerts
- Performance monitoring
- Schedule management

### Maintenance
- Preventive maintenance scheduling
- Repair tracking
- Service history
- Cost analysis
- Vendor management

### Reservations
- Vehicle booking system
- Calendar integration
- Conflict prevention
- Usage tracking
- Cost allocation

### Document Management
- Document storage and tracking
- Expiry notifications
- Renewal management
- Digital document archive

### Analytics & Reporting
- Comprehensive dashboards
- KPI tracking
- Cost analysis
- Performance metrics
- Custom report generation

## Usage

### Basic Operations
1. **Vehicle Management**
   ```
   Fleet Management > Vehicles > Vehicles
   ```
   - Add new vehicles
   - Track vehicle status
   - Monitor costs

2. **Driver Management**
   ```
   Fleet Management > Drivers > Drivers
   ```
   - Manage driver profiles
   - Track assignments
   - Monitor performance

3. **Maintenance**
   ```
   Fleet Management > Operations > Maintenance
   ```
   - Schedule services
   - Track repairs
   - Monitor costs

4. **Reservations**
   ```
   Fleet Management > Operations > Reservations
   ```
   - Book vehicles
   - Manage schedules
   - Track usage

### Dashboard Operations
1. **Main Dashboard**
   ```
   Fleet Dashboard > Dashboards
   ```
   - View overall fleet status
   - Monitor key metrics
   - Track performance

2. **KPI Dashboard**
   ```
   Fleet Dashboard > KPI Dashboard
   ```
   - Configure KPIs
   - Set targets
   - Monitor trends

## Development

### Module Structure
```
gestion_fleet/
├── README.md
├── fleet_advanced_management/
│   ├── README.md
│   ├── models/
│   │   ├── fleet_vehicle.py
│   │   ├── fleet_driver.py
│   │   ├── fleet_maintenance.py
│   │   ├── fleet_reservation.py
│   │   ├── fleet_expense.py
│   │   └── fleet_document.py
│   ├── views/
│   │   ├── fleet_vehicle_views.xml
│   │   ├── fleet_driver_views.xml
│   │   └── ...
│   └── security/
│       ├── ir.model.access.csv
│       └── fleet_security.xml
└── fleet_dashboard/
    ├── README.md
    ├── models/
    │   ├── fleet_dashboard.py
    │   └── fleet_kpi.py
    ├── static/
    │   └── src/
    │       ├── js/
    │       ├── css/
    │       └── xml/
    └── views/
        ├── dashboard_views.xml
        └── kpi_dashboard_views.xml
│       ├── css/
│       └── xml/
└── views/
    ├── dashboard_views.xml
    └── kpi_dashboard_views.xml
```

### Extending the Modules
- Follow Odoo's inheritance mechanisms
- Use proper dependency management
- Maintain security configurations
- Follow coding standards

## Support
For support and bug reports, please create an issue in the repository or contact:
- Email: support@yourcompany.com
- Website: https://www.yourcompany.com

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under LGPL-3 - see the LICENSE file for details.

## Authors
- Your Company Name
- Contributors list

## Acknowledgments
- Odoo Community
- Contributors
- Users providing feedback
