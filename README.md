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
