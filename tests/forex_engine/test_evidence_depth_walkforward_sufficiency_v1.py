from __future__ import annotations

import ast
import json
from pathlib import Path

from automation.forex_engine import evidence_depth_walkforward_sufficiency_v1 as module


ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATHS = [
    ROOT / "automation" / "forex_engine" / "evidence_depth_walkforward_sufficiency_v1.py",
    ROOT / "scripts" / "forex_delivery" / "run_evidence_depth_walkforward_sufficiency_v1.py",
]


def test_result_is_deterministic_and_json_serializable():
    first = module.run_evidence_depth_walkforward_sufficiency_v1()
    second = module.run_evidence_depth_walkforward_sufficiency_v1()

    assert first == second
    json.dumps(first)


def test_insufficient_sample_blocks_promotion():
    result = module.run_evidence_depth_walkforward_sufficiency_v1(
        {"observed_trade_count": 10, "observed_walkforward_windows": 6}
    )

    assert result["insufficient_sample_block"] is True
    assert result["promotion_allowed"] is False
    assert "insufficient_sample" in result["promotion_blockers"]


def test_walkforward_insufficiency_blocks_promotion():
    result = module.run_evidence_depth_walkforward_sufficiency_v1(
        {"observed_trade_count": 40, "observed_walkforward_windows": 2}
    )

    assert result["walkforward_gate_cleared"] is False
    assert result["promotion_allowed"] is False
    assert "walkforward_window_insufficiency" in result["promotion_blockers"]


def test_protected_booleans_remain_false():
    result = module.run_evidence_depth_walkforward_sufficiency_v1()

    for field in module.PROTECTED_FALSE_FIELDS:
        assert result[field] is False


def test_source_has_no_forbidden_runtime_imports_or_calls():
    forbidden_imports = {"os", "dotenv", "requests", "urllib", "subprocess", "socket", "http"}
    forbidden_text = ("os.environ", "dotenv", "requests", "urllib", "subprocess")
    for path in SOURCE_PATHS:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports.update(
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )
        assert not forbidden_imports.intersection(imports)
        for text in forbidden_text:
            assert text not in source
