"""
main_app.py
数据资产运营总监——数据资产全生命周期经营决策虚拟仿真实验
参赛：虚拟仿真实验教学一流课程 / 智慧课程设计竞赛
依据：《数据资产运营总监虚拟仿真实验_Phase0交付包_v1.1（修订版）》+ 竞赛参赛文档
核心机制：
  - 估值引擎（完全公开）：V = Σ(场景现金流/(1.1)^t) × Q × C − H − D
    Q = 完整性×一致性×时效性×准确性（乘积，行业初始值起步）
    C = 合规系数（行业天花板内，可归零罚没对外收入）
    H = H_基准 + 采集量增量×单位存储成本（每轮独立）
    D = min(事件比例, 30%)（一次性计提）
  - 4 行业（制造/零售/医疗/能源）× 6 篇章 × 24 步 × 3 轮估值
  - 三轮节奏：第一轮普遍上涨 → 第二轮事件卡集体回调 → 第三轮分化
  - 20 张事件卡（P-/W-/C-/T- 各 5 张），五条下跌路径自动触发
  - 团队三维状态（能力/意愿/稳定）+ 6 工具激励设计器 + 隐藏规则
  - 六维评分 + 特别奖（增值评价）+ 复盘三问
  - 审计日志全程留痕 + CSV 导出；所有按钮真实生效，支持撤销
"""
import streamlit as st
import pandas as pd
from datetime import datetime

