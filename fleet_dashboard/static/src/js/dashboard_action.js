odoo.define('fleet_dashboard.dashboard_action', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
    var session = require('web.session');

    var FleetDashboardAction = AbstractAction.extend({
        template: 'FleetDashboardMain',
        events: {
            'click .o_fleet_dashboard_action': '_onDashboardActionClick',
            'click .o_refresh_dashboard': '_onRefreshDashboard',
        },

        init: function(parent, action) {
            this._super.apply(this, arguments);
            this.dashboardData = {};
            this.datetime = luxon.DateTime;
        },

        willStart: function() {
            var self = this;
            return this._super.apply(this, arguments).then(function() {
                return self._fetchDashboardData();
            });
        },

        start: function() {
            var self = this;
            return this._super.apply(this, arguments).then(function() {
                self._renderCharts();
            });
        },

        _fetchDashboardData: function() {
            var self = this;
            return rpc.query({
                model: 'fleet.dashboard',
                method: 'get_dashboard_data',
                args: [],
            }).then(function(result) {
                self.dashboardData = result;
            });
        },

        _renderCharts: function() {
            if (!this.dashboardData) return;

            // Vehicle Status Chart
            var vehicleCtx = this.$('.o_vehicle_status_chart')[0].getContext('2d');
            new Chart(vehicleCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Available', 'In Maintenance', 'Reserved'],
                    datasets: [{
                        data: [
                            this.dashboardData.available_vehicles,
                            this.dashboardData.in_maintenance_vehicles,
                            this.dashboardData.reserved_vehicles
                        ],
                        backgroundColor: ['#28a745', '#ffc107', '#17a2b8']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });

            // Monthly Revenue Chart
            var revenueCtx = this.$('.o_monthly_revenue_chart')[0].getContext('2d');
            new Chart(revenueCtx, {
                type: 'line',
                data: {
                    labels: this.dashboardData.revenue_labels,
                    datasets: [{
                        label: 'Revenue',
                        data: this.dashboardData.revenue_data,
                        borderColor: '#007bff',
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

            // Fuel Consumption Chart
            var fuelCtx = this.$('.o_fuel_consumption_chart')[0].getContext('2d');
            new Chart(fuelCtx, {
                type: 'bar',
                data: {
                    labels: this.dashboardData.fuel_labels,
                    datasets: [{
                        label: 'Consumption (L)',
                        data: this.dashboardData.fuel_data,
                        backgroundColor: '#20c997'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

            // Maintenance Cost Chart
            var maintenanceCtx = this.$('.o_maintenance_cost_chart')[0].getContext('2d');
            new Chart(maintenanceCtx, {
                type: 'bar',
                data: {
                    labels: this.dashboardData.maintenance_labels,
                    datasets: [{
                        label: 'Cost',
                        data: this.dashboardData.maintenance_data,
                        backgroundColor: '#fd7e14'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        },

        _onDashboardActionClick: function(ev) {
            ev.preventDefault();
            var $action = $(ev.currentTarget);
            var actionName = $action.attr('name');
            var actionData = $action.data();
            
            this.do_action(actionName, {
                additional_context: actionData
            });
        },

        _onRefreshDashboard: function(ev) {
            ev.preventDefault();
            this._fetchDashboardData().then(this._renderCharts.bind(this));
        },
    });

    core.action_registry.add('fleet_dashboard.main', FleetDashboardAction);

    return FleetDashboardAction;
});
