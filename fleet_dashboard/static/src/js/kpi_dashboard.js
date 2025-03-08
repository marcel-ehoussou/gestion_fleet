odoo.define('fleet_dashboard.kpi_dashboard', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
    var session = require('web.session');

    var FleetKPIDashboard = AbstractAction.extend({
        template: 'FleetKPIDashboard',
        events: {
            'click .o_kpi_dashboard_action': '_onKPIActionClick',
            'click .o_refresh_kpis': '_onRefreshKPIs',
        },

        init: function(parent, action) {
            this._super.apply(this, arguments);
            this.kpiData = {};
        },

        willStart: function() {
            var self = this;
            return this._super.apply(this, arguments).then(function() {
                return self._fetchKPIData();
            });
        },

        start: function() {
            var self = this;
            return this._super.apply(this, arguments).then(function() {
                self._renderKPIs();
            });
        },

        _fetchKPIData: function() {
            var self = this;
            return rpc.query({
                model: 'fleet.kpi',
                method: 'get_kpi_data',
                args: [],
            }).then(function(result) {
                self.kpiData = result;
            });
        },

        _renderKPIs: function() {
            var self = this;
            if (!this.kpiData || !this.kpiData.kpis) return;

            _.each(this.kpiData.kpis, function(kpi) {
                if (!kpi.display_graph) return;

                var chartElement = self.$('.o_kpi_chart_' + kpi.id)[0];
                if (!chartElement) return;

                var ctx = chartElement.getContext('2d');
                var chartConfig = self._prepareChartConfig(kpi);
                new Chart(ctx, chartConfig);
            });
        },

        _prepareChartConfig: function(kpi) {
            var config = {
                type: kpi.graph_type || 'line',
                data: {
                    labels: kpi.history_labels || [],
                    datasets: [{
                        label: kpi.name,
                        data: kpi.history_data || [],
                        borderColor: kpi.color || '#007bff',
                        backgroundColor: this._getBackgroundColor(kpi.color),
                        fill: kpi.graph_type === 'area'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },
                    plugins: {
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    }
                }
            };

            if (kpi.graph_type === 'pie' || kpi.graph_type === 'doughnut') {
                config.data.datasets[0].backgroundColor = this._generateColorPalette(kpi.history_data.length);
            }

            return config;
        },

        _getBackgroundColor: function(color) {
            if (!color) return 'rgba(0, 123, 255, 0.1)';
            var rgb = this._hexToRgb(color);
            return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.1)`;
        },

        _hexToRgb: function(hex) {
            var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
            return result ? {
                r: parseInt(result[1], 16),
                g: parseInt(result[2], 16),
                b: parseInt(result[3], 16)
            } : null;
        },

        _generateColorPalette: function(count) {
            var colors = [
                '#007bff', '#28a745', '#ffc107', '#dc3545', '#17a2b8',
                '#6610f2', '#fd7e14', '#20c997', '#e83e8c', '#6f42c1'
            ];
            var palette = [];
            for (var i = 0; i < count; i++) {
                palette.push(colors[i % colors.length]);
            }
            return palette;
        },

        _onKPIActionClick: function(ev) {
            ev.preventDefault();
            var $action = $(ev.currentTarget);
            var actionName = $action.attr('name');
            var actionData = $action.data();
            
            this.do_action(actionName, {
                additional_context: actionData
            });
        },

        _onRefreshKPIs: function(ev) {
            ev.preventDefault();
            this._fetchKPIData().then(this._renderKPIs.bind(this));
        },
    });

    core.action_registry.add('fleet_dashboard.kpi', FleetKPIDashboard);

    return FleetKPIDashboard;
});
