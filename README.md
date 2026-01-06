# Invest Bot

投资助手，用于计算股息率与美债收益率的利差并提供操作建议。

## 配置指南 (src/config.py)

脚本支持通过 `src/config.py` 进行手动配置。当配置项不为 `None` 时，系统将优先使用手动配置的值，而不是从 API 实时获取。

### 全局配置
- `MANUAL_US_RATE`: 手动设置美债收益率基准（例如 `4.25`）。如果为 `None`，则从 `yfinance` 获取。

### A股策略配置 (`A_SHARE_CONFIG`)
- `CODE`: ETF 代码（如 `511010`）。
- `MANUAL_PRICE`: 手动设置 ETF 当前价格。
- `MANUAL_TTM_DIV`: 手动设置过去 12 个月的总分红额。
- `THRESHOLDS`: 利差阈值设置。

### 港股策略配置 (`HK_SHARE_TARGETS`)
每个目标股票可以独立配置：
- `manual_div`: 每股分红金额。
- `MANUAL_PRICE`: 手动设置该股票当前价格。

### 运行方式
确保已安装 `uv`，然后执行：

```bash
# A股策略
uv run -m src.strategy_a_share

# 港股策略
uv run -m src.strategy_hk_us
```

## 使用 AI 助手（Prompts）

仓库内提供了两份可直接复制到 ChatGPT/Gemini 等助手里的操作指引，用于把“搜索数据 → 填配置 → 运行脚本 → 输出方案”流程标准化。

### 1) `PROMPT_AGENT.md`（SOP/综合方案）
适合你按 `INVESTMENT_SOP.md` 做“整月资金路由”的场景：
- 搜索实时数据（利率、价格、分红）并更新 `src/config.py`
- 运行综合方案：`uv run -m src.advisor 20000`
- 执行结束后把 `src/config.py` 里的手动字段恢复为 `None`，避免下次误用旧数据

### 2) `PROMPT_CORE_DCA.md`（核心定投，不卖出）
适合“只做定投、偏稳定现金流”的场景（只调整当月新增资金在红利权益/防御资产之间的比例）：
- 每次运行前用搜索工具获取并填写：
  - `A_SHARE_CONFIG["MANUAL_PRICE"]`
  - `A_SHARE_CONFIG["MANUAL_TTM_DIV"]`（到手现金流口径）
  - `A_SHARE_CONFIG["MANUAL_INDEX_YIELD"]`（指数口径，用于资产配置决策）
- 运行本月方案：`uv run -m src.strategy_core_dca 20000`
- 可选：对比 A股分红资产池（含个股/ETF）：`uv run -m src.strategy_a_share_dividend_targets`
