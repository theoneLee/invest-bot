import argparse
from datetime import datetime

from src.config import A_SHARE_CONFIG, A_SHARE_DIVIDEND_TARGETS, CNY_HURDLE_RATE, CORE_DCA_CONFIG


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def _get_target_manual_inputs(
    code: str, target: dict
) -> tuple[float | None, float | None, float | None]:
    if code == A_SHARE_CONFIG.get("CODE"):
        price = A_SHARE_CONFIG.get("MANUAL_PRICE")
        ttm_div = A_SHARE_CONFIG.get("MANUAL_TTM_DIV")
        index_yield = A_SHARE_CONFIG.get("MANUAL_INDEX_YIELD")
    else:
        price = target.get("MANUAL_PRICE")
        ttm_div = target.get("MANUAL_TTM_DIV")
        index_yield = target.get("MANUAL_INDEX_YIELD")

    price = float(price) if price is not None else None
    ttm_div = float(ttm_div) if ttm_div is not None else None
    index_yield = float(index_yield) if index_yield is not None else None
    return price, ttm_div, index_yield


def decide_action(spread_vs_hurdle: float) -> str:
    th = CORE_DCA_CONFIG["SPREAD_THRESHOLDS"]
    if spread_vs_hurdle >= th["OVERWEIGHT"]:
        return "OVERWEIGHT"
    if spread_vs_hurdle >= th["NEUTRAL"]:
        return "DCA"
    return "DEFENSE"


def analyze():
    hurdle = float(CNY_HURDLE_RATE)
    results: dict[str, dict] = {}

    for code, target in A_SHARE_DIVIDEND_TARGETS.items():
        price, ttm_div, index_yield = _get_target_manual_inputs(code, target)
        cash_yield = (ttm_div / price) * 100 if (price and ttm_div and price > 0) else None
        decision_yield = index_yield if index_yield is not None else cash_yield

        if decision_yield is None:
            results[code] = {
                "name": target.get("name", code),
                "signal": "DATA_MISSING",
                "metrics": None,
                "note": "请先在 src/config.py 填写 MANUAL_INDEX_YIELD（ETF推荐）或 MANUAL_PRICE+MANUAL_TTM_DIV（现金流口径）。",
            }
            continue

        spread = float(decision_yield) - hurdle
        signal = decide_action(spread)

        results[code] = {
            "name": target.get("name", code),
            "signal": signal,
            "metrics": {
                "price": price,
                "ttm_div": ttm_div,
                "cash_yield": cash_yield,
                "index_yield": index_yield,
                "decision_yield": decision_yield,
                "hurdle_rate": hurdle,
                "spread_vs_hurdle": spread,
            },
            "note": None,
        }

    return results


def run():
    print("\n=== A股分红资产池：本月是否值得加仓（只针对新增资金，不做卖出）===")
    print(f"门槛利率(CNY): {CNY_HURDLE_RATE:.2f}% | 阈值: {CORE_DCA_CONFIG['SPREAD_THRESHOLDS']}")
    print("-" * 70)

    results = analyze()

    for code, res in results.items():
        name = res["name"]
        sig = res["signal"]
        if sig == "DATA_MISSING":
            print(f"{name} ({code}): DATA_MISSING")
            print(f"  - {res['note']}")
            continue

        m = res["metrics"]
        print(f"{name} ({code})")
        price_disp = f"{m['price']:.3f}" if m["price"] is not None else "N/A"
        ttm_div_disp = f"{m['ttm_div']:.3f}" if m["ttm_div"] is not None else "N/A"
        cash_yield_disp = f"{m['cash_yield']:.2f}%" if m["cash_yield"] is not None else "N/A"
        index_yield_disp = f"{m['index_yield']:.2f}%" if m["index_yield"] is not None else "N/A"
        print(
            f"  - 现价: {price_disp} | TTM分红: {ttm_div_disp} | 到手现金流口径: {cash_yield_disp} | 指数口径: {index_yield_disp}"
        )
        print(f"  - 用于决策的收益率口径: {m['decision_yield']:.2f}% | 利差: {m['spread_vs_hurdle']:+.2f}%")
        if sig == "OVERWEIGHT":
            print("  - 结论: 值得加大买入（本月新增资金可倾斜到该标的）")
        elif sig == "DCA":
            print("  - 结论: 可正常定投（按计划买入）")
        else:
            print("  - 结论: 不建议加仓（新增资金更偏向防御资产/现金类）")


def main():
    parser = argparse.ArgumentParser(description="A-share dividend targets (manual inputs; no selling)")
    _ = parser.parse_args()
    run()


if __name__ == "__main__":
    main()
