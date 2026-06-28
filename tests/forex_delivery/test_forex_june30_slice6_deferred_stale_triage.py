import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVIEW_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_JUNE30_SLICE6_DEFERRED_STALE_TRIAGE_V1.json"
)
MATRIX_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_JUNE30_SLICE6_DEFERRED_STALE_MATRIX_V1.json"
)
REPORT_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_JUNE30_SLICE6_DEFERRED_STALE_TRIAGE_V1_REPORT.md"
)
QUEUE_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_JUNE30_SLICE6_DEFERRED_STALE_QUEUE_V1.md"
)

FINAL_OWNER_SENTENCE = (
    "AIOS Forex Slice 6 is complete for deferred/stale triage only: "
    "deferred/stale items 74 are classified into owner-review, superseded, "
    "already-covered, or post-June-30 backlog outcomes, while broker/API, "
    "credentials, account access, demo/live trading, order action, money "
    "movement, safety bypass, production, and autonomy remain blocked."
)

FORBIDDEN_ACTIONS = [
    "claiming closure without source proof",
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
    "safety gate bypass",
    "safety gate weakening",
    "safety gate deletion",
    "credential persistence",
    "account identifier persistence",
    "raw private evidence",
    "broker connection",
    "live endpoint use",
]

REQUIRED_FUTURE_GATES = [
    "explicit owner approval",
    "final owner decision brief",
    "no closure without source proof",
    "no broker/API access",
    "no credential access",
    "no account access",
    "no trade execution",
    "no production activation",
    "no autonomy activation",
    "safety gate preservation",
]

ALLOWED_OUTCOMES = {
    "KEEP_FOR_FINAL_OWNER_REVIEW",
    "CLOSE_AS_SUPERSEDED",
    "CLOSE_AS_ALREADY_COVERED",
    "DEFER_TO_POST_JUNE30_BACKLOG",
}

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


def test_slice_6_outputs_exist() -> None:
    assert REVIEW_PATH.exists()
    assert MATRIX_PATH.exists()
    assert REPORT_PATH.exists()
    assert QUEUE_PATH.exists()


def test_review_json_required_values() -> None:
    data = load_review()
    assert data["target_date"] == "2026-06-30"
    assert data["deferred_or_stale_count"] == 74
    assert data["deferred_stale_items_count"] == 74
    assert data["repo_actionable_open_count"] == 0
    assert data["slice_status"] == "COMPLETE_FOR_DEFERRED_STALE_TRIAGE_ONLY"
    assert (
        data["deferred_stale_triage_decision"]
        == "APPROVE_TRIAGE_ONLY_NO_RUNTIME_AUTHORITY"
    )
    assert data["handoff_to_next_slice"] == "Slice 7 Final Owner Decision Brief"


def test_matrix_json_required_values() -> None:
    data = load_matrix()
    assert data["target_date"] == "2026-06-30"
    assert data["deferred_or_stale_count"] == 74
    assert data["item_count"] == 74
    assert len(data["items"]) == 74
    assert data["review_classification"] == "DEFERRED_STALE_TRIAGE_ONLY"
    for item in data["items"]:
        assert item["item_id"]
        assert item["source_status"] == "DEFERRED_WITH_REASON"
        assert item["completion_status"] == "DEFERRED_WITH_REASON"
        assert item["current_status"] == "DEFERRED_WITH_REASON"
        assert item["review_classification"] == "DEFERRED_STALE_TRIAGE_ONLY"
        assert item["triage_outcome"] in ALLOWED_OUTCOMES
        assert item["triage_reason"]
        assert item["allowed_next_action"]
        assert item["blocked_actions"]


def test_triage_outcome_counts_sum_to_74() -> None:
    data = load_matrix()
    counts = data["triage_outcome_counts"]
    assert set(counts) == ALLOWED_OUTCOMES
    assert sum(counts.values()) == 74


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
