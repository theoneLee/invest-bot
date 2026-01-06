# Agent Instruction Prompt

Copy and paste the following text into your AI assistant (e.g., Gemini, ChatGPT) to automate your monthly investment process.

---

**Role:** You are an expert quantitative investment assistant.

**Task:** 
1. **Search** for the real-time market data listed below using Google Search or similar tools.
2. **Update** the `src/config.py` file with the retrieved values.
3. **Execute** the advisor script to generate the investment plan.

**Step 1: Data to Search**
Please find the latest values for:
1. **US 3-Month Treasury Bill Rate** (e.g., "US 3-month treasury rate" or "^IRX").
2. **A-Share Dividend Low Volatility ETF (563020)**:
   - Current Price (e.g., "563020 价格" or "红利低波50ETF").
   - TTM Dividend (e.g., "563020 TTM分红" or search for "H30269指数 分红").
3. **HK Stocks**:
   - **CCB (0939.HK)**: Current Price (HKD) and Dividend per share (HKD).
   - **CNOOC (0883.HK)**: Current Price (HKD) and Dividend per share (HKD).
   - **HSBC (0005.HK)**: Current Price (HKD) and Dividend per share (HKD/USD).
   - **GX Hang Seng High Div (3110.HK)**: Current Price (HKD) and Annual Dividend per share (HKD).

**Step 2: Update Configuration**
Modify `src/config.py` with the found values. Use the following format (replace placeholders):

```python
# 市场配置
BENCHMARK_TICKER = "^TNX"

# [UPDATE THIS]
MANUAL_US_RATE = 4.xx 

# A股策略配置
A_SHARE_CONFIG = {
    "CODE": "563020",
    # [UPDATE THIS]
    "MANUAL_PRICE": 3.xxx,
    "MANUAL_TTM_DIV": 0.xxx, 
    "THRESHOLDS": {
        "BUY_DIP": 2.0,
        "NORMAL_BUY": 1.0,
        "TAKE_PROFIT": -0.5,
        "STOP_BUY": 0.0
    }
}

# 港股策略配置
HK_THRESHOLDS = {
    "BUY_DIP": 3.0,
    "NORMAL_BUY": 1.5,
    "TAKE_PROFIT": -1.0,
    "STOP_BUY": 0.5
}

HK_SHARE_TARGETS = {
    "0939.HK": {
        "name": "建设银行",
        # [UPDATE THIS]
        "manual_div": 0.xx, 
        "MANUAL_PRICE": 5.xx
    },
    "0883.HK": {
        "name": "中国海洋石油",
        # [UPDATE THIS]
        "manual_div": 1.xx, 
        "MANUAL_PRICE": 18.xx
    },
    "0005.HK": {
        "name": "汇丰控股",
        # [UPDATE THIS]
        "manual_div": 3.xx,
        "MANUAL_PRICE": 60.xx
    },
    "3110.HK": {
        "name": "GX恒生高股息",
        # [UPDATE THIS]
        "manual_div": 2.xx,
        "MANUAL_PRICE": 22.xx
    }
}
```

**Step 3: Execute Advisor**
Run the following command to generate the plan for a total budget of 20,000 (adjust if needed):

```bash
uv run -m src.advisor 20000
```

**Step 4: Cleanup**
VERY IMPORTANT: After the execution is finished and you have provided the advice, **revert** all manual configuration values (`MANUAL_US_RATE`, `MANUAL_PRICE`, `MANUAL_TTM_DIV`, `manual_div`) in `src/config.py` back to `None` (or their original default values) to ensure future runs start from a clean state.
