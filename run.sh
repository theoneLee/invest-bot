#!/bin/bash
echo ">>> 开始执行月度定投决策计算..."
uv run -m src.strategy_a_share
uv run -m src.strategy_hk_us
echo ">>> 计算结束。"