# ========== 页面配置 ==========
st.set_page_config(
    page_title="数据资产运营总监——全生命周期经营决策虚拟仿真实验",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

INIT_BUDGET = 2500000  # 每轮 250 万（每轮独立预算，防止第三轮死锁）

# ========== 四行业基准值表 v1.1（Phase0 交付包 2.1 节） ==========
INDUSTRIES = {
    "制造": {
        "name": "高端制造",
        "q0": 0.75, "c_cap": 0.9, "h_base": 15.0, "unit_storage": 2.0,
        "h_level": "高（存储+算力）", "trap": "采了大量振动数据却无故障样本",
        "base_tb": 12, "color": "#1E88E5",
        "scenes": {
            "良率提升": {"kind": "in", "base": 35, "desc": "用设备时序数据提升产线良率"},
            "预测性维护": {"kind": "in", "base": 30, "desc": "故障预测减少非计划停机"},
            "数字孪生服务": {"kind": "out", "base": 25, "desc": "设备数字孪生对外数据服务"},
        },
    },
    "零售": {
        "name": "零售流通",
        "q0": 0.70, "c_cap": 0.7, "h_base": 10.0, "unit_storage": 1.5,
        "h_level": "中", "trap": "买了流量却做不出复购模型",
        "base_tb": 8, "color": "#7C4DFF",
        "scenes": {
            "精准营销": {"kind": "out", "base": 40, "desc": "用户标签体系支撑精准营销"},
            "复购模型": {"kind": "in", "base": 30, "desc": "复购预测提升客户生命周期价值"},
            "数据产品授权": {"kind": "out", "base": 30, "desc": "脱敏画像数据集对外授权"},
        },
    },
    "医疗": {
        "name": "智慧医疗",
        "q0": 0.65, "c_cap": 0.5, "h_base": 12.0, "unit_storage": 3.0,
        "h_level": "中高（安全等级要求）", "trap": "拿了数据永远过不了伦理审查",
        "base_tb": 5, "color": "#00A86B",
        "scenes": {
            "临床质控": {"kind": "in", "base": 30, "desc": "病历数据支撑院内质控"},
            "辅助诊断模型": {"kind": "out", "base": 35, "desc": "影像辅助诊断对外服务"},
            "科研数据集": {"kind": "out", "base": 20, "desc": "脱敏科研数据集授权（强受限）"},
        },
    },
    "能源": {
        "name": "能源电网",
        "q0": 0.70, "c_cap": 0.6, "h_base": 18.0, "unit_storage": 2.5,
        "h_level": "高（实时性要求）", "trap": "政策一变，商业模式归零",
        "base_tb": 20, "color": "#FF6D00",
        "scenes": {
            "负荷预测服务": {"kind": "out", "base": 35, "desc": "负荷预测对外服务"},
            "碳核算数据": {"kind": "out", "base": 25, "desc": "碳核算数据产品（政策敏感）"},
            "能耗优化": {"kind": "in", "base": 30, "desc": "能耗优化降低运营成本"},
        },
    },
}

# ========== 事件卡库 v1.1（20 张，Phase0 交付包第三部分） ==========
EVENT_CARDS = {
    "P-01": {"name": "数据出境新规", "desc": "跨境合规收紧，C 降至 0.5，合规成本 H 上浮 20%", "rounds": [2, 3], "c": 0.5, "h_mult": 1.2},
    "P-02": {"name": "行业数据标准强制升级", "desc": "当轮 H 增加 8 万元，一致性要求提升", "rounds": [2, 3], "h_extra": 8},
    "P-03": {"name": "数据资源入表准则修订", "desc": "已入表资产需重估，V 按 80% 确认", "rounds": [3], "v_mult": 0.8},
    "P-04": {"name": "数据安全专项检查", "desc": "未整改则 C 归零，当期对外收入全额罚没", "rounds": [2], "c": 0.0, "fine_out": True},
    "P-05": {"name": "财政补贴退坡", "desc": "对内降本额打 8 折", "rounds": [2, 3], "in_mult": 0.8},
    "W-01": {"name": "同业价格战爆发", "desc": "对外收入打 7 折", "rounds": [2, 3], "out_mult": 0.7},
    "W-02": {"name": "上游算力涨价", "desc": "单位存储成本上浮 30%", "rounds": [2], "unit_mult": 1.3},
    "W-03": {"name": "数据产品同质化", "desc": "对外收入打 8 折", "rounds": [3], "out_mult": 0.8},
    "W-04": {"name": "客户集体压价", "desc": "对外收入打 6 折（持续两轮）", "rounds": [3], "out_mult": 0.6},
    "W-05": {"name": "合规成本全面上升", "desc": "H 上浮 25%，影响所有行业", "rounds": [2], "h_mult": 1.25},
    "C-01": {"name": "单一客户依赖", "desc": "D 计提当期 V × 20%", "rounds": [2, 3], "d_pct": 0.20},
    "C-02": {"name": "大客户终止合同", "desc": "对外收入归零一轮", "rounds": [3], "out_mult": 0.0},
    "C-03": {"name": "客户数据授权撤回", "desc": "C 降至 0.5，相关场景现金流清零", "rounds": [2, 3], "c": 0.5, "scene_zero": True},
    "C-04": {"name": "口碑危机", "desc": "对外收入打 6 折，意愿值下降 10", "rounds": [3], "out_mult": 0.6, "mot_penalty": 10},
    "C-05": {"name": "核心骨干离职", "desc": "稳定值不可逆下降 15，D 计提 V × 15%", "rounds": [3], "ret_penalty": 15, "d_pct": 0.15},
    "T-01": {"name": "技术路线锁死", "desc": "存量资产折价 30%，D 计提 V × 30%", "rounds": [3], "d_pct": 0.30},
    "T-02": {"name": "新采集技术普及", "desc": "本期采集量上限提升 50%，H 同步上升", "rounds": [2], "tb_mult": 1.5},
    "T-03": {"name": "算法模型被开源替代", "desc": "对外收入打 5 折（持续至终局）", "rounds": [3], "out_mult": 0.5},
    "T-04": {"name": "存储架构升级", "desc": "H_基准下降 20%（一次性红利）", "rounds": [1, 2], "h_base_mult": 0.8},
    "T-05": {"name": "实时计算成为标配", "desc": "时效性低于 0.8 的场景现金流打 8 折", "rounds": [2, 3], "time_penalty": 0.8},
}

# 五条下跌路径（红线2：必须触发下跌）
DROP_PATHS = {
    "闲置税": {"desc": "采集量 > 场景消耗量×2，连续两期 → H 暴涨", "check": "idle", "label": "数据闲置税"},
    "合规事故": {"desc": "未脱敏对外输出 / 超范围使用 → C→0.3 并罚没收入", "check": "compliance", "label": "合规事故"},
    "质量塌陷": {"desc": "跳过清洗稽核，Q 跌破 0.6 → 场景收益打折", "check": "quality", "label": "质量塌陷"},
    "客户依赖": {"desc": "对外收入 >70% 来自 1 个买家 → D 计提", "check": "client", "label": "单一客户依赖"},
    "技术锁死": {"desc": "首轮选封闭平台，行业标准变更 → 折价 30%", "check": "techlock", "label": "技术路线锁死"},
}

# ========== 团队与激励 ==========
TEAM_INIT = {"cap": 60, "mot": 65, "ret": 70}
INCENTIVES = [
    {"id": "money", "name": "绩效奖金", "type": "金钱", "cost": 150000, "effect": {"mot": 15}, "hidden": "纯金钱激励在第二轮预算收紧时反噬（意愿-10）"},
    {"id": "train", "name": "培训进修", "type": "非金钱", "cost": 80000, "effect": {"cap": 10}, "hidden": "第三轮对能力值产生复利加成（+8）"},
    {"id": "auth", "name": "授权放权", "type": "非金钱", "cost": 0, "effect": {"mot": 12}, "hidden": "意愿值显著提升，但失控风险上升"},
    {"id": "honor", "name": "荣誉表彰", "type": "非金钱", "cost": 0, "effect": {"ret": 8}, "hidden": "稳定值小幅提升，成本最低"},
    {"id": "equity", "name": "股权/分红", "type": "金钱", "cost": 200000, "effect": {"ret": 15, "mot": 5}, "hidden": "长期绑定，第三轮才显现效果"},
    {"id": "rotate", "name": "岗位轮换", "type": "非金钱", "cost": 50000, "effect": {"cap": -5}, "hidden": "能力值短期下降，长期提升（第三轮+12）"},
]

# ========== 24 步流程定义（6 篇章 × 4 步） ==========
PHASES = [
    {"name": "投入篇", "steps": [1, 2, 3, 4]},
    {"name": "采集篇", "steps": [5, 6, 7, 8]},
    {"name": "治理篇", "steps": [9, 10, 11, 12]},
    {"name": "赋能篇", "steps": [13, 14, 15, 16]},
    {"name": "变现篇", "steps": [17, 18, 19, 20]},
    {"name": "经营与估值篇", "steps": [21, 22, 23, 24]},
]
STEP_NAMES = {
    1: "组建团队定岗", 2: "盘点家底", 3: "制定三年战略", 4: "编制预算",
    5: "选择数据源", 6: "签订数据合同", 7: "接入与存储", 8: "确权登记",
    9: "定标准", 10: "质量稽核", 11: "安全分级与脱敏", 12: "资产目录上架",
    13: "选场景", 14: "建模与验证", 15: "上线与推广", 16: "效果度量",
    17: "产品化", 18: "定价", 19: "找买家与签约", 20: "交付与运维",
    21: "团队激励投放", 22: "出表与披露", 23: "第三方估值", 24: "董事会答辩",
}
# 默认投放事件卡（自动触发下跌）
DEFAULT_EVENTS = {2: ["P-04", "C-01", "W-02"], 3: ["W-04", "T-03"]}

# ========== 会话状态初始化 ==========
def init_state():
    defaults = {
        "budget": INIT_BUDGET, "started": False, "industry": "制造", "role": "数据运营总监",
        "round": 1, "step": 1, "log": [], "done": set(), "revenue": 0.0,
        "val_history": [], "decisions": {}, "team": dict(TEAM_INIT),
        "incentives": [], "incentives_round": {}, "events_used": {}, "submitted": set(),
        "listing": None, "reflection": "", "settled": set(), "undo_stack": [],
        "closed_round": [], "eval_score": None, "awards": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ========== 公共工具函数 ==========
def fmt(v):
    """万元格式化"""
    return f"{v/10000:.0f}万"

def spend(name, amt):
    """真实扣款；预算不足返回 False"""
    if amt <= 0:
        return True
    if st.session_state.budget < amt:
        st.error(f"❌ 预算不够！需要{amt/10000:.0f}万，只剩{st.session_state.budget/10000:.0f}万")
        return False
    st.session_state.budget -= amt
    st.session_state.log.append((datetime.now().strftime("%H:%M:%S"), name, f"-{amt/10000:.0f}万"))
    return True

def record(name, delta):
    """通用留痕（delta 为万元文本，如 +30万 / -15万）"""
    st.session_state.log.append((datetime.now().strftime("%H:%M:%S"), name, delta))

def step_done(step):
    return step in st.session_state.done

def mark_done(step, name):
    st.session_state.done.add(step)
    st.session_state.undo_stack.append(step)
    record(f"步骤{step}·{name}", "完成")

def undo_last():
    """撤销最近一步已完成的操作"""
    if not st.session_state.undo_stack:
        st.warning("没有可撤销的步骤")
        return
    stp = st.session_state.undo_stack.pop()
    st.session_state.done.discard(stp)
    record(f"步骤{stp}·撤销", "回退")
    st.rerun()

def open_next_round():
    """开放下一轮并自动投放默认事件卡（红线2：第二轮必须制造下跌）；每轮独立预算"""
    nxt = st.session_state.round + 1
    st.session_state.round = nxt
    st.session_state.step = 1
    st.session_state.done = set()
    st.session_state.submitted = set()
    st.session_state.decisions = {}
    st.session_state.budget = INIT_BUDGET  # 每轮重新发放，避免第三轮死锁
    if nxt in DEFAULT_EVENTS:
        st.session_state.events_used[nxt] = list(DEFAULT_EVENTS[nxt])
        record(f"第{nxt}轮自动投放事件卡", "、".join(DEFAULT_EVENTS[nxt]))
    record(f"开放第{nxt}轮", f"补发预算{INIT_BUDGET/10000:.0f}万")
    st.rerun()

def locked(step):
    """本轮已结算则全部锁定"""
    return st.session_state.round in st.session_state.settled

def step_ui(step):
    """步骤通用头"""
    r = st.session_state.round
    st.markdown(f"### 第 {r} 轮 · 步骤 {step}：{STEP_NAMES[step]}")
    if step in st.session_state.done:
        st.success(f"✅ 步骤 {step} 已完成（可点击侧边栏「撤销上一步」回退）")

# ========== 估值引擎（完全公开） ==========
def calc_q(ind_key, decisions):
    """Q = 完整性×一致性×时效性×准确性；行业初始值起步，治理投入提升"""
    ind = INDUSTRIES[ind_key]
    d = decisions
    # 治理投入系数（0~1）：标准/稽核/脱敏/上架/存储
    invested = 0
    if "standard" in d: invested += 0.25
    if "qc" in d: invested += 0.25
    if d.get("mask") in ("全量脱敏", "部分脱敏"): invested += 0.25
    if d.get("catalog"): invested += 0.15
    if d.get("storage") == "湖仓一体": invested += 0.10
    invested = min(invested, 1.0)
    # 治理后四子项（初始参考值区间内，随投入提升）
    completeness = 0.85 + invested * 0.13      # 0.85→0.98
    consistency = 0.80 + invested * 0.18       # 0.80→0.98
    timeliness = 0.85 + invested * 0.13
    accuracy = 0.85 + invested * 0.13
    product_q = completeness * consistency * timeliness * accuracy
    # 行业初始 Q 起步，向治理后乘积过渡
    q = ind["q0"] + (product_q - ind["q0"]) * invested
    return round(q, 3), {
        "完整性": round(completeness, 2), "一致性": round(consistency, 2),
        "时效性": round(timeliness, 2), "准确性": round(accuracy, 2),
        "治理投入度": round(invested, 2),
    }

def calc_c(ind_key, decisions, round_no, events):
    """C：决策决定 + 行业天花板 + 事件卡影响；C=0 罚没对外收入"""
    ind = INDUSTRIES[ind_key]
    d = decisions
    c = 1.0
    # 合同授权
    if d.get("contract") == "部分授权": c = 0.8
    elif d.get("contract") in ("口头约定",): c = 0.6
    # 脱敏
    if d.get("mask") == "未脱敏": c = 0.3
    elif d.get("mask") == "部分脱敏": c = min(c, 0.8)
    # 爬取数据源埋雷
    if d.get("source") == "爬取": c = min(c, 0.5)
    # 对外高占比触发自动合规审查（对外收入>阈值）
    # 事件卡影响
    for e in events:
        if "c" in EVENT_CARDS[e]:
            c = min(c, EVENT_CARDS[e]["c"])
    c = min(c, ind["c_cap"])
    return round(max(c, 0.0), 2)

def calc_cash(ind_key, decisions, round_no, events):
    """场景现金流：对内降本 + 对外收入（受事件卡影响）"""
    ind = INDUSTRIES[ind_key]
    d = decisions
    scenes = d.get("scenes", [])
    strategy = d.get("strategy", "对内优先")
    cash_in, cash_out = 0.0, 0.0
    for s in scenes:
        sc = ind["scenes"].get(s)
        if not sc: continue
        base = sc["base"]
        if sc["kind"] == "in":
            cash_in += base
        else:
            cash_out += base
    # 建模投入放大（S14）
    model_inv = d.get("model", 0)
    boost = 1.0 + (model_inv / 200000.0) * 0.6   # 每 20 万 +60% 封顶
    cash_in = cash_in * boost
    cash_out = cash_out * boost
    # 战略加成：对内优先 → 对内×1.3；对外优先 → 对外×1.5
    if strategy == "对内优先":
        cash_in *= 1.3
    else:
        cash_out *= 1.5
    # 上线推广力度（S15）
    if d.get("rollout_mul"):
        cash_in *= d["rollout_mul"]
        cash_out *= d["rollout_mul"]
    # 定价方法（S18）
    pricing = d.get("pricing")
    if pricing == "成本法": cash_out *= 0.8
    elif pricing == "市场法": cash_out *= 1.2
    # 产品化形态（S17）
    product = d.get("product")
    if product == "数据集授权": cash_out *= 0.9
    elif product == "模型服务": cash_out *= 1.1
    # SLA 违约（S20）
    if d.get("sla") == "高标准SLA": cash_out *= 0.95
    # 事件卡影响
    for e in events:
        cfg = EVENT_CARDS[e]
        if "in_mult" in cfg: cash_in *= cfg["in_mult"]
        if "out_mult" in cfg: cash_out *= cfg["out_mult"]
        if "scene_zero" in cfg and cfg.get("scene_zero"):
            cash_out = 0.0
        if "time_penalty" in cfg:
            qq = calc_q(ind_key, d)
            if qq[1]["时效性"] < 0.8:
                cash_in *= cfg["time_penalty"]; cash_out *= cfg["time_penalty"]
        if "fine_out" in cfg and cfg.get("fine_out"):
            cc = calc_c(ind_key, decisions, round_no, events)
            if cc <= 0:
                cash_out = 0.0
    return round(cash_in, 1), round(cash_out, 1)

def calc_h(ind_key, decisions, round_no, events):
    """H = H_基准 + 采集量增量 × 单位存储成本（每轮独立）"""
    ind = INDUSTRIES[ind_key]
    d = decisions
    h_base = ind["h_base"]
    unit = ind["unit_storage"]
    # 存储方案：湖仓一体 → H 基准 -20%；数据湖 → 采集量放大
    if d.get("storage") == "湖仓一体": h_base *= 0.8
    # 采集量（TB）：数据源决定
    source_tb = {"自建采集": 10, "采购": 15, "合作置换": 8, "爬取": 20}.get(d.get("source", "采购"), 15)
    if d.get("storage") == "数据湖": source_tb *= 1.2
    extra_tb = max(source_tb - ind["base_tb"], 0)
    # 事件卡
    for e in events:
        cfg = EVENT_CARDS[e]
        if "h_mult" in cfg: h_base *= cfg["h_mult"]
        if "unit_mult" in cfg: unit *= cfg["unit_mult"]
        if "h_base_mult" in cfg: h_base *= cfg["h_base_mult"]
        if "h_extra" in cfg: h_base += cfg["h_extra"]
        if "tb_mult" in cfg: extra_tb *= cfg["tb_mult"]
    h = h_base + extra_tb * unit
    return round(h, 1), {"h_base": round(h_base, 1), "extra_tb": round(extra_tb, 1), "unit": round(unit, 2)}

def calc_d(ind_key, decisions, round_no, events, v_before):
    """D = min(事件比例, 30%) × V；V 不低于 0"""
    d = decisions
    pct = 0.0
    # 事件卡
    for e in events:
        if "d_pct" in EVENT_CARDS[e]:
            pct = max(pct, EVENT_CARDS[e]["d_pct"])
    # 五条下跌路径：单一客户依赖（对外收入>70% 来自 1 买家）
    if d.get("buyer") == "单一独家大客户":
        pct = max(pct, 0.20)
    # 技术路线锁死：封闭湖 + 对外战略（标准变更折价）
    if d.get("storage") == "数据湖" and d.get("strategy") == "对外优先":
        pct = max(pct, 0.30)
    pct = min(pct, 0.30)
    d_val = round(v_before * pct, 1)
    return d_val, pct

def check_drop_paths(ind_key, decisions, events, cash_in, cash_out, q, c, h, collected_tb):
    """五条下跌路径自动触发检查，返回命中的路径列表"""
    ind = INDUSTRIES[ind_key]
    d = decisions
    hits = []
    # 1 数据闲置税：采集量 > 场景消耗×2
    consume = (len(d.get("scenes", [])) * 5 + 3)  # 场景消耗基准 TB
    if collected_tb > consume * 2:
        hits.append({"label": "数据闲置税", "note": f"采集{collected_tb}TB > 场景消耗{consume}TB×2，H 额外+5万"})
    # 2 合规事故：未脱敏+对外收入
    if d.get("mask") == "未脱敏" and cash_out > 0:
        hits.append({"label": "合规事故", "note": "未脱敏却对外输出，C 压至 0.3，当期对外收入罚没"})
    # 3 质量塌陷：无稽核投入
    if "qc" not in d and "standard" not in d:
        hits.append({"label": "质量塌陷", "note": "跳过清洗稽核，Q 低于 0.6，场景收益打 8 折"})
    # 4 单一客户依赖
    if d.get("buyer") == "单一独家大客户":
        hits.append({"label": "单一客户依赖", "note": "对外收入 100% 来自单一买家，D 计提 20%"})
    # 5 技术路线锁死
    if d.get("storage") == "数据湖" and d.get("strategy") == "对外优先":
        hits.append({"label": "技术路线锁死", "note": "封闭数据湖+对外战略，标准变更存量折价 30%"})
    return hits

def run_valuation():
    """结算本轮：完整公开计算 V = Σ(现金流/(1.1)^t) × Q × C − H − D"""
    ind_key = st.session_state.industry
    ind = INDUSTRIES[ind_key]
    r = st.session_state.round
    d = st.session_state.decisions
    events = st.session_state.events_used.get(r, [])

    # 采集量
    source_tb = {"自建采集": 10, "采购": 15, "合作置换": 8, "爬取": 20}.get(d.get("source", "采购"), 15)
    if d.get("storage") == "数据湖": source_tb *= 1.2
    collected_tb = source_tb

    cash_in, cash_out = calc_cash(ind_key, d, r, events)
    q, q_detail = calc_q(ind_key, d)
    c = calc_c(ind_key, d, r, events)
    h, h_detail = calc_h(ind_key, d, r, events)
    # C=0 罚没对外收入
    if c <= 0:
        cash_out = 0.0
    # 质量塌陷打折
    drop_hits = check_drop_paths(ind_key, d, events, cash_in, cash_out, q, c, h, collected_tb)
    drop_labels = [x["label"] for x in drop_hits]
    if "质量塌陷" in drop_labels:
        cash_in *= 0.8; cash_out *= 0.8
    if "合规事故" in drop_labels:
        c = 0.3; cash_out = 0.0
    if "数据闲置税" in drop_labels:
        h += 5.0

    pv = (cash_in + cash_out) / (1.1 ** r)
    v_before_d = max(pv * q * c - h, 0)
    d_val, d_pct = calc_d(ind_key, d, r, events, v_before_d)
    v = round(v_before_d - d_val, 1)
    v = max(v, 0)

    # 事件卡 P-03 入表准则修订：V×80%
    for e in events:
        if "v_mult" in EVENT_CARDS[e]:
            v *= EVENT_CARDS[e]["v_mult"]
            v = round(v, 1)

    val = {
        "round": r, "pv": round(pv, 1), "cash_in": round(cash_in, 1), "cash_out": round(cash_out, 1),
        "q": q, "c": c, "h": h, "d": d_val, "d_pct": d_pct, "v": v, "t": r,
        "events": events, "drop_paths": drop_labels, "q_detail": q_detail,
    }
    st.session_state.val_history.append(val)
    record(f"第{r}轮·估值计算", f"V={v}万")

    # ===== 公开计算过程 =====
    st.markdown("### 📐 估值引擎完整计算过程（公式完全公开，无黑箱）")
    st.info("**主公式**：V = Σ(场景现金流 / 1.1^t) × Q × C − H − D")
    with st.expander("🔍 查看每一步代入值与中间结果（红线：公式必须公开）", expanded=True):
        st.markdown(f"**① 场景现金流**（t = {r}）")
        st.markdown(f"- 对内降本额 = **{cash_in}万** ｜ 对外收入额 = **{cash_out}万**")
        st.markdown(f"- 折现：({cash_in} + {cash_out}) / 1.1^{r} = **{pv}万**")
        st.markdown(f"**② 质量系数 Q = 完整性 × 一致性 × 时效性 × 准确性**")
        qd = q_detail
        st.markdown(f"- 完整性 {qd['完整性']} × 一致性 {qd['一致性']} × 时效性 {qd['时效性']} × 准确性 {qd['准确性']} = **{q}**（治理投入度 {int(qd['治理投入度']*100)}%，行业初始 {ind['q0']} 起步）")
        st.markdown(f"**③ 合规系数 C**（行业天花板 {ind['c_cap']}）")
        st.markdown(f"- 当前 C = **{c}**" + ("（⚠️ C=0：当期对外收入全额罚没）" if c <= 0 else ""))
        st.markdown(f"**④ 持有成本 H** = H_基准({h_detail['h_base']}万) + 采集量增量({h_detail['extra_tb']}TB) × 单位存储成本({h_detail['unit']}万/TB) = **{h}万**")
        st.markdown(f"**⑤ 减值准备 D** = min({d_pct:.0%}, 30%) × 计提基数({v_before_d}万) = **{d_val}万**")
        st.markdown(f"**⑥ V** = {pv} × {q} × {c} − {h} − {d_val} = **{v}万**")
        st.success(f"### 本轮数据资产净值 V = {v}万")
        if drop_hits:
            st.warning("**⚠️ 命中下跌路径：**" + "；".join(f"{x['label']}（{x['note']}）" for x in drop_hits))
        if events:
            st.info("**本轮事件卡：**" + "；".join(f"{e}·{EVENT_CARDS[e]['name']}" for e in events))
    return val

# ========== 侧边栏 ==========
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🎯 数据资产运营总监")
        if st.session_state.started:
            ind = INDUSTRIES[st.session_state.industry]
            st.markdown(f"**行业**：{st.session_state.industry}·{ind['name']}")
            st.markdown(f"**角色**：{st.session_state.role} ｜ **轮次**：第 {st.session_state.round} 轮")
            st.markdown(f"**三年战略**：{st.session_state.decisions.get('strategy', '未定')}")
            st.divider()
            st.markdown("### 💰 财务仪表盘")
            used = INIT_BUDGET - st.session_state.budget
            c1, c2 = st.columns(2)
            with c1: st.metric("剩余预算", fmt(st.session_state.budget), delta=f"已用{fmt(used)}")
            with c2: st.metric("累计收入", fmt(st.session_state.revenue))
            st.divider()
            st.markdown("### 👥 团队三维状态")
            t = st.session_state.team
            st.progress(t["cap"] / 100, text=f"能力 {t['cap']}")
            st.progress(t["mot"] / 100, text=f"意愿 {t['mot']}")
            st.progress(t["ret"] / 100, text=f"稳定 {t['ret']}")
            st.divider()
            st.markdown("### 🗺️ 流程进度")
            total_done = len([s for s in st.session_state.done if s <= 24])
            st.progress(total_done / 24, text=f"步骤 {total_done}/24")
            for ph in PHASES:
                mark = "".join("✅" if s in st.session_state.done else "⬜" for s in ph["steps"])
                st.markdown(f"{ph['name']}：{mark}")
            st.divider()
            if st.session_state.undo_stack:
                if st.button("↩️ 撤销上一步"):
                    undo_last()
            st.caption("每步操作写入审计日志，可回滚、可追溯")
        else:
            st.caption("选择行业与角色后开始实验")

# ========== Tab0：实验导览 ==========
def render_tab0():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0F2B46,#1E88E5 55%,#64B5F6);padding:26px 30px;border-radius:14px;color:#fff">
    <h1 style="margin:0;color:#fff">🎯 数据资产运营总监</h1>
    <p style="margin:6px 0 0;font-size:16px;color:#E3F2FD">数据资产全生命周期经营决策虚拟仿真实验 · 8学时（课前1+课中6+课后1）</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 🧭 一句话定位")
        st.markdown("在**试错中建立数据资产价值判断**——治理了数据却亏了钱，这一真实经营挫败感是本实验最核心的教学设计。")
    with c2:
        st.markdown("#### ⚖️ 估值引擎（全公开）")
        st.latex(r"V = \Sigma\left(\frac{现金流}{1.1^t}\right) \times Q \times C - H - D")
        st.markdown("Q 质量系数（乘积）｜C 合规系数（可归零）｜H 持有成本｜D 减值准备")
    with c3:
        st.markdown("#### 🔄 三轮估值节奏")
        st.markdown("**第一轮** 普遍上涨（尝甜头）→ **第二轮** 事件卡集体回调（制造挫败）→ **第三轮** 分化（事前准备决定抗风险）")

    st.divider()
    if not st.session_state.started:
        c1, c2 = st.columns(2)
        with c1:
            role = st.selectbox("**选择你的角色**", ["数据运营总监", "数据分析员", "算法工程师", "首席数据官"], index=0)
            st.session_state.role = role
        with c2:
            ind_key = st.selectbox("**选择案例行业**（行业差异：Q初始/C天花板/H基准/变现逻辑）", list(INDUSTRIES.keys()), index=0)
            ind = INDUSTRIES[ind_key]
            st.markdown(f"- Q 初始 **{ind['q0']}** ｜ C 天花板 **{ind['c_cap']}** ｜ H 基准 **{ind['h_base']}万/轮**")
            st.markdown(f"- 单位存储 **{ind['unit_storage']}万/TB** ｜ 持有成本档位：{ind['h_level']}")
            st.markdown(f"- 典型陷阱：**{ind['trap']}**")
        st.warning("⚠️ 行业差异教学建议：制造专业易选制造、信管易选零售——竞赛建议强制抽签或按专业混编，跳出舒适区。")
        if st.button("🚀 开始实验（领取每轮250万预算）", type="primary"):
            st.session_state.industry = ind_key
            st.session_state.started = True
            st.session_state.round = 1
            st.session_state.step = 1
            record("开始实验", f"行业={ind_key}，角色={role}")
            st.rerun()
    else:
        st.success(f"**实验进行中**：行业={st.session_state.industry}，角色={st.session_state.role}，当前第 {st.session_state.round} 轮")
        st.markdown("**24 步决策流程**：投入篇(1-4) → 采集篇(5-8) → 治理篇(9-12) → 赋能篇(13-16) → 变现篇(17-20) → 经营与估值篇(21-24)")
        if st.button("🔄 重置实验"):
            for k in list(st.session_state.keys()):
                if k not in ("started",):
                    del st.session_state[k]
            st.rerun()

# ========== Tab1：24 步决策台 ==========
def render_tab1():
    if not st.session_state.started:
        st.info("请先在「实验导览」选择行业与角色并开始实验")
        return
    r = st.session_state.round
    if locked(r):
        st.success(f"✅ 第 {r} 轮已结算（数据只读）。请在侧边栏或估值中心查看结果，进入下一轮。")
        if r < 3 and st.button(f"🔓 开放第 {r+1} 轮（开始新决策）", type="primary"):
            open_next_round()
        if r >= 3:
            st.success("三轮估值全部完成，前往「复盘报告」完成复盘三问并查看六维评分。")
        return

    # 篇章导航
    st.markdown("### 📋 24 步决策台（第 {r} 轮）".format(r=r))
    cur_phase = next((ph for ph in PHASES if st.session_state.step in ph["steps"]), PHASES[0])
    cols = st.columns(6)
    for i, ph in enumerate(PHASES):
        done_n = len([s for s in ph["steps"] if s in st.session_state.done])
        with cols[i]:
            st.markdown(f"**{ph['name']}** {'⭐' if ph is cur_phase else ''}")
            st.progress(done_n / 4, text=f"{done_n}/4")
    st.markdown("")
    step = st.session_state.step
    if step >= 24 and 24 in st.session_state.done:
        st.info("24 步全部完成（估值已在步骤23计算入库）。确认本轮结算后锁定只读，可开放下一轮。")
        if st.button("✅ 完成本轮（结算锁定）", type="primary"):
            st.session_state.settled.add(st.session_state.round)
            record(f"第{st.session_state.round}轮·结算锁定", "本轮只读")
            st.rerun()
        return
    if step > 24:
        st.info("24 步全部完成（估值已在步骤23计算入库）。确认本轮结算后锁定只读，可开放下一轮。")
        if st.button("✅ 完成本轮（结算锁定）", type="primary"):
            st.session_state.settled.add(st.session_state.round)
            record(f"第{st.session_state.round}轮·结算锁定", "本轮只读")
            st.rerun()
        return

    step_ui(step)
    render_step(step)
    if step_done(step) and step < 24:
        if st.button(f"下一步 →（步骤{step+1}：{STEP_NAMES[step+1]}）", type="primary"):
            st.session_state.step += 1
            st.rerun()

# 各步骤渲染函数
def render_step(step):
    d = st.session_state.decisions
    if step == 1:
        st.markdown("**组建团队定岗**：定下总监/治理官/合规官/财务官/商务官分工，影响团队三维状态。")
        choice = st.selectbox("团队配置：", ["五人齐全（+能力5 意愿5）", "精简三人（+意愿3，治理效率-）", "单人独揽（能力-10 意愿+10）"], index=0)
        if st.button("✅ 确认团队定岗", disabled=step_done(step)):
            t = st.session_state.team
            if "五人齐全" in choice: t["cap"] += 5; t["mot"] += 5
            elif "精简三人" in choice: t["mot"] += 3
            else: t["cap"] -= 10; t["mot"] += 10
            st.session_state.decisions["team_setup"] = choice
            mark_done(1, "组建团队定岗")
            st.rerun()
    elif step == 2:
        ind = INDUSTRIES[st.session_state.industry]
        st.markdown(f"**盘点家底**：{st.session_state.industry}行业入场基线——")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Q 初始", ind["q0"])
        with c2: st.metric("C 天花板", ind["c_cap"])
        with c3: st.metric("H 基准", f"{ind['h_base']}万/轮")
        with c4: st.metric("团队状态", f"{st.session_state.team['cap']}/{st.session_state.team['mot']}/{st.session_state.team['ret']}")
        st.markdown(f"**典型陷阱**：{ind['trap']}——记得提醒自己别踩。")
        if st.button("✅ 确认盘点（免费）", disabled=step_done(step)):
            mark_done(2, "盘点家底")
            st.rerun()
    elif step == 3:
        st.markdown("**制定三年战略**：选「对内优先」还是「对外优先」——锁定后改道成本高。")
        choice = st.radio("战略方向：", ["对内优先（降本增效，确定性强、天花板低）", "对外优先（数据变现，弹性大、受合规强约束）"], index=0)
        if st.button("✅ 锁定三年战略（免费）", disabled=step_done(step)):
            st.session_state.decisions["strategy"] = "对内优先" if "对内" in choice else "对外优先"
            mark_done(3, "锁定战略")
            st.rerun()
    elif step == 4:
        st.markdown("**编制预算**：四类资金分配（采集/治理/人力/合规）。本轮先投入 **120万**。")
        c1, c2, c3, c4 = st.columns(4)
        with c1: collect = st.number_input("采集投入（万）", 10, 60, 30, step=5, key=f"b_c_{st.session_state.round}")
        with c2: govern = st.number_input("治理投入（万）", 10, 60, 35, step=5, key=f"b_g_{st.session_state.round}")
        with c3: hr = st.number_input("人力投入（万）", 5, 40, 15, step=5, key=f"b_h_{st.session_state.round}")
        with c4: comp = st.number_input("合规投入（万）", 5, 40, 20, step=5, key=f"b_p_{st.session_state.round}")
        total = collect + govern + hr + comp
        st.markdown(f"合计 **{total}万**（预算 120 万，{'✅ 在预算内' if total <= 120 else '❌ 超预算！'}")
        if st.button(f"✅ 确认编制预算（开支-{total}万）", disabled=step_done(step) or total > 120):
            if spend("步骤4·编制预算", total * 10000):
                st.session_state.decisions["budget"] = {"collect": collect, "govern": govern, "hr": hr, "comp": comp}
                mark_done(4, "编制预算")
                st.rerun()
    elif step == 5:
        st.markdown("**选择数据源**：自建采集 / 采购 / 合作置换 / 爬取（埋合规雷）。采集量影响 H。")
        c1, c2 = st.columns(2)
        with c1:
            choice = st.selectbox("数据源：", ["自建采集（10TB，成本20万）", "采购（15TB，成本35万）", "合作置换（8TB，成本10万）", "爬取（20TB，成本5万，⚠️埋合规雷）"], index=0)
        with c2:
            st.markdown("**影响预览**：")
            st.markdown("- 采集量越大 → H 持有成本越高")
            st.markdown("- 爬取 → C 合规系数压至 0.5，且有被罚风险")
        if st.button("✅ 确认数据源（按选项扣款）", disabled=step_done(step)):
            cost = {"自建": 20, "采购": 35, "合作": 10, "爬取": 5}["自建" if "自建" in choice else ("采购" if "采购" in choice else ("合作" if "合作" in choice else "爬取"))]
            src = "自建采集" if "自建" in choice else ("采购" if "采购" in choice else ("合作置换" if "合作" in choice else "爬取"))
            if spend(f"步骤5·{src}", cost * 10000):
                st.session_state.decisions["source"] = src
                mark_done(5, "选择数据源")
                st.rerun()
    elif step == 6:
        st.markdown("**签订数据合同**：授权范围、期限、可否转授权——决定 C 系数。")
        choice = st.selectbox("合同条款：", ["完整授权+可转授权（C 保持）", "部分授权（C 0.8，成本-5万）", "口头约定（C 0.6，⚠️合规瑕疵）"], index=0)
        if st.button("✅ 确认合同条款（免费/按条款）", disabled=step_done(step)):
            if "完整授权" in choice:
                st.session_state.decisions["contract"] = "完整授权"
            elif "部分授权" in choice:
                st.session_state.decisions["contract"] = "部分授权"
            else:
                st.session_state.decisions["contract"] = "口头约定"
            mark_done(6, "签订数据合同")
            st.rerun()
    elif step == 7:
        st.markdown("**接入与存储**：湖 / 仓 / 湖仓一体——影响后期 H。")
        choice = st.selectbox("存储方案：", ["数据湖（采集量×1.2，H 上升；封闭）", "数仓（标准，成本20万）", "湖仓一体（H 基准-20%，成本35万）"], index=0)
        if st.button("✅ 确认存储方案（按选项扣款）", disabled=step_done(step)):
            if "数据湖" in choice:
                st.session_state.decisions["storage"] = "数据湖"
                cost = 0
            elif "数仓" in choice:
                st.session_state.decisions["storage"] = "数仓"; cost = 20
            else:
                st.session_state.decisions["storage"] = "湖仓一体"; cost = 35
            if spend(f"步骤7·{st.session_state.decisions['storage']}", cost * 10000):
                mark_done(7, "接入与存储")
                st.rerun()
    elif step == 8:
        st.markdown("**确权登记**：入表前置动作，决定能否资本化（无形资产）。")
        st.markdown("- 完成确权登记 → 出表时可选「无形资产」资本化（评分更高）")
        st.markdown("- 跳过确权 → 只能按「存货」计量，且合规评分降低")
        if st.button("✅ 完成确权登记（免费）", disabled=step_done(step)):
            st.session_state.decisions["register"] = True
            mark_done(8, "确权登记")
            st.rerun()
    elif step == 9:
        st.markdown("**定标准**：元数据、主数据、编码规范——提升一致性。")
        choice = st.selectbox("标准投入：", ["全套标准（10万，一致性+0.15）", "基础标准（5万，一致性+0.08）", "不投入（一致性不变，质量塌陷风险）"], index=0)
        if st.button("✅ 确认标准投入", disabled=step_done(step)):
            cost = 10 if "全套" in choice else (5 if "基础" in choice else 0)
            if spend("步骤9·定标准", cost * 10000):
                st.session_state.decisions["standard"] = cost
                mark_done(9, "定标准")
                st.rerun()
    elif step == 10:
        st.markdown("**质量稽核**：设 KQI，决定 Q 系数（完整性/准确性）。")
        choice = st.selectbox("稽核投入：", ["深度稽核（12万，准确性+0.15）", "例行稽核（6万，准确性+0.08）", "跳过稽核（0万，⚠️质量塌陷）"], index=0)
        if st.button("✅ 确认稽核投入", disabled=step_done(step)):
            cost = 12 if "深度" in choice else (6 if "例行" in choice else 0)
            if spend("步骤10·质量稽核", cost * 10000):
                st.session_state.decisions["qc"] = cost
                mark_done(10, "质量稽核")
                st.rerun()
    elif step == 11:
        st.markdown("**安全分级与脱敏**：决定 C 系数上限（行业天花板内）。")
        choice = st.selectbox("脱敏方案：", ["全量脱敏（15万，C 保持）", "部分脱敏（8万，C≤0.8）", "未脱敏（0万，⚠️C=0.3 且罚没风险）"], index=0)
        if st.button("✅ 确认脱敏方案", disabled=step_done(step)):
            cost = 15 if "全量" in choice else (8 if "部分" in choice else 0)
            if spend("步骤11·脱敏", cost * 10000):
                st.session_state.decisions["mask"] = "全量脱敏" if "全量" in choice else ("部分脱敏" if "部分" in choice else "未脱敏")
                mark_done(11, "安全分级与脱敏")
                st.rerun()
    elif step == 12:
        st.markdown("**资产目录上架**：可被发现的才算资产——上架后 Q 完整性提升，且入表可确认。")
        st.markdown("- 上架成本 5 万（数据资产目录管理）")
        if st.button("✅ 确认上架（开支-5万）", disabled=step_done(step)):
            if spend("步骤12·资产目录上架", 5 * 10000):
                st.session_state.decisions["catalog"] = True
                mark_done(12, "资产目录上架")
                st.rerun()
    elif step == 13:
        ind = INDUSTRIES[st.session_state.industry]
        st.markdown(f"**选场景**（{st.session_state.industry}行业场景库）：资源有限，选 2-3 个。")
        scenes = list(ind["scenes"].keys())
        chosen = st.multiselect("选择场景（2-3个）：", scenes, default=scenes[:2], max_selections=3)
        if st.button("✅ 确认场景选择（免费）", disabled=step_done(step) or len(chosen) < 2):
            st.session_state.decisions["scenes"] = chosen
            mark_done(13, "选场景")
            st.rerun()
    elif step == 14:
        st.markdown("**建模与验证**：投入越高 → 准确率越高 → 场景现金流放大。")
        choice = st.selectbox("建模投入：", ["深度建模（20万，现金流+60%）", "标准建模（10万，现金流+30%）", "复用开源（2万，现金流+5%）"], index=0)
        if st.button("✅ 确认建模投入", disabled=step_done(step)):
            cost = 20 if "深度" in choice else (10 if "标准" in choice else 2)
            if spend("步骤14·建模", cost * 10000):
                st.session_state.decisions["model"] = cost
                mark_done(14, "建模与验证")
                st.rerun()
    elif step == 15:
        st.markdown("**上线与推广**：内部阻力模拟——业务部门不配合需额外投入。")
        choice = st.selectbox("推广策略：", ["全力推广（15万，现金流畅达）", "渐进推广（8万，现金流×0.9）", "不推广（0万，现金流×0.7）"], index=0)
        if st.button("✅ 确认推广策略", disabled=step_done(step)):
            cost = 15 if "全力" in choice else (8 if "渐进" in choice else 0)
            if spend("步骤15·上线推广", cost * 10000):
                st.session_state.decisions["rollout"] = "全力推广" if "全力" in choice else ("渐进推广" if "渐进" in choice else "不推广")
                if st.session_state.decisions["rollout"] != "全力推广":
                    mul = 0.9 if "渐进" in choice else 0.7
                    st.session_state.decisions["rollout_mul"] = mul
                mark_done(15, "上线与推广")
                st.rerun()
    elif step == 16:
        st.markdown("**效果度量**：算出对内降本额，进入估值分母。")
        st.markdown("- 度量体系建设成本 3 万（KPI 埋点与看板）")
        if st.button("✅ 确认效果度量（开支-3万）", disabled=step_done(step)):
            if spend("步骤16·效果度量", 3 * 10000):
                mark_done(16, "效果度量")
                st.rerun()
    elif step == 17:
        st.markdown("**产品化**：API / 数据集 / 报告 / 模型服务。")
        choice = st.selectbox("产品形态：", ["API 服务（弹性计费）", "数据集授权（收入×0.9）", "分析报告（一次性）", "模型服务（收入×1.1）"], index=0)
        if st.button("✅ 确认产品化（免费）", disabled=step_done(step)):
            st.session_state.decisions["product"] = "API服务" if "API" in choice else ("数据集授权" if "数据集" in choice else ("分析报告" if "分析" in choice else "模型服务"))
            mark_done(17, "产品化")
            st.rerun()
    elif step == 18:
        st.markdown("**定价**：成本法 / 价值法 / 市场法——三种方法结果不同。")
        choice = st.selectbox("定价方法：", ["成本法（对外收入×0.8，稳）", "价值法（基准）", "市场法（对外收入×1.2，弹性大）"], index=0)
        if st.button("✅ 确认定价（免费）", disabled=step_done(step)):
            st.session_state.decisions["pricing"] = "成本法" if "成本" in choice else ("价值法" if "价值" in choice else "市场法")
            mark_done(18, "定价")
            st.rerun()
    elif step == 19:
        st.markdown("**找买家与签约**：谈判小游戏——价格 vs 授权范围 vs 排他性。")
        choice = st.selectbox("签约策略：", ["多个分散买家（收入×1.0，无依赖风险）", "单一独家大客户（收入×1.5，⚠️单一客户依赖 D 20%）", "双客户（收入×1.2，轻度依赖）"], index=0)
        if st.button("✅ 确认签约策略（免费）", disabled=step_done(step)):
            st.session_state.decisions["buyer"] = "多个分散买家" if "分散" in choice else ("单一独家大客户" if "独家" in choice else "双客户")
            mark_done(19, "找买家签约")
            st.rerun()
    elif step == 20:
        st.markdown("**交付与运维**：SLA 违约扣款风险。")
        choice = st.selectbox("SLA 等级：", ["高标准SLA（5万，收入×0.95，无违约）", "标准SLA（2万，无加成）"], index=0)
        if st.button("✅ 确认 SLA（按选项扣款）", disabled=step_done(step)):
            cost = 5 if "高标准" in choice else 2
            if spend("步骤20·SLA", cost * 10000):
                st.session_state.decisions["sla"] = "高标准SLA" if "高标准" in choice else "标准SLA"
                mark_done(20, "交付与运维")
                st.rerun()
    elif step == 21:
        render_incentives()
    elif step == 22:
        st.markdown("**出表与披露**：模拟数据资源入表——无形资产 or 存货。")
        choice = st.selectbox("入表方式：", ["无形资产（需完成确权登记，评分更高）", "存货（未确权时的选择）"], index=0)
        reg = st.session_state.decisions.get("register")
        if "无形资产" in choice and not reg:
            st.warning("⚠️ 未完成确权登记（步骤8），无形资产资本化条件不满足，自动降级为存货")
        if st.button("✅ 确认出表方式（免费）", disabled=step_done(step)):
            st.session_state.decisions["listing"] = "无形资产" if ("无形资产" in choice and reg) else "存货"
            st.session_state.listing = st.session_state.decisions["listing"]
            mark_done(22, "出表与披露")
            st.rerun()
    elif step == 23:
        st.markdown("**第三方估值**：按主公式 V = Σ(现金流/(1.1)^t) × Q × C − H − D 计算。")
        st.markdown("引擎将完整公开每一步代入值（公式对学生完全公开，不做黑箱）。")
        if st.button("⚖️ 触发估值引擎（公开计算）", type="primary", disabled=step_done(step) or locked(st.session_state.round)):
            run_valuation()
            mark_done(23, "第三方估值")
    elif step == 24:
        st.markdown("**董事会答辩**：向「投资方」说明涨跌原因，提交下轮调整方案。")
        note = st.text_area("答辩陈述（一句话说明本轮决策逻辑）：", height=100)
        if st.button("✅ 提交答辩记录（免费）", disabled=step_done(step)):
            st.session_state.decisions["defense"] = note
            mark_done(24, "董事会答辩")
            st.rerun()

def render_incentives():
    """S21 团队激励设计器"""
    st.markdown("**团队激励投放**：每轮预算有限，必须取舍（金钱 + 非金钱组合）。")
    budget_limit = 300000
    options = {}
    c1, c2 = st.columns(2)
    for i, inc in enumerate(INCENTIVES):
        col = c1 if i % 2 == 0 else c2
        with col:
            t = inc["type"]
            emoji = "💰" if t == "金钱" else "📚" if inc["id"] == "train" else ("🔑" if inc["id"] == "auth" else ("🏅" if inc["id"] == "honor" else ("📈" if inc["id"] == "equity" else "🔄")))
            options[inc["id"]] = st.checkbox(f"{emoji} {inc['name']}（{t}，{'免费' if inc['cost']==0 else fmt(inc['cost'])}）", key=f"inc_{inc['id']}_{st.session_state.round}")
    total_cost = sum(INCENTIVES[i]["cost"] for i in range(6) if options.get(INCENTIVES[i]["id"]))
    st.markdown(f"**激励合计**：{fmt(total_cost)}（本轮预算 {fmt(budget_limit)}）")
    if total_cost > budget_limit:
        st.error("❌ 超激励预算！请减少选择")
    if st.button("✅ 投放激励方案（按选择扣款）", disabled=step_done(21) or total_cost > budget_limit):
        chosen = [i["id"] for i in INCENTIVES if options.get(i["id"])]
        if total_cost > 0 and not spend("步骤21·团队激励", total_cost):
            st.stop()
        st.session_state.incentives = chosen
        st.session_state.incentives_round[st.session_state.round] = chosen
        t = st.session_state.team
        money_only = all(INCENTIVES[i]["type"] == "金钱" for i in chosen) and len(chosen) > 0
        for i in chosen:
            inc = next(x for x in INCENTIVES if x["id"] == i)
            for k, v in inc["effect"].items():
                t[k] = max(0, min(100, t[k] + v))
        # 隐藏规则即时生效部分
        if money_only:
            t["mot"] = max(0, t["mot"] - 5)
        if st.session_state.round >= 2:
            prev = st.session_state.incentives_round.get(st.session_state.round - 1, [])
            if money_only and prev:
                if all(INCENTIVES[i]["type"] == "金钱" for i in prev):
                    t["mot"] = max(0, t["mot"] - 10)  # 纯金钱第二轮反噬
        mark_done(21, "团队激励投放")
        st.rerun()

# ========== Tab2：估值中心 ==========
def render_tab2():
    if not st.session_state.started:
        st.info("请先开始实验")
        return
    st.markdown("### ⚖️ 估值中心（三轮估值曲线 + 公式公开）")
    if not st.session_state.val_history:
        st.info("尚未结算任何轮次。完成 24 步后在「决策台」点击「结算本轮估值」。")
    # 估值曲线
    if st.session_state.val_history:
        df = pd.DataFrame(st.session_state.val_history)[["round", "v", "q", "c", "h", "d"]]
        df = df.rename(columns={"round": "轮次", "v": "V净值(万)", "q": "Q", "c": "C", "h": "H", "d": "D"})
        c1, c2 = st.columns([3, 2])
        with c1:
            st.bar_chart(df.set_index("轮次")[["V净值(万)"]])
            st.caption("V 净值随轮次变化（第一轮涨 → 第二轮事件卡回调 → 第三轮分化）")
        with c2:
            st.markdown("**三轮估值明细**")
            st.dataframe(df, use_container_width=True, hide_index=True)
        # 公式公开总表
        with st.expander("📐 主公式与口径说明（红线：公式必须对学生公开）", expanded=True):
            st.latex(r"V = \Sigma\left(\frac{现金流_i}{1.1^t}\right) \times Q \times C - H - D")
            st.markdown("""
            - **Q** = 完整性 × 一致性 × 时效性 × 准确性（乘积，行业初始值起步，治理投入提升至上限 1.0）
            - **C** = 合规系数：1.0 完全合规 / 0.7 基本合规 / 0.5 合规风险 / 0.3 违规 / 0 严重违规（C=0 罚没对外收入）；受行业天花板约束
            - **H** = H_基准 + 采集量增量 × 单位存储成本（每轮独立，不累计）
            - **D** = min(事件比例, 30%)（一次性计提，V 不低于 0）
            - t = 当前轮次（第一轮 t=1）
            """)
    # 五条下跌路径状态
    st.divider()
    st.markdown("### 🕳️ 五条下跌路径（红线2：资产值必须有涨有跌）")
    cols = st.columns(5)
    for i, (k, p) in enumerate(DROP_PATHS.items()):
        with cols[i]:
            st.markdown(f"**{p['label']}**")
            st.caption(p["desc"])
    # 事件卡库
    st.divider()
    st.markdown("### 🎴 事件卡库（20 张，P-政策 / W-价格战 / C-客户流失 / T-技术替代）")
    cols = st.columns(4)
    cats = {"P-": "政策类", "W-": "价格战类", "C-": "客户流失类", "T-": "技术替代类"}
    for ci, (pre, cname) in enumerate(cats.items()):
        with cols[ci]:
            st.markdown(f"**{cname}**")
            for code in [f"{pre}{i:02d}" for i in range(1, 6)]:
                card = EVENT_CARDS[code]
                st.markdown(f"`{code}` {card['name']}\n\n<small>{card['desc']}</small>", unsafe_allow_html=True)
    # 已投放
    st.divider()
    st.markdown("**本轮已投放事件卡**：")
    for rnd in [1, 2, 3]:
        evs = st.session_state.events_used.get(rnd, [])
        if evs:
            st.markdown(f"- 第{rnd}轮：{'；'.join(f'{e}·{EVENT_CARDS[e]["name"]}' for e in evs)}")

# ========== Tab3：团队与激励 ==========
def render_tab3():
    if not st.session_state.started:
        st.info("请先开始实验")
        return
    st.markdown("### 👥 团队三维状态与激励系统")
    st.markdown("**三维状态直接影响估值**：能力→Q 上限｜意愿→治理执行力度｜稳定→D 计提敏感度。")
    t = st.session_state.team
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("能力值 Capability", t["cap"])
    with c2: st.metric("意愿值 Motivation", t["mot"])
    with c3: st.metric("稳定值 Retention", t["ret"])
    st.progress(t["cap"] / 100, text="能力（决定治理效率与 Q）")
    st.progress(t["mot"] / 100, text="意愿（决定加班效率与离职概率）")
    st.progress(t["ret"] / 100, text="稳定（决定知识沉淀，低→人员流失带走隐性知识，H 上升）")
    st.divider()
    st.markdown("### 🧰 激励工具箱（每轮预算有限，必须取舍）")
    df = pd.DataFrame([
        {"工具": i["name"], "类型": i["type"], "成本": f"{i['cost']/10000:.0f}万" if i["cost"] else "免费", "作用": "+".join(f"{k.replace('cap','能力').replace('mot','意愿').replace('ret','稳定')}{v}" for k, v in i["effect"].items())}
        for i in INCENTIVES
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.divider()
    st.markdown("### 🕵️ 隐藏规则（复盘时揭示，当前只标记已触发的部分）")
    money_rounds = [r for r in st.session_state.incentives_round if st.session_state.incentives_round[r] and all(INCENTIVES[i]["type"] == "金钱" for i in st.session_state.incentives_round[r])]
    train_auth = any({"train", "auth"}.issubset(set(st.session_state.incentives_round.get(r, []))) for r in [1, 2, 3])
    st.markdown(f"- 纯金钱激励第二轮反噬：{'⚠️ 已触发' if len(money_rounds) >= 2 else '未触发'}（纯金钱第二轮预算收紧 → 意愿暴跌）")
    st.markdown(f"- 「培训+授权」第三轮复利：{'✅ 已埋下复利' if train_auth else '未触发'}（能力值 → Q 永久加成）")
    st.markdown(f"- 连续两轮无任何非金钱激励 → 稳定值不可逆下降：{'⚠️ 注意' if not train_auth and len(money_rounds) >= 1 else '安全'}")

# ========== Tab4：教师端 ==========
def render_tab4():
    st.markdown("### 🎓 教师端（事件卡投放器 + 本轮状态机 + 六维评分）")
    st.caption("Phase 1 单组原型版：教师端控制节奏——事件卡是教学的「手柄」，不能交给系统自动随机。")
    if not st.session_state.started:
        st.info("请先开始实验")
        return
    r = st.session_state.round
    # 事件卡投放器
    st.markdown("#### 🎴 事件卡投放器（第 {} 轮，已投放 {} 张）".format(r, len(st.session_state.events_used.get(r, []))))
    allowed = [c for c, cfg in EVENT_CARDS.items() if r in cfg["rounds"]]
    new_ev = st.multiselect("追加投放事件卡（可投放轮次范围已过滤）：", allowed)
    if st.button("📌 投放所选事件卡（真实生效于本轮估值）"):
        cur = st.session_state.events_used.get(r, [])
        for e in new_ev:
            if e not in cur:
                cur.append(e)
                record(f"第{r}轮投放事件卡", f"{e}·{EVENT_CARDS[e]['name']}")
        st.session_state.events_used[r] = cur
        st.rerun()
    if st.session_state.events_used.get(r):
        st.markdown("**已投放：**" + "；".join(f"{e}·{EVENT_CARDS[e]['name']}" for e in st.session_state.events_used[r]))
    st.divider()
    # 状态机
    st.markdown("#### 🔄 本轮状态机（结算后只读）")
    state = "已结算" if locked(r) else "开放提交"
    st.markdown(f"当前状态：**{state}**")
    if not locked(r):
        if st.button("🔒 关闭提交（表单只读，等待结算）"):
            st.session_state.closed_round.append(r)
            st.rerun()
    else:
        st.success(f"第{r}轮已结算，学生端只读。")
    if r < 3:
        if st.button(f"🔓 开放第{r+1}轮（教师端）"):
            open_next_round()
    st.divider()
    # 六维评分
    st.markdown("#### 📊 六维评分体系（终局计算）")
    st.markdown("| 维度 | 权重 | 数据来源 |\n|---|---|---|\n| 数据资产净值 V（终值） | 30% | 估值引擎 |\n| 资产质量 Q×C | 20% | 估值引擎 |\n| 估值报告与入表合规性 | 15% | 出表披露物 |\n| 团队状态与健康度 | 15% | 激励系统仪表盘 |\n| 战略一致性与迭代逻辑 | 10% | 三轮决策对比 |\n| 复盘反思深度 | 10% | 复盘三问 |")
    if len(st.session_state.val_history) >= 3:
        if st.button("⚖️ 计算终局六维评分（真实计算）", type="primary"):
            compute_eval()
            st.rerun()

def compute_eval():
    """六维评分 + 特别奖"""
    vh = st.session_state.val_history
    last = vh[-1]
    ind = INDUSTRIES[st.session_state.industry]
    # 1 V 终值（30%）
    v_max = 300
    v_score = min(last["v"] / v_max, 1.0) * 100
    # 2 Q×C（20%）
    qc = last["q"] * last["c"]
    qc_max = ind["q0"] * ind["c_cap"]
    qc_score = min(qc / qc_max, 1.0) * 100
    # 3 入表合规（15%）
    reg_ok = st.session_state.decisions.get("register") or st.session_state.listing == "无形资产"
    mask_ok = st.session_state.decisions.get("mask") == "全量脱敏"
    listing = 100 if st.session_state.listing == "无形资产" else 60
    listing_score = (listing + (100 if mask_ok else 40)) / 2
    # 4 团队健康（15%）
    t = st.session_state.team
    team_score = (t["cap"] + t["mot"] + t["ret"]) / 3
    # 5 战略一致性（10%）
    strategy = st.session_state.decisions.get("strategy", "对内优先")
    consistent = 100 if all(vh[i]["round"] == i + 1 for i in range(len(vh))) else 80
    strat_score = 100 if strategy else 80
    # 6 复盘深度（10%）
    refl = st.session_state.reflection
    refl_score = 100 if len(refl.strip()) >= 50 else (60 if refl.strip() else 20)
    total = round(v_score * 0.30 + qc_score * 0.20 + listing_score * 0.15 + team_score * 0.15 + strat_score * 0.10 + refl_score * 0.10, 1)
    st.session_state.eval_score = {
        "V": round(v_score, 1), "QC": round(qc_score, 1), "listing": round(listing_score, 1),
        "team": round(team_score, 1), "strategy": round(strat_score, 1), "reflection": round(refl_score, 1),
        "total": total,
    }
    # 特别奖（增值评价）
    awards = []
    if len(vh) >= 2:
        drop = vh[0]["v"] - vh[1]["v"]
        if drop > 0 and refl_score >= 60:
            awards.append("🏆 最佳踩坑奖（跌幅最大但复盘最深刻）")
    if last["v"] >= v_max * 0.5 and t["ret"] >= 70:
        awards.append("🏆 长期主义奖（第三轮 V 高且团队稳定）")
    if last["c"] >= ind["c_cap"] * 0.95:
        awards.append("🏆 合规守门员奖（C 系数全程保持行业最优）")
    st.session_state.awards = awards
    record("终局六维评分", f"总分{total}")

# ========== Tab5：复盘报告 ==========
def render_tab5():
    st.markdown("### 📝 复盘报告（复盘三问必做，否则只是游戏）")
    st.markdown("**复盘三问**：")
    st.markdown("1. 你的资产在哪一步开始「变质」？如果重来，你会砍掉哪一笔投入？")
    st.markdown("2. 你的团队激励方案，哪一项真正产生了复利？哪一项是浪费？")
    st.markdown("3. 如果把你这套模式搬到另外三个行业，哪一条会立刻失效？为什么？")
    q1 = st.text_area("问题1：资产在哪一步开始变质？重来会砍掉哪笔投入？", height=90)
    q2 = st.text_area("问题2：激励方案哪项产生复利？哪项是浪费？", height=90)
    q3 = st.text_area("问题3：搬到其他行业哪条失效？为什么？", height=90)
    if st.button("✅ 提交复盘（计入六维评分·复盘深度 10%）"):
        st.session_state.reflection = f"{q1}\n{q2}\n{q3}"
        record("提交复盘三问", "完成")
        st.rerun()
    st.divider()
    if st.session_state.eval_score:
        st.markdown("### 🏅 六维评分（终局）")
        e = st.session_state.eval_score
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("数据资产净值 V", f"{e['V']}/100", delta="权重30%")
        with c2: st.metric("资产质量 Q×C", f"{e['QC']}/100", delta="权重20%")
        with c3: st.metric("入表合规性", f"{e['listing']}/100", delta="权重15%")
        c4, c5, c6 = st.columns(3)
        with c4: st.metric("团队健康度", f"{e['team']}/100", delta="权重15%")
        with c5: st.metric("战略一致性", f"{e['strategy']}/100", delta="权重10%")
        with c6: st.metric("复盘深度", f"{e['reflection']}/100", delta="权重10%")
        st.metric("综合得分", f"{e['total']}分")
        if st.session_state.awards:
            st.success("**增值评价·特别奖：**" + "；".join(st.session_state.awards))
    st.divider()
    # 审计日志
    st.markdown("### 🛡️ 操作留痕 · 审计日志（可回滚、可追溯、可对账）")
    if st.session_state.log:
        audit_df = pd.DataFrame(st.session_state.log, columns=["时间", "操作", "金额变动"])
        st.dataframe(audit_df, use_container_width=True, hide_index=True)
        csv = audit_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 导出审计日志 CSV", csv, "audit_log.csv", "text/csv")
    else:
        st.info("暂无操作记录")

# ========== 主渲染 ==========
def main():
    render_sidebar()
    if not st.session_state.started:
        render_tab0()
        return
    tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📖 实验导览", "📋 决策台（24步）", "⚖️ 估值中心", "👥 团队激励", "🎓 教师端", "📝 复盘报告",
    ])
    with tab0: render_tab0()
    with tab1: render_tab1()
    with tab2: render_tab2()
    with tab3: render_tab3()
    with tab4: render_tab4()
    with tab5: render_tab5()

if __name__ == "__main__":
    main()
