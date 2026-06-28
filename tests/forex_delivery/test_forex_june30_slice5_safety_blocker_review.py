import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVIEW_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_JUNE30_SLICE5_SAFETY_BLOCKER_REVIEW_V1.json"
)
MATRIX_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_JUNE30_SLICE5_SAFETY_BLOCKER_MATRIX_V1.json"
)
REPORT_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_JUNE30_SLICE5_SAFETY_BLOCKER_REVIEW_V1_REPORT.md"
)
QUEUE_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_JUNE30_SLICE5_SAFETY_BLOCKER_QUEUE_V1.md"
)

FINAL_OWNER_SENTENCE = (
    "AIOS Forex Slice 5 is complete for gate-preserving safety review only: "
    "safety-blocked items 25 are classified for safety review, while safety "
    "bypass, safety weakening, safety deletion, broker/API, credentials, "
    "account access, demo/live trading, order action, money movement, "
    "production, and autonomy remain blocked."
)

FORBIDDEN_ACTIONS = [
    "safety gate bypass",
    "safety gate weakening",
    "safety gate deletion",
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
    "safety gate preservation",
    "no safety gate bypass",
    "no safety gate weakening",
    "no safety gate deletion",
    "kill-switch validation",
    "max-loss validation",
    "daily-stop validation",
    "one-order-only rule",
    "micro-size rule",
    "stop-loss required",
    "take-profit required",
    "broker permission review",
    "sanitized evidence review",
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


def test_slice_5_outputs_exist() -> None:
    assert REVIEW_PATH.exists()
    assert MATRIX_PATH.exists()
    assert REPORT_PATH.exists()
    assert QUEUE_PATH.exists()


def test_review_json_required_values() -> None:
    data = load_review()
    assert data["target_date"] == "2026-06-30"
    assert data["safety_blocked_count"] == 25
    assert data["safety_blocker_items_count"] == 25
    assert data["repo_actionable_open_count"] == 0
    assert data["slice_status"] == "COMPLETE_FOR_GATE_PRESERVING_SAFETY_REVIEW_ONLY"
    assert data["safety_review_decision"] == "APPROVE_GATE_PRESERVING_REVIEW_ONLY"
    assert data["handoff_to_next_slice"] == "Slice 6 Deferred/Stale Triage"


def test_matrix_json_required_values() -> None:
    data = load_matrix()
    assert data["target_date"] == "2026-06-30"
    assert data["safety_blocked_count"] == 25
    assert data["item_count"] == 25
    assert len(data["items"]) == 25
    assert data["review_classification"] == "GATE_PRESERVING_SAFETY_REVIEW_ONLY"
    for item in data["items"]:
        assert item["item_id"]
        assert item["source_status"] == "SAFETY_BLOCKED"
        assert item["completion_status"] == "SAFETY_BLOCKED"
        assert item["current_status"] == "SAFETY_BLOCKED"
        assert item["review_classification"] == "GATE_PRESERVING_SAFETY_REVIEW_ONLY"
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
