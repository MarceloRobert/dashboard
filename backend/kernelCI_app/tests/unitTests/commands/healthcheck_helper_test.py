from django.test import SimpleTestCase, override_settings
from unittest.mock import Mock, patch

from kernelCI_app.management.commands.helpers.healthcheck import (
    run_with_healthcheck_monitoring,
)


@override_settings(
    HEALTHCHECK_MONITORING_URLS={
        "job-1": "private-token",
        "job-2": "https://example.com/ping/job-2",
    }
)
class TestRunWithHealthcheckMonitoring(SimpleTestCase):
    @patch("kernelCI_app.management.commands.helpers.healthcheck.requests.get")
    def test_success_path_pings_start_and_success(self, mock_get):
        response = Mock()
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        result = run_with_healthcheck_monitoring(
            monitoring_id="job-1", action=lambda: "ok"
        )

        assert result == "ok"
        assert mock_get.call_count == 2
        mock_get.assert_any_call("https://hc-ping.com/private-token/start", timeout=10)
        mock_get.assert_any_call(
            "https://hc-ping.com/private-token/success", timeout=10
        )

    @patch("kernelCI_app.management.commands.helpers.healthcheck.requests.get")
    def test_failure_path_pings_start_and_fail(self, mock_get):
        response = Mock()
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        with self.assertRaisesRegex(RuntimeError, "boom"):
            run_with_healthcheck_monitoring(
                monitoring_id="job-1",
                action=lambda: (_ for _ in ()).throw(RuntimeError("boom")),
            )

        assert mock_get.call_count == 2
        mock_get.assert_any_call("https://hc-ping.com/private-token/start", timeout=10)
        mock_get.assert_any_call("https://hc-ping.com/private-token/fail", timeout=10)

    @patch("kernelCI_app.management.commands.helpers.healthcheck.requests.get")
    def test_no_monitoring_id_skips_pings(self, mock_get):
        result = run_with_healthcheck_monitoring(monitoring_id=None, action=lambda: 42)

        assert result == 42
        mock_get.assert_not_called()

    @patch("kernelCI_app.management.commands.helpers.healthcheck.requests.get")
    def test_unknown_monitoring_id_skips_network_and_runs_action(self, mock_get):
        result = run_with_healthcheck_monitoring(
            monitoring_id="missing-id", action=lambda: "ran"
        )

        assert result == "ran"
        mock_get.assert_not_called()

    @patch("kernelCI_app.management.commands.helpers.healthcheck.requests.get")
    def test_full_url_monitoring_value_is_supported(self, mock_get):
        response = Mock()
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        run_with_healthcheck_monitoring(monitoring_id="job-2", action=lambda: None)

        mock_get.assert_any_call("https://example.com/ping/job-2/start", timeout=10)
        mock_get.assert_any_call("https://example.com/ping/job-2/success", timeout=10)
