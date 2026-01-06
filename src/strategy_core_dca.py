import argparse
from datetime import datetime

from src.config import A_SHARE_CONFIG, CNY_HURDLE_RATE, CORE_DCA_CONFIG


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def get_a_share_inputs():
    price = A_SHARE_CONFIG.get("MANUAL_PRICE")
    ttm_div = A_SHARE_CONFIG.get("MANUAL_TTM_DIV")
    index_yield = A_SHARE_CONFIG.get("MANUAL_INDEX_YIELD")

    price = float(price) if price is not None else None
    ttm_div = float(ttm_div) if ttm_div is not None else None
    index_yield = float(index_yield) if index_yield is not None else None

    return price, ttm_div, index_yield


def decide_equity_ratio(spread_vs_hurdle: float) -> float:
    cfg = CORE_DCA_CONFIG
    th = cfg["SPREAD_THRESHOLDS"]

    if spread_vs_hurdle >= th["OVERWEIGHT"]:
        return float(cfg["EQUITY_MAX"])
    if spread_vs_hurdle >= th["NEUTRAL"]:
        return float(cfg["EQUITY_BASE"])
    return float(cfg["EQUITY_MIN"])


def analyze(monthly_amount: float):
    price, ttm_div, index_yield = get_a_share_inputs()
    cash_yield = (ttm_div / price) * 100 if (price and ttm_div and price > 0) else None
    if cash_yield is None and index_yield is None:
        return {"signal": "DATA_ERROR", "metrics": None, "plan": None}

    hurdle = float(CNY_HURDLE_RATE)
    decision_yield = index_yield if index_yield is not None else cash_yield
    spread = float(decision_yield) - hurdle

    equity_ratio = decide_equity_ratio(spread)
    equity_amount = monthly_amount * equity_ratio
    defense_amount = monthly_amount - equity_amount

    th = CORE_DCA_CONFIG["SPREAD_THRESHOLDS"]
    price_overweight = (
        (ttm_div / ((hurdle + th["OVERWEIGHT"]) / 100)) if (ttm_div is not None) else None
    )
    price_neutral = (
        (ttm_div / ((hurdle + th["NEUTRAL"]) / 100)) if (ttm_div is not None) else None
    )

    return {
        "signal": "OVERWEIGHT" if equity_ratio == CORE_DCA_CONFIG["EQUITY_MAX"] else "DCA",
        "metrics": {
            "code": A_SHARE_CONFIG["CODE"],
            "price": price,
            "ttm_div": ttm_div,
            "cash_yield": cash_yield,
            "index_yield": index_yield,
            "decision_yield": decision_yield,
            "hurdle_rate": hurdle,
            "spread_vs_hurdle": spread,
            "price_overweight": price_overweight,
            "price_neutral": price_neutral,
        },
        "plan": {
            "monthly_amount": monthly_amount,
            "equity_ratio": equity_ratio,
            "equity_amount": equity_amount,
            "defense_amount": defense_amount,
            "equity_target": f"A股红利低波ETF {A_SHARE_CONFIG['CODE']}",
            "defense_target": CORE_DCA_CONFIG["DEFENSE_SUGGESTION"],
        },
    }


def run(monthly_amount: float):
    print("\n=== 核心定投策略（不卖出，仅调整新增资金比例）===")
    res = analyze(monthly_amount)

    if res["signal"] == "DATA_ERROR":
        print(
            "数据缺失：请在 src/config.py 填写 A_SHARE_CONFIG 的 MANUAL_INDEX_YIELD（推荐）或 MANUAL_PRICE+MANUAL_TTM_DIV（用于现金流口径）。"
        )
        return

    m = res["metrics"]
    p = res["plan"]

    price_disp = f"{m['price']:.3f}" if m["price"] is not None else "N/A"
    ttm_div_disp = f"{m['ttm_div']:.3f}" if m["ttm_div"] is not None else "N/A"
    print(f"标的: {m['code']} | 现价: {price_disp} | TTM分红: {ttm_div_disp}")

    cash_yield_disp = f"{m['cash_yield']:.2f}%" if m["cash_yield"] is not None else "N/A"
    index_yield_disp = f"{m['index_yield']:.2f}%" if m["index_yield"] is not None else "N/A"
    print(
        f"到手现金流口径: {cash_yield_disp} | 指数口径: {index_yield_disp} | 门槛(CNY): {m['hurdle_rate']:.2f}%"
    )
    print(f"用于决策的收益率口径: {m['decision_yield']:.2f}% | 利差: {m['spread_vs_hurdle']:+.2f}%")
    print(
        f"阈值：OVERWEIGHT 需要收益率≥{m['hurdle_rate'] + CORE_DCA_CONFIG['SPREAD_THRESHOLDS']['OVERWEIGHT']:.2f}%"
        f" | NEUTRAL 需要收益率≥{m['hurdle_rate'] + CORE_DCA_CONFIG['SPREAD_THRESHOLDS']['NEUTRAL']:.2f}%"
    )
    if m["price_overweight"] is not None and m["price_neutral"] is not None:
        print(
            f"现金流口径参考价位：OVERWEIGHT 价(<): {m['price_overweight']:.3f} | NEUTRAL 价(<): {m['price_neutral']:.3f}"
        )
    print("-" * 40)

    print(f"本月新增资金: {p['monthly_amount']:,.2f}")
    print(f"权益（上限 {CORE_DCA_CONFIG['EQUITY_MAX']:.0%}）: {p['equity_amount']:,.2f}  -> {p['equity_target']}")
    print(f"防御/现金类: {p['defense_amount']:,.2f} -> {p['defense_target']}")
    print("-" * 40)
    print("执行原则：不做卖出；只在“红利权益/防御资产”之间调节当月新增资金比例。")


def main():
    parser = argparse.ArgumentParser(description="Core DCA strategy (no selling; tilt new contributions)")
    parser.add_argument("amount", type=float, help="Monthly available funds (e.g. 20000)")
    args = parser.parse_args()
    run(args.amount)


if __name__ == "__main__":
    main()
