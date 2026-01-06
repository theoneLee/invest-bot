import yfinance as yf
from src.config import HK_SHARE_TARGETS, HK_THRESHOLDS, BENCHMARK_TICKER, MANUAL_US_RATE

def get_metrics(code, info):
    try:
        if info.get("MANUAL_PRICE") is not None:
            price = float(info["MANUAL_PRICE"])
        else:
            ticker = yf.Ticker(code)
            price = ticker.fast_info.last_price
            if not price: 
                price = ticker.history(period="1d")['Close'].iloc[-1]
        
        # 优先使用 config.py 里的 manual_div
        manual_div = info.get('manual_div')
        gross_div = manual_div if manual_div else 0.0
        
        # 扣税 10%
        net_div = gross_div * 0.9
        net_yield = (net_div / price) * 100
        return price, net_yield
    except:
        return None, None

def analyze():
    results = {}
    
    if MANUAL_US_RATE is not None:
        us_rate = float(MANUAL_US_RATE)
    else:
        try:
            us_rate = yf.Ticker(BENCHMARK_TICKER).history(period="1d")['Close'].iloc[-1]
        except:
            us_rate = 4.0
            
    cfg = HK_THRESHOLDS
    
    for code, info in HK_SHARE_TARGETS.items():
        price, net_yield = get_metrics(code, info)
        if price is None: 
            results[code] = {"signal": "DATA_ERROR", "metrics": None}
            continue
        
        spread = net_yield - us_rate
        
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
            
        results[code] = {
            "signal": signal,
            "metrics": {
                "price": price,
                "net_yield": net_yield,
                "us_rate": us_rate,
                "spread": spread,
                "name": info['name']
            }
        }
    return results

def run():
    print(f"\n=== 港股策略 (税后) vs 美债 ===")
    results = analyze()
    
    # Get US rate from first result or default (bit hacky for display but analyze has logic)
    # Actually better to just grab it from one of the results if valid
    us_rate_disp = 4.0
    for r in results.values():
        if r["metrics"]:
            us_rate_disp = r["metrics"]["us_rate"]
            break
            
    print(f"🇺🇸 美债基准: {us_rate_disp:.2f}%")
    cfg = HK_THRESHOLDS

    for code, res in results.items():
        if res["signal"] == "DATA_ERROR":
            print(f"Skipping {code}: Data Error")
            continue
            
        m = res["metrics"]
        sig = res["signal"]
        
        print(f"\n🇭🇰 {m['name']} ({code})")
        print(f"   现价: {m['price']:.2f} | 净回报: {m['net_yield']:.2f}% | 利差: {m['spread']:+.2f}%")

        if sig == "STRONG_BUY":
            print(f"   🟢 [STRONG BUY] 补仓！(目标 > 美债+{cfg['BUY_DIP']}%)")
        elif sig == "BUY":
            print(f"   🔵 [BUY] 正常定投。")
        elif sig == "SELL":
            print(f"   🔴 [SELL] 止盈/换仓！回报已低于美债。")
        elif sig == "STOP":
            print(f"   🟠 [STOP] 停买。")
        else:
            print(f"   🟡 [HOLD] 观望。")

if __name__ == "__main__":
    run()
