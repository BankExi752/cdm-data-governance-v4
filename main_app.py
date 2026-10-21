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
  - 4 行业（制造/零售/医疗/能源）× 6 篇章 × 25 步 × 3 轮估值
  - 三轮节奏：第一轮普遍上涨 → 第二轮事件卡集体回调 → 第三轮分化
  - 20 张事件卡（P-/W-/C-/T- 各 5 张），五条下跌路径自动触发
  - 团队三维状态（能力/意愿/稳定）+ 6 工具激励设计器 + 隐藏规则
  - 六维评分 + 特别奖（增值评价）+ 复盘三问
  - 审计日志全程留痕 + CSV 导出；所有按钮真实生效，支持撤销
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import os, csv, threading, time as _time, re

# ========== 页面配置 ==========
import textwrap

def md_html(s):
    """逐行去掉前导缩进后以 HTML 渲染（避免 Markdown 把缩进行当代码块显示原文）"""
    lines = [ln.strip() for ln in s.splitlines()]
    return st.markdown("\n".join(lines), unsafe_allow_html=True)

st.set_page_config(
    page_title="数据资产运营总监——基于九层能力框架的数据资产化与合规治理虚拟仿真实验",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ========== 数据资产·深蓝科技主题 v3.2（纯视觉 CSS，零逻辑改动） ==========
_THEME_CSS = """<style>
:root{
  --dp-blue:#1554F0; --dp-deep:#0F2B46; --dp-cyan:#00B8D9;
  --dp-bg:#F6F9FE; --dp-card:#FFFFFF; --dp-ink:#1B2A41; --dp-line:#E4EDF9;
}
html, body, [data-testid="stAppViewContainer"]{
  background:linear-gradient(180deg,#F6F9FE 0%,#EDF3FB 100%);
  font-family:"Microsoft YaHei","PingFang SC","Source Han Sans SC",system-ui,sans-serif;
  color:var(--dp-ink);
}
[data-testid="stHeader"]{background:rgba(246,249,254,.0);}
/* 主按钮：科技蓝渐变 */
.stButton > button{
  border-radius:10px;font-weight:600;
  background:linear-gradient(135deg,#1554F0,#00B8D9);color:#fff;border:none;
  box-shadow:0 3px 10px rgba(21,84,240,.22);
  transition:transform .15s, box-shadow .15s;
}
.stButton > button:hover{transform:translateY(-1px);box-shadow:0 6px 16px rgba(21,84,240,.32);color:#fff;}
.stButton > button:active{transform:translateY(0);}
/* Tab 导航：选中高亮 */
.stTabs [data-baseweb="tab-list"]{gap:6px;border-bottom:2px solid var(--dp-line);}
.stTabs [data-baseweb="tab"]{
  border-radius:10px 10px 0 0;padding:10px 16px;font-weight:600;color:#4A5A78;font-size:15px;
}
.stTabs [aria-selected="true"]{
  color:var(--dp-blue);background:linear-gradient(180deg,rgba(21,84,240,.10),rgba(21,84,240,0));
}
/* 进度条：渐变 */
.stProgress > div > div > div{background:linear-gradient(90deg,#1554F0,#00B8D9);border-radius:8px;}
/* 侧边栏：浅蓝科技面板（控件保持深字可读） */
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#EAF2FC 0%,#F6F9FE 100%);
  border-right:1px solid var(--dp-line);
}
[data-testid="stSidebar"] .stMarkdown h1,[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3{color:var(--dp-deep);}
/* 指标卡 / 表格卡片化 */
[data-testid="stMetric"]{
  background:var(--dp-card);border:1px solid var(--dp-line);border-radius:14px;
  padding:10px 12px;box-shadow:0 3px 12px rgba(15,43,70,.06);
}
/* 指标值防截断：窄容器（侧边栏/小窗口）下不用省略号，完整显示并自适应字号 */
[data-testid="stMetricValue"]{
  overflow:visible !important; text-overflow:clip !important;
  white-space:normal !important; line-height:1.25;
  font-size:clamp(18px, 4.2vw, 26px);
}
[data-testid="stMetricLabel"]{font-size:13px;color:#4A5A78;padding-bottom:4px;}
[data-testid="stMetricDelta"]{font-size:13px;}
[data-testid="stDataFrame"],[data-testid="stTable"]{
  border-radius:12px;overflow:hidden;box-shadow:0 3px 12px rgba(15,43,70,.06);
}
/* expander / 分割卡片 */
[data-testid="stExpander"]{
  border:1px solid var(--dp-line);border-radius:12px;
  background:rgba(255,255,255,.72);box-shadow:0 2px 8px rgba(15,43,70,.04);
}
[data-testid="stExpander"] summary{font-weight:600;}
/* 正文排版 */
.stMarkdown p,.stMarkdown li{line-height:1.75;}
/* 滚动条 */
::-webkit-scrollbar{width:8px;height:8px;}
::-webkit-scrollbar-thumb{background:#C9D8EE;border-radius:8px;}
::-webkit-scrollbar-track{background:transparent;}
</style>"""

def apply_theme():
    """注入全局主题样式（纯视觉）"""
    st.markdown(_THEME_CSS, unsafe_allow_html=True)

apply_theme()

INIT_BUDGET = 3500000  # 每轮 350 万（v2.0 校准：含赋能45万/年薪计入H/来源成本；标准路径约需 278 万，留余量应对事件卡）

# ========== 四行业基准值表 v3.1（未来能源/未来信息/未来制造/未来健康，成德绵三域流转） ==========
INDUSTRIES = {
    "未来制造": {
        "name": "人形机器人·低空经济（蜀工智能）",
        "enterprise": "蜀工智能", "flow": "成都整机 → 绵阳训练场 → 自贡试飞",
        "q0": 0.75, "c_cap": 0.9, "h_base": 15.0, "unit_storage": 1.5,
        "h_level": "高（存储+算力）", "trap": "采了大量振动数据却无故障样本",
        "base_tb": 12, "color": "#1E88E5",
        "scenes": {
            "良率提升": {"kind": "in", "base": 180, "desc": "用设备时序数据提升产线良率"},
            "预测性维护": {"kind": "in", "base": 150, "desc": "故障预测减少非计划停机"},
            "数字孪生服务": {"kind": "out", "base": 130, "desc": "设备数字孪生对外数据服务"},
        },
    },
    "未来信息": {
        "name": "6G 卫星·算力（蜀光智算）",
        "enterprise": "蜀光智算", "flow": "成都算法 → 绵阳芯片 → 资阳卫星",
        "q0": 0.70, "c_cap": 0.7, "h_base": 10.0, "unit_storage": 1.2,
        "h_level": "中", "trap": "买了流量却做不出复购模型",
        "base_tb": 8, "color": "#7C4DFF",
        "scenes": {
            "算力调度优化": {"kind": "in", "base": 180, "desc": "调度日志优化算力资源与能耗"},
            "卫星遥感数据服务": {"kind": "out", "base": 220, "desc": "遥感影像对外数据服务"},
            "算法模型对外输出": {"kind": "out", "base": 160, "desc": "AI 算法能力对外授权"},
        },
    },
    "未来健康": {
        "name": "核医疗·脑机（蜀康生命）",
        "enterprise": "蜀康生命", "flow": "成都临床 → 绵阳解码芯片 → 乐山核素",
        "q0": 0.65, "c_cap": 0.5, "h_base": 12.0, "unit_storage": 2.0,
        "h_level": "中高（安全等级要求）", "trap": "拿了数据永远过不了伦理审查",
        "base_tb": 5, "color": "#00A86B",
        "scenes": {
            "临床质控": {"kind": "in", "base": 170, "desc": "病历数据支撑院内质控"},
            "辅助诊断模型": {"kind": "out", "base": 190, "desc": "影像辅助诊断对外服务"},
            "科研数据集": {"kind": "out", "base": 120, "desc": "脱敏科研数据集授权（强受限）"},
        },
    },
    "未来能源": {
        "name": "绿色氢能（蜀能智造）",
        "enterprise": "蜀能智造", "flow": "成都研发 → 德阳制造/检测 → 攀西制氢",
        "q0": 0.70, "c_cap": 0.6, "h_base": 18.0, "unit_storage": 1.8,
        "h_level": "高（实时性要求）", "trap": "政策一变，商业模式归零",
        "base_tb": 20, "color": "#FF6D00",
        "scenes": {
            "制氢负荷预测服务": {"kind": "out", "base": 190, "desc": "制氢负荷预测对外服务"},
            "碳核算数据": {"kind": "out", "base": 140, "desc": "碳核算数据产品（政策敏感）"},
            "能耗优化": {"kind": "in", "base": 170, "desc": "能耗优化降低运营成本"},
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

# ========== v3.1 新增：团队成员画像（激励方案·成员画像，对症下药） ==========
TEAM_PROFILES = [
    {"name": "数据工程师 小张", "situation": "技术很强，但觉得没成长空间，想学新东西", "fit": "培训+授权（海底捞式：授权一线决策）"},
    {"name": "运营 小李", "situation": "父母年迈需照顾家庭，希望收入稳定有保障", "fit": "关怀福利 / 「孝心工资」类自定义激励（胖东来式）"},
    {"name": "客户 王总", "situation": "复购犹豫，很在意服务响应速度与被尊重的感觉", "fit": "关怀福利 / 公开表彰"},
]

# ========== v2.0 新增①：董事会组阁 8 角色（6 必选 + 2 可选，年薪计入当轮 H） ==========
ROLE_TEAM = [
    {"id": "de", "name": "数据工程师", "must": True, "salary": 12, "desc": "负责采集和清洗，把数据搬进来、洗干净", "effect": "采集效率+20%，清洗质量+10%"},
    {"id": "dg", "name": "数据治理师", "must": True, "salary": 10, "desc": "定标准、做质检，保证数据不乱", "effect": "Q 上限+0.05"},
    {"id": "co", "name": "合规专员", "must": True, "salary": 8, "desc": "审核数据能不能用、能不能卖，守住红线", "effect": "C 系数+0.05，事故概率-30%"},
    {"id": "alg", "name": "算法工程师", "must": True, "salary": 14, "desc": "建模做场景，把数据变成能用的东西", "effect": "赋能场景成功率+25%"},
    {"id": "pm", "name": "产品经理", "must": True, "salary": 10, "desc": "对接买家，把数据包装成能卖的产品", "effect": "对外收入+15%，成交周期-20%"},
    {"id": "op", "name": "运营经理", "must": True, "salary": 9, "desc": "管客户、管复购，让买家持续买单", "effect": "客户留存+15%"},
    {"id": "cons", "name": "行业顾问", "must": False, "salary": 7, "desc": "懂本行业门道，帮你避开行业特有坑", "effect": "行业陷阱识别+30%"},
    {"id": "legal", "name": "法务", "must": False, "salary": 8, "desc": "审合同，保证签的合同不出问题", "effect": "合同纠纷概率-40%"},
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

# ========== v3.1：数据来源与采集限值（六渠道并行，V3.1 方案第七节） ==========
SOURCE_TYPES = [
    {"id": "内部", "name": "公司内部（含异地分支）", "limit_tb": 30, "unit_cost": 1.0, "base_tb": 20, "over": "超过 30 TB 部分存储成本翻倍，H 显著上升", "compliance": "需有内部授权记录", "trust_pt": 40},
    {"id": "行业", "name": "行业数据源（协会/同行脱敏）", "limit_tb": 15, "unit_cost": 2.0, "base_tb": 8, "over": "超限需补签授权协议", "compliance": "需行业授权，不得超范围使用", "trust_pt": 30},
    {"id": "政府", "name": "政府公开数据", "limit_tb": 10, "unit_cost": 0.3, "base_tb": 6, "over": "超限触发合规审查", "compliance": "须遵守开放平台 robots 协议", "trust_pt": 35},
    {"id": "爬取", "name": "爬取的公开网站", "limit_tb": 8, "unit_cost": 0.5, "base_tb": 6, "over": "超限即触发合规事故，C 直接降至 0.3", "compliance": "必须有授权，超范围采集直接违规", "trust_pt": 10},
    {"id": "第三方", "name": "第三方购买", "limit_tb": 20, "unit_cost": 3.0, "base_tb": 15, "over": "超限部分需追加预算，否则交付延期一轮", "compliance": "需签订采购合同并完成脱敏", "trust_pt": 25},
    {"id": "外包", "name": "外包获取（委托采集/标注）", "limit_tb": 15, "unit_cost": 2.5, "base_tb": 6, "over": "超限需追加外包预算", "compliance": "需外包合同+确权，标注质量需验收", "trust_pt": 20},
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

# ========== v8.4 新增①：董事会三年任务书（步骤1，董事会视角落地） ==========
BOARD_TASK = {
    "title": "董事会三年任务书（本任 CEO 的 KPI）",
    "intro": "董事会发钱，也要看业绩。组阁前先领任务：这三年你带领团队要交付什么。任务书会写进审计日志，作为终局六维评分「战略一致性」的对照基准。",
    "goals": [
        {"kpi": "三年累计数据资产净值 V", "target": "≥ 300 万", "why": "V 是最终成绩单，直接计入六维评分（权重 30%）"},
        {"kpi": "合规零事故", "target": "C 系数全程不归零", "why": "C=0 当轮对外收入全额罚没；合规是底线，不是加分项"},
        {"kpi": "团队健康", "target": "能力 / 意愿 / 稳定 ≥ 65", "why": "三维状态决定 Q 上限与 D 计提敏感度，人垮了资产就垮"},
        {"kpi": "跑通对外变现", "target": "至少 1 个变现场景对外产生收入", "why": "对内降本只是保底，对外变现才是估值弹性来源"},
    ],
}

# ========== v3.1：行业 SWOT（步骤3，V3.1 方案第五节，含三域流转视角） ==========
INDUSTRY_SWOT = {
    "未来制造": {
        "S": "产线数据丰富（传感器+视觉）、制造场景明确，对内降本见效快",
        "W": "数据分散在三域（成都整机/绵阳训练场/自贡试飞）、缺统一标准、无血缘追溯",
        "O": "政策鼓励工业数据要素流通、AI 质检需求爆发、数字孪生对外服务增长",
        "T": "竞争对手抢数据、合规罚款、算法事故；只采不用触发「数据闲置税」",
    },
    "未来信息": {
        "S": "算力与算法数据高频、实时，变现渠道多（遥感/算法/算力服务）",
        "W": "C 天花板低（0.7），卫星与算力数据合规约束强；买了流量却做不出复购模型",
        "O": "6G/卫星遥感/算力服务市场大；算法能力对外授权需求爆发",
        "T": "价格战直接打掉对外收入；口碑危机打击意愿值；单一客户依赖计提 D",
    },
    "未来健康": {
        "S": "核医疗/脑机数据专业壁垒高、稀缺性强；院内质控价值确定",
        "W": "C 天花板最低（0.5），伦理审查难过；单位存储成本最高（2万/TB）",
        "O": "辅助诊断/科研数据集需求大；政策鼓励医疗数据合规流通",
        "T": "拿了数据永远过不了伦理审查；安全专项检查未整改 C 归零、收入罚没",
    },
    "未来能源": {
        "S": "制氢与能耗实时数据价值密度高；负荷预测/能耗优化对外需求稳定",
        "W": "H 基准最高（18万/轮）；商业模式强依赖政策与氢能补贴",
        "O": "碳核算数据产品（政策敏感但空间大）；绿氢产业链兴起带来新场景",
        "T": "政策一变商业模式归零；数据出境新规/标准强制升级冲击大",
    },
}

# ========== v8.4 新增③：预算 A/B/C 三方案（步骤4，方案对比 + 一键填充） ==========
BUDGET_PLANS = [
    {"id": "A", "name": "A 方案 · 稳字当头", "collect": 30, "govern": 25, "hr": 20, "comp": 25, "total": 100,
     "desc": "合规拉满、治理保底，求稳不出事；代价是对外变现弹性小", "fit": "新手 / 未来健康·未来能源等强监管行业"},
    {"id": "B", "name": "B 方案 · 攻守均衡", "collect": 35, "govern": 35, "hr": 15, "comp": 20, "total": 105,
     "desc": "采集与治理并重、兼顾合规，标准路径（参考基准）", "fit": "大多数团队首选"},
    {"id": "C", "name": "C 方案 · 进攻优先", "collect": 45, "govern": 40, "hr": 10, "comp": 10, "total": 105,
     "desc": "采集+治理拉满赌 Q 提升，合规投入少——C 有跌破风险", "fit": "对 Q 有信心、愿承担合规风险"},
]

# ========== v8.4 新增④：什么是敏感数据（步骤11，小白也能识别） ==========
SENSITIVE_DATA_EXAMPLES = [
    {"类型": "个人信息", "例子": "姓名、身份证号、手机号、住址、人脸照片", "为什么敏感": "能直接定位到具体个人，受《个人信息保护法》保护", "脱敏成本": "高"},
    {"类型": "企业经营秘密", "例子": "客户名单、采购价、成本结构、未公开财报", "为什么敏感": "泄露损害企业利益，受《反不正当竞争法》保护", "脱敏成本": "中"},
    {"类型": "财务与账户数据", "例子": "银行卡号、交易流水、发票信息", "为什么敏感": "涉及资金安全，泄露即重大事故", "脱敏成本": "高"},
    {"类型": "健康与生物信息", "例子": "病历、体检报告、指纹、基因数据", "为什么敏感": "敏感个人信息，处理需单独同意，医疗行业尤其严格", "脱敏成本": "极高"},
    {"类型": "未成年人信息", "例子": "学籍信息、未成年人位置轨迹", "为什么敏感": "受《未成年人保护法》特殊保护，处理门槛更高", "脱敏成本": "高"},
]

# ========== v8.4 新增⑤：定价方法白话解释（步骤18） ==========
PRICING_EXPLAIN = [
    {"方法": "成本法", "一句话": "按「做这份数据花了多少钱」定价：成本 + 合理利润", "例子": "采集清洗共花 50 万，加 20% 利润 → 对外卖 60 万", "优点": "简单稳当，不会亏本", "缺点": "不管买家觉得值多少，可能定低了", "引擎": "对外收入 × 0.8（保守）"},
    {"方法": "价值法", "一句话": "按「这份数据帮买家多赚了多少钱」定价：价值分成", "例子": "数据帮客户多赚 200 万 → 按 25% 分成收 50 万", "优点": "买家觉得值，价格天花板高", "缺点": "价值不好衡量，谈价周期长", "引擎": "基准（不乘系数）"},
    {"方法": "市场法", "一句话": "看市场上同类数据卖多少钱，随行就市", "例子": "同行同类数据集卖 45~55 万，你取中值 50 万", "优点": "买家容易接受、成交快", "缺点": "遇价格战直接被打折", "引擎": "对外收入 × 1.2（弹性大，风险也大）"},
]

# ========== v8.4 新增⑥：数据确权登记七步流程（步骤8） ==========
# 依据：国家数据局《数据产权登记工作指引（试行）》（申请→受理→审查→公示→异议处理→信息存证→凭证核发）
REGISTER_FLOW = [
    {"step": "① 申请", "desc": "向登记机构提交数据资源清单、来源证明与权属材料；选择登记类型（初次 / 转让 / 变更 / 续期 / 注销）"},
    {"step": "② 受理", "desc": "登记机构形式审查申请材料，材料齐全即受理并出具受理凭证"},
    {"step": "③ 审查", "desc": "核实数据权利人身份、检查数据文件与申请信息一致性、确认权属清晰"},
    {"step": "④ 公示", "desc": "在登记机构官网发布登记信息，公开征求意见，接受社会监督"},
    {"step": "⑤ 异议处理", "desc": "公示期内有利害关系人提出异议的，登记机构调查核实并作出处理"},
    {"step": "⑥ 信息存证", "desc": "登记信息与申请材料上链存证，保证可追溯、不可篡改"},
    {"step": "⑦ 凭证核发", "desc": "核发数据产权登记凭证——权属确立的法定证明，也是入表资本化的依据"},
]

# ========== v8.4 新增⑦：政策与标准依据（参考文献，估值中心与首页共用） ==========
REFERENCE_DOCS = [
    "GB/T 46353—2025《信息技术 大数据 数据资产价值评估》",
    "财政部《企业数据资源相关会计处理暂行规定》（财会〔2023〕11号）",
    "财政部《关于加强数据资产管理的指导意见》（财资〔2023〕141号）",
    "中国资产评估协会《数据资产评估指导意见》（中评协〔2023〕17号）",
    "中国信通院《数据资产管理实践白皮书（6.0版）》",
    "中共中央、国务院《关于构建数据基础制度更好发挥数据要素作用的意见》（“数据二十条”）",
    "国家数据局《数据产权登记工作指引（试行）》",
    "国家数据局等《“数据要素×”三年行动计划（2024—2026年）》",
    "《中华人民共和国个人信息保护法》《中华人民共和国数据安全法》",
]

# ========== 25 步流程定义（6 篇章，末篇 5 步含问卷调查） ==========
PHASES = [
    {"name": "投入篇", "steps": [1, 2, 3, 4], "aim": "定好团队与预算——开局底子"},
    {"name": "采集篇", "steps": [5, 6, 7, 8], "aim": "拿到数据并安全存好——原料入仓"},
    {"name": "治理篇", "steps": [9, 10, 11, 12], "aim": "清洗/脱敏/上架——提升 Q、守住 C"},
    {"name": "赋能篇", "steps": [13, 14, 15, 16], "aim": "建模并推广场景——让数据有用"},
    {"name": "变现篇", "steps": [17, 18, 19, 20], "aim": "产品化与签约——把数据卖成钱"},
    {"name": "经营与估值篇", "steps": [21, 22, 23, 24, 25], "aim": "激励团队、披露估值、问卷收尾——算总账"},
]
STEP_NAMES = {
    1: "召开董事会·组阁", 2: "盘点家底", 3: "制定三年战略", 4: "编制预算",
    5: "选择数据源", 6: "签订数据合同", 7: "接入存储与可信溯源", 8: "确权登记",
    9: "定标准", 10: "质检标注与质量稽核", 11: "安全分级与脱敏", 12: "资产目录上架与可信度评估",
    13: "赋能方案三选一", 14: "建模与验证", 15: "上线与推广", 16: "效果度量",
    17: "产品化与数据变现", 18: "定价", 19: "签署数据交易合同", 20: "交付与运维",
    21: "团队激励投放", 22: "出表与披露", 23: "第三方估值", 24: "董事会答辩",
    25: "问卷调查",
}
# 默认投放事件卡（自动触发下跌）
DEFAULT_EVENTS = {2: ["P-04", "C-01", "W-02"], 3: ["W-04", "T-03"]}

# ========== 会话状态初始化 ==========
def init_state():
    defaults = {
        "budget": INIT_BUDGET, "started": False, "industry": "未来制造", "role": "数据运营总监",
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
        "gold_ai": {},                                # v3.1 金点子AI判定 {轮次: {score,verdict,advice,tags}}
        "gold_votes": {},                             # v3.1 金点子方案罗列·班级投票 {轮次: {方案: 票数}}
        "gold_voter_used": {},                        # v3.1 每人已投票数 {轮次: n}
        "gold_top1": {},                              # v3.1 票选Top1 {轮次: 方案}
        "action_plan": {},                            # 步骤2文档修复：AI 按步操作建议简版 {轮次: [str]}
        "mask_quiz_ok": {},                           # 脱敏小课堂测验 {轮次: bool}
        "audit_trail": {},                            # S7 审计留痕勾选 {轮次: bool}
        # v8.4 新增字段
        "custom_incentives": {},                      # 自定义激励方案 {轮次: {name, type, cost, ...}}
        # v25 新增字段
        "survey": {},                                 # 第25步问卷调查 {轮次: {q1,q2,q3,q4,q5}}
        "student": None,                              # 实名注册 {班级, 学号, 姓名}
        "klass": "",                                  # 班级编号登录（进入主界面前必填）
        "teacher_authed": False,                      # 教师端口令门控
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ========== 公共工具函数 ==========

# ===== 教师端数据层（对照「金税四期·教师端代码说明」补齐：students/logs/assessments CSV） =====
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
_io_lock = threading.Lock()
TEACHER_PASS = "tax2026"  # 教师端默认口令，正式比赛/演示前请修改并重新部署


def _read_csv(name):
    """读取 data/ 下 CSV；不存在返回 []；空单元格不再变 NaN（修复导出崩溃的关键）"""
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path):
        return []
    with _io_lock:
        try:
            return pd.read_csv(path, dtype=str, keep_default_na=False).to_dict("records")
        except Exception:
            return []


def _append_csv(name, row, cols):
    """追加一行到 data/ 下 CSV（首次自动建表头，线程锁防并发写坏）"""
    path = os.path.join(DATA_DIR, name)
    with _io_lock:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            fresh = not os.path.exists(path)
            with open(path, "a", encoding="utf-8-sig", newline="") as f:
                w = csv.writer(f)
                if fresh:
                    w.writerow(cols)
                w.writerow(row)
        except Exception:
            pass


def _esc(s):
    """HTML 转义，防止学生输入破坏表格"""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _reg_name(klass, sid):
    for r in _read_csv("students.csv"):
        if str(r.get("班级", "")).strip() == str(klass).strip() and str(r.get("学号", "")).strip() == str(sid).strip():
            return str(r.get("姓名", ""))
    return "未注册"


def _reg_time(klass, sid):
    for r in _read_csv("students.csv"):
        if str(r.get("班级", "")).strip() == str(klass).strip() and str(r.get("学号", "")).strip() == str(sid).strip():
            return str(r.get("注册时间", ""))
    return ""


def save_student(klass, sid, name):
    """实名注册落库；同班同学号返回 False（防顶替）"""
    for r in _read_csv("students.csv"):
        if str(r.get("班级", "")).strip() == str(klass).strip() and str(r.get("学号", "")).strip() == str(sid).strip():
            return False
    _append_csv("students.csv", [klass, sid, name, _time.strftime("%Y-%m-%d %H:%M:%S")],
                ["班级", "学号", "姓名", "注册时间"])
    append_log("注册", f"班级 {klass} · 学号 {sid} · 姓名 {name}")
    return True


def append_log(action, detail, step=None, v=None, total=None, outcome=None):
    """操作留痕：注册/开始实验/每步完成/撤销/结算/问卷提交均写入 data/logs.csv"""
    s = st.session_state
    try:
        stu = s.get("student", {})
        sid = str(stu.get("学号", ""))
        name = str(stu.get("姓名", ""))
        klass = str(stu.get("班级", ""))
    except Exception:
        sid = name = klass = ""
    _append_csv("logs.csv", [
        _time.strftime("%Y-%m-%d %H:%M:%S"), str(klass), str(sid), str(name),
        str(action), str(detail),
        "" if step is None else str(step),
        "" if v is None else str(v),
        "" if total is None else str(total),
        "" if outcome is None else str(outcome),
    ], ["时间", "班级", "学号", "姓名", "操作", "详情", "步骤", "估值V", "六维总分", "定性"])


def aggregate_student(klass, sid):
    """从日志聚合单个学生的成绩档案（完成步数 / 最新估值V / 六维总分 / 问卷激励均分 / 定性）"""
    rows = [r for r in _read_csv("logs.csv")
            if str(r.get("班级", "")).strip() == str(klass).strip()
            and str(r.get("学号", "")).strip() == str(sid).strip()]
    steps, v_latest, total_latest, outcome, last = set(), None, None, "", ""
    q3_vals = []
    for r in rows:
        if str(r.get("步骤", "")).strip().isdigit():
            steps.add(int(str(r["步骤"]).strip()))
        if str(r.get("时间", "")).strip():
            last = str(r["时间"])
        if str(r.get("操作", "")).strip() == "结算估值":
            raw = str(r.get("估值V", "")).strip()
            if raw and raw.lower() not in ("nan", "none"):
                try:
                    v_latest = float(raw)
                except ValueError:
                    pass
            outcome = "已结算"
        if str(r.get("操作", "")).strip() == "六维评分" and str(r.get("六维总分", "")).strip():
            try:
                total_latest = float(str(r["六维总分"]).strip())
            except ValueError:
                pass
        if str(r.get("操作", "")).strip() == "问卷调查":
            det = str(r.get("详情", ""))
            m = re.search(r"Q3激励=(\d)", det)
            if m:
                try:
                    q3_vals.append(float(m.group(1)))
                except ValueError:
                    pass
    q3_avg = round(sum(q3_vals) / len(q3_vals), 1) if q3_vals else None
    return {
        "班级": klass, "学号": sid, "姓名": _reg_name(klass, sid),
        "注册时间": _reg_time(klass, sid), "完成步数": len(steps),
        "最新估值V": v_latest, "六维总分": total_latest,
        "问卷激励均分": q3_avg, "定性": outcome or "未结算", "最后活动": last,
    }


def export_scores_df(klass=None):
    """教师端成绩表：每个学生一行（按班级过滤可选；实时聚合自操作日志）"""
    stus = _read_csv("students.csv")
    recs = []
    for r in stus:
        k, sid = str(r.get("班级", "")).strip(), str(r.get("学号", "")).strip()
        if klass and klass != "全部班级" and k != klass:
            continue
        recs.append(aggregate_student(k, sid))
    df = pd.DataFrame(recs, columns=["班级", "学号", "姓名", "注册时间", "完成步数",
                                     "最新估值V", "六维总分", "问卷激励均分", "定性", "最后活动"])
    return df.sort_values(["班级", "学号"]).reset_index(drop=True)


def save_assessment(klass, sid, comment):
    """教师评估保存到 data/assessments.csv（同学生覆盖更新）"""
    rows = _read_csv("assessments.csv")
    now = _time.strftime("%Y-%m-%d %H:%M:%S")
    for i, r in enumerate(rows):
        if str(r.get("班级", "")).strip() == str(klass).strip() and str(r.get("学号", "")).strip() == str(sid).strip():
            rows[i]["评语"] = comment
            rows[i]["评估时间"] = now
            break
    else:
        rows.append({"班级": klass, "学号": sid, "评语": comment, "评估时间": now})
    path = os.path.join(DATA_DIR, "assessments.csv")
    with _io_lock:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8-sig")
        except Exception:
            pass


def html_table(df, max_rows=60):
    """成绩表格 HTML 渲染（替代 st.dataframe，避免 pyarrow 依赖）"""
    if df is None or len(df) == 0:
        return "<div style='color:#64748b;font-size:13px;padding:8px'>暂无数据</div>"
    cols = list(df.columns)
    head = "".join(f"<th style='border:1px solid #e2e8f0;padding:6px 10px;background:#f1f5f9;"
                   f"color:#2563eb;font-size:12px;text-align:left'>{_esc(c)}</th>" for c in cols)
    body = ""
    for i, (_, r) in enumerate(df.head(max_rows).iterrows()):
        bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
        tds = ""
        for c in cols:
            v = r[c]
            txt = "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v)
            tds += f"<td style='border:1px solid #e2e8f0;padding:6px 10px;color:#334155;font-size:12px'>{_esc(txt)}</td>"
        body += f"<tr style='background:{bg}'>{tds}</tr>"
    more = (f"<div style='color:#64748b;font-size:12px;padding:6px 2px'>"
            f"仅显示前 {max_rows} 行，共 {len(df)} 行——导出 CSV 可查看全部</div>" if len(df) > max_rows else "")
    return (f"<div style='overflow-x:auto;border:1px solid #e2e8f0;border-radius:8px;background:#ffffff'>"
            f"<table style='border-collapse:collapse;width:100%'><thead><tr>{head}</tr></thead>"
            f"<tbody>{body}</tbody></table>{more}</div>")


# ===== 教师端数据层结束 =====
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
    append_log("完成步骤", name, step=step)

def undo_last():
    """撤销最近一步已完成的操作"""
    if not st.session_state.undo_stack:
        st.warning("没有可撤销的步骤")
        return
    stp = st.session_state.undo_stack.pop()
    st.session_state.done.discard(stp)
    record(f"步骤{stp}·撤销", "回退")
    append_log("撤销", f"步骤{stp}回退", step=stp)
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
    # v8.4：脱敏强化投入（≥3万 → C 上限 +0.05，更抗安全专项检查）
    if d.get("mask_extra", 0) >= 3 and d.get("mask") != "未脱敏":
        c = min(c + 0.05, 1.0)
    # 爬取数据源埋雷（v9.1：支持多选数据源，任一选中"爬取"即触发）
    sources = d.get("sources") or [d.get("source", "内部")]
    if "爬取" in sources: c = min(c, 0.5)
    # v2.0 新增⑥：爬取超限 → 合规事故，C 直接 0.3
    if d.get("source_over_limit") and "爬取" in sources:
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
    # v3.1：数据变现·对外成交价（滑块定价：50万基准→系数1.0，封顶×1.5）
    price = d.get("product_price", 0)
    if price and cash_out > 0:
        cash_out *= min(0.5 + price / 100.0, 1.5)
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
    # v9.1：多选数据源时，渠道成本已含在步骤5单价中，不再叠加引擎越限惩罚（避免重复计费）；仅单选保留
    over_tb = max(raw_tb - src_cfg["limit_tb"], 0)
    over_cost = 0.0
    if len(d.get("sources") or [src]) == 1 and over_tb > 0:
        if src == "内部":
            over_cost = over_tb * unit * 2
        elif src == "第三方":
            over_cost = over_tb * 3.0  # 每超 1TB 追加 3 万采购预算
    extra_tb = max(source_tb - ind["base_tb"], 0)
    # 团队年薪（v2.0 新增①：年薪直接计入当轮 H）
    salary = d.get("team_salary", 0.0)
    # v8.4：辅助渠道成本（步骤5 多渠道数据源）追加计入 H
    channel_cost = d.get("channel_cost", 0.0)
    # 事件卡
    for e in events:
        cfg = EVENT_CARDS[e]
        if "h_mult" in cfg: h_base *= cfg["h_mult"]
        if "unit_mult" in cfg: unit *= cfg["unit_mult"]
        if "h_base_mult" in cfg: h_base *= cfg["h_base_mult"]
        if "h_extra" in cfg: h_base += cfg["h_extra"]
        if "tb_mult" in cfg: extra_tb *= cfg["tb_mult"]
    h = h_base + extra_tb * unit + over_cost + salary + channel_cost
    return round(h, 1), {"h_base": round(h_base, 1), "extra_tb": round(extra_tb, 1), "unit": round(unit, 2), "over_cost": round(over_cost, 1), "salary": round(salary, 1), "channel_cost": round(channel_cost, 1)}

def calc_t(decisions):
    """v2.0 新增⑨：数据可信度 T = 来源合法清晰40 + 责任人签字30 + 可追溯审计30；T<50 对外变现收入打 5 折
    v9.1：支持多选数据源——来源得分取「选中源中最不合法」的得分（木桶效应：一个脏渠道拉低整体信任）"""
    d = decisions
    pts = 0
    detail = {}
    # ① 来源合法清晰（40）：内部 40 / 第三方购买 25 / 爬取 10；多选时取最低
    sources = d.get("sources") or [d.get("source", "内部")]
    src_cfgs = [next((s for s in SOURCE_TYPES if s["id"] == x), SOURCE_TYPES[0]) for x in sources]
    src_pt = min(c["trust_pt"] for c in src_cfgs) if src_cfgs else 40
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

    # 采集量（TB）：v2.0 来源类型 + 用户输入（越限判定用放大前 raw_tb）；v8.4 + 辅助渠道采集量
    src = d.get("source", "内部")
    src_cfg = next((s for s in SOURCE_TYPES if s["id"] == src), SOURCE_TYPES[0])
    raw_tb = d.get("source_tb", src_cfg["limit_tb"])
    source_tb = raw_tb * (1.2 if d.get("storage") == "数据湖" else 1.0)
    collected_tb = raw_tb + d.get("channel_tb", 0)

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
    # v3.1：金点子方案罗列·班级投票 Top1 → 本轮估值 V+3%（直接落地）
    top1 = st.session_state.gold_top1.get(r)
    if top1 and st.session_state.gold_votes.get(r, {}).get(top1, 0) > 0:
        v = round(v * 1.03, 1)
        top1_note = f"（含票选Top1方案落地 V+3%）"
    else:
        top1_note = ""

    val = {
        "round": r, "pv": round(pv, 1), "cash_in": round(cash_in, 1), "cash_out": round(cash_out, 1),
        "q": q, "c": c, "h": h, "d": d_val, "d_pct": d_pct, "v": v, "t": r,
        "events": events, "drop_paths": drop_labels, "q_detail": q_detail,
        # v2.0 新增字段：可信度 T / 团队状态 / 赋能方案
        "t_score": t, "t_detail": t_detail,
        "team": dict(st.session_state.team),
        "empower": d.get("empower_plan"),
        # v9.1：本轮关键操作摘要（供三轮前后对比 + AI 建议）
        "ops": {
            "战略": d.get("strategy", "未定"),
            "数据源": "+".join(d.get("sources") or [d.get("source", "内部")]),
            "采集量TB": d.get("source_tb", 0),
            "累计投入万": round((INIT_BUDGET - st.session_state.budget) / 10000, 1),
            "脱敏": d.get("mask", "未做"),
            "赋能": d.get("empower_plan", "未选"),
            "定价": d.get("pricing", "未定"),
            "确权": "✅" if d.get("register") else "❌",
            "激励方案": "、".join(d.get("incentives", [])) if d.get("incentives") else ("自定义:" + str(d.get("custom_incentives", {}).get("name", "")) if d.get("custom_incentives", {}).get("name") else "无"),
        },
        "top1_note": top1_note,
    }
    st.session_state.val_history.append(val)
    record(f"第{r}轮·估值计算", f"V={v}万")
    append_log("结算估值", f"第{r}轮 V={v}万", step=23, v=v, outcome="已结算")
    # v2026-10-20：结算后生成「下一轮按步操作建议」→ 写入侧边栏「下一轮待办」
    prev_v = st.session_state.val_history[-2] if len(st.session_state.val_history) >= 2 else None
    st.session_state.action_plan[r] = gen_action_plan(st.session_state.decisions, st.session_state.industry, val, prev_v)

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
        st.markdown(f"**④ 持有成本 H** = H_基准({h_detail['h_base']}万) + 采集量增量({h_detail['extra_tb']}TB) × 单位存储成本({h_detail['unit']}万/TB)" + (f" + 辅助渠道({h_detail.get('channel_cost', 0)}万)" if h_detail.get("channel_cost", 0) > 0 else "") + f" = **{h}万**")
        st.markdown(f"**⑤ 减值准备 D** = min({d_pct:.0%}, 30%) × 计提基数({v_before_d}万) = **{d_val}万**")
        st.markdown(f"**⑥ V** = {pv} × {q} × {c} − {h} − {d_val} = **{v}万**")
        st.success(f"### 本轮数据资产净值 V = {v}万")
        if drop_hits:
            st.warning("**⚠️ 命中下跌路径：**" + "；".join(f"{x['label']}（{x['note']}）" for x in drop_hits))
        if events:
            st.info("**本轮事件卡：**" + "；".join(f"{e}·{EVENT_CARDS[e]['name']}" for e in events))
    return val

def gen_ai_tips(d, ind_key, val):
    """v9.1：AI 估值提升建议——基于本轮决策短板自动生成下一轮行动清单（规则引擎，不依赖外部 API）"""
    ind = INDUSTRIES[ind_key]
    tips = []
    # 质量 Q
    if val["q"] < 0.85:
        tips.append(("📊 质量系数 Q 偏低（{:.2f}）".format(val["q"]), "下一轮加大「治理篇」预算（数据标准/质检/元数据），Q 每提升 0.1，V 直接放大约 10%。"))
    # 合规 C
    if val["c"] < ind["c_cap"]:
        tips.append(("⚖️ 合规系数 C 未到行业天花板（{:.2f}/{:.2f}）".format(val["c"], ind["c_cap"]), "补齐三板斧：合同完整授权 + 全量脱敏 + 确权登记；C 每提升 0.1，V 放大约 10%。"))
    # 可信度 T
    if val.get("t_score", 0) < 50:
        tips.append(("🔐 可信度 T={}（<50，对外收入打 5 折）".format(val.get("t_score", 0)), "优先补三块：①完成确权登记（+30）②开启审计留痕（+30）③数据源换内部/第三方（来源分更高）。T 到 50 后对外收入立即不再打折。"))
    # 数据源
    sources = d.get("sources") or [d.get("source", "内部")]
    if "爬取" in sources:
        tips.append(("🕸️ 数据源含「爬取」渠道", "爬取会把整体 C 和 T 拉低（木桶效应）。若爬取没带来超额收益，下轮换内部/第三方；如必须用，采集量务必压在限值内。"))
    if d.get("source_over_limit"):
        tips.append(("🚨 爬取渠道超限", "已触发合规事故 C=0.3、对外收入罚没。下轮采集量滑块必须控制在爬取限值 8TB 以内。"))
    # 脱敏
    if d.get("mask") == "未脱敏":
        tips.append(("🛡️ 本轮未脱敏", "C=0.3 且对外收入全额罚没风险。下轮必须做全量脱敏（15 万）——这是对外变现的入场券。"))
    elif d.get("mask") == "部分脱敏":
        tips.append(("🛡️ 本轮仅部分脱敏", "C 上限被压在 0.8。下轮升级全量脱敏 + 强化投入 ≥3 万（C 上限 +0.05）。"))
    # 确权登记
    if not d.get("register"):
        tips.append(("📋 未完成确权登记", "确权后：T+30、入表可选无形资产（评分更高）、对外谈判加分。步骤 8 是高分必做项。"))
    # 审计留痕
    if not d.get("audit_trail"):
        tips.append(("🧾 未开启审计留痕", "步骤 7 勾选「血缘 + 审计留痕」，T 直接 +30，是目前性价比最高的 30 分。"))
    # 持有成本 H
    if val["h"] > 100:
        tips.append(("💾 持有成本 H={}万偏高".format(val["h"]), "压缩采集量（数据不是越多越好）、选湖仓一体存储（H 基准 -20%）、精简非必要角色/渠道；H 每降 10 万，V 直接 +10 万。"))
    # 减值 D
    if val["d"] > 0:
        tips.append(("📉 本轮减值 D={}万（{:.0%}）".format(val["d"], val["d_pct"]), "对照下跌路径提示：避免单一客户依赖（买家分散）、盯紧事件卡预警，及时调整战略方向。"))
    # 对外变现
    if val["cash_out"] > 0 and val.get("t_score", 0) >= 50:
        tips.append(("💰 对外变现已跑通", "T≥50 后对外收入不再打折。下轮可加大对外场景并用市场法定价（×1.2），同时保持买家分散避免依赖。"))
    elif val["cash_out"] <= 0:
        tips.append(("🚀 本轮没有对外收入", "尝试选「对外」型场景（数字孪生/精准营销/辅助诊断等），配合全量脱敏+确权+审计，开启对外变现第二曲线。"))
    # 建模投入
    if d.get("model", 0) < 10:
        tips.append(("🧮 建模投入不足（{:.0f}万）".format(d.get("model", 0) / 10000), "步骤 14 建模每投 10 万 → 场景现金流 +30%，是目前性价比较高的放大手段。"))
    # 定价
    if d.get("pricing") == "成本法" and val["cash_out"] > 0:
        tips.append(("🏷️ 定价用了成本法（×0.8）", "若数据质量 Q 高、买家竞争激烈，可改市场法（×1.2）或价值法（基准），同一份数据卖出更高价。"))
    # 兜底
    if not tips:
        tips.append(("🏆 本轮决策扎实", "保持节奏：守住全量脱敏、确权、审计留痕三条底线，把资金投向当前 Q/C/T 中最低的一项，估值会稳步上涨。"))
    return tips


# ========== v3.1 新增：AI 运营辅导（估值报告·3 条针对性建议，V3.1 方案第十九项） ==========
def ai_coach(d, ind_key, val, prev=None):
    """按 V3.1 触发条件表（优先级排序）生成至多 3 条主建议——先合规、再信任、后成本/质量/变现。"""
    ind = INDUSTRIES[ind_key]
    rules = []
    c, q, t = val.get("c", 0), val.get("q", 0), val.get("t_score", 0)
    h, dv = val.get("h", 0), val.get("d", 0)
    cash_out = val.get("cash_out", 0)
    # 1. 合规 C 短板（最高优先级：C 是 V 的乘数）
    if c < ind["c_cap"]:
        rules.append(("⚖️ 合规补课（C={:.2f}<天花板{:.2f}）".format(c, ind["c_cap"]), "V=现金流×Q×C，C 每提 0.1，V 放大 10%。下轮优先：合同完整授权 + 全量脱敏 + 确权登记，把 C 顶到行业天花板。"))
    # 2. 可信度 T 短板（买家信任）
    if t < 50:
        rules.append(("🔐 可信度提升（T={}<50，对外收入打5折）".format(t), "做全可信溯源四步闭环（血缘/审计/回滚/授权）+ 确权登记，T 过 50 后对外收入立即不再打折。"))
    # 3. 持有成本 H 占比超 30%（V3.1：H 占预算>30% 精简团队）
    gross = cash_out + val.get("cash_in", 0)
    if gross > 0 and h > 0.3 * gross:
        rules.append(("💾 持有成本偏高（H={}万，占毛现金流{:.0%}）".format(h, h / gross), "压缩采集量、换湖仓一体（H 基准-20%）、精简非必要角色/渠道——H 每降 10 万，V 直接 +10 万。"))
    # 4. 质量 Q 短板
    if q < 0.8:
        rules.append(("📊 质量补课（Q={:.2f}）".format(q), "加大数据标准/质检标注投入（自研+深度稽核），Q 每提 0.1，V 放大约 10%。"))
    # 5. 减值 D（风险）
    if dv > 0:
        rules.append(("📉 减值风险（D={}万）".format(dv), "对照下跌路径：买家分散避免单一依赖、盯紧事件卡预警并及时调整战略。"))
    # 6. 变现（无对外收入 / 有收入但可放大）
    if cash_out <= 0:
        rules.append(("🚀 变现缺口（本轮无对外收入）", "选「对外」型场景（数字孪生/遥感/辅助诊断等）+ 全量脱敏 + 确权 + 溯源，并在步骤 17 提高成交价，打开变现第二曲线。"))
    elif t >= 50:
        rules.append(("💰 变现放大（对外收入{}万）".format(round(cash_out, 1)), "T≥50 收入不打折：提高产品成交价（市场基准 50 万 → 系数×1.0，封顶×1.5）并保持买家分散。"))
    # 7. 兜底：V 正且 C 已到顶
    if not rules:
        rules.append(("🏆 本轮估值稳健", "合规、信任、质量都在线：下一轮把资金投向 Q/C/T 最低的一项并做产品化变现，估值会继续上行。"))
    return rules[:3]


# ========== v2026-10-20：按步骤操作建议（学生执行难度最低）+ 本轮操作复盘 ==========
def gen_action_plan(d, ind_key, val, prev=None):
    """生成「下一轮按步骤操作清单」——每条都带步骤号，学生照着做就行（简版进侧边栏）"""
    ind = INDUSTRIES[ind_key]
    plan = []
    sources = d.get("sources") or [d.get("source", "内部")]
    # 步骤5：数据源
    if "爬取" in sources and val.get("c", 1.0) < ind["c_cap"]:
        plan.append("步骤5：别勾「爬取」数据源（它会把 C 和 T 拉低）；确需用就压到限值 8TB 内")
    elif not sources or (not d.get("source_tb")):
        plan.append("步骤5：多勾几个数据源（内部+第三方），采集量按预算 20~30TB 取")
    # 步骤6：合同（步骤19 落库值为「完整授权」）
    if not d.get("contract") or d.get("contract") != "完整授权":
        plan.append("步骤6：合同选「完整授权」（C 不打折，签在步骤 19）")
    # 步骤7：可信溯源
    if not d.get("audit_trail"):
        plan.append("步骤7：可信溯源四步全勾（血缘/审计/回滚/授权），可信度 T +30")
    # 步骤8：确权
    if not d.get("register"):
        plan.append("步骤8：完成确权登记（T+30，且入表可选无形资产）")
    # 步骤10：质检标注
    if d.get("qa_mode") == "公开招标":
        plan.append("步骤10：标注模式改「自研团队」或「AI预标注」（招标会触发返工扣款 10 万）")
    if d.get("qc", 0) < 12:
        plan.append("步骤10：稽核投入上「深度稽核」（准确性+0.15，Q 提升最明显）")
    # 步骤11：脱敏（落库值为「全量脱敏/部分脱敏/未脱敏」）
    if d.get("mask") != "全量脱敏":
        plan.append("步骤11：全量脱敏 15 万（不脱敏 C=0.3，对外收入全罚没）")
    # 步骤12：目录上架
    if not d.get("catalog"):
        plan.append("步骤12：资产目录上架（Q 完整性提升，5 万）")
    # 步骤13：赋能
    if not d.get("empower_plan"):
        plan.append("步骤13：选一个赋能方案（A/B/C，Q 加成 +0.03~+0.10）")
    # 步骤14：建模（落库值为元）
    if d.get("model", 0) < 100000:
        plan.append("步骤14：建模投入提到 10 万以上（现金流放大）")
    # 步骤17：定价
    cur_q, _ = calc_q(ind_key, d)
    if val.get("cash_out", 0) > 0:
        if cur_q >= 0.8:
            plan.append("步骤17：成交价定 80~120 万（Q 高吃得下高价，吃满 ×1.5）")
        elif cur_q >= 0.6:
            plan.append("步骤17：成交价定 50~80 万（Q 中等，按市场基准小幅加价）")
        else:
            plan.append("步骤17：成交价定 30~50 万（Q 弱先跑量，别定太高）")
    # 步骤18：定价方法
    if d.get("pricing") == "成本法" and val.get("cash_out", 0) > 0:
        plan.append("步骤18：定价改「市场法」（对外收入 ×1.2）")
    # 步骤19：买家
    if "单一独家大客户" in (d.get("buyer_choice", "")):
        plan.append("步骤19：买家结构改「多个分散买家」（去掉 D 20% 的依赖风险）")
    # 步骤21：激励
    if not d.get("incentives") and not d.get("custom_incentives", {}).get("name"):
        plan.append("步骤21：投一个激励（对照成员画像：小张→培训、小李→关怀福利）")
    # 步骤22：入表
    if d.get("listing") == "存货" and d.get("register"):
        plan.append("步骤22：入表方式改「无形资产」（已确权，评分更高）")
    if not plan:
        plan.append("保持本轮节奏：守住脱敏/确权/溯源底线，把资金投给当前 Q/C/T 最低的一项。")
    return plan[:8]


def gen_round_review(d, val):
    """本轮操作复盘：做得好 / 做得不好（基于审计字段自动判定）"""
    goods, bads = [], []
    if d.get("register"): goods.append("确权登记 ✅（步骤8）")
    else: bads.append("未确权登记（步骤8）→ T-30、入表只能走存货")
    if d.get("mask") == "全量脱敏": goods.append("全量脱敏 ✅（步骤11）")
    elif d.get("mask") == "部分脱敏": bads.append("仅部分脱敏（步骤11）→ C 被压在 0.8 以下")
    else: bads.append("未脱敏（步骤11）→ C=0.3、对外收入有罚没风险")
    if d.get("audit_trail"): goods.append("可信溯源四步闭环 ✅（步骤7，T+30）")
    else: bads.append("未做可信溯源四步（步骤7）→ 缺「可追溯审计」30 分")
    if d.get("contract") == "完整授权": goods.append("合同完整授权 ✅（步骤19）")
    elif d.get("contract"): bads.append("合同授权不完整（步骤6）→ C 被压低")
    if d.get("qa_mode") == "公开招标": bads.append("标注选公开招标（步骤10）→ 触发返工扣款 10 万")
    if val.get("c", 0) >= 0.8: goods.append(f"合规 C={val['c']} ≥ 0.8 ✅")
    else: bads.append(f"合规 C={val['c']} 偏低 → 对外收入按 C 打折")
    if val.get("q", 0) >= 0.8: goods.append(f"质量 Q={val['q']} ≥ 0.8 ✅")
    elif val.get("q", 0) >= 0.6: goods.append(f"质量 Q={val['q']} 中等")
    else: bads.append(f"质量 Q={val['q']} 偏弱 → 补标准/质检")
    if val.get("cash_out", 0) <= 0: bads.append("本轮没有对外收入 → 变现没跑起来")
    else: goods.append(f"对外变现已启动（收入 {val['cash_out']} 万）")
    if not goods: goods.append("本轮操作偏少，先按「下一步后果预告」把关键步骤补齐")
    if not bads: bads.append("没有明显失误，继续保持")
    return goods, bads

# ========== 侧边栏 ==========
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🎯 数据资产运营总监")
        st.markdown(f"**班级**：{st.session_state.get('klass', '—')}")
        if st.session_state.started:
            ind = INDUSTRIES[st.session_state.industry]
            st.markdown(f"**行业**：{st.session_state.industry}·{ind['name']}")
            st.markdown(f"**角色**：{st.session_state.role} ｜ **轮次**：第 {st.session_state.round} 轮")
            st.markdown(f"**三年战略**：{st.session_state.decisions.get('strategy', '未定')}")
            st.divider()
            st.markdown("### 💰 财务仪表盘")
            used = INIT_BUDGET - st.session_state.budget
            # v3.2.1 修复：侧边栏两列 metric 过窄导致数值被省略号截断（350万→35...），改单列直排全宽显示
            st.metric("剩余预算", fmt(st.session_state.budget), delta=f"已用{fmt(used)}")
            st.metric("累计收入", fmt(st.session_state.revenue))
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
                7: "存储方案：湖仓一体 H 基准-20%；可信溯源四步全做 → 可信度 T +30",
                11: "脱敏：全量 15万→C 保持；不脱敏→C=0.3 且对外收入罚没；需先过小测验",
                13: "赋能方案：A/B/C 三选一，立即开支 20/45/80 万，Q 加成 +0.03/+0.06/+0.10",
                19: "签合同：2/3/7 条填错会被阻止；单一独家大客户→D 20%",
                21: "激励：预算=现金×15%（上限50万），不能全选；纯金钱下轮意愿反噬",
                23: "估值结算：V = Σ现金流×Q×C−H−D，本轮收益/损失当场见分晓",
            }
            st.info(preview_map.get(st.session_state.step, "完成本步后继续推进 25 步流程；每步决策都真实扣款/生效，写审计日志、可撤销。"))
            st.divider()
            st.markdown("### ⚖️ 估值引擎拆解（每个字母都能看懂）")
            st.markdown("""
- **① 现金流折现**：Σ(现金流÷1.1ᵗ)——每个场景未来能赚的钱，折算回今天
- **× Q 质量系数**：数据干不干净（完整×一致×时效×准确）
- **× C 合规系数**：合不合规（违规可归零、罚没对外收入）
- **− H 持有成本**：存数据要花钱（存储+算力，每轮独立）
- **− D 减值准备**：风险事件计提（最多扣 30%）
- **= V 资产净值**：正=赚，负=亏
""")
            st.caption("记忆口诀：先看能赚多少（①），再看数据好不好（②③打折），最后扣掉养数据的钱（④）和踩坑的损失（⑤）。")
            st.divider()
            st.markdown("### 🗺️ 流程进度（点击任意格子跳转，右侧内容同步切换）")
            total_done = len([s for s in st.session_state.done if s <= 25])
            st.progress(total_done / 25, text=f"步骤 {total_done}/25")
            for ph in PHASES:
                cols = st.columns(len(ph["steps"]))
                for ci, s in enumerate(ph["steps"]):
                    done = s in st.session_state.done
                    with cols[ci]:
                        if st.button(("✅" if done else "") + str(s), key=f"nav_{s}", help=f"步骤{s}：{STEP_NAMES[s]}" + ("（已完成，点击可回看）" if done else ""), type="primary" if done else "secondary"):
                            st.session_state.step = s
                            st.rerun()
                st.caption(f"{ph['name']}：步骤 {ph['steps'][0]}-{ph['steps'][-1]}")
            st.divider()
            st.markdown("### 📋 下一轮待办（AI 简版，第 23 步结算后生成）")
            plan = st.session_state.action_plan.get(st.session_state.round, [])
            if plan:
                for item in plan:
                    st.markdown(f"- {item}")
            else:
                st.caption("完成本轮「步骤 23 第三方估值」结算后，这里会自动列出下一轮按步骤操作清单。")
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
    <p style="margin:6px 0 0;font-size:16px;color:#E3F2FD">基于九层能力框架的数据资产化与合规治理虚拟仿真实验 · 8学时（课前1+课中6+课后1）</p>
    </div>
    """)
    st.markdown("")

    # 实验地图：6篇章25步流程条
    st.markdown("### 🗺️ 实验地图：25 步决策全流程（从上到下依次完成）")
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
    # v2026-10-20：估值引擎拆解已移至左侧侧边栏（点击查看），首页保留实验地图与三轮节奏
    st.markdown("💡 **估值引擎怎么算？** 左侧侧边栏「⚖️ 估值引擎拆解」每个字母都有人话解释，随时可查。")

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

    # ===== v8.4 新增：实验介绍（对标国家级虚拟仿真实验申报格式） =====
    st.divider()
    st.markdown("### 📖 实验介绍（教学目标 · 原理 · 过程与方法）")
    with st.expander("🎯 实验教学目标（学完能干什么）", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**知识目标**")
            st.markdown("""
            - 理解数据资产「投入—采集—治理—赋能—变现—估值」全生命周期管理框架与**九层能力框架**
            - 掌握数据资产价值评估模型 V = Σ(现金流/1.1ᵗ) × Q × C − H − D 及其每个系数的含义
            - 熟悉数据确权登记、脱敏合规、**可信溯源四步闭环**、入表计量（无形资产/存货）等制度要求
            """)
        with c2:
            st.markdown("**能力目标**")
            st.markdown("""
            - 能在预算约束下做出团队组建、数据源选择、治理投入与变现定价的组合决策
            - 能通过审计日志与估值明细复盘决策因果，识别「质量塌陷/合规事故/数据闲置税」等下跌路径
            - 能编制数据交易合同、完成确权登记、可信溯源与资产入表披露的关键动作
            """)
        with c3:
            st.markdown("**素养目标**")
            st.markdown("""
            - 树立「数据是资产、合规是底线」的经营意识
            - 理解数据治理不仅是治理数据，更是治理「用数据的人」——激励、责任与信任
            - 培养面向真实企业的数据资产管理职业胜任力与批判性思维
            """)
    with st.expander("⚙️ 实验原理（核心要素仿真设计）", expanded=False):
        st.markdown("本实验以**数据资产价值评估公式**为主线，把企业数据资产管理拆成 6 个篇章 25 步决策（含收尾问卷调查），每步决策真实扣款/生效并写入审计日志。实验覆盖 **12 个核心知识点**（数据资产化、确权登记、可信溯源、脱敏合规、价值评估、入表披露、团队激励、风险防控、数据交易、跨域治理、AI 辅助决策、复盘迭代）。")
        st.markdown("**核心仿真要素：**")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            - **行业仿真**：未来能源/未来信息/未来制造/未来健康 4 行业（蜀字虚拟企业 + **成都—德阳—绵阳三域流转**），各有 Q 初始、C 天花板、H 基准、单位存储成本与典型陷阱
            - **数据仿真**：结构化/非结构化 5 类数据类型、**六渠道采集**（内部/行业/政府/爬取/购买/外包）与限值、质检标注三模式
            - **风险仿真**：20 张事件卡（P-政策/W-价格战/C-客户流失/T-技术替代）+ 五条下跌路径自动触发
            """)
        with c2:
            st.markdown("""
            - **组织仿真**：董事会组阁 8 角色（年薪计入 H）、团队能力/意愿/稳定三维状态、5 类激励工具 + **成员画像**与隐藏规则
            - **估值仿真**：三轮滚动估值（第一轮普遍上涨 → 第二轮事件卡回调 → 第三轮分化），估值报告双栏 + **AI 运营辅导**
            - **制度仿真**：确权登记七步流程、合同合规校验、数据资产入表（无形资产/存货）、**可信度 T 三维评估**与六维评分
            """)
        st.info("**公式红线**：估值引擎对师生完全公开，每一步代入值可查，不做黑箱。")
    with st.expander("🧭 实验教学过程与实验方法", expanded=False):
        st.markdown("**总学时 8 学时（课前 1 + 课中 6 + 课后 1）**")
        st.markdown("""
        - **课前 1 学时 · 自主预习**：阅读行业基线表与估值公式，完成行业选择预研（SWOT 素材），带着「选哪行、避哪个坑」进入课堂
        - **课中 6 学时 · 师生联动**：教师端掌握事件卡投放节奏（教学「手柄」）与状态机（开放提交→关闭提交→结算只读）；学生按 25 步完成三轮决策，每轮结算后教师即时点评
        - **课后 1 学时 · 问题分析探究**：完成复盘三问（资产在哪步变质？激励哪项产生复利？模式搬到其他行业哪条失效？），提交后进入六维评分与特别奖评定
        """)
        st.markdown("**实验考核（申报口径：操作 60% + 报告 30% + 综合 10%）**：")
        st.markdown("| 考核环节 | 权重 | 构成 |\n|---|---|---|\n| 实验操作过程 | 60% | 三轮 25 步决策完成度 + 估值净值 V + 操作审计留痕 |\n| 实验报告 | 30% | 复盘三问 + 估值报告 + 入表披露材料 |\n| 综合表现 | 10% | 课堂答辩 + 金点子创意 + 团队协作 |")
        st.caption("课中另有六维过程评价（V 终值 30% / Q×C 20% / 入表合规 15% / 团队健康 15% / 战略迭代 10% / 复盘深度 10%），与申报考核口径相互校验。")
    with st.expander("💻 实验必读（运行环境要求）", expanded=False):
        st.markdown("""
        - **网络要求**：出口带宽不低于 2M/s，支持 ≥1000 人并发在线（云端负载均衡）
        - **浏览器要求**：推荐 Chrome / Firefox 最新版；不支持移动端访问，请使用电脑浏览器
        - **硬件要求**：普通办公电脑即可（CPU 双核以上、内存 4G 以上、可联网）；无高算力依赖，全程云端运行
        - **操作系统要求**：Windows 7 及以上、macOS、Linux 均可
        - **账号要求**：无需注册，打开链接即用；如需保存进度请使用同一浏览器标签页完成三轮
        """)
    st.divider()

    if not st.session_state.started:
        st.markdown("### 🎮 开局设置（董事会视角：选行业 → 组阁 → 盘点 → 定首轮预算）")
        st.info("💡 你是**董事会成员**，不是执行者——钱怎么分、人怎么配、风险接不接受，都得自己拍板。第一轮先召开首次董事会，完成「选行业 → 组阁（组建团队）→ 盘点家底 → 定首轮预算」四项决策。")
        # v25 实名注册门控（对照教师端规范：注册后操作留痕到 data/logs.csv，教师端按班级/学号聚合成绩）
        st.markdown("#### 🪪 实名注册（教师端留痕必需，同班同学号不可重复）")
        st.markdown(f"**已登录班级**：`{st.session_state.klass}`（更换班级请刷新页面重新登录）")
        if st.session_state.get("student"):
            stu = st.session_state.student
            st.success(f"已注册：{stu.get('班级')} · {stu.get('学号')} · {stu.get('姓名')}")
        else:
            reg_c1, reg_c2 = st.columns(2)
            with reg_c1:
                reg_sid = st.text_input("学号", key="reg_sid", placeholder="如 20240001")
            with reg_c2:
                reg_name = st.text_input("姓名", key="reg_name", placeholder="你的真实姓名")
            if st.button("📝 确认注册（防顶替校验）"):
                reg_klass = st.session_state.klass
                if not (reg_klass.strip() and reg_sid.strip() and reg_name.strip()):
                    st.warning("学号 / 姓名不能为空。")
                elif save_student(reg_klass.strip(), reg_sid.strip(), reg_name.strip()):
                    st.session_state.student = {"班级": reg_klass.strip(), "学号": reg_sid.strip(), "姓名": reg_name.strip()}
                    st.success(f"注册成功：{reg_klass.strip()} · {reg_sid.strip()} · {reg_name.strip()}")
                    st.rerun()
                else:
                    st.error("该班级下此学号已注册（防顶替）——请确认学号或联系老师。")
            st.caption("注册后本实验全部操作（每步提交/撤销/结算/问卷）将实时留痕到教师端；不注册也可试玩，但教师端无法按学号聚合你的成绩。")
        st.divider()
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
        st.caption("👉 表中数值越小越省心；未来健康行业 C 天花板最低（0.5），对合规要求最苛刻——想挑战选它。")
        c1, c2 = st.columns(2)
        with c1:
            role = st.selectbox("**你在董事会中的身份**", ["数据运营总监", "数据分析员", "算法工程师", "首席数据官"], index=0)
            st.session_state.role = role
        with c2:
            # v3.1：行业选择改为单选卡片（圆点式，一眼可见四选项）
            ind_key = st.radio("**选择案例行业（单选卡片）**", list(INDUSTRIES.keys()), index=0, key="start_ind")
            ind = INDUSTRIES[ind_key]
            st.caption(f"选定「{ind_key}」→ 行业生成六类数据清单、三域流转（{ind.get('flow','')}）与专属风险事件库")
        st.warning("⚠️ 行业差异教学建议：制造专业易选未来制造、信息类专业易选未来信息——竞赛建议强制抽签或按专业混编，跳出舒适区。")
        if st.button("🚀 召开首次董事会（领取每轮350万预算）", type="primary"):
            st.session_state.industry = ind_key
            st.session_state.started = True
            st.session_state.round = 1
            st.session_state.step = 1
            record("开始实验", f"行业={ind_key}，角色={role}")
            append_log("开始实验", f"行业={ind_key}，角色={role}")
            st.rerun()
    else:
        ind = INDUSTRIES[st.session_state.industry]
        st.success(f"**实验进行中**：行业={st.session_state.industry}·{ind['name']}，角色={st.session_state.role}，当前第 {st.session_state.round} 轮")
        st.markdown(f"**你的行业基线**：Q 初始 {ind['q0']} ｜ C 天花板 {ind['c_cap']} ｜ H 基准 {ind['h_base']}万/轮 ｜ 单位存储 {ind['unit_storage']}万/TB ｜ 典型陷阱：{ind['trap']}")
        st.markdown("**25 步决策流程**：投入篇(1-4) → 采集篇(5-8) → 治理篇(9-12) → 赋能篇(13-16) → 变现篇(17-20) → 经营与估值篇(21-25，含问卷收尾)")
        if st.button("🔄 重置实验"):
            for k in list(st.session_state.keys()):
                if k not in ("started",):
                    del st.session_state[k]
            st.rerun()

    # ===== v8.4 新增：政策与标准依据（参考文献） =====
    st.divider()
    st.markdown("### 📚 政策与标准依据（估值公式与实验设计的制度出处）")
    for doc in REFERENCE_DOCS:
        st.markdown(f"- {doc}")
    st.caption("实验中的估值模型、确权登记流程、入表计量与脱敏要求均按上述国家标准与政策文件设计，供课后查证。")

# ========== Tab1：25 步决策台 ==========
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
    st.markdown("### 📋 25 步决策台（第 {r} 轮）".format(r=r))
    cur_phase = next((ph for ph in PHASES if st.session_state.step in ph["steps"]), PHASES[0])
    cols = st.columns(6)
    for i, ph in enumerate(PHASES):
        done_n = len([s for s in ph["steps"] if s in st.session_state.done])
        with cols[i]:
            st.markdown(f"**{ph['name']}** {'⭐' if ph is cur_phase else ''}")
            st.progress(done_n / len(ph["steps"]), text=f"{done_n}/{len(ph['steps'])}")
    # 当前步骤引导条
    stp = st.session_state.step
    if stp <= 25:
        prev_part = f"<span style='color:#43A047;font-weight:600'>← {STEP_NAMES[stp-1]} ✅</span>" if stp > 1 and (stp-1) in st.session_state.done else ("<span style='color:#B0BEC5'>← 起点</span>" if stp == 1 else f"<span style='color:#90A4AE'>← {STEP_NAMES[stp-1]}</span>")
        cur_part = f"<span style='background:#1E88E5;color:#fff;border-radius:8px;padding:2px 10px;font-weight:800'>📍 第{stp}步 · {STEP_NAMES[stp]}</span>"
        nxt_part = f"<span style='color:#90A4AE'>→ {STEP_NAMES[stp+1]}</span>" if stp < 25 else ""
        st.markdown(f"<div style='background:#F5F9FF;border:1px solid #BBDEFB;border-radius:10px;padding:8px 14px;font-size:14px'>{prev_part}　{cur_part}　{nxt_part}</div>", unsafe_allow_html=True)
    st.markdown("")
    step = st.session_state.step
    if step >= 25 and 25 in st.session_state.done:
        st.info("25 步全部完成（估值已在步骤23计算入库，问卷已在步骤25提交）。确认本轮结算后锁定只读，可开放下一轮。")
        if st.button("✅ 完成本轮（结算锁定）", type="primary"):
            st.session_state.settled.add(st.session_state.round)
            record(f"第{st.session_state.round}轮·结算锁定", "本轮只读")
            st.rerun()
        return
    if step > 25:
        st.info("25 步全部完成（估值已在步骤23计算入库，问卷已在步骤25提交）。确认本轮结算后锁定只读，可开放下一轮。")
        if st.button("✅ 完成本轮（结算锁定）", type="primary"):
            st.session_state.settled.add(st.session_state.round)
            record(f"第{st.session_state.round}轮·结算锁定", "本轮只读")
            st.rerun()
        return

    step_ui(step)
    render_step(step)
    if step_done(step) and step < 25:
        if st.button(f"下一步 →（步骤{step+1}：{STEP_NAMES[step+1]}）", type="primary"):
            st.session_state.step += 1
            st.rerun()

# 各步骤渲染函数
def render_step(step):
    d = st.session_state.decisions
    if step == 1:
        # v2.0 修改①+新增②：董事会开局 · 组阁（8 角色，6 必选 + 2 可选，年薪计入当轮 H）
        # v8.4：新增董事会三年任务书（KPI 领取，董事会视角落地）
        st.markdown("**召开首次董事会 · 组阁**：你是**董事会成员**，拍板定人。8 个角色里 6 个必选、2 个可选；**团队年薪直接计入当轮 H（持有成本）**——人不是白用的。")
        st.info("💡 小白提示：董事会就是公司里拍板大事的那几个人。钱怎么分、人怎么配、风险接不接受，都得自己定。")
        with st.expander("📜 董事会三年任务书（先领 KPI，再组阁）", expanded=True):
            st.markdown(f"**{BOARD_TASK['title']}**")
            st.markdown(BOARD_TASK["intro"])
            task_df = pd.DataFrame([{"KPI": g["kpi"], "目标": g["target"], "为什么": g["why"]} for g in BOARD_TASK["goals"]])
            st.dataframe(task_df, use_container_width=True, hide_index=True)
            st.markdown("💬 董事会的话：**人不配齐、预算不花在刀刃上，任务书就是废纸。** 组阁花的年薪会直接抬升本轮 H——人不是白用的，但没人，后面 23 步寸步难行。")
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
        # v8.4：数据类型图示化（图片/音频/视频…用「图形卡片」直观呈现）+ 行业数据示例
        ind = INDUSTRIES[st.session_state.industry]
        st.markdown(f"**盘点家底**（{st.session_state.industry}行业）：先搞清楚“我有什么”，再决定“我缺什么、要不要花钱买/采”。")
        st.info("💡 小白提示：很多团队一上来就花钱买数据，最后发现手里的数据本来就能用——这就是现实中“重复造轮子”的坑。")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Q 初始", ind["q0"])
        with c2: st.metric("C 天花板", ind["c_cap"])
        with c3: st.metric("H 基准", f"{ind['h_base']}万/轮")
        with c4: st.metric("团队状态", f"{st.session_state.team['cap']}/{st.session_state.team['mot']}/{st.session_state.team['ret']}")
        st.markdown("**🧰 现有家底——五类数据类型盘点（图示版）**")
        # 图示法：五类数据用图形卡片直观展示（修改方案：不用文字堆砌，先看图再读表）
        type_icons = [
            ("📄", "文件 / 表格", "Excel·CSV·PDF", "做统计、出报表、喂模型", "坑：格式乱、清洗贵"),
            ("🖼️", "图片", "产品图·监控截图·影像", "图像识别、质检、审核", "坑：体积大、存得贵、含人脸"),
            ("🎧", "音频", "客服录音·设备运转声", "语音质检、故障预警", "坑：转写贵、涉隐私需脱敏"),
            ("🎬", "视频", "监控录像·产线画面", "行为识别、工艺质检", "坑：最占存储"),
            ("📡", "传感器流数据", "温度·压力·位置上报", "实时监控、预测性维护", "坑：频率越高 H 涨越快"),
        ]
        icon_html = """
        <div style="display:flex;gap:10px;flex-wrap:wrap;padding:4px 0">
        {cards}
        </div>
        """
        icon_cards = []
        for emoji, name, ex, use, trap in type_icons:
            icon_cards.append(f"""
            <div style="flex:1;min-width:150px;background:#F5F9FF;border:1px solid #BBDEFB;border-radius:12px;padding:12px;text-align:center">
            <div style="font-size:34px">{emoji}</div>
            <div style="font-weight:800;color:#0D47A1;margin-top:4px">{name}</div>
            <div style="font-size:12px;color:#455A64;margin-top:4px">{ex}</div>
            <div style="font-size:12px;color:#1565C0;margin-top:4px">{use}</div>
            <div style="font-size:11px;color:#C62828;margin-top:4px">{trap}</div>
            </div>""")
        md_html(icon_html.format(cards="".join(icon_cards)))
        st.markdown("**📋 五类数据明细表（看图之后再看表，每类都给了企业里的真实样例）**")
        type_samples = {
            "文件 / 表格": "销售明细表 120 万行（近 3 年）",
            "图片": "产品质检照片 3,000 张/天（含不合格样本）",
            "音频": "客服录音 2,000 条/月（含投诉与好评）",
            "视频": "产线/门店监控录像 7×24 小时（存 90 天）",
            "传感器流数据": "设备温度/压力/流量 5 秒/条（全年约 630 万条）",
        }
        inv_rows = []
        for x in DATA_TYPE_INVENTORY:
            inv_rows.append({"类型": x["name"], "是什么": x["desc"], "企业里的真实样例": type_samples.get(x["name"], "见上图"), "能干什么": x["use"], "常见坑": x["trap"]})
        st.dataframe(pd.DataFrame(inv_rows), use_container_width=True, hide_index=True)
        # v3.1：行业数据示例（图示法落地：具体到“多少张照片、能干什么”，四新行业）
        # v2026-10-20：每行业附「案例·降本增效」——处理这批数据后能省/赚多少（与引擎场景现金流对应）
        ind_example = {
            "未来制造": "产线摄像头拍下的**不合格产品照片 3,000 张**——处理好了就能训练质检模型，把产品合格率从 95% 提到 98%",
            "未来信息": "调度平台实时上报的**结构化日志（API 每 30 秒一条）**——规整后做算力调度优化，是卫星/算法服务的底子",
            "未来健康": "脱敏后的历史病历 **5,000 份**——结构化清洗后支撑临床质控，但必须过伦理审查才能用",
            "未来能源": "加氢站设备实时上报的**压力/温度/流量数据（每 5 秒一条）**——时序建模后做制氢负荷预测，是能耗优化的底子",
        }
        ind_case = {
            "未来制造": "把照片清洗+标注成质检样本 → 训练质检模型 → **合格率 95%→98%**，良率提升场景**每轮多赚约 180 万**（引擎「良率提升」场景现金流）",
            "未来信息": "把日志规整成标准格式 → 算力调度优化 → 闲置算力降 20%，**每轮多赚约 180 万**（引擎「算力调度优化」场景现金流）",
            "未来健康": "病历结构化+脱敏 → 临床质控 → 质控效率提升，**每轮省约 170 万**（引擎「临床质控」场景现金流）",
            "未来能源": "时序数据建模 → 制氢负荷预测 → 氢能调度更准，**每轮多赚约 190 万**（引擎「制氢负荷预测服务」场景现金流）",
        }
        st.markdown(f"**🔎 你在「{st.session_state.industry}」行业手里的牌**：{ind_example.get(st.session_state.industry, '')}")
        st.success(f"💹 **案例·降本增效**：{ind_case.get(st.session_state.industry, '')}——这就是「数据变钱」的起点，先盘清手里的牌，别急着花钱买。")
        st.markdown(f"**⚠️ 行业典型陷阱**：{ind['trap']}——记得提醒自己别踩。")
        if st.button("✅ 确认盘点完成（免费）", disabled=step_done(step)):
            mark_done(2, "盘点家底")
            st.rerun()
    elif step == 3:
        st.markdown("**制定三年战略**：选「对内优先」还是「对外优先」——锁定后改道成本高。")
        st.info("💡 小白提示：战略不是喊口号。先用 SWOT 看清自己（优势/劣势/机会/威胁），再选方向——对内是保底，对外是弹性，两条路风险完全不同。")
        # v8.4：行业 SWOT 四象限展示（修改方案：战略展开细化，方便小白理解）
        sw = INDUSTRY_SWOT.get(st.session_state.industry, {})
        sw_html = """
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:4px 0">
          <div style="background:#E8F5E9;border:2px solid #43A047;border-radius:12px;padding:12px">
            <div style="font-weight:800;color:#1B5E20">💪 优势 S</div>
            <div style="font-size:13px;color:#2E7D32;margin-top:4px">{S}</div>
          </div>
          <div style="background:#FFF3E0;border:2px solid #FB8C00;border-radius:12px;padding:12px">
            <div style="font-weight:800;color:#E65100">🪨 劣势 W</div>
            <div style="font-size:13px;color:#F57C00;margin-top:4px">{W}</div>
          </div>
          <div style="background:#E3F2FD;border:2px solid #1E88E5;border-radius:12px;padding:12px">
            <div style="font-weight:800;color:#0D47A1">🚀 机会 O</div>
            <div style="font-size:13px;color:#1976D2;margin-top:4px">{O}</div>
          </div>
          <div style="background:#FFEBEE;border:2px solid #E53935;border-radius:12px;padding:12px">
            <div style="font-weight:800;color:#C62828">⚠️ 威胁 T</div>
            <div style="font-size:13px;color:#D32F2F;margin-top:4px">{T}</div>
          </div>
        </div>
        """
        md_html(sw_html.format(**sw))
        choice = st.radio("战略方向：", ["对内优先（降本增效，确定性强、天花板低）", "对外优先（数据变现，弹性大、受合规强约束）"], index=0)
        # v8.4：3 年目标细化（选定方向后给出可执行的三年拆解）
        if "对内" in choice:
            st.markdown("**三年拆解（对内优先）**：① 第1年 治理打底（Q 拉高、合规守住）→ ② 第2年 场景降本（良率/能耗/质控场景跑通）→ ③ 第3年 局部对外（把最稳的场景产品化试水）。")
        else:
            st.markdown("**三年拆解（对外优先）**：① 第1年 数据合规化（脱敏+确权+审计留痕，T 拉满）→ ② 第2年 产品化（数据集/API 上线，找分散买家）→ ③ 第3年 规模变现（多场景多买家，避开单一客户依赖）。")
        if st.button("✅ 锁定三年战略（免费）", disabled=step_done(step)):
            st.session_state.decisions["strategy"] = "对内优先" if "对内" in choice else "对外优先"
            mark_done(3, "锁定战略")
            st.rerun()
    elif step == 4:
        # v2.0 新增⑫：预算后果预告横幅
        # v8.4：A/B/C 三套预算方案对比表 + 一键填充（修改方案：罗列方案做表格对比，方便理解）
        st.markdown("**编制预算**：四类资金分配（采集/治理/人力/合规）。本轮先投入 **120万**。")
        st.warning("⏭️ **后果预告**：预算花在「治理」上 → Q 升；花在「合规」上 → C 守住；花太少 → 后续可能出现「质量塌陷」「合规事故」扣款。下轮会投放事件卡（政策/价格战/客户流失/技术替代），留足现金才有对策。")
        st.markdown("**💡 三套参考方案（先看对比，再决定怎么分钱）**")
        plan_df = pd.DataFrame([
            {"方案": p["name"], "采集": f"{p['collect']}万", "治理": f"{p['govern']}万", "人力": f"{p['hr']}万", "合规": f"{p['comp']}万", "合计": f"{p['total']}万", "思路": p["desc"], "适合": p["fit"]}
            for p in BUDGET_PLANS
        ])
        st.dataframe(plan_df, use_container_width=True, hide_index=True)
        pc1, pc2, pc3 = st.columns(3)
        for i, p in enumerate(BUDGET_PLANS):
            col = [pc1, pc2, pc3][i]
            with col:
                if st.button(f"📥 套用 {p['name']}", key=f"bp_{p['id']}_{st.session_state.round}"):
                    st.session_state[f"b_c_{st.session_state.round}"] = p["collect"]
                    st.session_state[f"b_g_{st.session_state.round}"] = p["govern"]
                    st.session_state[f"b_h_{st.session_state.round}"] = p["hr"]
                    st.session_state[f"b_p_{st.session_state.round}"] = p["comp"]
                    st.rerun()
        st.caption("也可以不套用，直接在下方手动微调——每类投入都有上限和下限。")
        c1, c2, c3, c4 = st.columns(4)
        with c1: collect = st.slider("采集投入（万）", 10, 60, 30, step=5, key=f"b_c_{st.session_state.round}", help="市场基准 30 万，区间 10~60 万")
        with c2: govern = st.slider("治理投入（万）", 10, 60, 35, step=5, key=f"b_g_{st.session_state.round}", help="市场基准 35 万，区间 10~60 万")
        with c3: hr = st.slider("人力投入（万）", 5, 40, 15, step=5, key=f"b_h_{st.session_state.round}", help="市场基准 15 万，区间 5~40 万")
        with c4: comp = st.slider("合规投入（万）", 5, 40, 20, step=5, key=f"b_p_{st.session_state.round}", help="市场基准 20 万，区间 5~40 万")
        total = collect + govern + hr + comp
        st.markdown(f"合计 **{total}万**（预算 120 万，{'✅ 在预算内' if total <= 120 else '❌ 超预算！'}")
        if st.button(f"✅ 确认编制预算（开支-{total}万）", disabled=step_done(step) or total > 120):
            if spend("步骤4·编制预算", total * 10000):
                st.session_state.decisions["budget"] = {"collect": collect, "govern": govern, "hr": hr, "comp": comp}
                mark_done(4, "编制预算")
                st.rerun()
    elif step == 5:
        # v2.0 新增⑥+⑪：数据来源与采集限值 + 常见数据类型小课堂
        # v8.4：多渠道数据源 + 滚动条调采集量
        # v9.1：数据源改为【多选题】（勾选即多渠道），合规按木桶效应判定
        st.markdown("**选择数据源与采集量**：真实公司的数据从来不是一个渠道——**公司内部 + 行业共享 + 购买/爬取公开数据**往往同时进行。")
        st.info("💡 小白提示：爬取数据虽然单价便宜，但越限后果最重——合规红线不因“数据便宜”而放宽。便宜的数据可能最贵。多选数据源时，只要其中有一个渠道不合规，整体可信度就被它拉低（木桶效应）。")
        with st.expander("📚 常见数据类型小课堂（先建立直觉再选数据）", expanded=False):
            kinds_df = pd.DataFrame([{"类型": x["name"], "是什么": x["desc"], "例子": x["example"], "在实验中的处理": x["handle"]} for x in DATA_KINDS_CLASS])
            st.dataframe(kinds_df, use_container_width=True, hide_index=True)
            st.caption("结构化最好清洗（Q 加成最高）；非结构化存得贵（H 高）。")
        # —— 数据源多选（v9.1：checkbox 多选，至少选 1 个）——
        st.markdown("**① 数据源（多选，至少选 1 个）**——勾选的每个渠道都会产生采集量与成本：")
        src_df = pd.DataFrame([
            {"渠道": s["name"], "采集限值": f"{s['limit_tb']}TB", "单位成本": f"{s['unit_cost']}万/TB", "可信度T": s["trust_pt"], "基础采集量": f"{s['base_tb']}TB", "说明": s["compliance"]}
            for s in SOURCE_TYPES
        ])
        st.dataframe(src_df, use_container_width=True, hide_index=True)
        selected_sources = []
        for s in SOURCE_TYPES:
            key = f"src_{s['id']}_{st.session_state.round}"
            if s["id"] == "内部":
                default_check = True
            else:
                default_check = st.session_state.get(key, False)
            if st.checkbox(f"{s['name']}（限值 {s['limit_tb']}TB · {s['unit_cost']}万/TB · 可信度 {s['trust_pt']}）", value=default_check, key=key):
                selected_sources.append(s["id"])
        if not selected_sources:
            st.error("⚠️ 至少勾选 1 个数据源（公司内部数据是底线，建议至少保留它）")
        # 采集量：基础量之和 + 额外滚动条
        src_cfgs = [next(s for s in SOURCE_TYPES if s["id"] == x) for x in selected_sources]
        base_tb = sum(s["base_tb"] for s in src_cfgs) if src_cfgs else 0
        cheapest_unit = min(s["unit_cost"] for s in src_cfgs) if src_cfgs else 1.0
        st.markdown("**② 额外采集量（拖动滚动条调整）**——基础采集量之外再多采一些：")
        extra_tb = st.slider(
            f"额外采集量（TB，当前基础 {base_tb}TB）", 0, 15, 0, step=1,
            key=f"src_extra_{st.session_state.round}",
            help="拉得越多，H 越高；若勾选了「爬取的」，基础 6TB + 额外超过 8TB 即触发爬取越限（合规事故，C 降至 0.3）。",
        )
        total_tb = base_tb + extra_tb
        base_cost = sum(s["base_tb"] * s["unit_cost"] for s in src_cfgs) if src_cfgs else 0
        extra_cost = round(extra_tb * cheapest_unit, 1)
        total_cost = round(base_cost + extra_cost, 1)
        # 越限检查：爬取限值 8TB，基础 6 + 额外
        over = 0
        over_note = ""
        if "爬取" in selected_sources:
            craw_tb = next(s["base_tb"] for s in src_cfgs if s["id"] == "爬取") + extra_tb
            if craw_tb > 8:
                over = craw_tb - 8
                over_note = f"⚠️ **越限预告**：爬取渠道共 {craw_tb}TB 超过限值 8TB（超 {over}TB）——触发合规事故，C 直接降至 0.3"
        if over > 0:
            st.warning(over_note)
        st.info(f"💰 **本步支出预览**：基础采集 {base_tb}TB（{base_cost}万）＋ 额外 {extra_tb}TB（{extra_cost}万，按最低价渠道 {cheapest_unit}万/TB） = **{total_cost}万**；总采集量 **{total_tb}TB**")
        src_label = "+".join(selected_sources) if selected_sources else "未选"
        if st.button(f"✅ 确认数据源（开支-{total_cost}万）", disabled=step_done(step) or not selected_sources):
            if spend(f"步骤5·{src_label}", int(total_cost * 10000)):
                st.session_state.decisions["sources"] = selected_sources
                # 引擎主源 = 多选中可信度最低的渠道（木桶效应，决定 C/T 底线）
                st.session_state.decisions["source"] = min(src_cfgs, key=lambda s: s["trust_pt"])["id"]
                st.session_state.decisions["source_tb"] = total_tb
                st.session_state.decisions["source_over_limit"] = over > 0
                st.session_state.decisions["channels"] = [s["name"] for s in src_cfgs]
                st.session_state.decisions["channel_cost"] = round(total_cost, 1)
                # v9.1：多选后全部采集量已含在 source_tb 中，channel_tb 置 0 避免重复计入 collected_tb
                st.session_state.decisions["channel_tb"] = 0
                mark_done(5, "选择数据源")
                st.rerun()
    elif step == 6:
        st.markdown("**签订数据合同**：授权范围、期限、可否转授权——决定 C 系数。")
        st.info("💡 小白提示：签合同不是走形式。授权范围写多宽、能不能转授权，直接决定这笔数据买卖合不合规——C 系数就是合同的「体检表」。")
        # v8.4：样例合同直观展示（修改方案：模拟几份合同样例，让学生直观感受）
        with st.expander("📄 样例合同长什么样？（先看两份真实感样例，再选你的条款）", expanded=False):
            st.markdown("**样例 1 · 完整授权（合规标杆）**")
            st.markdown("""
            > **数据授权使用合同（样例）**
            > 甲方（数据提供方）：XX 智造数据有限公司
            > 乙方（数据使用方）：XX 零售集团
            > 一、授权数据：2024 年 1—12 月脱敏用户画像数据集（约 8TB）
            > 二、授权范围：**完整授权**，乙方可用于精准营销及内部经营分析
            > 三、转授权：**允许转授权**（需书面告知甲方）
            > 四、合规承诺：甲方保证数据来源合法、已按《个人信息保护法》完成脱敏；乙方不得超范围使用
            > 五、期限：12 个月 ｜ 金额：50 万元
            > **结论：C 系数保持最高档——授权清晰、责任明确。**
            """)
            st.markdown("**样例 2 · 口头约定（反面教材）**")
            st.markdown("""
            > 甲：这批数据你拿去用吧，回头按销量分成。
            > 乙：行，那我先用着。
            > **——没有书面授权、没有用途限制、没有责任条款。**
            > **结论：C 系数直接掉到 0.6（合规瑕疵）。一旦出事，甲乙双方都说不清，罚没的是你的对外收入。**
            """)
        choice = st.radio("合同条款（单选）：", ["完整授权+可转授权（C 保持）", "部分授权（C 0.8，成本-5万）", "口头约定（C 0.6，⚠️合规瑕疵）"], index=0)
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
        # v3.1：接入存储 + 可信溯源四步闭环（血缘→审计→回滚→授权，四步全做 T 提升）
        # v2026-10-20：存储方案专业词给小白解释
        st.markdown("**接入存储 + 可信溯源**：选存储方案（影响 H），再做**血缘追溯 → 审计日志 → 版本回滚 → 跨域授权**四步闭环——四步全部完成，可信度 T 的「可追溯审计」30 分到手。")
        st.info("💡 小白提示：可信溯源就是给数据装「行车记录仪」——从哪来（血缘）、谁改过（审计）、出事故能还原（回滚）、谁有权用（授权）。**数据越可信，同事和客户越敢用、越会用**——买家看到这些记录才敢买你的数据。")
        with st.expander("📖 三个存储方案 · 白话解释（先看懂再选）", expanded=False):
            st.markdown("""
- **🪣 数据湖**：把数据先原样存进一个大池子（便宜、快，先存了再说），要用时再整理。缺点：不整理就「封闭」用不起来，采集量越多存储成本涨得越快（H 上升）。
- **🏬 数仓**：先按标准整理好、再存进规整的仓库（干净、好查），整理要花钱（成本 20 万），但数据好用了。
- **🏛️ 湖仓一体**：池子+仓库的优点都要（又能存原样、又能规整查询），存储成本基准再降 20%，是三个里最省长期钱的，只是入场费最高（成本 35 万）。
""")
        choice = st.radio("存储方案（单选）：", ["数据湖（采集量×1.2，H 上升；封闭）", "数仓（标准，成本20万）", "湖仓一体（H 基准-20%，成本35万）"], index=0)
        # v3.1：可信溯源四步闭环
        st.markdown("**🔗 可信溯源四步闭环（V3.1 补齐，来自企业实践）**")
        st.caption("为什么做这四步？**数据越可信，同事和客户越会使用**——有血缘能查来源、有审计能对账、能回滚不怕出事、授权清楚才敢共享。四步全做，可信度 T 的「可追溯审计」+30 分。")
        trust_steps = [
            ("血缘追溯", "记录数据从「哪个源、哪条管道」来的，能画溯源图谱"),
            ("不可篡改审计日志", "每次读写/变更都留痕且不可篡改，可对账"),
            ("版本回滚演练", "模拟一次数据污染事故，演练恢复到污染前版本"),
            ("跨域授权链签署", "成都—德阳—绵阳三域间授权链条逐级签署确认"),
        ]
        tsteps = {}
        tcols = st.columns(4)
        for i, (tname, tdesc) in enumerate(trust_steps):
            with tcols[i]:
                tsteps[tname] = st.checkbox(f"✅ {tname}", key=f"trust_{i}_{st.session_state.round}")
                st.caption(tdesc)
        n_trust = sum(1 for v in tsteps.values() if v)
        st.progress(n_trust / 4, text=f"可信溯源进度 {n_trust}/4" + ("（✅ 四步完成 → T「可追溯审计」+30）" if n_trust == 4 else "（四步全做才有 T+30，少一步都不算闭环）"))
        audit_ok = n_trust == 4
        if st.button("✅ 确认存储与溯源（按选项扣款）", disabled=step_done(step)):
            if "数据湖" in choice:
                st.session_state.decisions["storage"] = "数据湖"
                cost = 0
            elif "数仓" in choice:
                st.session_state.decisions["storage"] = "数仓"; cost = 20
            else:
                st.session_state.decisions["storage"] = "湖仓一体"; cost = 35
            st.session_state.decisions["audit_trail"] = audit_ok
            st.session_state.decisions["trust_steps"] = [k for k, v in tsteps.items() if v]
            if spend(f"步骤7·{st.session_state.decisions['storage']}", cost * 10000):
                mark_done(7, "接入存储与可信溯源")
                st.rerun()
    elif step == 8:
        # v8.4：确权登记七步标准流程（依据国家数据局《数据产权登记工作指引（试行）》，修改方案：联网查证正确流程、深入浅出）
        st.markdown("**确权登记 + 责任人签字**：入表前置动作，决定能否资本化（无形资产）；签字即负责，可信度 T +30。")
        st.markdown("- 完成确权登记 → 出表时可选「无形资产」资本化（评分更高）；**责任人签字 → 可信度 T +30**")
        st.markdown("- 跳过确权 → 只能按「存货」计量，且合规评分降低")
        st.info("💡 小白提示：确权就是给数据资产办「房产证」——先证明这数据是你的、来源合法，才能把它当资产写进报表。没有证，只能当「存货」贱卖。")
        with st.expander("🗂️ 确权登记标准流程（七步，依据国家数据局《数据产权登记工作指引（试行）》）", expanded=True):
            reg_html = """
            <div style="display:flex;gap:8px;flex-wrap:wrap;padding:4px 0">
            {cards}
            </div>
            """
            reg_cards = []
            for i, rf in enumerate(REGISTER_FLOW):
                reg_cards.append(f"""
                <div style="flex:1;min-width:150px;background:{'#E8F5E9' if i < 3 else ('#E3F2FD' if i < 5 else '#FFF3E0')};border:1px solid #90CAF9;border-radius:10px;padding:10px">
                <div style="font-weight:800;color:#0D47A1;font-size:14px">{rf['step']}</div>
                <div style="font-size:12px;color:#37474F;margin-top:4px">{rf['desc']}</div>
                </div>""")
            md_html(reg_html.format(cards="".join(reg_cards)))
            st.caption("登记类型覆盖：初次登记 / 转让登记 / 变更登记 / 续期登记 / 注销登记；本实验完成「初次登记」即可满足资本化条件。")
        if st.button("✅ 完成确权登记并签字（免费）", disabled=step_done(step)):
            st.session_state.decisions["register"] = True
            mark_done(8, "确权登记")
            st.rerun()
    elif step == 9:
        st.markdown("**定标准**：元数据、主数据、编码规范——提升一致性。")
        choice = st.radio("标准投入（单选）：", ["全套标准（10万，一致性+0.15）", "基础标准（5万，一致性+0.08）", "不投入（一致性不变，质量塌陷风险）"], index=0)
        if st.button("✅ 确认标准投入", disabled=step_done(step)):
            cost = 10 if "全套" in choice else (5 if "基础" in choice else 0)
            if spend("步骤9·定标准", cost * 10000):
                st.session_state.decisions["standard"] = cost
                mark_done(9, "定标准")
                st.rerun()
    elif step == 10:
        # v3.1：质检标注三模式（自研/招标/AI混合，招标可能触发返工扣款）+ 质量稽核投入
        st.markdown("**质检标注 + 质量稽核**：标注模式三选一（决定 Q 与返工风险），再决定稽核投入（决定准确性）。")
        st.info("💡 小白提示：标注就是给数据「贴标签」（这张照片是良品/次品、这段录音是好/坏评）。自研稳、招标省事但可能返工、AI 预标注快但需要人工质检兜底——现实中也是这三选一。")
        qa_mode = st.radio("标注模式（三选一）：", ["自研团队标注（免费，质量最稳）", "公开招标标注（6万，⚠️可能触发返工扣款+10万）", "AI 预标注+人工质检（8万，标注快、Q 加成高）"], index=0, key=f"qa_{st.session_state.round}")
        qa_cost = 6 if "招标" in qa_mode else (8 if "AI" in qa_mode else 0)
        if "招标" in qa_mode:
            st.warning("⚠️ **招标风险提示**：外部标注质量不可控，模拟「质量不合格→返工扣款」事件，确认后追加 **10 万返工费**。")
        choice = st.radio("质量稽核投入：", ["深度稽核（12万，准确性+0.15）", "例行稽核（6万，准确性+0.08）", "跳过稽核（0万，⚠️质量塌陷）"], index=0, key=f"qc_{st.session_state.round}")
        total_cost10 = qa_cost + (10 if "招标" in qa_mode else 0) + (12 if "深度" in choice else (6 if "例行" in choice else 0))
        if st.button(f"✅ 确认质检标注与稽核（开支-{total_cost10}万）", disabled=step_done(step)):
            cost = qa_cost + (10 if "招标" in qa_mode else 0) + (12 if "深度" in choice else (6 if "例行" in choice else 0))
            if spend("步骤10·质检标注与稽核", cost * 10000):
                st.session_state.decisions["qa_mode"] = "自研团队" if "自研" in qa_mode else ("公开招标" if "招标" in qa_mode else "AI预标注+人工质检")
                st.session_state.decisions["qa_rework"] = "招标" in qa_mode
                st.session_state.decisions["qc"] = 12 if "深度" in choice else (6 if "例行" in choice else 0)
                mark_done(10, "质检标注与质量稽核")
                st.rerun()
    elif step == 11:
        # v2.0 新增⑧：脱敏小课堂 + 前置 2 题测验
        # v8.4：什么是敏感数据（示例罗列，小白也能识别）+ 脱敏投入滚动条
        st.markdown("**安全分级与脱敏**：决定 C 系数上限（行业天花板内）。")
        with st.expander("📖 脱敏小课堂（先看懂再动手）", expanded=False):
            st.markdown("**一句话解释**：脱敏就是把数据里能认出具体某个人的信息去掉或换掉，让它既能用来分析，又不会泄露谁是谁——就像把成绩单上的名字遮住，老师还能统计平均分，但不知道是谁考的。")
            st.markdown("**为什么要脱敏？** 数据里往往藏着身份证号、手机号、住址、病历等“能定位到具体的人”的信息。直接拿出去卖或用，等于把别人的隐私公开了——这是违法的（违反《个人信息保护法》），也是本实验中 **C 系数会归零** 的原因。")
            st.markdown("**脱敏的难点**：脱得太狠，数据就没用了（Q 下降）；脱得太轻，隐私还在泄露（C 下降）。真实企业每天都在做这个取舍。")
            mask_df = pd.DataFrame([{"方法": x["name"], "怎么做": x["desc"], "举例": x["example"], "适用": x["fit"]} for x in MASK_METHODS])
            st.dataframe(mask_df, use_container_width=True, hide_index=True)
        # v8.4：什么是敏感数据（修改方案：罗列示例、数量、成本，让小白理解）
        with st.expander("🔍 什么是敏感数据？（先认识要保护的东西，再决定花多少钱脱敏）", expanded=True):
            sens_df = pd.DataFrame(SENSITIVE_DATA_EXAMPLES)
            st.dataframe(sens_df, use_container_width=True, hide_index=True)
            st.caption("一句话：**能定位到具体的人 / 泄露会出事的数据，都是敏感数据。** 医疗、金融、未成年人数据最敏感，脱敏成本也最高。")
        st.markdown("**📝 前置小测验（共 4 题，答对 3 题才能执行脱敏）**")
        q1 = st.radio("Q1：脱敏的目的是？", ["A. 让数据更好看", "B. 去掉/替换能识别个人的信息，既能分析又不泄露", "C. 删除所有数据"], key=f"mq1_{st.session_state.round}")
        q2 = st.radio("Q2：手机号 138****6721 用了哪种脱敏方法？", ["A. 掩码", "B. 哈希", "C. 泛化"], key=f"mq2_{st.session_state.round}")
        q3 = st.radio("Q3：员工姓名「李明」需要脱敏，以下哪种做法最合适？", ["A. 掩码为「李*」（保留姓氏、隐藏名）", "B. 直接删除整条员工记录", "C. 原样保存，因为姓名不算敏感信息"], key=f"mq3_{st.session_state.round}")
        q4 = st.multiselect("Q4（多选）：下列哪些做法能保障个人信息安全？", ["A. 对敏感字段加密存储", "B. 只收集业务必需的最少信息（最小化）", "C. 把脱敏后的数据包公开分享给所有人", "D. 定期删除不再需要的过期数据"], key=f"mq4_{st.session_state.round}")
        score = int("B" in q1) + int("A" in q2) + int("A" in q3) + int(set(q4) == {"A. 对敏感字段加密存储", "B. 只收集业务必需的最少信息（最小化）", "D. 定期删除不再需要的过期数据"})
        q_ok = score >= 3
        st.session_state.mask_quiz_ok[st.session_state.round] = q_ok
        st.progress(score / 4, text=f"测验得分 {score}/4")
        if not q_ok:
            st.warning("❌ 未通过（需答对 3 题）。提示：Q1 选 B（去标识化）；Q2 选 A（掩码）；Q3 选 A（姓名可掩码）；Q4 别选 C（公开分享会泄露）。")
        choice = st.radio("脱敏方案（单选卡片）：", ["全量脱敏（15万，C 保持）", "部分脱敏（8万，C≤0.8）", "未脱敏（0万，⚠️C=0.3 且罚没风险）"], index=0, key=f"mask_{st.session_state.round}")
        # v8.4：脱敏投入滚动条（修改方案：滚动条拉动、给范围、给收益）
        extra_mask = st.slider(
            "额外脱敏投入（匿名化/加密强化，0~5 万）：", 0, 5, 0, step=1,
            key=f"mask_extra_{st.session_state.round}",
            help="拉满 3 万以上 → 加密与匿名化强化，C 上限 +0.05（更抗「安全专项检查」事件卡）；0 万则保持方案原值。",
        )
        if extra_mask >= 3:
            st.info(f"🛡️ 强化脱敏生效：C 上限 +0.05（本步合计开支：{15 + extra_mask if '全量' in choice else 8 + extra_mask if '部分' in choice else extra_mask}万）")
        if st.button("✅ 确认脱敏方案", disabled=step_done(step) or not q_ok):
            cost = 15 if "全量" in choice else (8 if "部分" in choice else 0)
            cost += extra_mask
            if spend("步骤11·脱敏", cost * 10000):
                st.session_state.decisions["mask"] = "全量脱敏" if "全量" in choice else ("部分脱敏" if "部分" in choice else "未脱敏")
                st.session_state.decisions["mask_extra"] = extra_mask
                mark_done(11, "安全分级与脱敏")
                st.rerun()
    elif step == 12:
        # v3.1：资产目录上架 + 数据可信度评估（创新点·来自企业实践，三维评分 T）
        st.markdown("**资产目录上架 + 数据可信度评估**：上架让资产可被发现（Q 完整性提升、入表可确认）；同时做**可信度 T 三维评分**（创新点·来自企业实践）。")
        st.info("💡 小白提示：可信度解决「买家信不信你」——就像买东西看「正品保证」：来源清楚、有人负责、能追溯，买家才敢买、才肯出高价。")
        st.markdown("- 上架成本 5 万（数据资产目录管理）")
        # v3.1 创新点：数据可信度三维评分（来源40 + 责任人30 + 可追溯审计30）
        t_now, t_detail = calc_t(st.session_state.decisions)
        t_band = "高可信（80–100）" if t_now >= 80 else ("中可信（50–79）" if t_now >= 50 else "低可信（0–49）")
        band_color = "#43A047" if t_now >= 80 else ("#FB8C00" if t_now >= 50 else "#E53935")
        with st.expander("🎯 数据可信度评估（来源合法40 + 责任人签字30 + 可追溯审计30）", expanded=True):
            st.markdown(f"**当前可信度 T = {t_now}（{t_band}）**")
            st.progress(t_now / 100, text=f"T={t_now} ｜ {t_band}")
            t_rows = []
            for k, v in [("来源合法清晰(40)", t_detail.get("来源合法清晰", 0)), ("责任人签字(30·确权)", t_detail.get("责任人签字", 0)), ("可追溯审计(30·溯源四步)", t_detail.get("可追溯审计", 0))]:
                missing = {"来源合法清晰(40)": 40, "责任人签字(30·确权)": 30, "可追溯审计(30·溯源四步)": 30}[k] - v
                t_rows.append({"维度": k, "得分": v, "满分": 30 if "30" in k else 40, "缺口": missing})
            st.dataframe(pd.DataFrame(t_rows), use_container_width=True, hide_index=True)
            st.markdown(f"<span style='color:{band_color};font-weight:700'>💡 T < 50 → 对外变现收入打 5 折；T ≥ 50 买家才敢买。当前缺口：{sum(r['缺口'] for r in t_rows)} 分</span>", unsafe_allow_html=True)
            st.caption("**创新点标注**：数据可信度是企业构建高质量数据集的重要依据。本步骤对数据进行来源合法性、责任人签字、可追溯审计三维评分，形成可信度 T 指标（80-100 高可信 / 50-79 中可信 / 0-49 低可信），T<50 时对外变现收入打 5 折。该设计源自企业实践，是本实验的核心创新点之一。")
        if st.button("✅ 确认上架并完成可信度评估（开支-5万）", disabled=step_done(step)):
            if spend("步骤12·资产目录上架", 5 * 10000):
                st.session_state.decisions["catalog"] = True
                mark_done(12, "资产目录上架与可信度评估")
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
        # v8.4：滚动条调建模投入（修改方案：拖动滚动条选择花多少钱，实时显示收益区间）
        # v2026-10-20：先给当前 Q 值与判断标准——学生不知道去哪看 Q、当前适不适合投
        st.markdown("**建模与验证**：投入越高 → 准确率越高 → 场景现金流放大。")
        st.info("💡 小白提示：建模不是越贵越好——深度建模 20 万现金流 +60%，但如果你手里数据质量 Q 不高，模型再强也白搭。**先看 Q，再决定投入。**")
        cur_q, _ = calc_q(st.session_state.industry, st.session_state.decisions)
        if cur_q >= 0.8:
            q_advice = "数据质量好（Q≥0.8）→ 放心上 **深度建模（20 万）**，放大 +60% 最划算"
            q_color = "#43A047"
        elif cur_q >= 0.6:
            q_advice = "数据质量中等（0.6≤Q<0.8）→ 建议 **标准建模（10 万）**，先稳再冲"
            q_color = "#FB8C00"
        else:
            q_advice = "数据质量偏弱（Q<0.6）→ 先别砸钱建模，回「治理篇」补标准/质检把 Q 拉起来，再投 **标准建模（10 万）**"
            q_color = "#E53935"
        st.markdown(f"**📊 当前数据质量 Q = {cur_q:.2f}**（完整×一致×时效×准确，由治理投入决定）")
        st.progress(min(cur_q, 1.0), text=f"Q={cur_q:.2f} ｜ 判断标准：Q<0.6 差 / 0.6~0.8 中 / ≥0.8 好")
        st.markdown(f"<span style='color:{q_color};font-weight:700'>💡 当前该投多少：{q_advice}</span>", unsafe_allow_html=True)
        st.caption("去哪看 Q？→ 完成第 9-12 步后，本步实时显示；结算后也可在「估值中心」查看每轮 Q 值。")
        model_inv = st.slider(
            "建模投入（万）：", 2, 20, 10, step=1,
            key=f"model_{st.session_state.round}",
            help="2 万（复用开源）→ 10 万（标准建模）→ 20 万（深度建模）；投入每增加 10 万，场景现金流约 +30%。",
        )
        boost = 1.0 + (model_inv * 10000 / 200000.0) * 0.6  # 引擎口径：每 20 万 +60%
        gain_pct = (boost - 1.0) * 100
        st.markdown(f"📈 **投入 {model_inv}万 → 场景现金流 ×{boost:.2f}（+{gain_pct:.0f}%）**")
        st.progress(min(gain_pct / 60, 1.0), text=f"现金流放大 {gain_pct:.0f}%")
        if st.button(f"✅ 确认建模投入（开支-{model_inv}万）", disabled=step_done(step)):
            cost = model_inv
            if spend("步骤14·建模", cost * 10000):
                st.session_state.decisions["model"] = cost
                mark_done(14, "建模与验证")
                st.rerun()
    elif step == 15:
        st.markdown("**上线与推广**：内部阻力模拟——业务部门不配合需额外投入。")
        choice = st.radio("推广策略（单选）：", ["全力推广（15万，现金流畅达）", "渐进推广（8万，现金流×0.9）", "不推广（0万，现金流×0.7）"], index=0)
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
        # v3.1：产品化 + 数据变现（对外成交价滑块，市场价基准+限定区间）
        st.markdown("**产品化与数据变现**：选产品形态，再定对外成交价——成交价越高收入越多，但过高卖不出去。")
        st.info("💡 小白提示：产品化就是把数据「打包成能卖的东西」（API/数据集/报告/模型服务），数据变现就是把它真正卖出去换回现金。成交价不是拍脑袋——参考市场价（50万基准），太低亏本、太高没人买。")
        choice = st.radio("产品形态：", ["API 服务（弹性计费）", "数据集授权（收入×0.9）", "分析报告（一次性）", "模型服务（收入×1.1）"], index=0, key=f"prod_{st.session_state.round}")
        # v2026-10-20：按当前数据质量 Q 给建议参考价 + 理由（学生小白不知道定多少）
        cur_q, _ = calc_q(st.session_state.industry, st.session_state.decisions)
        if cur_q >= 0.8:
            price_advice = ("建议定 **80~120 万**", "你手里数据质量高（Q≥0.8），买家认品质，定高也有人买，吃满 ×1.5 封顶", "Q≥0.8 数据硬气")
        elif cur_q >= 0.6:
            price_advice = ("建议定 **50~80 万**", "数据质量中等（0.6≤Q<0.8），按市场基准 50 万往上小步加价，别一上来冲 120 万", "0.6≤Q<0.8 求稳")
        else:
            price_advice = ("建议定 **30~50 万**", "数据质量偏弱（Q<0.6），定太高买家不买账（流标风险），先低价跑量攒口碑", "Q<0.6 先跑量")
        st.markdown(f"**💡 建议参考价**：{price_advice[0]}（理由：{price_advice[1]}）")
        st.caption(f"定价依据：当前 Q={cur_q:.2f}（{price_advice[2]}）。高价需 Q 支撑，Q 越高越能定高价。")
        price = st.slider(
            "对外成交价（万元，市场价基准 50 万）：", 0, 150, 50, step=5,
            key=f"price_{st.session_state.round}",
            help="50 万为市场基准（收入系数×1.0）；定到 100 万以上需数据质量 Q 支撑，否则有流标风险；定价越高对外收入放大越多（封顶×1.5）。",
        )
        price_coef = min(0.5 + price / 100.0, 1.5)
        st.markdown(f"💵 **定价预览**：成交价 **{price}万** → 对外收入系数 **×{price_coef:.2f}**" + ("（超过 100 万已封顶 ×1.5，需高 Q 支撑）" if price > 100 else ""))
        if st.button("✅ 确认产品化与成交价（免费）", disabled=step_done(step)):
            st.session_state.decisions["product"] = "API服务" if "API" in choice else ("数据集授权" if "数据集" in choice else ("分析报告" if "分析" in choice else "模型服务"))
            st.session_state.decisions["product_price"] = price
            record("步骤17·产品化与数据变现", f"{st.session_state.decisions['product']}·成交价{price}万")
            mark_done(17, "产品化与数据变现")
            st.rerun()
    elif step == 18:
        # v8.4：定价方法白话解释 + 案例（修改方案：专业词汇给小白解释 + 样例展示，避免选不明白）
        st.markdown("**定价**：成本法 / 价值法 / 市场法——三种方法结果不同。")
        st.info("💡 小白提示：定价就是回答「这份数据卖多少钱」——按成本定、按价值定、还是按市场定，三种答案差很多。先看下表再选。")
        with st.expander("📖 三种定价方法 · 白话解释 + 算例（先看懂再选）", expanded=True):
            pr_df = pd.DataFrame([{"方法": x["方法"], "一句话解释": x["一句话"], "算例": x["例子"], "优点": x["优点"], "缺点": x["缺点"], "引擎效果": x["引擎"]} for x in PRICING_EXPLAIN])
            st.dataframe(pr_df, use_container_width=True, hide_index=True)
            st.markdown("**💡 怎么选？** 手里数据 Q 高、买家竞争激烈 → 市场法吃弹性；想求稳不亏本 → 成本法；数据帮买家赚钱明显 → 价值法。")
        choice = st.radio("定价方法（单选）：", ["成本法（对外收入×0.8，稳）", "价值法（基准）", "市场法（对外收入×1.2，弹性大）"], index=0, horizontal=True)
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
            legal_src = st.radio("第二条【校验】数据来源合法性：", ["内部授权（合法）", "合规采集（合法）", "来源不明确（违规）"], key=f"cl_{st.session_state.round}")
            st.markdown("**📝 第三条「用途限制」怎么填？**（小白引导）")
            st.markdown("> 用途限制 = **写明数据「只能拿来干什么、不能拿来干什么」**。\n> 参考写法：`仅用于会员复购预测与内部经营分析，禁止转售、禁止用于第三方广告投放`。\n> 关键：① 具体到业务场景（如：客户画像/复购预测/风控建模）；② 明确禁止事项（如：不得转售/不得用于与合同无关用途）；③ 一句话能说清，别只写“数据分析”这种笼统词。")
            use_limit = st.text_input("第三条【校验】用途限制（具体用途，非空）：", placeholder="例：仅用于会员复购预测，禁止转售与广告投放", key=f"cu_{st.session_state.round}")
            liability = st.radio("第七条【校验】法律责任承担方：", ["甲方承担（数据方负责）", "乙方承担", "双方各半"], key=f"clb_{st.session_state.round}")
            q_floor = st.number_input("第六条 Q 下限（0.5-0.9）：", 0.5, 0.9, 0.7, step=0.05, key=f"cq_{st.session_state.round}")
        buyer_choice = st.radio("买家结构（单选，影响下跌路径）：", ["多个分散买家（收入×1.0，无依赖风险）", "单一独家大客户（收入×1.5，⚠️单一客户依赖 D 20%）", "双客户（收入×1.2，轻度依赖）"], index=0)
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
        choice = st.radio("SLA 等级（单选）：", ["高标准SLA（5万，收入×0.95，无违约）", "标准SLA（2万，无加成）"], index=0)
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
        choice = st.radio("入表方式（单选）：", ["无形资产（需完成确权登记，评分更高）", "存货（未确权时的选择）"], index=0)
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
            st.rerun()
        # v3.1：估值报告双栏（V变化 + 四因子拆解）+ AI 提分辅导（3 条针对性建议）
        last = st.session_state.val_history[-1] if st.session_state.val_history else None
        if last and last.get("round") == st.session_state.round:
            st.divider()
            prev = st.session_state.val_history[-2] if len(st.session_state.val_history) >= 2 else None
            st.markdown("### 📊 估值报告（双栏：V 变化 + 四因子拆解）" + (f" {last.get('top1_note','')}" if last.get("top1_note") else ""))
            cL, cR = st.columns(2)
            with cL:
                st.markdown("**V 净值变化**")
                if prev:
                    delta = last["v"] - prev["v"]
                    arrow = "🟢 上涨" if delta > 0 else ("🔴 下跌" if delta < 0 else "⚪ 持平")
                    st.markdown(f"上轮 **{prev['v']}万** → 本轮 **{last['v']}万**（{arrow} **{delta:+.1f}万**）")
                    st.progress(min(abs(delta) / max(abs(prev["v"]), 1), 1.0), text=f"变化幅度 {delta:+.1f}万")
                else:
                    st.markdown(f"首轮估值 **{last['v']}万**（基准起点）")
                st.markdown(f"- 现金流入：**{last['cash_in']}万** ｜ 现金流出：**{last['cash_out']}万**")
                st.markdown(f"- 折现后 PV：**{round((last['cash_in'] + last['cash_out']) / (1.1 ** last['round']), 1)}万**")
            with cR:
                st.markdown("**四因子拆解（Q/C/H/D）**")
                fac_rows = []
                for name, key in [("质量 Q", "q"), ("合规 C", "c"), ("持有成本 H", "h"), ("减值 D", "d")]:
                    cur = last.get(key, 0)
                    if prev and key in prev:
                        old = prev[key]
                        fac_rows.append({"因子": name, "上轮": old, "本轮": cur, "变化": round(cur - old, 2) if isinstance(cur, float) else cur - old})
                    else:
                        fac_rows.append({"因子": name, "上轮": "-", "本轮": cur, "变化": "-"})
                st.dataframe(pd.DataFrame(fac_rows), use_container_width=True, hide_index=True)
                st.markdown(f"**可信度 T = {last.get('t_score', 0)}**" + ("（✅ ≥50 对外不打折）" if last.get("t_score", 0) >= 50 else "（⚠️ <50 对外收入打 5 折）"))
            st.divider()
            st.markdown("### 🤖 AI 运营辅导（先看懂字母，再听建议）")
            st.info("**字母对照表（小白必看）**：**Q**=数据质量系数｜**C**=合规系数｜**H**=持有成本｜**D**=减值准备｜**T**=数据可信度｜**V**=资产净值（正=赚、负=亏）。下面每条建议都能在左侧找到对应步骤，按步骤号照做即可。")
            for title, body in ai_coach(st.session_state.decisions, st.session_state.industry, last, prev):
                st.markdown(f"- **{title}**：{body}")
            st.markdown("### 📋 下一轮按步操作建议（总结版，照着做就行）")
            for item in st.session_state.action_plan.get(st.session_state.round, []):
                st.markdown(f"- {item}")
            with st.expander("📋 完整版：先复盘第 1-25 步 → 再梳理做得好/不好 → 最后逐条建议 + 理由"):
                goods, bads = gen_round_review(st.session_state.decisions, last)
                st.markdown("**① 本轮操作复盘（按 1-25 步梳理）**")
                st.markdown(f"**✅ 做得好**：{'；'.join(goods)}")
                st.markdown(f"**⚠️ 待改进**：{'；'.join(bads)}")
                st.markdown("**② 逐条建议 + 理由**")
                for title, body in gen_ai_tips(st.session_state.decisions, st.session_state.industry, last):
                    st.markdown(f"- **{title}**：{body}")
    elif step == 24:
        st.markdown("**董事会答辩**：向「投资方」说明涨跌原因，提交下轮调整方案。")
        note = st.text_area("答辩陈述（一句话说明本轮决策逻辑）：", height=100)
        if st.button("✅ 提交答辩记录（免费）", disabled=step_done(step)):
            st.session_state.decisions["defense"] = note
            mark_done(24, "董事会答辩")
            st.rerun()
    elif step == 25:
        # v25：问卷调查（实验收尾反馈，不扣预算、不计入估值，仅供教师端汇总与教学改进）
        st.markdown("**问卷调查**：本轮 24 步决策已全部走完。结束前花 1 分钟反馈真实感受——问卷**不扣预算、不影响估值**，答案会汇总到教师端，作为课程优化依据。")
        st.info("💡 问卷是「实验的镜子」：你填的内容将出现在教师端「问卷调查汇总」，不参与 V/Q/C/H/D 任何计算。")
        rnd = st.session_state.round
        q1 = st.radio("Q1 本轮收获最大的环节是？（单选）", ["投入与组阁", "数据采集", "治理与脱敏", "赋能建模", "变现定价", "经营估值"], index=None, key=f"sv1_{rnd}")
        q2 = st.radio("Q2 估值公式 V = Σ(场景现金流/1.1ᵗ) × Q × C − H − D，你现在的理解程度？（单选）", ["完全理解，能独立计算", "基本理解，对照公示会算", "部分理解，需要提示", "没理解，需要补讲"], index=None, key=f"sv2_{rnd}")
        q3 = st.slider("Q3 本轮团队激励效果，你打几分？（1-5）", 1, 5, 3, key=f"sv3_{rnd}")
        q4 = st.radio("Q4 事件卡带来的压力与你的应对，你的感受是？（单选）", ["很有挑战，应对从容", "有压力但扛住了", "压力较大，有些手忙脚乱", "没感觉，影响不大"], index=None, key=f"sv4_{rnd}")
        q5 = st.text_area("Q5 开放建议：本轮哪一步让你最困惑？或你想对老师说的话？（选填）", height=90, key=f"sv5_{rnd}")
        if st.button("✅ 提交问卷（免费，汇总至教师端）", disabled=step_done(25)):
            st.session_state.survey[rnd] = {
                "q1": q1 or "未选", "q2": q2 or "未选", "q3": q3, "q4": q4 or "未选", "q5": (q5 or "").strip(),
            }
            record(f"第{rnd}轮·问卷调查", "已提交")
            append_log("问卷调查", f"Q1={q1 or '未选'};Q2={q2 or '未选'};Q3激励={q3};Q4={q4 or '未选'};Q5={(q5 or '').strip()[:40]}", step=25, outcome="已提交")
            mark_done(25, "问卷调查")
            st.rerun()

def render_incentives():
    """S21 团队激励设计器（v2.0：5 工具，预算=现金×15% 上限 50 万，不能全选，金点子征集；v3.1：成员画像前置）"""
    st.markdown("**团队激励投放**：每轮激励总预算 = 团队当前现金 × 15%（上限 50 万），在 5 个工具中组合，**不能全选**。")
    st.info("💡 工具箱参考真实企业实践：海底捞（授权一线、师徒制）、胖东来（高薪+高福利+尊重员工）。")
    # v3.1：成员画像（对症下药——先懂人，再设计激励）
    st.markdown("### 👤 成员画像（先懂人，再激励）")
    prof_rows = []
    for p in TEAM_PROFILES:
        prof_rows.append({"成员": p["name"], "情况介绍": p["situation"], "适合的激励": p["fit"]})
    st.dataframe(pd.DataFrame(prof_rows), use_container_width=True, hide_index=True)
    st.caption("💡 激励的尽头是懂人：看到「小李父母年迈」，你就知道为什么胖东来会给员工父母发「孝心工资」。下面的工具组合和自定义方案，都该对着画像来。")
    # v2026-10-20：预算上限用 round 取整（原 int 截断会让“上限1万”实际只有 9千多），且允许等于上限
    budget_limit = min(round(st.session_state.budget * 0.15), 500000)
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
    # v8.4：自定义激励方案（修改方案：单独对话框，学生提自己的见解——孝心工资、弹性工时等，参照胖东来）
    st.divider()
    st.markdown("### ✍️ 自定义激励方案（可选，写出你的创意）")
    st.info("💡 好激励不是抄工具箱。胖东来给员工父母发「孝心工资」、海底捞给一线授权——**激励的尽头是懂人**。这里允许你设计工具箱里没有的方案，真实生效。")
    cust_name = st.text_input("方案名称（如：孝心工资 / 弹性工时 / 内部创业孵化……）：", key=f"cust_n_{st.session_state.round}")
    cust_type = st.radio("方案类型：", ["非金钱（关怀类，稳团队）", "金钱（现金类，提意愿）"], index=0, horizontal=True, key=f"cust_t_{st.session_state.round}")
    cust_cost = st.slider("本方案预算（万，0~20）：", 0, 20, 5, step=1, key=f"cust_c_{st.session_state.round}", help="非金钱关怀类推荐小预算（孝心工资 5 万就很有温度）；现金类预算越大意愿加得越多。")
    has_custom = bool(cust_name.strip())
    if has_custom:
        cust_effect = "意愿+8、稳定+4（非金钱·关怀复利）" if "非金钱" in cust_type else "意愿+10（金钱，下轮有反噬风险）"
        st.success(f"✅ 自定义方案已就绪：**{cust_name.strip()}**（{cust_type.split('（')[0]}，预算 {cust_cost}万）→ 效果：{cust_effect}")
    st.markdown(f"**激励合计**：{fmt(total_cost + (cust_cost if has_custom else 0) * 10000)}（本轮预算上限 {fmt(budget_limit)}）")
    if total_cost + (cust_cost if has_custom else 0) * 10000 > budget_limit:
        st.error("❌ 超激励预算！请减少选择或降低自定义方案预算")
    if n_chosen >= 5:
        st.warning("⚠️ 不能全选：5 个工具箱至少舍弃 1 个——什么都给，等于什么都没给。")
    can_go = (total_cost + (cust_cost if has_custom else 0) * 10000) <= budget_limit and n_chosen < 5
    if st.button("✅ 投放激励方案（按选择扣款）", disabled=step_done(21) or not can_go):
        chosen = [i["id"] for i in INCENTIVES if options.get(i["id"])]
        total_spend = total_cost
        if has_custom:
            total_spend += cust_cost * 10000
        if total_spend > 0 and not spend("步骤21·团队激励", total_spend):
            st.stop()
        st.session_state.incentives = chosen
        st.session_state.incentives_round[st.session_state.round] = chosen
        t = st.session_state.team
        money_only = all(INC_BY_ID[i]["type"] == "金钱" for i in chosen) and len(chosen) > 0
        for i in chosen:
            inc = next(x for x in INCENTIVES if x["id"] == i)
            for k, v in inc["effect"].items():
                t[k] = max(0, min(100, t[k] + v))
        # v8.4：自定义激励真实生效
        if has_custom:
            if "非金钱" in cust_type:
                t["mot"] = max(0, min(100, t["mot"] + 8))
                t["ret"] = max(0, min(100, t["ret"] + 4))
                st.session_state.custom_incentives[st.session_state.round] = {"name": cust_name.strip(), "type": "非金钱", "cost": cust_cost, "mot": 8, "ret": 4}
            else:
                t["mot"] = max(0, min(100, t["mot"] + 10))
                money_only = True
                st.session_state.custom_incentives[st.session_state.round] = {"name": cust_name.strip(), "type": "金钱", "cost": cust_cost, "mot": 10}
            record(f"第{st.session_state.round}轮·自定义激励", f"{cust_name.strip()[:12]}（{cust_cost}万）")
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
    # v2.0 新增⑩：金点子征集
    # v9.1：输入框【始终显示】——学生随时可写，结算前提交记为「预提交」，结算后由教师评估
    # v3.1：提交即 AI 判定（规则引擎五维评分）+ 方案罗列·班级投票（每人3票，Top1 V+3%）
    st.divider()
    st.markdown("### 💡 我的激励金点子（随时可写，提交即 AI 判定）")
    already = st.session_state.gold_ideas.get(st.session_state.round, "")
    settled_ok = st.session_state.round in st.session_state.settled or step_done(23)
    idea = st.text_area("提出文档里没有的激励创意（如：弹性工时、内部创业孵化……）：", value=already, height=80, key=f"idea_{st.session_state.round}", placeholder="例：给数据工程师发「弹性工时券」，每周可任选一天远程办公……")
    if st.button("📤 提交金点子并 AI 判定", disabled=bool(already)):
        if idea.strip():
            st.session_state.gold_ideas[st.session_state.round] = idea.strip()
            st.session_state.gold_ai[st.session_state.round] = judge_gold_idea(idea.strip())
            record(f"第{st.session_state.round}轮·金点子", idea.strip()[:20])
            st.rerun()
    # v3.1：AI 判定结果卡（本地规则引擎，无需外部 API）
    if st.session_state.gold_ideas.get(st.session_state.round):
        idea_text = st.session_state.gold_ideas[st.session_state.round]
        j = st.session_state.gold_ai.get(st.session_state.round) or judge_gold_idea(idea_text)
        if j["verdict"] == "优秀":
            st.success(f"🤖 **AI 判定：优秀（{j['score']} 分）**——{j['advice']}")
        elif j["verdict"] == "合格":
            st.info(f"🤖 **AI 判定：合格（{j['score']} 分）**——{j['advice']}")
        else:
            st.error(f"🤖 **AI 判定：不合格（{j['score']} 分）**——{j['advice']}")
        st.caption("判定依据：" + " / ".join(j["tags"]))
    if not settled_ok:
        st.caption("💬 金点子随时可写：结算前提交保存为「预提交」，完成第 23 步估值结算后，教师端可评估采纳（采纳 → 稳定+10 意愿+10 V+5%）。")
    # v3.1：方案罗列 + 班级投票（每人 3 票，单选圆点式，实时排行，Top1 V+3%）
    if st.session_state.gold_ideas:
        st.markdown("#### 🗳️ 金点子方案罗列·班级投票（每人 3 票，票选 Top1 → 该方案直接落地 V+3%）")
        votes = st.session_state.gold_votes.setdefault(st.session_state.round, {})
        used = st.session_state.gold_voter_used.get(st.session_state.round, 0)
        options = {f"第{r}轮·{i[:18]}": (r, i) for r, i in list(st.session_state.gold_ideas.items())[-6:]}
        if options:
            pick = st.radio("● 单选式投票：每个方案前有圆点，投出你宝贵的一票（每人共 3 票）：", list(options.keys()), key=f"gv_{st.session_state.round}")
            if st.button(f"🗳️ 投出 1 票（剩余 {max(3 - used, 0)} 票）", disabled=used >= 3):
                votes[pick] = votes.get(pick, 0) + 1
                st.session_state.gold_voter_used[st.session_state.round] = used + 1
                st.rerun()
        if votes:
            ranked = sorted(votes.items(), key=lambda x: -x[1])
            top = ranked[0]
            st.session_state.gold_top1[st.session_state.round] = top[0]
            st.markdown("**实时票数排行：**")
            for lab, n in ranked:
                mark = " 👑Top1" if lab == top[0] else ""
                st.markdown(f"- {lab}：**{n} 票**{mark}")
            st.caption("结算估值时，本轮票选 Top1 方案自动落地（V+3%）。")

# ========== Tab2：估值中心 ==========
def render_tab2():
    if not st.session_state.started:
        st.info("请先开始实验")
        return
    st.markdown("### ⚖️ 估值中心（三轮估值曲线 + 公式公开）")
    if not st.session_state.val_history:
        st.info("尚未结算任何轮次。完成 25 步后在「决策台」点击「结算本轮估值」。")
    # 估值曲线
    if st.session_state.val_history:
        df = pd.DataFrame(st.session_state.val_history)[["round", "v", "q", "c", "h", "d", "cash_in", "cash_out", "pv"]]
        df = df.rename(columns={"round": "轮次", "v": "V净值(万)", "q": "Q", "c": "C", "h": "H", "d": "D", "cash_in": "现金流入(万)", "cash_out": "现金流出(万)", "pv": "折现PV(万)"})
        st.markdown("#### 📈 三轮净值走势（一眼看懂涨跌）")
        c1, c2 = st.columns([3, 2])
        with c1:
            st.line_chart(df.set_index("轮次")[["V净值(万)"]], height=260)
            st.caption("绿涨红跌：第一轮普遍上涨 → 第二轮事件卡回调 → 第三轮分化。")
        with c2:
            st.markdown("**三轮估值明细**（每轮现金流入/流出与折现后 PV 都记录在案，方便对比）")
            st.dataframe(df, use_container_width=True, hide_index=True)
        # v2026-10-20：V=0 核对与解释（不是 bug，是引擎的合规/成本账）
        lastv = st.session_state.val_history[-1]["v"]
        if lastv <= 0:
            st.warning("**❓ 为什么 V 是 0 甚至为负？（已核对：这是估值引擎的正常结果，不是系统故障）**\n\n"
                       "可能原因：\n"
                       "- **合规系数 C=0**：未脱敏 / 数据源含「爬取」且超限 / 触发违规事件卡 → 对外收入全罚没（去步骤 6、7、10、11 补合规）；\n"
                       "- **入不敷出**：场景收入为 0，而持有成本 H 太高（采集量大 + 存储贵 + 角色多）→ 养数据的钱比赚的钱多；\n"
                       "- **减值 D 计提**：单一客户依赖 / 风险事件 → 扣 30%。\n\n"
                       "**解法**：下一轮把合规四件套（合同完整授权 → 全量脱敏 → 可信溯源 → 确权）做满，再压采集量控 H，V 就会回正。")
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
        # v9.1：三轮操作与估值前后对比（操作→结果，一眼看懂三轮决策差异）
        if st.session_state.val_history:
            st.markdown("#### 🕹️ 三轮操作与估值前后对比（操作→结果）")
            st.caption("每一行是一轮：左边看你当时做了什么操作，右边看估值结果——三轮放一起，就能看清“哪一步操作真正抬高了估值”。")
            ops_rows = []
            for x in st.session_state.val_history:
                op = x.get("ops", {})
                ops_rows.append({
                    "轮次": f"第{x['round']}轮",
                    "战略": op.get("战略", "-"),
                    "数据源": op.get("数据源", "-"),
                    "脱敏": op.get("脱敏", "-"),
                    "赋能": op.get("赋能", "-"),
                    "定价": op.get("定价", "-"),
                    "确权": op.get("确权", "-"),
                    "V净值(万)": x["v"], "Q": x["q"], "C": x["c"], "H": x["h"], "D": x["d"],
                })
            ops_df = pd.DataFrame(ops_rows)
            st.dataframe(ops_df, use_container_width=True, hide_index=True)
            if len(st.session_state.val_history) >= 2:
                diff = st.session_state.val_history[-1]["v"] - st.session_state.val_history[-2]["v"]
                last_op = st.session_state.val_history[-1].get("ops", {})
                if diff > 0:
                    st.success(f"💡 **结论**：第{len(st.session_state.val_history)}轮相对上一轮 **V 上升 {diff:.1f}万**。复盘哪些操作是功臣（如本轮 {last_op.get('战略','-')}战略 + {last_op.get('数据源','-')}数据源 + {last_op.get('脱敏','-')}），下轮继续强化。")
                elif diff < 0:
                    st.error(f"💡 **结论**：第{len(st.session_state.val_history)}轮相对上一轮 **V 下降 {abs(diff):.1f}万**。对照下跌路径提示，找出拖后腿的操作（如 {last_op.get('数据源','-')} 数据源 / 未脱敏 / 单一客户），下轮立即修正。")
                else:
                    st.info("💡 **结论**：本轮 V 与上轮持平，需通过 AI 建议找短板，打破瓶颈。")
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
    # v8.4：估值公式政策与标准依据（修改方案：估值公式要有文献支撑，不是拍脑袋）
    st.divider()
    st.markdown("### 📚 估值公式与实验设计的政策依据")
    for doc in REFERENCE_DOCS:
        st.markdown(f"- {doc}")
    st.caption("估值模型口径（现金流折现、Q/C/H/D 系数、数据可信度 T）均参考上述国家与行业标准设计；确权登记流程依据国家数据局《数据产权登记工作指引（试行）》。")

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
    # v8.4：自定义激励方案展示（修改方案：激励的尽头是懂人——学生原创方案）
    if st.session_state.custom_incentives:
        st.divider()
        st.markdown("### 💡 团队自定义激励（学生原创方案，真实生效）")
        for rid, ci in st.session_state.custom_incentives.items():
            st.markdown(f"- **第{rid}轮 · {ci['name']}**（{ci['type']}，{ci['cost']}万）→ 意愿 +{ci.get('mot', 0)}" + (f"、稳定 +{ci.get('ret', 0)}" if ci.get("ret") else "") + "　✅ 已生效")

# ========== Tab4：教师端 ==========
def render_tab4():
    st.markdown("### 🎓 教师端（事件卡投放器 + 本轮状态机 + 六维评分 + 学生数据后台）")
    st.caption("对照「教师端代码说明」补齐：口令门控 · 实名注册留痕 · 按班级聚合成绩 · 评估 · CSV 导出。")
    # ── 口令门控（默认 tax2026，正式使用前请修改 TEACHER_PASS 常量） ──
    if not st.session_state.get("teacher_authed"):
        st.markdown("**教师口令**：请输入教师口令进入后台。")
        pwd = st.text_input("教师口令", key="teacher_pwd", type="password")
        if st.button("🔑 进入教师端", key="teacher_login", type="primary"):
            if pwd == TEACHER_PASS:
                st.session_state.teacher_authed = True
                st.success("教师端登录成功：可查看学生成绩、操作记录、评估并按班级导出。")
                st.rerun()
            else:
                st.error("口令错误，请重试。")
        return
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
    st.divider()
    # 问卷调查汇总（第 25 步，v25 新增）
    st.markdown("#### 📋 问卷调查汇总（第 25 步，各轮）")
    if not st.session_state.survey:
        st.caption("暂无问卷提交。学生完成第 25 步问卷后在此汇总（不参与估值计算）。")
    else:
        sv_rows = []
        for rnd in sorted(st.session_state.survey):
            sv = st.session_state.survey[rnd]
            sv_rows.append({
                "轮次": f"第{rnd}轮",
                "收获最大环节": sv.get("q1", "—"),
                "公式理解": sv.get("q2", "—"),
                "激励评分": sv.get("q3", "—"),
                "事件应对": sv.get("q4", "—"),
                "开放建议": sv.get("q5", "—") or "—",
            })
        st.dataframe(pd.DataFrame(sv_rows), use_container_width=True, hide_index=True)
        st.caption("问卷答案仅用于教学改进参考，不计入估值与六维评分。")
    st.divider()
    # ===== 学生数据后台（对照教师端规范：汇总卡 / 成绩表 / 导出 / 详情评估） =====
    st.markdown("#### 📊 学生数据后台（实时聚合自 data/logs.csv）")
    st.info("本地形态：数据写在应用目录 data/；已部署形态：云端实例共享 data/，学生操作实时留痕，教师在线查看。")
    df = export_scores_df()
    classes = sorted(df["班级"].unique().tolist()) if len(df) else []
    # 汇总卡：学生数 / 完成实验数 / 平均估值V / 班级数
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("学生数", len(df))
    m2.metric("已完成实验(≥25步)", int((df["完成步数"] >= 25).sum()) if len(df) else 0)
    m3.metric("平均估值V(万)", f"{round(df['最新估值V'].mean(), 1)}" if len(df) and pd.notna(df["最新估值V"]).any() else "—")
    m4.metric("班级数", len(classes))
    # 班级筛选 + 成绩表
    klass = st.selectbox("按班级筛选", ["全部班级"] + classes, key="teacher_klass_filter") if classes else "全部班级"
    df2 = export_scores_df(klass)
    st.markdown("**学生成绩表**（实时聚合自操作日志：完成步数 / 最新估值V / 六维总分 / 问卷激励均分）")
    st.markdown(html_table(df2), unsafe_allow_html=True)
    # 导出（成绩档案 / 操作日志）+ 退出
    e1, e2, e3 = st.columns(3)
    with e1:
        st.download_button("📥 导出本班成绩档案（CSV）",
                           df2.to_csv(index=False).encode("utf-8-sig"),
                           file_name=f"cdm_vlab_{klass}_scores.csv", mime="text/csv",
                           key="teacher_export_scores")
    with e2:
        logs = _read_csv("logs.csv")
        if klass != "全部班级":
            logs = [r for r in logs if str(r.get("班级", "")).strip() == klass.strip()]
        st.download_button("📥 导出操作日志（CSV）",
                           pd.DataFrame(logs).to_csv(index=False).encode("utf-8-sig"),
                           file_name=f"cdm_vlab_{klass}_logs.csv", mime="text/csv",
                           key="teacher_export_logs")
    with e3:
        if st.button("🚪 退出教师端", key="teacher_logout"):
            st.session_state.teacher_authed = False
            st.rerun()
    # 学生详情 + 操作记录 + 教师评估
    st.divider()
    st.markdown("**学生详情与教师评估**（选中学生 → 查看完整操作记录 → 填写评估评语）")
    if len(df2):
        pick = st.selectbox("选择学生（学号 · 姓名）",
                            [f"{r['学号']} · {r['姓名']}" for _, r in df2.iterrows()], key="teacher_pick")
        sid = pick.split(" · ")[0]
        row = df2[df2["学号"] == sid].iloc[0]
        st.markdown(f"**{row['班级']} · {row['学号']} · {row['姓名']}** ｜ "
                    f"完成 {row['完成步数']}/25 步 ｜ 最新估值 V {row['最新估值V'] if pd.notna(row['最新估值V']) else '—'} 万 ｜ "
                    f"六维总分 {row['六维总分'] if pd.notna(row['六维总分']) else '—'} ｜ 定性 {row['定性']}")
        sub = [r for r in _read_csv("logs.csv")
               if str(r.get("班级", "")).strip() == str(row["班级"]).strip()
               and str(r.get("学号", "")).strip() == sid.strip()]
        st.markdown(f"**操作记录（{len(sub)} 条）**")
        if sub:
            st.markdown(html_table(pd.DataFrame(sub), max_rows=40), unsafe_allow_html=True)
        prev = ""
        for r in _read_csv("assessments.csv"):
            if str(r.get("班级", "")).strip() == str(row["班级"]).strip() and \
               str(r.get("学号", "")).strip() == sid.strip():
                prev = r.get("评语", "")
        comment = st.text_area(f"教师评语（{row['学号']}）", value=prev, key="teacher_comment")
        if st.button("💾 保存评估", key="teacher_save_assess"):
            save_assessment(str(row["班级"]), sid, comment)
            st.success("评估已保存至 data/assessments.csv")
            st.rerun()
    else:
        st.caption("暂无学生注册数据——学生完成实名注册后自动出现在这里。")

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


# ========== v3.1 新增：金点子 AI 判定（本地规则引擎，五维评分，V3.1 方案第十八项） ==========
_BAD_WORDS = ("违法", "泄露", "泄密", "窃取", "侵犯隐私", "违规", "克扣", "加班无薪", "贿赂", "回扣")
_GOOD_WORDS = ("父母", "孝心", "家庭", "成长", "培训", "授权", "弹性", "工时", "关怀", "尊重", "表彰", "带薪", "轮岗", "师徒", "健康", "保险", "食堂", "宿舍", "绩效")


def judge_gold_idea(idea, d=None):
    """金点子 AI 判定：合规性30 + 画像适配25 + 经济性20 + 创新性15 + 可执行性10（规则引擎，无需外部 API）"""
    if not idea or not idea.strip():
        return {"score": 0, "verdict": "不合格", "advice": "金点子不能为空。", "tags": []}
    tags = []
    # ① 合规性 30 分：含敏感/违法词 → 一票否决（0 分不合格）
    if any(w in idea for w in _BAD_WORDS):
        tags.append("含合规风险表述")
        return {"score": 0, "verdict": "不合格", "advice": "⚠️ 检测到违法/违规风险表述（如泄密、克扣、贿赂等），该方案不能落地。请改写为合法、尊重员工权益的激励措施。", "tags": tags}
    legal_score = 30
    # ② 适配度 25 分：与成员画像关键词匹配越多越对症
    fit_hits = sum(1 for w in _GOOD_WORDS if w in idea)
    fit_score = min(25, 8 + fit_hits * 6)
    tags.append(f"画像适配 {fit_hits} 项" if fit_hits else "画像适配一般")
    # ③ 经济性 20 分：含量化成本 → 高分
    econ_score = 20 if any(ch.isdigit() for ch in idea) or "万" in idea or "%" in idea else 10
    tags.append("有量化成本" if econ_score == 20 else "建议补充预算/成本数字")
    # ④ 创新性 15 分：不与工具箱 5 工具重名 → 高分
    builtin = {"现金奖金", "培训", "股权", "福利", "表彰"}
    innov_score = 15 if not any(b in idea for b in builtin) else 5
    tags.append("创新度高" if innov_score == 15 else "与工具箱已有工具重叠，创新性一般")
    # ⑤ 可执行性 10 分：描述越具体越可落地
    exec_score = 10 if len(idea) >= 15 else 4
    tags.append("可落地" if exec_score == 10 else "建议写具体：给谁、做什么、成本多少")
    score = legal_score + fit_score + econ_score + innov_score + exec_score
    verdict = "优秀" if score >= 80 else ("合格" if score >= 60 else "不合格")
    if verdict == "优秀":
        advice = "🌟 方案合规、对症、有量化、有创新且可落地——直接采纳：稳定+10、意愿+10、该轮估值 V+5%。"
    elif verdict == "合格":
        advice = "👍 方案总体可行，建议再补" + ("量化成本" if econ_score == 10 else "") + ("、写具体落地细节" if exec_score == 4 else "") + "。采纳后可提升团队稳定与意愿。"
    else:
        advice = "⚠️ 方案偏空泛或与工具箱重叠，先对照成员画像完善，再提交。"
    return {"score": score, "verdict": verdict, "advice": advice, "tags": tags}

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
    append_log("六维评分", f"总分{total}", step=99, total=total, outcome="已评分")
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
    # v2026-10-20：给小白学生先看「做了什么→得到什么→评点→建议」，再看复盘三问
    vh = st.session_state.val_history
    if vh:
        last = vh[-1]
        d = st.session_state.decisions
        st.markdown("### 📋 ① 操作步骤概况（你 1-25 步做了什么）")
        op = last.get("ops", {})
        op_rows = [
            {"步骤段": "1-4 投入篇", "做了什么": f"行业={st.session_state.industry}｜战略={op.get('战略','-')}｜已投入={op.get('累计投入万','-')}万"},
            {"步骤段": "5-8 采集篇", "做了什么": f"数据源={op.get('数据源','-')}｜采集量={op.get('采集量TB','-')}TB｜确权={op.get('确权','-')}"},
            {"步骤段": "9-12 治理篇", "做了什么": f"脱敏={op.get('脱敏','-')}"},
            {"步骤段": "13-16 赋能篇", "做了什么": f"赋能={op.get('赋能','-')}"},
            {"步骤段": "17-20 变现篇", "做了什么": f"定价={op.get('定价','-')}｜激励={op.get('激励方案','-')}"},
            {"步骤段": "21-25 经营与问卷篇", "做了什么": "已结算估值 + 董事会答辩 + 问卷调查" if st.session_state.reflection or last.get("round") else "待完成"},
        ]
        st.dataframe(pd.DataFrame(op_rows), use_container_width=True, hide_index=True)
        st.markdown("### 💼 ② 数据资产概况（含 V 净值）")
        mc = st.columns(4)
        with mc[0]: st.metric("资产净值 V", f"{last['v']}万", delta=f"第{last['round']}轮")
        with mc[1]: st.metric("质量 Q", f"{last['q']}")
        with mc[2]: st.metric("合规 C", f"{last['c']}")
        with mc[3]: st.metric("持有成本 H", f"{last['h']}万")
        st.markdown(f"- 可信度 T = **{last.get('t_score', 0)}**（≥50 对外收入不打折，<50 打 5 折）｜ 现金流入 **{last['cash_in']}万** / 流出 **{last['cash_out']}万** / 折现后 PV **{last['pv']}万**")
        if len(vh) >= 2:
            trend = "、".join(f"第{x['round']}轮 {x['v']}万" for x in vh)
            st.caption(f"三轮净值走势：{trend}。")
        st.markdown("### 🧐 ③ 评点：做得好 / 待改进")
        goods, bads = gen_round_review(d, last)
        st.markdown(f"**✅ 做得好**：{'；'.join(goods)}")
        st.markdown(f"**⚠️ 待改进**：{'；'.join(bads)}")
        st.markdown("### 🎯 ④ 建议方案（下一轮照做）")
        for item in st.session_state.action_plan.get(st.session_state.round, gen_action_plan(d, st.session_state.industry, last)):
            st.markdown(f"- {item}")
        st.divider()
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
def render_klass_login():
    """最开始的班级编号登录面板：输入班级编号后才进入实验（教师端按班级聚合留痕/成绩）"""
    st.markdown("")
    md_html("""
    <div style="max-width:680px;margin:36px auto 0;background:linear-gradient(135deg,#0F2B46,#1E88E5 60%,#64B5F6);border-radius:16px;padding:32px 40px;color:#fff;text-align:center">
    <div style="font-size:40px">🎯</div>
    <h1 style="margin:8px 0 6px;color:#fff">数据资产运营总监 · 虚拟仿真实验</h1>
    <div style="font-size:15px;color:#E3F2FD">数据资产化与合规治理全生命周期经营决策 · 8 学时（课前1+课中6+课后1）</div>
    </div>
    """)
    st.markdown("### 🔐 班级登录")
    st.info("请输入你的**班级编号**进入实验。登录后需完成实名注册（学号/姓名），全部操作将实时留痕到教师端，教师按班级编号查看与导出成绩。")
    with st.form("klass_login_form"):
        klass = st.text_input("班级编号", key="klass_login_input", placeholder="如 财管2401")
        submitted = st.form_submit_button("🔓 登录进入实验", type="primary")
    if submitted:
        if not klass.strip():
            st.warning("请输入班级编号。")
        else:
            st.session_state.klass = klass.strip()
            st.session_state.student = None  # 更换班级后需重新实名注册
            st.rerun()


def main():
    if not st.session_state.get("klass"):
        render_klass_login()
        return
    render_sidebar()
    if not st.session_state.started:
        render_tab0()
        return
    tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📖 实验导览", "📋 决策台（25步）", "⚖️ 估值中心", "👥 团队激励", "🎓 教师端", "📝 复盘报告",
    ])
    with tab0: render_tab0()
    with tab1: render_tab1()
    with tab2: render_tab2()
    with tab3: render_tab3()
    with tab4: render_tab4()
    with tab5: render_tab5()

if __name__ == "__main__":
    main()
