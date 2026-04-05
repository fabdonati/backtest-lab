from __future__ import annotations


def trading_cost(position_change: float, transaction_cost_bps: float, slippage_bps: float) -> float:
    basis_points = transaction_cost_bps + slippage_bps
    return abs(position_change) * (basis_points / 10_000.0)
