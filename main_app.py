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
import textwrap

def md_html(s):
    """逐行去掉前导缩进后以 HTML 渲染（避免 Markdown 把缩进行当代码块显示原文）"""
    lines = [ln.strip() for ln in s.splitlines()]
    return st.markdown("\n".join(lines), unsafe_allow_html=True)

st.set_page_config(
    page_title="数据资产运营总监——全生命周期经营决策虚拟仿真实验",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

INIT_BUDGET = 3500000  # 每轮 350 万（v2.0 校准：含赋能45万/年薪计入H/来源成本；标准路径约需 278 万，留余量应对事件卡）

# ========== 四行业基准值表 v1.1（Phase0 交付包 2.1 节） ==========
INDUSTRIES = {
    "制造": {
        "name": "高端制造",
        "q0": 0.75, "c_cap": 0.9, "h_base": 15.0, "unit_storage": 2.0,
        "h_level": "高（存储+算力）", "trap": "采了大量振动数据却无故障样本",
        "base_tb": 12, "color": "#1E88E5",
        "scenes": {
            "良率提升": {"kind": "in", "base": 105, "desc": "用设备时序数据提升产线良率"},
            "预测性维护": {"kind": "in", "base": 90, "desc": "故障预测减少非计划停机"},
            "数字孪生服务": {"kind": "out", "base": 75, "desc": "设备数字孪生对外数据服务"},
        },
    },
    "零售": {
        "name": "零售流通",
        "q0": 0.70, "c_cap": 0.7, "h_base": 10.0, "unit_storage": 1.5,
        "h_level": "中", "trap": "买了流量却做不出复购模型",
        "base_tb": 8, "color": "#7C4DFF",
        "scenes": {
            "精准营销": {"kind": "out", "base": 120, "desc": "用户标签体系支撑精准营销"},
            "复购模型": {"kind": "in", "base": 90, "desc": "复购预测提升客户生命周期价值"},
            "数据产品授权": {"kind": "out", "base": 90, "desc": "脱敏画像数据集对外授权"},
        },
    },
    "医疗": {
        "name": "智慧医疗",
        "q0": 0.65, "c_cap": 0.5, "h_base": 12.0, "unit_storage": 3.0,
        "h_level": "中高（安全等级要求）", "trap": "拿了数据永远过不了伦理审查",
        "base_tb": 5, "color": "#00A86B",
        "scenes": {
            "临床质控": {"kind": "in", "base": 90, "desc": "病历数据支撑院内质控"},
            "辅助诊断模型": {"kind": "out", "base": 105, "desc": "影像辅助诊断对外服务"},
            "科研数据集": {"kind": "out", "base": 60, "desc": "脱敏科研数据集授权（强受限）"},
        },
    },
    "能源": {
        "name": "能源电网",
        "q0": 0.70, "c_cap": 0.6, "h_base": 18.0, "unit_storage": 2.5,
        "h_level": "高（实时性要求）", "trap": "政策一变，商业模式归零",
        "base_tb": 20, "color": "#FF6D00",
        "scenes": {
            "负荷预测服务": {"kind": "out", "base": 105, "desc": "负荷预测对外服务"},
            "碳核算数据": {"kind": "out", "base": 75, "desc": "碳核算数据产品（政策敏感）"},
            "能耗优化": {"kind": "in", "base": 90, "desc": "能耗优化降低运营成本"},
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

# ========== 团队与激励（v2.0：5 工具，参考海底捞/胖东来） ==========
TEAM_INIT = {"cap": 60, "mot": 65, "ret": 70}
INCENTIVES = [
    {"id": "money", "name": "加薪 / 奖金", "type": "金钱", "cost": 200000, "effect": {"mot": 15}, "hidden": "锚定效应后反噬：下一轮意愿 -10（常规做法，非长久之计）", "ref": "常规做法"},
    {"id": "train", "name": "培训 + 授权", "type": "非金钱", "cost": 120000, "effect": {"cap": 15}, "hidden": "第三轮产生复利（能力值 → Q 加成）", "ref": "海底捞：授权一线决策"},
    {"id": "care", "name": "关怀福利", "type": "非金钱", "cost": 80000, "effect": {"ret": 10, "mot": 5}, "hidden": "稳定 +10、意愿 +5", "ref": "胖东来：高福利 + 尊重员工"},
    {"id": "honor", "name": "公开表彰", "type": "非金钱", "cost": 20000, "effect": {"mot": 8, "ret": 5}, "hidden": "意愿 +8、稳定 +5（低成本高回报）", "ref": "海底捞：评选明星员工"},
    {"id": "equity", "name": "股权激励承诺", "type": "金钱", "cost": 0, "effect": {"ret": 15}, "hidden": "承诺需兑现，未兑现稳定暴跌 -20", "ref": "胖东来：利润分享"},
]
INC_BY_ID = {x["id"]: x for x in INCENTIVES}  # id→激励项 映射（incentives_round 里存的是 id）

# ========== v2.0 新增①：董事会组阁 8 角色（6 必选 + 2 可选，年薪计入当轮 H） ==========
ROLE_TEAM = [
    {"id": "de", "name": "数据工程师", "must": True, "salary": 18, "desc": "负责采集和清洗，把数据搬进来、洗干净", "effect": "采集效率+20%，清洗质量+10%"},
    {"id": "dg", "name": "数据治理师", "must": True, "salary": 15, "desc": "定标准、做质检，保证数据不乱", "effect": "Q 上限+0.05"},
    {"id": "co", "name": "合规专员", "must": True, "salary": 12, "desc": "审核数据能不能用、能不能卖，守住红线", "effect": "C 系数+0.05，事故概率-30%"},
    {"id": "alg", "name": "算法工程师", "must": True, "salary": 20, "desc": "建模做场景，把数据变成能用的东西", "effect": "赋能场景成功率+25%"},
    {"id": "pm", "name": "产品经理", "must": True, "salary": 14, "desc": "对接买家，把数据包装成能卖的产品", "effect": "对外收入+15%，成交周期-20%"},
    {"id": "op", "name": "运营经理", "must": True, "salary": 13, "desc": "管客户、管复购，让买家持续买单", "effect": "客户留存+15%"},
    {"id": "cons", "name": "行业顾问（可选）", "must": False, "salary": 10, "desc": "懂本行业门道，帮你避开行业特有坑", "effect": "行业陷阱识别+30%"},
    {"id": "legal", "name": "法务（可选）", "must": False, "salary": 11, "desc": "审合同，保证签的合同不出问题", "effect": "合同纠纷概率-40%"},
]
ROLE_BY_ID = {x["id"]: x for x in ROLE_TEAM}

# ========== v2.0 新增③：家底盘点——五类数据类型清单 ==========
DATA_TYPE_INVENTORY = [
    {"name": "文件 / 表格", "desc": "Excel、CSV、Word、PDF 这类能直接打开看的文档", "use": "做统计、出报表、喂给模型训练", "trap": "格式乱、字段含义不清，清洗要花很多钱"},
    {"name": "图片", "desc": "产品图、监控截图、医学影像、遥感图", "use": "做图像识别、质量检测、内容审核", "trap": "体积大、存得贵，且可能含人脸等敏感信息"},
    {"name": "音频", "desc": "客服录音、设备运转声、会议录音", "use": "做语音质检、故障预警、情绪分析", "trap": "转写成本高，涉及隐私需脱敏"},
    {"name": "视频", "desc": "监控录像、产线画面、直播回放", "use": "做行为识别、安防、工艺质检", "trap": "最占存储，一 TB 视频存一年很贵"},
    {"name": "传感器流数据", "desc": "设备实时上报的温度、压力、位置等连续数据", "use": "做实时监控、预测性维护", "trap": "采集频率越高越值钱，但 H 涨得也最快"},
]

# ========== v2.0 新增⑤：A/B/C 三套赋能方案 ==========
EMPOWER_PLANS = [
    {"id": "A", "name": "A 方案·基础版（省钱）", "cost": 20, "period": 1, "q_bonus": 0.03, "cash_desc": "低（对内降本为主）", "cash_in_mul": 1.1, "cash_out_mul": 1.0, "effective": 1.0, "risk": "效果弱，易被竞品超越", "fit": "预算紧、求稳"},
    {"id": "B", "name": "B 方案·进阶版（均衡）", "cost": 45, "period": 2, "q_bonus": 0.06, "cash_desc": "中（对内+少量对外）", "cash_in_mul": 1.15, "cash_out_mul": 1.15, "effective": 0.8, "risk": "风险收益均衡，推荐首选", "fit": "大多数团队的最优解"},
    {"id": "C", "name": "C 方案·领先版（重投入）", "cost": 80, "period": 3, "q_bonus": 0.10, "cash_desc": "高（对内+对外双变现）", "cash_in_mul": 1.2, "cash_out_mul": 1.3, "effective": 0.6, "risk": "前期现金压力大，失败损失大", "fit": "有信心、现金充足"},
]

# ========== v2.0 新增⑥：数据来源与采集限值 ==========
SOURCE_TYPES = [
    {"id": "内部", "name": "公司给的（内部）", "limit_tb": 30, "unit_cost": 1.0, "over": "超过 30 TB 部分存储成本翻倍，H 显著上升", "compliance": "需有内部授权记录", "trust_pt": 40},
    {"id": "爬取", "name": "爬取的（外部）", "limit_tb": 10, "unit_cost": 0.5, "over": "超限即触发合规事故，C 直接降至 0.3", "compliance": "必须有授权，超范围采集直接违规", "trust_pt": 10},
    {"id": "第三方", "name": "第三方购买", "limit_tb": 20, "unit_cost": 3.0, "over": "超限部分需追加预算，否则交付延期一轮", "compliance": "需签订采购合同并完成脱敏", "trust_pt": 25},
]

# ========== v2.0 新增⑦：数据产品交易合同（关键条，2/3/7 条合规校验） ==========
CONTRACT_CLAUSES = [
    "第一条　标的：甲方向乙方提供【填写：API / 数据包 / 分析报告】，数据规模【填写：XX TB】，覆盖周期【填写：X 个月】。",
    "第二条　数据来源与合法性：甲方保证数据来源合法（内部授权 / 合规采集），并已按《个人信息保护法》完成脱敏处理。【校验项】",
    "第三条　用途限制：乙方仅可将数据用于【填写：具体用途】，不得转售、不得用于约定外的其他用途。【校验项】",
    "第四条　交付方式与周期：甲方于合同签订后【填写：X】个工作日内完成交付，通过【填写：交付方式】提供。",
    "第五条　价格与结算：合同总额【填写：XX 万元】，分【填写：1/2/3】期支付，逾期按每日【填写：X】% 计违约金。",
    "第六条　质量保证：甲方保证数据质量系数 Q ≥【填写：0.X】，低于约定值乙方有权要求补数或退款。",
    "第七条　合规与责任：因数据来源违法、未脱敏、超范围使用导致的法律责任，由【填写：甲方 / 乙方 / 双方】承担。【校验项】",
    "第八条　保密条款：双方对本合同内容及数据内容负有保密义务，期限为合同终止后【填写：X】年。",
    "第九条　争议解决：因本合同产生的争议，双方协商解决；协商不成的，提交【填写：仲裁机构】仲裁。",
]

# ========== v2.0 新增⑧：脱敏四方法 ==========
MASK_METHODS = [
    {"name": "掩码", "desc": "把中间几位换成 * 号，只留头尾", "example": "手机号 138****6721", "fit": "手机号、身份证号"},
    {"name": "哈希", "desc": "把原文变成一串乱码，不可逆", "example": "“张三”→ a3f5…", "fit": "需要去重但不用看原文"},
    {"name": "泛化", "desc": "把精确值换成大概范围", "example": "“28 岁”→“20–30 岁”", "fit": "年龄、收入、地址"},
    {"name": "截断", "desc": "直接删掉这一列或这一部分", "example": "删掉“具体门牌号”", "fit": "用不到的敏感字段"},
]

# ========== v2.0 新增⑨：数据可信度 T（40+30+30） ==========
TRUST_POINTS = {
    "source_legal": 40,  # 数据来源合法清晰
    "signer": 30,        # 有责任人签字（确权登记）
    "audit": 30,         # 可追溯审计（血缘+审计留痕）
}

# ========== v2.0 新增⑪：常见数据类型小课堂 ==========
DATA_KINDS_CLASS = [
    {"name": "结构化数据", "desc": "整整齐齐排成表格，一行一条记录", "example": "Excel 订单表、数据库里的客户信息", "handle": "最好清洗，Q 加成最高"},
    {"name": "半结构化数据", "desc": "有点结构但没那么规整", "example": "JSON 日志、XML 报文、邮件", "handle": "需先规整化，中等难度"},
    {"name": "非结构化数据", "desc": "没有固定行列，计算机不好直接读", "example": "图片、音频、视频、长文本", "handle": "需额外处理，存得贵、H 高"},
]

# ========== 24 步流程定义（6 篇章 × 4 步） ==========
PHASES = [
    {"name": "投入篇", "steps": [1, 2, 3, 4], "aim": "定好团队与预算——开局底子"},
    {"name": "采集篇", "steps": [5, 6, 7, 8], "aim": "拿到数据并安全存好——原料入仓"},
    {"name": "治理篇", "steps": [9, 10, 11, 12], "aim": "清洗/脱敏/上架——提升 Q、守住 C"},
    {"name": "赋能篇", "steps": [13, 14, 15, 16], "aim": "建模并推广场景——让数据有用"},
    {"name": "变现篇", "steps": [17, 18, 19, 20], "aim": "产品化与签约——把数据卖成钱"},
    {"name": "经营与估值篇", "steps": [21, 22, 23, 24], "aim": "激励团队、披露估值——算总账"},
]
STEP_NAMES = {
    1: "召开董事会·组阁", 2: "盘点家底", 3: "制定三年战略", 4: "编制预算",
    5: "选择数据源", 6: "签订数据合同", 7: "接入与存储", 8: "确权登记",
    9: "定标准", 10: "质量稽核", 11: "安全分级与脱敏", 12: "资产目录上架",
    13: "赋能方案三选一", 14: "建模与验证", 15: "上线与推广", 16: "效果度量",
    17: "产品化", 18: "定价", 19: "签署数据交易合同", 20: "交付与运维",
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
        # v2.0 新增字段
        "team_roster": [], "team_salary": 0.0,       # 董事会组阁：8 角色与年薪合计
        "trust_t": 0, "trust_detail": {},             # 数据可信度 T
        "empower_plan": None, "empower_reason": "",   # 赋能 A/B/C 三选一
        "contract_filled": {},                        # 合同签署填写项
        "gold_ideas": {},                             # 金点子 {轮次: 文本}
        "gold_idea_adopted": {},                      # 金点子采纳 {轮次: True}
        "mask_quiz_ok": {},                           # 脱敏小课堂测验 {轮次: bool}
        "audit_trail": {},                            # S7 审计留痕勾选 {轮次: bool}
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
    # v2.0 新增⑤：赋能方案对 Q 的加成（A/B/C 三选一）
    emp = d.get("empower_plan")
    if emp:
        bonus = next((p["q_bonus"] for p in EMPOWER_PLANS if p["id"] == emp), 0.0)
        q = min(q + bonus, 0.99)
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
    # v2.0 新增⑥：爬取超限 → 合规事故，C 直接 0.3
    if d.get("source_over_limit") and d.get("source") == "爬取":
        c = min(c, 0.3)
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
    # v2.0 新增⑤：赋能方案现金流乘数（A/B/C）
    emp = d.get("empower_plan")
    if emp:
        p = next((x for x in EMPOWER_PLANS if x["id"] == emp), None)
        if p:
            cash_in *= p["cash_in_mul"] * p["effective"]
            cash_out *= p["cash_out_mul"] * p["effective"]
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
    """H = H_基准 + 采集量增量 × 单位存储成本 + 团队年薪（v2.0：8角色年薪计入当轮 H）"""
    ind = INDUSTRIES[ind_key]
    d = decisions
    h_base = ind["h_base"]
    unit = ind["unit_storage"]
    # 存储方案：湖仓一体 → H 基准 -20%；数据湖 → 采集量放大
    if d.get("storage") == "湖仓一体": h_base *= 0.8
    # 采集量（TB）：v2.0 来源类型（内部/爬取/第三方）+ 用户输入采集量
    src = d.get("source", "内部")
    src_cfg = next((s for s in SOURCE_TYPES if s["id"] == src), SOURCE_TYPES[0])
    raw_tb = d.get("source_tb", src_cfg["limit_tb"])
    source_tb = raw_tb * (1.2 if d.get("storage") == "数据湖" else 1.0)
    # 越限处理：按采集量（放大前）判定是否超过来源限值——内部超限部分存储成本翻倍；第三方超限追加预算
    over_tb = max(raw_tb - src_cfg["limit_tb"], 0)
    over_cost = 0.0
    if over_tb > 0:
        if src == "内部":
            over_cost = over_tb * unit * 2
        elif src == "第三方":
            over_cost = over_tb * 3.0  # 每超 1TB 追加 3 万采购预算
    extra_tb = max(source_tb - ind["base_tb"], 0)
    # 团队年薪（v2.0 新增①：年薪直接计入当轮 H）
    salary = d.get("team_salary", 0.0)
    # 事件卡
    for e in events:
        cfg = EVENT_CARDS[e]
        if "h_mult" in cfg: h_base *= cfg["h_mult"]
        if "unit_mult" in cfg: unit *= cfg["unit_mult"]
        if "h_base_mult" in cfg: h_base *= cfg["h_base_mult"]
        if "h_extra" in cfg: h_base += cfg["h_extra"]
        if "tb_mult" in cfg: extra_tb *= cfg["tb_mult"]
    h = h_base + extra_tb * unit + over_cost + salary
    return round(h, 1), {"h_base": round(h_base, 1), "extra_tb": round(extra_tb, 1), "unit": round(unit, 2), "over_cost": round(over_cost, 1), "salary": round(salary, 1)}

def calc_t(decisions):
    """v2.0 新增⑨：数据可信度 T = 来源合法清晰40 + 责任人签字30 + 可追溯审计30；T<50 对外变现收入打 5 折"""
    d = decisions
    pts = 0
    detail = {}
    # ① 来源合法清晰（40）：内部 40 / 第三方购买 25 / 爬取 10
    src = d.get("source", "内部")
    src_cfg = next((s for s in SOURCE_TYPES if s["id"] == src), SOURCE_TYPES[0])
    src_pt = src_cfg["trust_pt"]
    pts += src_pt; detail["来源合法清晰"] = src_pt
    # ② 责任人签字（30）：确权登记完成
    signer_pt = 30 if d.get("register") else 0
    pts += signer_pt; detail["责任人签字"] = signer_pt
    # ③ 可追溯审计（30）：S7 勾选血缘+审计留痕
    audit_pt = 30 if d.get("audit_trail") else 0
    pts += audit_pt; detail["可追溯审计"] = audit_pt
    return pts, detail

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

    # 采集量（TB）：v2.0 来源类型 + 用户输入（越限判定用放大前 raw_tb）
    src = d.get("source", "内部")
    src_cfg = next((s for s in SOURCE_TYPES if s["id"] == src), SOURCE_TYPES[0])
    raw_tb = d.get("source_tb", src_cfg["limit_tb"])
    source_tb = raw_tb * (1.2 if d.get("storage") == "数据湖" else 1.0)
    collected_tb = raw_tb

    cash_in, cash_out = calc_cash(ind_key, d, r, events)
    q, q_detail = calc_q(ind_key, d)
    c = calc_c(ind_key, d, r, events)
    h, h_detail = calc_h(ind_key, d, r, events)
    # v2.0 新增⑨：数据可信度 T（T<50 对外变现收入打 5 折）
    t, t_detail = calc_t(d)
    if t < 50:
        cash_out *= 0.5
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
        # v2.0 新增字段：可信度 T / 团队状态 / 赋能方案
        "t_score": t, "t_detail": t_detail,
        "team": dict(st.session_state.team),
        "empower": d.get("empower_plan"),
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
        st.markdown(f"**③' 数据可信度 T** = 来源合法清晰({t_detail.get('来源合法清晰',0)}) + 责任人签字({t_detail.get('责任人签字',0)}) + 可追溯审计({t_detail.get('可追溯审计',0)}) = **{t}**" + ("（⚠️ T<50：对外变现收入打 5 折）" if t < 50 else "（✅ T≥50：买家信任，收入不打折）"))
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
            st.markdown("### ⏭️ 下一步后果预告")
            preview_map = {
                1: "组阁 8 角色：年薪合计直接计入本轮 H（人不是白用的）",
                4: "预算分配：治理投入→Q 升；合规投入→C 守住；投入太少→质量塌陷/合规事故扣款",
                5: "选数据源：采集量越大 H 越高；爬取超限→C 直接 0.3（合规事故）",
                7: "存储方案：湖仓一体 H 基准-20%；开启审计留痕→可信度 T +30",
                11: "脱敏：全量 15万→C 保持；不脱敏→C=0.3 且对外收入罚没；需先过小测验",
                13: "赋能方案：A/B/C 三选一，立即开支 20/45/80 万，Q 加成 +0.03/+0.06/+0.10",
                19: "签合同：2/3/7 条填错会被阻止；单一独家大客户→D 20%",
                21: "激励：预算=现金×15%（上限50万），不能全选；纯金钱下轮意愿反噬",
                23: "估值结算：V = Σ现金流×Q×C−H−D，本轮收益/损失当场见分晓",
            }
            st.info(preview_map.get(st.session_state.step, "完成本步后继续推进 24 步流程；每步决策都真实扣款/生效，写审计日志、可撤销。"))
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

# ========== Tab0：实验导览（实验说明书式） ==========
def render_tab0():
    md_html("""
    <div style="background:linear-gradient(135deg,#0F2B46,#1E88E5 55%,#64B5F6);padding:26px 30px;border-radius:14px;color:#fff">
    <h1 style="margin:0;color:#fff">🎯 数据资产运营总监</h1>
    <p style="margin:6px 0 0;font-size:16px;color:#E3F2FD">数据资产全生命周期经营决策虚拟仿真实验 · 8学时（课前1+课中6+课后1）</p>
    </div>
    """)
    st.markdown("")

    # 实验地图：6篇章24步流程条
    st.markdown("### 🗺️ 实验地图：24 步决策全流程（从上到下依次完成）")
    flow_html = """
    <div style="display:flex;gap:10px;flex-wrap:nowrap;overflow-x:auto;padding:6px 0">
    {phases}
    </div>
    <div style="margin-top:8px;font-size:13px;color:#37474F;background:#ECEFF1;border-radius:10px;padding:10px 14px">
    💡 <b>逻辑主线</b>：先把「数据当资产」的<b>底子</b>打好（投入→采集→治理），再把「资产变钱」的<b>变现</b>跑通（赋能→变现→经营估值）。前 12 步决定 Q/C/H 的底子，后 12 步决定现金流的来源——两边都做好，V 才会高。
    </div>
    """
    phase_blocks = []
    for ph in PHASES:
        step_marks = " · ".join(f"{s}" for s in ph["steps"])
        phase_blocks.append(f"""
        <div style="flex:1;min-width:150px;background:#F5F9FF;border:1px solid #BBDEFB;border-radius:12px;padding:12px">
        <div style="font-weight:700;color:#0D47A1;font-size:15px">{ph['name']}</div>
        <div style="font-size:12px;color:#1565C0;margin-top:4px">步骤 {ph['steps'][0]}-{ph['steps'][-1]}</div>
        <div style="font-size:12px;color:#455A64;margin-top:6px">{ph['aim']}</div>
        </div>
        """)
    md_html(flow_html.format(phases="".join(phase_blocks)))
    st.markdown("")

    # 估值公式拆解（彩色块）
    st.markdown("### ⚖️ 估值引擎拆解（每个字母都能看懂）")
    formula_html = """
    <div style="display:flex;gap:8px;align-items:stretch;flex-wrap:wrap;padding:10px 0">
      <div style="flex:2;min-width:220px;background:#E8F5E9;border:2px solid #43A047;border-radius:12px;padding:12px">
        <div style="font-size:12px;color:#2E7D32">① 现金流折现</div>
        <div style="font-size:20px;font-weight:800;color:#1B5E20;font-family:monospace">Σ(现金流 ÷ 1.1ᵗ)</div>
        <div style="font-size:12px;color:#388E3C">每个变现场景未来能赚多少钱，折算回今天</div>
      </div>
      <div style="flex:1;min-width:110px;background:#E3F2FD;border:2px solid #1E88E5;border-radius:12px;padding:12px">
        <div style="font-size:12px;color:#1565C0">② Q 质量系数</div>
        <div style="font-size:20px;font-weight:800;color:#0D47A1;font-family:monospace">× Q</div>
        <div style="font-size:12px;color:#1976D2">数据干不干净：完整×一致×时效×准确</div>
      </div>
      <div style="flex:1;min-width:110px;background:#F3E5F5;border:2px solid #8E24AA;border-radius:12px;padding:12px">
        <div style="font-size:12px;color:#6A1B9A">③ C 合规系数</div>
        <div style="font-size:20px;font-weight:800;color:#4A148C;font-family:monospace">× C</div>
        <div style="font-size:12px;color:#7B1FA2">合不合规：违规可归零、罚没对外收入</div>
      </div>
      <div style="flex:1;min-width:110px;background:#FFF3E0;border:2px solid #FB8C00;border-radius:12px;padding:12px">
        <div style="font-size:12px;color:#E65100">④ H 持有成本</div>
        <div style="font-size:20px;font-weight:800;color:#EF6C00;font-family:monospace">− H</div>
        <div style="font-size:12px;color:#F57C00">存数据要花钱：存储+算力（每轮独立）</div>
      </div>
      <div style="flex:1;min-width:110px;background:#FFEBEE;border:2px solid #E53935;border-radius:12px;padding:12px">
        <div style="font-size:12px;color:#C62828">⑤ D 减值准备</div>
        <div style="font-size:20px;font-weight:800;color:#B71C1C;font-family:monospace">− D</div>
        <div style="font-size:12px;color:#D32F2F">风险事件计提：最多扣 30%</div>
      </div>
      <div style="flex:0.6;min-width:90px;background:#263238;border-radius:12px;padding:12px;display:flex;flex-direction:column;justify-content:center">
        <div style="font-size:12px;color:#90A4AE">= 资产净值</div>
        <div style="font-size:20px;font-weight:800;color:#FFF;font-family:monospace">V</div>
        <div style="font-size:12px;color:#B0BEC5">正 = 赚，负 = 亏</div>
      </div>
    </div>
    <div style="font-size:13px;color:#37474F;background:#F5F5F5;border-radius:10px;padding:8px 14px;margin-top:4px">
    📌 <b>记忆口诀</b>：先看<b>能赚多少</b>（①），再看<b>数据好不好</b>（②③打折），最后扣掉<b>养数据的钱</b>（④）和<b>踩坑的损失</b>（⑤）。
    </div>
    """
    md_html(formula_html)
    st.markdown("")

    # 三轮节奏时间轴
    st.markdown("### 🔄 三轮节奏（为什么做三轮？）")
    timeline_html = """
    <div style="display:flex;gap:10px;align-items:stretch;padding:6px 0">
      <div style="flex:1;background:#E8F5E9;border-top:5px solid #43A047;border-radius:0 0 12px 12px;padding:12px">
        <div style="font-weight:800;color:#1B5E20">第 1 轮 · 普遍上涨</div>
        <div style="font-size:13px;color:#388E3C;margin-top:6px">基础治理就见效，估值上涨——<b>先尝到甜头</b>，建立信心</div>
      </div>
      <div style="align-self:center;font-size:22px;color:#90A4AE">➜</div>
      <div style="flex:1;background:#FFF3E0;border-top:5px solid #FB8C00;border-radius:0 0 12px 12px;padding:12px">
        <div style="font-weight:800;color:#E65100">第 2 轮 · 事件卡回调</div>
        <div style="font-size:13px;color:#F57C00;margin-top:6px">政策/竞争/技术事件集体打压估值——<b>制造挫败感</b>，暴露认知误区</div>
      </div>
      <div style="align-self:center;font-size:22px;color:#90A4AE">➜</div>
      <div style="flex:1;background:#E3F2FD;border-top:5px solid #1E88E5;border-radius:0 0 12px 12px;padding:12px">
        <div style="font-weight:800;color:#0D47A1">第 3 轮 · 分化</div>
        <div style="font-size:13px;color:#1976D2;margin-top:6px">事前准备充分的组抗住风险、估值回升——<b>事前准备决定抗风险能力</b></div>
      </div>
    </div>
    """
    md_html(timeline_html)
    st.divider()

    if not st.session_state.started:
        st.markdown("### 🎮 开局设置（董事会视角：选行业 → 组阁 → 盘点 → 定首轮预算）")
        st.info("💡 你是**董事会成员**，不是执行者——钱怎么分、人怎么配、风险接不接受，都得自己拍板。第一轮先召开首次董事会，完成「选行业 → 组阁（组建团队）→ 盘点家底 → 定首轮预算」四项决策。")
        # 四行业对比卡
        ind_rows = []
        for k, ind in INDUSTRIES.items():
            ind_rows.append({
                "行业": f"{k}·{ind['name']}",
                "Q 初始": ind["q0"], "C 天花板": ind["c_cap"], "H 基准(万/轮)": ind["h_base"],
                "单位存储(万/TB)": ind["unit_storage"], "难度": "较难" if ind["h_base"] >= 15 else "适中",
                "典型陷阱": ind["trap"],
            })
        st.dataframe(pd.DataFrame(ind_rows), use_container_width=True, hide_index=True)
        st.caption("👉 表中数值越小越省心；医疗健康行业 C 天花板最低（0.5），对合规要求最苛刻——想挑战选它。")
        c1, c2 = st.columns(2)
        with c1:
            role = st.selectbox("**你在董事会中的身份**", ["数据运营总监", "数据分析员", "算法工程师", "首席数据官"], index=0)
            st.session_state.role = role
        with c2:
            ind_key = st.selectbox("**选择案例行业**", list(INDUSTRIES.keys()), index=0)
            ind = INDUSTRIES[ind_key]
        st.warning("⚠️ 行业差异教学建议：制造专业易选制造、信管易选零售——竞赛建议强制抽签或按专业混编，跳出舒适区。")
        if st.button("🚀 召开首次董事会（领取每轮350万预算）", type="primary"):
            st.session_state.industry = ind_key
            st.session_state.started = True
            st.session_state.round = 1
            st.session_state.step = 1
            record("开始实验", f"行业={ind_key}，角色={role}")
            st.rerun()
    else:
        ind = INDUSTRIES[st.session_state.industry]
        st.success(f"**实验进行中**：行业={st.session_state.industry}·{ind['name']}，角色={st.session_state.role}，当前第 {st.session_state.round} 轮")
        st.markdown(f"**你的行业基线**：Q 初始 {ind['q0']} ｜ C 天花板 {ind['c_cap']} ｜ H 基准 {ind['h_base']}万/轮 ｜ 单位存储 {ind['unit_storage']}万/TB ｜ 典型陷阱：{ind['trap']}")
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
    # 当前步骤引导条
    stp = st.session_state.step
    if stp <= 24:
        prev_part = f"<span style='color:#43A047;font-weight:600'>← {STEP_NAMES[stp-1]} ✅</span>" if stp > 1 and (stp-1) in st.session_state.done else ("<span style='color:#B0BEC5'>← 起点</span>" if stp == 1 else f"<span style='color:#90A4AE'>← {STEP_NAMES[stp-1]}</span>")
        cur_part = f"<span style='background:#1E88E5;color:#fff;border-radius:8px;padding:2px 10px;font-weight:800'>📍 第{stp}步 · {STEP_NAMES[stp]}</span>"
        nxt_part = f"<span style='color:#90A4AE'>→ {STEP_NAMES[stp+1]}</span>" if stp < 24 else ""
        st.markdown(f"<div style='background:#F5F9FF;border:1px solid #BBDEFB;border-radius:10px;padding:8px 14px;font-size:14px'>{prev_part}　{cur_part}　{nxt_part}</div>", unsafe_allow_html=True)
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
        # v2.0 修改①+新增②：董事会开局 · 组阁（8 角色，6 必选 + 2 可选，年薪计入当轮 H）
        st.markdown("**召开首次董事会 · 组阁**：你是**董事会成员**，拍板定人。8 个角色里 6 个必选、2 个可选；**团队年薪直接计入当轮 H（持有成本）**——人不是白用的。")
        st.info("💡 小白提示：董事会就是公司里拍板大事的那几个人。钱怎么分、人怎么配、风险接不接受，都得自己定。")
        salary_total = 0.0
        chosen_ids = []
        cols = st.columns(2)
        for i, role in enumerate(ROLE_TEAM):
            with cols[i % 2]:
                must_tag = "（必选）" if role["must"] else "（可选）"
                checked = role["must"]
                ok = st.checkbox(f"{role['name']}{must_tag} · 年薪 {role['salary']}万", value=checked, key=f"roster_{role['id']}_{st.session_state.round}")
                if ok:
                    chosen_ids.append(role["id"]); salary_total += role["salary"]
                st.caption(f"{role['desc']}｜{role['effect']}")
        st.markdown(f"**组阁年薪合计**：**{salary_total:.0f}万/轮**（直接计入本轮 H；多招一个人，等于每月多一笔固定开销）")
        if not all(r["must"] for r in ROLE_TEAM if r["must"]) and not st.session_state.get("roster_ok"):
            st.warning("⚠️ 6 个必选角色不能少（数据工程师/治理师/合规专员/算法工程师/产品经理/运营经理）")
        if st.button("✅ 锁定组阁（年薪计入 H）", disabled=step_done(step) or not all(r["must"] for r in ROLE_TEAM if r["must"])):
            st.session_state.decisions["team_setup"] = [r["name"] for r in ROLE_TEAM if r["id"] in chosen_ids]
            st.session_state.decisions["team_roster"] = chosen_ids
            st.session_state.decisions["team_salary"] = salary_total
            t = st.session_state.team
            # 角色带来的团队三维加成（简化：按角色特性给基础三维增益）
            t["cap"] = min(100, t["cap"] + 3); t["mot"] = min(100, t["mot"] + 3); t["ret"] = min(100, t["ret"] + 3)
            record("步骤1·董事会组阁", f"{len(chosen_ids)}人，年薪{salary_total:.0f}万")
            mark_done(1, "董事会组阁")
            st.rerun()
    elif step == 2:
        # v2.0 新增③：家底盘点清单（五类数据类型）
        ind = INDUSTRIES[st.session_state.industry]
        st.markdown(f"**盘点家底**（{st.session_state.industry}行业）：先搞清楚“我有什么”，再决定“我缺什么、要不要花钱买/采”。")
        st.info("💡 小白提示：很多团队一上来就花钱买数据，最后发现手里的数据本来就能用——这就是现实中“重复造轮子”的坑。")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Q 初始", ind["q0"])
        with c2: st.metric("C 天花板", ind["c_cap"])
        with c3: st.metric("H 基准", f"{ind['h_base']}万/轮")
        with c4: st.metric("团队状态", f"{st.session_state.team['cap']}/{st.session_state.team['mot']}/{st.session_state.team['ret']}")
        st.markdown("**🧰 现有家底——五类数据类型盘点**")
        inv_df = pd.DataFrame([{"类型": x["name"], "是什么": x["desc"], "能干什么": x["use"], "常见坑": x["trap"]} for x in DATA_TYPE_INVENTORY])
        st.dataframe(inv_df, use_container_width=True, hide_index=True)
        st.markdown(f"**⚠️ 行业典型陷阱**：{ind['trap']}——记得提醒自己别踩。")
        if st.button("✅ 确认盘点完成（免费）", disabled=step_done(step)):
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
        # v2.0 新增⑫：预算后果预告横幅
        st.markdown("**编制预算**：四类资金分配（采集/治理/人力/合规）。本轮先投入 **120万**。")
        st.warning("⏭️ **后果预告**：预算花在「治理」上 → Q 升；花在「合规」上 → C 守住；花太少 → 后续可能出现「质量塌陷」「合规事故」扣款。下轮会投放事件卡（政策/价格战/客户流失/技术替代），留足现金才有对策。")
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
        # v2.0 新增⑥+⑪：数据来源与采集限值 + 常见数据类型小课堂
        st.markdown("**选择数据源与采集量**：数据分「公司给的」「爬取的」「第三方购买」三类，各有采集限值与越限后果。")
        st.info("💡 小白提示：爬取数据虽然单价便宜，但越限后果最重——合规红线不因“数据便宜”而放宽。便宜的数据可能最贵。")
        with st.expander("📚 常见数据类型小课堂（先建立直觉再选数据）", expanded=False):
            kinds_df = pd.DataFrame([{"类型": x["name"], "是什么": x["desc"], "例子": x["example"], "在实验中的处理": x["handle"]} for x in DATA_KINDS_CLASS])
            st.dataframe(kinds_df, use_container_width=True, hide_index=True)
            st.caption("结构化最好清洗（Q 加成最高）；非结构化存得贵（H 高）。")
        src_choice = st.selectbox("数据来源类型：", [s["name"] for s in SOURCE_TYPES], index=0)
        src_cfg = next(s for s in SOURCE_TYPES if s["name"] == src_choice)
        default_tb = src_cfg["limit_tb"]
        source_tb = st.number_input(f"采集量（TB，行业限值 {src_cfg['limit_tb']}TB）", 1, 80, int(default_tb), step=1, key=f"src_tb_{st.session_state.round}")
        over = max(source_tb - src_cfg["limit_tb"], 0)
        if over > 0:
            st.warning(f"⚠️ **越限预告**：超过 {src_cfg['limit_tb']}TB 共 {over}TB —— {src_cfg['over']}")
        st.markdown(f"**合规要求**：{src_cfg['compliance']} ｜ **单位成本**：{src_cfg['unit_cost']}万/TB")
        if st.button("✅ 确认数据源（按采集量扣款）", disabled=step_done(step)):
            cost = round(source_tb * src_cfg["unit_cost"], 1)
            if spend(f"步骤5·{src_choice}", int(cost * 10000)):
                st.session_state.decisions["source"] = src_cfg["id"]
                st.session_state.decisions["source_tb"] = source_tb
                st.session_state.decisions["source_over_limit"] = over > 0
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
        # v2.0 新增⑨：可追溯审计 → T 得分 +30
        audit_ok = st.checkbox("🛡️ 同步开启血缘追溯 + 审计留痕（免费，可信度 T +30）", key=f"audit_{st.session_state.round}")
        if st.button("✅ 确认存储方案（按选项扣款）", disabled=step_done(step)):
            if "数据湖" in choice:
                st.session_state.decisions["storage"] = "数据湖"
                cost = 0
            elif "数仓" in choice:
                st.session_state.decisions["storage"] = "数仓"; cost = 20
            else:
                st.session_state.decisions["storage"] = "湖仓一体"; cost = 35
            st.session_state.decisions["audit_trail"] = audit_ok
            if spend(f"步骤7·{st.session_state.decisions['storage']}", cost * 10000):
                mark_done(7, "接入与存储")
                st.rerun()
    elif step == 8:
        st.markdown("**确权登记 + 责任人签字**：入表前置动作，决定能否资本化（无形资产）；签字即负责，可信度 T +30。")
        st.markdown("- 完成确权登记 → 出表时可选「无形资产」资本化（评分更高）；**责任人签字 → 可信度 T +30**")
        st.markdown("- 跳过确权 → 只能按「存货」计量，且合规评分降低")
        if st.button("✅ 完成确权登记并签字（免费）", disabled=step_done(step)):
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
        # v2.0 新增⑧：脱敏小课堂 + 前置 2 题测验
        st.markdown("**安全分级与脱敏**：决定 C 系数上限（行业天花板内）。")
        with st.expander("📖 脱敏小课堂（先看懂再动手）", expanded=False):
            st.markdown("**一句话解释**：脱敏就是把数据里能认出具体某个人的信息去掉或换掉，让它既能用来分析，又不会泄露谁是谁——就像把成绩单上的名字遮住，老师还能统计平均分，但不知道是谁考的。")
            st.markdown("**为什么要脱敏？** 数据里往往藏着身份证号、手机号、住址、病历等“能定位到具体的人”的信息。直接拿出去卖或用，等于把别人的隐私公开了——这是违法的（违反《个人信息保护法》），也是本实验中 **C 系数会归零** 的原因。")
            st.markdown("**脱敏的难点**：脱得太狠，数据就没用了（Q 下降）；脱得太轻，隐私还在泄露（C 下降）。真实企业每天都在做这个取舍。")
            mask_df = pd.DataFrame([{"方法": x["name"], "怎么做": x["desc"], "举例": x["example"], "适用": x["fit"]} for x in MASK_METHODS])
            st.dataframe(mask_df, use_container_width=True, hide_index=True)
        st.markdown("**📝 前置小测验（答对 2 题才能执行脱敏）**")
        q1 = st.radio("Q1：脱敏的目的是？", ["A. 让数据更好看", "B. 去掉/替换能识别个人的信息，既能分析又不泄露", "C. 删除所有数据"], key=f"mq1_{st.session_state.round}")
        q2 = st.radio("Q2：手机号 138****6721 用了哪种脱敏方法？", ["A. 掩码", "B. 哈希", "C. 泛化"], key=f"mq2_{st.session_state.round}")
        q_ok = ("B" in q1) and ("A" in q2)
        st.session_state.mask_quiz_ok[st.session_state.round] = q_ok
        if not q_ok:
            st.warning("❌ 请先通过测验（Q1 选 B，Q2 选 A），通过后才能执行脱敏——避免凭感觉乱点。")
        choice = st.selectbox("脱敏方案：", ["全量脱敏（15万，C 保持）", "部分脱敏（8万，C≤0.8）", "未脱敏（0万，⚠️C=0.3 且罚没风险）"], index=0, key=f"mask_{st.session_state.round}")
        if st.button("✅ 确认脱敏方案", disabled=step_done(step) or not q_ok):
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
        # v2.0 新增⑤：A/B/C 三套赋能方案对比卡，强制三选一 + 记录原因（复盘第 2 问依据）
        st.markdown("**赋能方案三选一**：现实里企业做数字化要在“花多少钱、做多深”之间取舍。三选一后系统锁定方案。")
        st.info("💡 小白提示：给三个清楚的选项，比自由填空更容易理解“决策”的含义，也避免面对空白输入框不知道填什么。")
        plan_df = pd.DataFrame([
            {"方案": p["name"], "投入成本": f"{p['cost']}万", "建设周期": f"{p['period']}轮", "预期现金流": p["cash_desc"], "Q加成": f"+{p['q_bonus']:.2f}", "风险": p["risk"], "适用": p["fit"]}
            for p in EMPOWER_PLANS
        ])
        st.dataframe(plan_df, use_container_width=True, hide_index=True)
        chosen_plan = st.radio("选择赋能方案（选定即锁定）：", [p["name"] for p in EMPOWER_PLANS], index=1, key=f"emp_{st.session_state.round}")
        plan = next(p for p in EMPOWER_PLANS if p["name"] == chosen_plan)
        st.warning(f"⏭️ **后果预告**：选 {plan['id']} 方案 → 立即开支 {plan['cost']}万，本轮现金流按完成度 ×{plan['effective']:.0%}，Q +{plan['q_bonus']:.2f}；风险：{plan['risk']}")
        reason = st.text_area("📝 为什么选这个方案？（将作为复盘第 2 问的依据）", height=80, key=f"emp_r_{st.session_state.round}")
        if st.button(f"✅ 锁定 {plan['id']} 方案（开支-{plan['cost']}万）", disabled=step_done(step) or not reason.strip()):
            if spend("步骤13·赋能方案", plan["cost"] * 10000):
                st.session_state.decisions["empower_plan"] = plan["id"]
                st.session_state.decisions["empower"] = plan["id"]
                st.session_state.decisions["empower_reason"] = reason.strip()
                # 方案生效场景：默认取行业前 2 个变现场景作为承载（保持现金流引擎不变）
                ind = INDUSTRIES[st.session_state.industry]
                st.session_state.decisions["scenes"] = list(ind["scenes"].keys())[:2]
                mark_done(13, "赋能方案锁定")
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
        # v2.0 新增⑦：数据产品交易合同（可签署，2/3/7 条合规校验）
        st.markdown("**找买家与签署数据产品交易合同**：卖数据不是点一下按钮，而是要谈条件、担责任。逐条确认并签署本合同。")
        st.info("💡 小白提示：很多企业数据卖不出去，问题就出在合同条款说不清、责任划分不明。签完这份合同，你会直观感受到“卖数据要谈条件、担责任”。")
        with st.expander("📄 合同全文（9 条，关键条款留空待填）", expanded=False):
            for cl in CONTRACT_CLAUSES:
                st.markdown(cl)
            st.markdown("甲方签字（盖章）：____________　　乙方签字（盖章）：____________　　签署日期：____ 年 __ 月 __ 日")
        c1, c2 = st.columns(2)
        with c1:
            party_a = st.text_input("甲方（数据提供方）名称：", key=f"ca_{st.session_state.round}")
            party_b = st.text_input("乙方（数据购买方）名称：", key=f"cb_{st.session_state.round}")
            tb_size = st.number_input("数据规模（TB）：", 1, 100, 5, key=f"ct_{st.session_state.round}")
            cover_mon = st.number_input("覆盖周期（月）：", 1, 36, 6, key=f"cm_{st.session_state.round}")
            total_amt = st.number_input("合同总额（万元）：", 1, 500, 50, key=f"cs_{st.session_state.round}")
        with c2:
            legal_src = st.selectbox("第二条【校验】数据来源合法性：", ["内部授权（合法）", "合规采集（合法）", "来源不明确（违规）"], key=f"cl_{st.session_state.round}")
            use_limit = st.text_input("第三条【校验】用途限制（具体用途，非空）：", key=f"cu_{st.session_state.round}")
            liability = st.radio("第七条【校验】法律责任承担方：", ["甲方承担（数据方负责）", "乙方承担", "双方各半"], key=f"clb_{st.session_state.round}")
            q_floor = st.number_input("第六条 Q 下限（0.5-0.9）：", 0.5, 0.9, 0.7, step=0.05, key=f"cq_{st.session_state.round}")
        buyer_choice = st.selectbox("买家结构（影响下跌路径）：", ["多个分散买家（收入×1.0，无依赖风险）", "单一独家大客户（收入×1.5，⚠️单一客户依赖 D 20%）", "双客户（收入×1.2，轻度依赖）"], index=0)
        # 合规校验（第 2、3、7 条）
        errs = []
        if "来源不明确" in legal_src: errs.append("第 2 条：数据来源不合法，合同不能签（需内部授权或合规采集）")
        if not use_limit.strip(): errs.append("第 3 条：用途限制不能为空，必须写明数据只能用于什么")
        if "乙方承担" in liability or "双方各半" in liability: errs.append("第 7 条：法律责任必须由甲方（数据提供方）承担——来源违法/未脱敏/超范围使用，责任在数据方")
        if not party_a.strip() or not party_b.strip(): errs.append("甲乙方名称必填")
        for e in errs:
            st.error(f"❌ {e}")
        if st.button("✍️ 签署合同（真实生效）", disabled=step_done(step) or bool(errs)):
            st.session_state.decisions["contract"] = "完整授权"
            st.session_state.decisions["contract_filled"] = {"甲方": party_a, "乙方": party_b, "TB": tb_size, "周期月": cover_mon, "总额万": total_amt, "用途": use_limit, "Q下限": q_floor, "责任方": "甲方"}
            st.session_state.decisions["buyer"] = "多个分散买家" if "分散" in buyer_choice else ("单一独家大客户" if "独家" in buyer_choice else "双客户")
            record("步骤19·签署数据交易合同", f"总额{total_amt}万·{use_limit[:10]}…")
            mark_done(19, "签署数据合同")
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
    """S21 团队激励设计器（v2.0：5 工具，预算=现金×15% 上限 50 万，不能全选，金点子征集）"""
    st.markdown("**团队激励投放**：每轮激励总预算 = 团队当前现金 × 15%（上限 50 万），在 5 个工具中组合，**不能全选**。")
    st.info("💡 工具箱参考真实企业实践：海底捞（授权一线、师徒制）、胖东来（高薪+高福利+尊重员工）。")
    budget_limit = min(int(st.session_state.budget * 0.15), 500000)
    options = {}
    c1, c2 = st.columns(2)
    for i, inc in enumerate(INCENTIVES):
        col = c1 if i % 2 == 0 else c2
        with col:
            t = inc["type"]
            emoji = "💰" if t == "金钱" else ("📚" if inc["id"] == "train" else ("💼" if inc["id"] == "care" else ("🏅" if inc["id"] == "honor" else "📈")))
            options[inc["id"]] = st.checkbox(f"{emoji} {inc['name']}（{t}，{'免费' if inc['cost']==0 else fmt(inc['cost'])}）", key=f"inc_{inc['id']}_{st.session_state.round}")
            st.caption(f"{inc['ref']}｜{inc['hidden']}")
    total_cost = sum(inc["cost"] for inc in INCENTIVES if options.get(inc["id"]))
    n_chosen = sum(1 for v in options.values() if v)
    st.markdown(f"**激励合计**：{fmt(total_cost)}（本轮预算上限 {fmt(budget_limit)}）")
    if total_cost > budget_limit:
        st.error("❌ 超激励预算！请减少选择")
    if n_chosen >= 5:
        st.warning("⚠️ 不能全选：5 个工具至少要舍弃 1 个——什么都给，等于什么都没给。")
    can_go = total_cost <= budget_limit and n_chosen < 5
    if st.button("✅ 投放激励方案（按选择扣款）", disabled=step_done(21) or not can_go):
        chosen = [i["id"] for i in INCENTIVES if options.get(i["id"])]
        if total_cost > 0 and not spend("步骤21·团队激励", total_cost):
            st.stop()
        st.session_state.incentives = chosen
        st.session_state.incentives_round[st.session_state.round] = chosen
        t = st.session_state.team
        money_only = all(INC_BY_ID[i]["type"] == "金钱" for i in chosen) and len(chosen) > 0
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
                if all(INC_BY_ID[i]["type"] == "金钱" for i in prev):
                    t["mot"] = max(0, t["mot"] - 10)  # 纯金钱第二轮反噬
        mark_done(21, "团队激励投放")
        st.rerun()
    # v2.0 新增⑩：金点子征集（结算后开放）
    st.divider()
    st.markdown("### 💡 我的激励金点子（结算后开放，教师端评估采纳）")
    if st.session_state.round in st.session_state.settled or step_done(23):
        idea = st.text_area("提出文档里没有的激励创意（如：弹性工时、内部创业孵化……）：", height=80, key=f"idea_{st.session_state.round}")
        if st.button("📤 提交金点子"):
            if idea.strip():
                st.session_state.gold_ideas[st.session_state.round] = idea.strip()
                record(f"第{st.session_state.round}轮·金点子", idea.strip()[:20])
                st.success("✅ 已提交，等待教师端评估（采纳 → 稳定+10 意愿+10 V+5%）")
                st.rerun()
    else:
        st.caption("本轮结算后开放（需先完成第 23 步估值）。")

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
        st.markdown("#### 📈 三轮净值走势（一眼看懂涨跌）")
        c1, c2 = st.columns([3, 2])
        with c1:
            st.line_chart(df.set_index("轮次")[["V净值(万)"]], height=260)
            st.caption("绿涨红跌：第一轮普遍上涨 → 第二轮事件卡回调 → 第三轮分化。")
        with c2:
            st.markdown("**三轮估值明细**")
            st.dataframe(df, use_container_width=True, hide_index=True)
        # v2.0 新增④：现状 vs 上一轮（同口径对比，7 项指标）
        if len(st.session_state.val_history) >= 2:
            st.markdown("#### 🔁 现状 vs 上一轮（同口径对比 · 复盘仪表盘）")
            st.caption("别只盯 V 涨跌——看这 7 项，一眼找出“V 涨是因为 Q 上来了，还是 H 也跟着涨了”。")
            prev = st.session_state.val_history[-2]
            cur = st.session_state.val_history[-1]
            rows = []
            for label, key in [("资产净值 V（万）", "v"), ("质量系数 Q", "q"), ("合规系数 C", "c"), ("持有成本 H（万）", "h"), ("减值准备 D（万）", "d"), ("数据可信度 T", "t_score")]:
                pv_, cv_ = prev.get(key), cur.get(key)
                arrow = "↑" if cv_ > pv_ else ("↓" if cv_ < pv_ else "→")
                rows.append([label, pv_, cv_, arrow, ""])
            pt, ct = prev.get("team", {}), cur.get("team", {})
            for k, kname in [("cap", "团队·能力"), ("mot", "团队·意愿"), ("ret", "团队·稳定")]:
                pv_, cv_ = pt.get(k, 0), ct.get(k, 0)
                arrow = "↑" if cv_ > pv_ else ("↓" if cv_ < pv_ else "→")
                rows.append([kname, pv_, cv_, arrow, ""])
            cmp_df = pd.DataFrame(rows, columns=["指标", f"第{len(st.session_state.val_history)-1}轮", f"第{len(st.session_state.val_history)}轮", "变化", "原因说明（学生填）"])
            st.dataframe(cmp_df, use_container_width=True, hide_index=True)
        # 四系数每轮变化
        st.markdown("#### 🔍 影响估值的四个系数（Q/C/H/D 每轮变化）")
        c1, c2 = st.columns([3, 2])
        with c1:
            qc_df = df.set_index("轮次")[["Q", "C"]].copy()
            qc_df["H"] = df.set_index("轮次")["H"]
            qc_df["D"] = df.set_index("轮次")["D"]
            st.bar_chart(qc_df, height=260)
            st.caption("Q 质量 / C 合规 / H 持有成本 / D 减值——看哪一项拖了 V 的后腿。")
        with c2:
            # 每轮 V 的构成解读（自动生成一句话）
            for _, row in df.iterrows():
                verdict = "✅ 正资产" if row["V净值(万)"] > 0 else "⚠️ 负资产"
                st.markdown(f"**第{int(row['轮次'])}轮**：V={row['V净值(万)']:.1f}万（{verdict}）　Q={row['Q']:.2f}｜C={row['C']:.2f}｜H={row['H']:.1f}｜D={row['D']:.1f}")
            st.caption("同一组 Q 下，C 归零（合规出事）或 D 计提（事件损失）会直接把 V 打下去。")
        # 公式公开总表
        with st.expander("📐 主公式与口径说明（红线：公式必须对学生公开）", expanded=False):
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
    drop_html = """
    <div style="display:flex;gap:10px;flex-wrap:wrap;padding:4px 0">
    {cards}
    </div>
    """
    drop_cards = []
    for k, p in DROP_PATHS.items():
        drop_cards.append(f"""
        <div style="flex:1;min-width:150px;background:#FFF8F0;border:1px solid #FFCC80;border-radius:10px;padding:10px">
        <div style="font-weight:700;color:#BF360C;font-size:13px">{p['label']}</div>
        <div style="font-size:12px;color:#6D4C41;margin-top:4px">{p['desc']}</div>
        </div>
        """)
    md_html(drop_html.format(cards="".join(drop_cards)))
    # 事件卡库
    st.divider()
    st.markdown("### 🎴 事件卡库（20 张，P-政策 / W-价格战 / C-客户流失 / T-技术替代）")
    cols = st.columns(4)
    cats = {"P-": "📜 政策类", "W-": "⚔️ 价格战类", "C-": "👥 客户流失类", "T-": "🤖 技术替代类"}
    for ci, (pre, cname) in enumerate(cats.items()):
        with cols[ci]:
            st.markdown(f"**{cname}**")
            for code in [f"{pre}{i:02d}" for i in range(1, 6)]:
                card = EVENT_CARDS[code]
                st.markdown(f"`{code}` **{card['name']}**\n\n<small>{card['desc']}</small>", unsafe_allow_html=True)
    # 已投放
    st.divider()
    st.markdown("**📌 已投放事件卡**：")
    for rnd in [1, 2, 3]:
        evs = st.session_state.events_used.get(rnd, [])
        if evs:
            ev_html = "　".join(f"<span style='background:#FFF3E0;border:1px solid #FFB74D;border-radius:8px;padding:2px 8px;font-size:13px'>{e}·{EVENT_CARDS[e]['name']}</span>" for e in evs)
            st.markdown(f"- **第{rnd}轮**：{ev_html}", unsafe_allow_html=True)

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
    st.bar_chart(pd.DataFrame({"维度": ["能力", "意愿", "稳定"], "数值": [t["cap"], t["mot"], t["ret"]]}).set_index("维度"), height=220)
    st.caption("三根柱越高，团队越健康；低于 60 会拖累对应环节表现。")
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
    money_rounds = [r for r in st.session_state.incentives_round if st.session_state.incentives_round[r] and all(INC_BY_ID[i]["type"] == "金钱" for i in st.session_state.incentives_round[r])]
    train_auth = any("train" in st.session_state.incentives_round.get(r, []) for r in [1, 2, 3])
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
    if locked(r):
        cur = 3
    elif r in st.session_state.closed_round:
        cur = 2
    else:
        cur = 1
    state_html = """
    <div style="display:flex;gap:10px;align-items:center;padding:4px 0">
      {nodes}
    </div>
    """
    states = [("① 开放提交", "学生逐步入表决策"), ("② 关闭提交", "等待结算估值"), ("③ 已结算·只读", "数据锁定，可开下一轮")]
    nodes = []
    for i, (name, desc) in enumerate(states, start=1):
        active = (i == cur)
        done = (i < cur)
        color = "#43A047" if done else ("#1E88E5" if active else "#B0BEC5")
        bg = "#E8F5E9" if done else ("#E3F2FD" if active else "#ECEFF1")
        nodes.append(f"""
        <div style="flex:1;background:{bg};border:2px solid {color};border-radius:12px;padding:10px;text-align:center">
        <div style="font-weight:800;color:{'#1B5E20' if done else ('#0D47A1' if active else '#546E7A')}">{name}{' ✅' if done else ''}</div>
        <div style="font-size:12px;color:#546E7A;margin-top:4px">{desc}</div>
        </div>""")
        if i < 3:
            nodes.append('<div style="font-size:20px;color:#90A4AE">➜</div>')
    md_html(state_html.format(nodes="".join(nodes)))
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
    # v2.0 新增⑩：金点子评估（教师扮演"公司专员"）
    st.markdown("#### 💡 金点子评估（公司专员 · 教师扮演）")
    if st.session_state.gold_ideas:
        for rid, idea in list(st.session_state.gold_ideas.items()):
            adopted = st.session_state.gold_idea_adopted.get(rid, False)
            st.markdown(f"- **第{rid}轮金点子**：{idea}")
            if not adopted:
                if st.button(f"✅ 采纳第{rid}轮金点子（稳定+10 意愿+10 V+5%）"):
                    adopt_gold_idea(rid)
                    st.rerun()
            else:
                st.success(f"✅ 第{rid}轮已采纳：该组稳定+10 意愿+10，估值 V +5%")
    else:
        st.caption("暂无学生提交的金点子。")
    st.divider()
    # 六维评分
    st.markdown("#### 📊 六维评分体系（终局计算）")
    st.markdown("| 维度 | 权重 | 数据来源 |\n|---|---|---|\n| 数据资产净值 V（终值） | 30% | 估值引擎 |\n| 资产质量 Q×C | 20% | 估值引擎 |\n| 估值报告与入表合规性 | 15% | 出表披露物 |\n| 团队状态与健康度 | 15% | 激励系统仪表盘 |\n| 战略一致性与迭代逻辑 | 10% | 三轮决策对比 |\n| 复盘反思深度 | 10% | 复盘三问 |")
    if len(st.session_state.val_history) >= 3:
        if st.button("⚖️ 计算终局六维评分（真实计算）", type="primary"):
            compute_eval()
            st.rerun()

def adopt_gold_idea(rid):
    """v2.0 新增⑩：教师采纳金点子 → 稳定+10 意愿+10，该轮估值 V +5%"""
    st.session_state.gold_idea_adopted[rid] = True
    t = st.session_state.team
    t["ret"] = min(100, t["ret"] + 10)
    t["mot"] = min(100, t["mot"] + 10)
    for v in st.session_state.val_history:
        if v["round"] == rid:
            v["v"] = round(v["v"] * 1.05, 1)
    record(f"第{rid}轮金点子采纳", "稳定+10 意愿+10 V+5%")

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
    # v2.0：复盘三问与决策记录联动——展示学生在步骤13写下的赋能原因，作为问题2的依据
    if st.session_state.empower_reason:
        st.info(f"📌 你在步骤13写下的赋能方案选择原因（复盘第 2 问的依据）：**{st.session_state.empower_reason}**")
    st.markdown("**复盘三问**：")
    st.markdown("1. 你的资产在哪一步开始「变质」？如果重来，你会砍掉哪一笔投入？")
    st.markdown("2. 你的团队激励方案，哪一项真正产生了复利？哪一项是浪费？（结合你在步骤13写的赋能原因）")
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
        st.markdown(f"#### 综合得分：**{e['total']}分** / 100")
        st.progress(min(e["total"] / 100, 1.0))
        st.markdown("#### 📊 六维雷达对比（哪项强、哪项拖后腿，一目了然）")
        six_df = pd.DataFrame({
            "维度": ["资产净值V", "资产质量Q×C", "入表合规性", "团队健康度", "战略一致性", "复盘深度"],
            "得分": [e["V"], e["QC"], e["listing"], e["team"], e["strategy"], e["reflection"]],
            "权重": [30, 20, 15, 15, 10, 10],
        })
        cA, cB = st.columns([2, 1])
        with cA:
            st.bar_chart(six_df.set_index("维度")[["得分"]], height=240)
        with cB:
            st.markdown("**权重说明**")
            for _, row in six_df.iterrows():
                st.markdown(f"- {row['维度']}：权重 {row['权重']}%")
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
