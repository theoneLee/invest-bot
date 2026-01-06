
# 市场配置
BENCHMARK_TICKER = "^IRX"  # 3个月期美债收益率 (13 Week Treasury Bill)

# 全局手动覆盖 (如果不为空，则优先使用)
MANUAL_US_RATE = None  # 例如: 4.25

# 负债/机会成本基准（人民币）
# 用于“稳定现金流”策略的最低回报门槛：建议取较高的贷款利率或你自己的机会成本。
# 你提供的商业房贷利率为 3.0%，可作为默认门槛。
CNY_HURDLE_RATE = 3.0  # 单位: %

# 核心定投策略（不卖出，只调整当月新增资金在“红利权益/防御资产”之间的比例）
CORE_DCA_CONFIG = {
    # 当月新增资金的权益占比区间（上限按你的偏好设为 60%）
    "EQUITY_MIN": 0.40,
    "EQUITY_BASE": 0.50,
    "EQUITY_MAX": 0.60,
    # 利差阈值：股息率 - CNY_HURDLE_RATE
    "SPREAD_THRESHOLDS": {
        "OVERWEIGHT": 2.0,  # 利差>=2%：把新增资金权益打到上限
        "NEUTRAL": 1.0,     # 利差>=1%：按基础比例
    },
    # 防御资产仅给出“该买什么”的提示，不做数据抓取（按你的账户实际选择）
    "DEFENSE_SUGGESTION": "人民币货基/短债；或美元短债/短期国债（如 SGOV/T-Bills）",
}

# A股分红资产池（用于挑选“本月更值得加仓”的标的）
# 说明：
# - 股票分红口径建议用“过去12个月每股现金分红合计”（TTM），并手动维护。
# - 价格与分红默认都走手动（便于离线/网络受限环境）。
A_SHARE_DIVIDEND_TARGETS = {
    # ETF：默认复用 A_SHARE_CONFIG 的手动字段
    "563020": {
        "name": "红利低波 ETF",
        "kind": "etf",
        "MANUAL_PRICE": None,
        "MANUAL_TTM_DIV": None,
        "MANUAL_INDEX_YIELD": None,
    },
    # 中国神华
    "601088": {
        "name": "中国神华",
        "kind": "stock",
        "MANUAL_PRICE": None,
        "MANUAL_TTM_DIV": None,
    },
    # 农业银行
    "601288": {
        "name": "农业银行",
        "kind": "stock",
        "MANUAL_PRICE": None,
        "MANUAL_TTM_DIV": None,
    },
}

# A股策略配置
A_SHARE_CONFIG = {
    "CODE": "563020",  # 红利低波 ETF
    "MANUAL_PRICE": None,   # 手动覆盖价格
    "MANUAL_TTM_DIV": None, # 手动覆盖分红 (总额)
    # 指数口径股息率（用于资产配置决策；与基金到手分红率可能不同）
    # 例：H30269 指数股息率 4.75 -> 填 4.75
    "MANUAL_INDEX_YIELD": None,  # 单位: %
    "THRESHOLDS": {
        "BUY_DIP": 2.0,      # 强力买入利差
        "NORMAL_BUY": 1.0,   # 正常买入利差
        "TAKE_PROFIT": -0.5, # 止盈利差
        "STOP_BUY": 0.0      # 停买利差
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
        "manual_div": 0.42, 
        "MANUAL_PRICE": None
    },
    "0883.HK": {
        "name": "中国海洋石油",
        "manual_div": 1.39, 
        "MANUAL_PRICE": None
    },
    "0005.HK": {
        "name": "汇丰控股",
        "manual_div": 5.14, 
        "MANUAL_PRICE": None
    },
    "3110.HK": {
        "name": "GX恒生高股息",
        "manual_div": 3.0, # Approximate, needs update
        "MANUAL_PRICE": None
    }
}
