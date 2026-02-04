import pytest
from unittest.mock import patch, MagicMock

# Import the functions and classes to be tested
from core.monitoring.monitor import AMPMonitor, get_system_status, generate_report, display_dashboard

class TestAMPMonitor:
    """Tests for the AMPMonitor class and related functions"""

    @pytest.fixture
    def monitor(self):
        """Fixture to create an AMPMonitor instance for testing"""
        with patch('core.monitoring.monitor.Path.mkdir'):
            monitor = AMPMonitor()
        return monitor

    def test_initialization(self, monitor):
        """Test that the AMPMonitor class initializes correctly"""
        assert monitor is not None
        assert monitor.config is not None
        assert "refresh_interval" in monitor.config

    def test_get_system_status_structure(self, monitor):
        """Test the structure of the dictionary returned by get_system_status"""
        with patch('core.monitoring.monitor.check_auth', return_value=True), \
             patch('core.monitoring.monitor.get_user_info', return_value={'user_id': 'testuser'}), \
             patch('core.monitoring.monitor.get_scheduler_status', return_value={'is_running': True}), \
             patch.object(monitor, 'get_job_status', return_value={'total_jobs': 0}), \
             patch.object(monitor, 'get_performance_metrics', return_value={'uptime_seconds': 100}):

            status = monitor.get_system_status()

            assert "timestamp" in status
            assert "authentication" in status
            assert "scheduler" in status
            assert "jobs" in status
            assert "performance" in status
            assert "alerts" in status

    def test_alert_generation(self, monitor):
        """Test that alerts are generated correctly based on system status"""
        # Scenario 1: No alerts
        with patch('core.monitoring.monitor.check_auth', return_value=True), \
             patch('core.monitoring.monitor.get_scheduler_status', return_value={'is_running': True}), \
             patch.object(monitor, 'get_job_status', return_value={'success_rate': 100.0, 'total_jobs': 10}):

            alerts = monitor.get_active_alerts()
            assert len(alerts) == 0

        # Scenario 2: Authentication alert
        with patch('core.monitoring.monitor.check_auth', return_value=False):
            alerts = monitor.get_active_alerts()
            assert len(alerts) > 0
            assert any("User not authenticated" in alert['message'] for alert in alerts)

        # Scenario 3: Scheduler alert
        with patch('core.monitoring.monitor.check_auth', return_value=True), \
             patch('core.monitoring.monitor.get_scheduler_status', return_value={'is_running': False}):
            alerts = monitor.get_active_alerts()
            assert len(alerts) > 0
            assert any("Scheduler not running" in alert['message'] for alert in alerts)