import unittest


def _read_file(path):
    with open(path, 'r', encoding='utf-8') as handle:
        return handle.read()


class ForexDashboardTruthStatusTests(unittest.TestCase):
    def test_orchestrator_status_module_has_display_only_safety(self):
        index_js = _read_file(r'services/orchestrator/index.js')
        truth_js = _read_file(r'services/orchestrator/forexDashboardTruthStatus.js')

        self.assertIn("PAPER_ONLY", index_js)
        self.assertIn("live_trading: false", index_js)
        self.assertIn("real_orders: false", index_js)
        self.assertIn("broker: false", index_js)
        self.assertIn("network_access: false", index_js)
        self.assertIn("GET /api/forex/session-status", index_js)
        self.assertNotIn("router.post('/forex", index_js)
        self.assertIn("module.exports = router", index_js)
        self.assertIn("buildForexDashboardTruthStatus", index_js)
        self.assertIn("display_only", truth_js)
        self.assertIn("paper_only: true", truth_js)

    def test_dashboard_js_is_display_only_projection_only(self):
        dashboard_js = _read_file(r'apps/dashboard/src/MinimalOperatorDashboard.jsx')
        self.assertIn("DISPLAY_ONLY", dashboard_js)
        self.assertIn("NO_RUNTIME_EVIDENCE", dashboard_js)
        self.assertIn("session-status", dashboard_js)
        self.assertIn("next_safe_action", dashboard_js)
        self.assertIn("FETCH", dashboard_js.upper())
        self.assertIn("Paper-only", dashboard_js)

    def test_orchestrator_and_dashboard_have_no_live_or_broker_execution_paths(self):
        index_js = _read_file(r'services/orchestrator/index.js')
        dashboard_js = _read_file(r'apps/dashboard/src/MinimalOperatorDashboard.jsx')
        self.assertNotIn("submit", index_js.lower())
        self.assertNotIn("order_submit", index_js.lower())
        self.assertNotIn("credential", index_js.lower())
        self.assertNotIn("socket", index_js.lower())
        self.assertNotIn("http://", index_js.lower())
        self.assertNotIn("https://", index_js.lower())
        self.assertNotIn("submit", dashboard_js.lower())
        self.assertNotIn("order_submit", dashboard_js.lower())
        self.assertNotIn("credential", dashboard_js.lower())

    def test_source_safety_scan(self):
        paths = [
            r'services/orchestrator/index.js',
            r'services/orchestrator/forexDashboardTruthStatus.js',
            r'services/orchestrator/forexDemoConnectorProofClosure.js',
            r'apps/dashboard/src/MinimalOperatorDashboard.jsx'
        ]
        forbidden = [
            'subprocess',
            'requests',
            'socket',
            'urllib',
            'os.system',
            'pathlib',
            'getenv',
            'environ',
            'account_id',
            'live order',
            'credential',
            'env.'
        ]
        for path in paths:
            source = _read_file(path)
            for token in forbidden:
                self.assertNotIn(token, source)

    def test_truth_projection_shape_tokens(self):
        truth_js = _read_file(r'services/orchestrator/forexDashboardTruthStatus.js')
        self.assertIn("candidates", truth_js)
        self.assertIn("previews", truth_js)
        self.assertIn("risk", truth_js)
        self.assertIn("open_trades", truth_js)
        self.assertIn("closed_trades", truth_js)
        self.assertIn("missing_evidence_warnings", truth_js)
