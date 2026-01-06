import argparse
import sys
from src.strategy_a_share import analyze as analyze_a
from src.strategy_hk_us import analyze as analyze_hk

def main():
    parser = argparse.ArgumentParser(description="Investment Advisor based on SOP")
    parser.add_argument("amount", type=float, help="Total available funds for this month (e.g. 20000)")
    args = parser.parse_args()
    
    total_amount = args.amount
    
    # 1. Base Allocation (2:4:3:1)
    alloc = {
        "growth": total_amount * 0.1,  # 10%
        "defense": total_amount * 0.2, # 20%
        "a_share": total_amount * 0.4, # 40%
        "hk_share": total_amount * 0.3 # 30%
    }
    
    print(f"\n💰 总资金: {total_amount:,.2f}")
    print("=" * 40)
    print(f"📊 基础配置 (2:4:3:1):")
    print(f"   - 增长层 (10%): {alloc['growth']:,.2f}")
    print(f"   - 防御层 (20%): {alloc['defense']:,.2f}")
    print(f"   - A股红利 (40%): {alloc['a_share']:,.2f}")
    print(f"   - 港股红利 (30%): {alloc['hk_share']:,.2f}")
    print("=" * 40)

    # 2. Get Signals
    print("\n🔍 正在分析市场信号...")
    try:
        res_a = analyze_a()
        res_hk = analyze_hk()
    except Exception as e:
        print(f"❌ 策略分析失败: {e}")
        return

    sig_a = res_a.get("signal", "HOLD") # Default to HOLD if error
    
    # Aggregated HK Signal: Pick the 'strongest' signal (prioritize buying if any opportunity)
    # Priority: STRONG_BUY > BUY > HOLD > STOP > SELL
    hk_priority = ["STRONG_BUY", "BUY", "HOLD", "STOP", "SELL"]
    sig_hk = "HOLD"
    
    # Simple logic: If any is STRONG_BUY, whole block is STRONG_BUY. 
    # If all are STOP, block is STOP.
    hk_signals = [v["signal"] for v in res_hk.values() if v["signal"] != "DATA_ERROR"]
    
    if not hk_signals:
        sig_hk = "HOLD" # No data
    elif "STRONG_BUY" in hk_signals:
        sig_hk = "STRONG_BUY"
    elif "BUY" in hk_signals:
        sig_hk = "BUY"
    elif "HOLD" in hk_signals:
        sig_hk = "HOLD"
    elif "STOP" in hk_signals:
        sig_hk = "STOP"
    else:
        sig_hk = "SELL"

    print(f"   - A股信号: {sig_a}")
    print(f"   - 港股信号: {sig_hk} (综合)")
    
    # 3. Dynamic Routing (SOP Logic)
    final_plan = {
        "buy_growth": alloc["growth"],
        "buy_defense": alloc["defense"], # Base defense
        "buy_a": alloc["a_share"],
        "buy_hk": alloc["hk_share"]
    }
    
    free_cash = 0
    
    # Process A-Share
    if sig_a in ["STOP", "SELL"]:
        print(f"   ⚠️ A股触发熔断/止盈 ({sig_a}) -> 预算转入防御层/自由资金")
        free_cash += final_plan["buy_a"]
        final_plan["buy_a"] = 0
    elif sig_a == "STRONG_BUY":
        # A-Share needs more money. Will check free cash later.
        pass
        
    # Process HK-Share
    if sig_hk in ["STOP", "SELL"]:
        print(f"   ⚠️ 港股触发熔断/止盈 ({sig_hk}) -> 预算转入防御层/自由资金")
        free_cash += final_plan["buy_hk"]
        final_plan["buy_hk"] = 0
    elif sig_hk == "STRONG_BUY":
        pass

    # Distribute Free Cash & Base Defense to STRONG BUY sectors
    # Candidates for extra funding
    candidates = []
    if sig_a == "STRONG_BUY": candidates.append("buy_a")
    if sig_hk == "STRONG_BUY": candidates.append("buy_hk")
    
    if candidates:
        # We have opportunities! Mobilize the Defense layer AND any free cash from stopped sectors.
        total_ammo = free_cash + final_plan["buy_defense"]
        
        # Zero out the defense buy because we are using it for offense
        final_plan["buy_defense"] = 0 
        
        # Split ammo equally (or proportionally? Let's do equal split for simplicity as per SOP "All in")
        ammo_per_sector = total_ammo / len(candidates)
        
        for sector in candidates:
            final_plan[sector] += ammo_per_sector
            print(f"   🚀 {sector} 触发吸血模式! 注入资金: {ammo_per_sector:,.2f}")
    else:
        # No strong buy opportunities. Free cash goes to Defense (SGOV)
        if free_cash > 0:
            final_plan["buy_defense"] += free_cash
            print(f"   🛡️ 无绝佳机会，闲置预算转入防御层: {free_cash:,.2f}")

    # 4. Final Report
    print("\n" + "=" * 40)
    print("🚀 最终执行方案 (本月):")
    print(f"1. [无脑定投] 纳指/BTC (增长层): {final_plan['buy_growth']:,.2f}")
    print(f"2. [防御/存钱] 美元短债 (SGOV):   {final_plan['buy_defense']:,.2f}")
    print(f"3. [A股红利]  510880 等:        {final_plan['buy_a']:,.2f}")
    print(f"4. [港股红利] 0939/0883 等:     {final_plan['buy_hk']:,.2f}")
    print("=" * 40)
    
    # Extra advice for SELL
    if sig_a == "SELL":
        print("💡 提示: A股建议卖出部分持仓锁定利润。" )
    if sig_hk == "SELL":
        print("💡 提示: 港股建议卖出部分持仓锁定利润。" )

if __name__ == "__main__":
    main()
