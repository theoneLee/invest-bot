import akshare as ak
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from src.config import A_SHARE_CONFIG, BENCHMARK_TICKER, MANUAL_US_RATE

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def get_data():
    try:
        # 获取美债
        if MANUAL_US_RATE is not None:
            us_rate = float(MANUAL_US_RATE)
        else:
            us_ticker = yf.Ticker(BENCHMARK_TICKER)
            # 加上 verify=False 或 proxy 如果在内网环境受限
            us_rate = us_ticker.history(period="1d")['Close'].iloc[-1]

        # 获取 A股 ETF
        code = A_SHARE_CONFIG["CODE"]
        
        if A_SHARE_CONFIG.get("MANUAL_PRICE") is not None:
            price = float(A_SHARE_CONFIG["MANUAL_PRICE"])
        else:
            etf_spot = ak.fund_etf_spot_em()
            target = etf_spot[etf_spot['代码'] == code]
            if target.empty: return None, None, None
            price = float(target.iloc[0]['最新价'])

        # 获取分红
        if A_SHARE_CONFIG.get("MANUAL_TTM_DIV") is not None:
            ttm_div = float(A_SHARE_CONFIG["MANUAL_TTM_DIV"])
        else:
            div_fn = getattr(ak, "fund_open_fund_dividend_em", None)
            if div_fn is None:
                log("当前 akshare 版本缺少 fund_open_fund_dividend_em；请在 src/config.py 手动填写 MANUAL_TTM_DIV。")
                return None, None, None

            div_df = div_fn(symbol=code)
            div_df['权益登记日'] = pd.to_datetime(div_df['权益登记日'])
            one_year_ago = datetime.now() - timedelta(days=365)
            ttm_div = div_df[div_df['权益登记日'] >= one_year_ago]['每份分红'].astype(float).sum()

        return price, ttm_div, us_rate
    except Exception as e:
        log(f"数据抓取失败: {e}")
        return None, None, None

def analyze():
    price, ttm_div, us_rate = get_data()
    if price is None:
        return {"signal": "DATA_ERROR", "metrics": None}

    etf_yield = (ttm_div / price) * 100
    spread = etf_yield - us_rate
    cfg = A_SHARE_CONFIG["THRESHOLDS"]

    # 反推价格
    price_buy_dip = ttm_div / ((us_rate + cfg["BUY_DIP"]) / 100)
    price_stop = ttm_div / ((us_rate + cfg["STOP_BUY"]) / 100)
    
    metrics = {
        "price": price,
        "ttm_div": ttm_div,
        "us_rate": us_rate,
        "etf_yield": etf_yield,
        "spread": spread,
        "price_buy_dip": price_buy_dip,
        "price_stop": price_stop
    }

    if spread >= cfg["BUY_DIP"]:
        signal = "STRONG_BUY"
    elif spread >= cfg["NORMAL_BUY"]:
        signal = "BUY"
    elif spread <= cfg["TAKE_PROFIT"]:
        signal = "SELL"
    elif spread <= cfg["STOP_BUY"]:
        signal = "STOP"
    else:
        signal = "HOLD"
    
    return {"signal": signal, "metrics": metrics}

def run():
    print(f"\n=== A股策略: {A_SHARE_CONFIG['CODE']} vs 美债 ===")
    result = analyze()
    
    if result["signal"] == "DATA_ERROR":
        print("数据获取失败，跳过。")
        return

    m = result["metrics"]
    print(f"当前价格: {m['price']:.3f} | TTM分红: {m['ttm_div']:.3f}")
    print(f"ETF股息率: {m['etf_yield']:.2f}% | 美债利率: {m['us_rate']:.2f}%")
    print(f"真实利差: {m['spread']:+.2f}%")
    print(f"📉 补仓价 (<): {m['price_buy_dip']:.3f} | ⛔ 停买价 (>): {m['price_stop']:.3f}")
    print("-" * 30)

    sig = result["signal"]
    cfg = A_SHARE_CONFIG["THRESHOLDS"]
    
    if sig == "STRONG_BUY":
        print("🟢 [STRONG BUY] 补仓！利差极大。")
    elif sig == "BUY":
        print("🔵 [BUY] 正常定投。")
    elif sig == "SELL":
        print("🔴 [SELL] 止盈！严重高估。")
    elif sig == "STOP":
        print("🟠 [STOP] 停止买入，存美元。")
    else:
        print("🟡 [HOLD] 观望。")

if __name__ == "__main__":
    run()
