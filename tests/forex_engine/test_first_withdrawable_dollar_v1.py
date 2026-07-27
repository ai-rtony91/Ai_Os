from automation.forex_engine.first_withdrawable_dollar_v1 import ANCHOR_ID, anchor_rank, evaluate_first_withdrawable_dollar

def evidence(**updates):
    value = {"evidence_genuine": True, "evidence_sanitized": True, "evidence_reproducible": True, "trade_is_real": True, "owner_approved_trade": True, "broker": "OANDA", "trade_closed": True, "gross_realized_profit": "1.25", "fees_and_costs": "0.20", "net_realized_profit": "1.05", "withdrawable_confirmed": True, "linked_bank_destination_confirmed": True, "withdrawal_owner_approved": True, "withdrawal_submitted": True}
    value.update(updates)
    return value

def test_single_anchor_is_canonical_and_milestones_are_dependencies():
    result = evaluate_first_withdrawable_dollar(evidence())
    assert result["anchor_id"] == ANCHOR_ID == "FIRST_WITHDRAWABLE_DOLLAR"
    assert result["lower_level_milestones_are_dependencies"] is True
    assert result["anchor_complete"] is True

def test_missing_or_fabricated_pl_cannot_complete_anchor():
    assert evaluate_first_withdrawable_dollar(evidence(net_realized_profit=None))["anchor_complete"] is False
    assert evaluate_first_withdrawable_dollar(evidence(evidence_genuine=False))["anchor_complete"] is False

def test_gross_profit_below_costs_and_net_below_one_fail():
    assert evaluate_first_withdrawable_dollar(evidence(gross_realized_profit="0.50", fees_and_costs="0.75", net_realized_profit="-0.25"))["anchor_complete"] is False
    assert evaluate_first_withdrawable_dollar(evidence(gross_realized_profit="1.10", fees_and_costs="0.20", net_realized_profit="0.90"))["anchor_complete"] is False

def test_withdrawable_and_submission_are_required_separately():
    assert evaluate_first_withdrawable_dollar(evidence(withdrawable_confirmed=False))["anchor_complete"] is False
    result = evaluate_first_withdrawable_dollar(evidence(withdrawal_submitted=False))
    assert result["anchor_complete"] is False
    assert result["next_verified_blocker"] == "OWNER_SUBMIT_APPROVED_WITHDRAWAL"

def test_protected_actions_remain_owner_gated():
    assert not any(evaluate_first_withdrawable_dollar(evidence())["protected_actions"].values())

def test_anchor_rank_favors_shortest_path_and_deprioritizes_unrelated_governance():
    _, close = anchor_rank({"verified_anchor_distance": 1, "removes_verified_anchor_dependency": True})
    _, far = anchor_rank({"verified_anchor_distance": 4, "removes_verified_anchor_dependency": True})
    _, governance = anchor_rank({"verified_anchor_distance": 0, "lane": "governance-expansion"})
    assert close > far > governance
