from __future__ import annotations

import inspect

from automation.forex_engine import forex_trust_safety_audit_v1
from automation.forex_engine import long_only_demo_readiness_orchestrator_v1
from automation.forex_engine import long_only_profitability_evidence_depth_gate_v1
from automation.forex_engine import long_only_risk_policy_contract_v1
from automation.forex_engine import long_only_supervisor_broker_proof_adapter_v1
from automation.forex_engine import oanda_long_only_order_intent_preview_v1


def test_demo_readiness_trust_spine_has_no_forbidden_runtime_apis():
    modules = (
        forex_trust_safety_audit_v1,
        long_only_demo_readiness_orchestrator_v1,
        long_only_profitability_evidence_depth_gate_v1,
        long_only_risk_policy_contract_v1,
        long_only_supervisor_broker_proof_adapter_v1,
        oanda_long_only_order_intent_preview_v1,
    )
    forbidden_tokens = (
        "import requests",
        "from requests",
        "import httpx",
        "from httpx",
        "import urllib",
        "from urllib",
        "import socket",
        "from socket",
        "import websockets",
        "from websockets",
        "oandapy",
        "dotenv",
        "keyring",
        "os.environ",
        "getenv(",
        "subprocess",
        "threading",
        "BackgroundScheduler",
        "open(",
        "read_text(",
        "write_text(",
    )
    for module in modules:
        source = inspect.getsource(module)
        for token in forbidden_tokens:
            assert token not in source
