import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_JUNE30_SLICE2_OWNER_BOUNDARY_DECISION_V1.json"
)
REPORT_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_JUNE30_SLICE2_OWNER_BOUNDARY_DECISION_V1_REPORT.md"
)
QUEUE_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_JUNE30_SLICE2_OWNER_BOUNDARY_QUEUE_V1.md"
)

FINAL_OWNER_SENTENCE = (
    "AIOS Forex Slice 2 is complete for next-review only: owner-protected "
    "boundary items 3 are approved for review classification, while broker/API, "
    "credentials, demo/live trading, money movement, production, and autonomy "
    "remain blocked."
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


def load_decision() -> dict:
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def combined_output_text() -> str:
    return "\n".join(
        [
            JSON_PATH.read_text(encoding="utf-8"),
            REPORT_PATH.read_text(encoding="utf-8"),
            QUEUE_PATH.read_text(encoding="utf-8"),
        ]
    )


def queue_item_rows() -> list[str]:
    queue = QUEUE_PATH.read_text(encoding="utf-8")
    return [
        line
        for line in queue.splitlines()
        if line.startswith("| FOREX-GOAL-")
        or line.startswith("| OWNER_PROTECTED_ITEM_")
        or line.startswith("| OWNER-")
    ]


def test_slice_2_outputs_exist() -> None:
    assert JSON_PATH.exists()
    assert REPORT_PATH.exists()
    assert QUEUE_PATH.exists()


def test_decision_json_required_values() -> None:
    data = load_decision()
    assert data["target_date"] == "2026-06-30"
    assert data["owner_protected_count"] == 3
    assert data["repo_actionable_open_count"] == 0
    assert data["slice_status"] == "COMPLETE_FOR_NEXT_REVIEW_ONLY"
    assert data["owner_decision"] == "APPROVE_NEXT_REVIEW_ONLY"


def test_queue_has_exactly_three_item_rows() -> None:
    assert len(queue_item_rows()) == 3


def test_forbidden_action_strings_exist() -> None:
    text = combined_output_text()
    for action in FORBIDDEN_ACTIONS:
        assert action in text


def test_final_owner_sentence_exists() -> None:
    data = load_decision()
    text = combined_output_text()
    assert data["final_owner_sentence"] == FINAL_OWNER_SENTENCE
    assert FINAL_OWNER_SENTENCE in text


def test_no_banned_placeholder_tokens_in_outputs() -> None:
    text = combined_output_text()
    for token in BANNED_TOKENS:
        assert token not in text
