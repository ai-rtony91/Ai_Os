import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVIEW_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_JUNE30_SLICE4_BROKER_LIVE_BOUNDARY_REVIEW_V1.json"
)
MATRIX_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_JUNE30_SLICE4_BROKER_LIVE_BOUNDARY_MATRIX_V1.json"
)
REPORT_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_JUNE30_SLICE4_BROKER_LIVE_BOUNDARY_REVIEW_V1_REPORT.md"
)
QUEUE_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_JUNE30_SLICE4_BROKER_LIVE_BOUNDARY_QUEUE_V1.md"
)

FINAL_OWNER_SENTENCE = (
    "AIOS Forex Slice 4 is complete for broker/live permission review only: "
    "broker/live boundary items 1750 are classified for permission review, while "
    "broker/API, credentials, account access, demo/live trading, order action, "
    "money movement, production, and autonomy remain blocked."
)

FORBIDDEN_ACTIONS = [
    "broker/API access",
    "credentials",
    "account access",
    "demo trade",
    "live trade",
    "order placement",
    "order closure",
    "money movement",
    "scheduler activation",
    "daemon activation",
    "webhook activation",
    "production activation",
    "autonomous trading",
    "credential persistence",
    "account identifier persistence",
    "raw private evidence",
    "broker connection",
    "live endpoint use",
]

REQUIRED_FUTURE_GATES = [
    "explicit owner approval",
    "broker permission review",
    "sanitized broker-read-only evidence review",
    "credential handling plan",
    "no credential persistence",
    "no account identifier persistence",
    "kill-switch validation",
    "max-loss validation",
    "daily-stop validation",
    "one-order-only rule",
    "micro-size rule",
    "stop-loss required",
    "take-profit required",
    "post-trade evidence capture",
    "final owner decision brief",
]

BANNED_TOKENS = [
    "TODO",
    "TBD",
    "@filename",
    "probably",
    "roughly",
    "approximately",
    "I estimate",
    "live ready",
    "profitable trading readiness: true",
    "autonomous trading readiness: true",
]


def load_review() -> dict:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def load_matrix() -> dict:
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


def combined_output_text() -> str:
    return "\n".join(
        [
            REVIEW_PATH.read_text(encoding="utf-8"),
            MATRIX_PATH.read_text(encoding="utf-8"),
            REPORT_PATH.read_text(encoding="utf-8"),
            QUEUE_PATH.read_text(encoding="utf-8"),
        ]
    )


def test_slice_4_outputs_exist() -> None:
    assert REVIEW_PATH.exists()
    assert MATRIX_PATH.exists()
    assert REPORT_PATH.exists()
    assert QUEUE_PATH.exists()


def test_review_json_required_values() -> None:
    data = load_review()
    assert data["target_date"] == "2026-06-30"
    assert data["broker_live_boundary_count"] == 1750
    assert data["broker_live_items_count"] == 1750
    assert data["repo_actionable_open_count"] == 0
    assert data["slice_status"] == "COMPLETE_FOR_BROKER_LIVE_PERMISSION_REVIEW_ONLY"
    assert data["broker_live_review_decision"] == "APPROVE_PERMISSION_REVIEW_ONLY_NO_ACCESS"
    assert data["handoff_to_next_slice"] == "Slice 5 Safety Blocker Review"


def test_matrix_json_required_values() -> None:
    data = load_matrix()
    assert data["target_date"] == "2026-06-30"
    assert data["broker_live_boundary_count"] == 1750
    assert data["item_count"] == 1750
    assert len(data["items"]) == 1750
    assert data["review_classification"] == "BROKER_LIVE_PERMISSION_REVIEW_ONLY"
    for item in data["items"]:
        assert item["item_id"]
        assert item["source_status"] == "LIVE_OR_BROKER_PERMISSION_REQUIRED"
        assert item["completion_status"] == "LIVE_OR_BROKER_PERMISSION_REQUIRED"
        assert item["current_status"] == "LIVE_OR_BROKER_PERMISSION_REQUIRED"
        assert item["review_classification"] == "BROKER_LIVE_PERMISSION_REVIEW_ONLY"
        assert item["allowed_next_action"]
        assert item["blocked_actions"]


def test_forbidden_action_strings_exist() -> None:
    text = combined_output_text()
    for action in FORBIDDEN_ACTIONS:
        assert action in text


def test_required_future_gates_exist() -> None:
    text = combined_output_text()
    for gate in REQUIRED_FUTURE_GATES:
        assert gate in text


def test_final_owner_sentence_exists() -> None:
    review = load_review()
    matrix = load_matrix()
    text = combined_output_text()
    assert review["final_owner_sentence"] == FINAL_OWNER_SENTENCE
    assert matrix["final_owner_sentence"] == FINAL_OWNER_SENTENCE
    assert FINAL_OWNER_SENTENCE in text


def test_no_banned_placeholder_tokens_in_outputs() -> None:
    text = combined_output_text()
    for token in BANNED_TOKENS:
        assert token not in text
