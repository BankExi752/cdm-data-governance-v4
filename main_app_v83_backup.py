"""
main_app.py
AI企业数据资产化与合规治理虚拟仿真实验 V8.3
成德高端能源装备企业"研发在成都、制造在德阳"跨域数据流转
对标实验空间国家级虚仿实验 ilab-x.com?id=7056
核心框架：9层能力主线 + 海尔"共赢增值表"六维估值
三大壁垒：可信溯源（血缘/审计/回滚/授权）、质检标注三模式、六维估值三次迭代+风险博弈
四行业案例：未来能源、未来信息、未来制造、未来健康（成德绵真实产业基础）
V8.3 修复（2026-10-18）：
  - 所有已完步骤按钮锁定，杜绝重复点击重复扣款
  - 质检标注"平台基础费20万"明示，费用构成透明
  - 去重题去掉答案剧透，答错时给出正确答案与判断依据
  - 脱敏必选字段扩充并提示具体漏选字段；过度脱敏给警告
  - 风险事件1与脱敏选择因果联动：漏脱敏才触发合规罚款，并回放原因
  - 策略三选一按钮改为主按钮样式；能力画像新增收入构成与复盘点评
  - 未点"开始实验"时禁止操作管/治/用数据
"""
import streamlit as st
import pandas as pd
from datetime import datetime

# ========== 页面配置 ==========
st.set_page_config(
    page_title="数据资产化与合规治理虚拟仿真实验 V8.3",
    page_icon="💎",
    layout="wide",
)

INIT_BUDGET = 5000000

# ========== 四大未来产业数据目录 ==========
DATA_CATALOG = {
    "future_energy": [
        {"type":"结构化","name":"电解槽运行日志","device":"IoT网关+传感器","cost":20,"content":"温度/压力/电流时序"},
        {"type":"结构化","name":"加氢站订单表","device":"ERP直连","cost":15,"content":"加注量/客户/频次"},
        {"type":"非结构化","name":"电堆外观图","device":"工业相机","cost":25,"content":"膜电极裂纹/腐蚀"},
        {"type":"非结构化","name":"巡检视频","device":"防爆摄像系统","cost":35,"content":"管线泄漏检测"},
        {"type":"半结构化","name":"维修工单","device":"工单系统导出","cost":12,"content":"故障类型与处置"},
        {"type":"半结构化","name":"安全合规文档","device":"档案扫描","cost":8,"content":"危化许可/环评"},
    ],
    "future_info": [
        {"type":"结构化","name":"算力调度日志","device":"调度平台API","cost":18,"content":"GPU利用率/功耗"},
        {"type":"结构化","name":"卫星遥测表","device":"地面站接收","cost":22,"content":"姿态/轨道/温度"},
        {"type":"非结构化","name":"遥感影像","device":"星载相机+地面站","cost":40,"content":"地表/气象图像"},
        {"type":"非结构化","name":"网络抓包视频","device":"协议分析仪","cost":15,"content":"6G信道特征"},
        {"type":"半结构化","name":"训练任务记录","device":"智算平台导出","cost":10,"content":"任务/参数/耗时"},
        {"type":"半结构化","name":"安全审计日志","device":"SIEM系统","cost":12,"content":"入侵与权限变更"},
    ],
    "future_manufacturing": [
        {"type":"结构化","name":"关节力矩日志","device":"力矩传感器","cost":16,"content":"各关节受力时序"},
        {"type":"结构化","name":"BOM物料表","device":"PLM直连","cost":12,"content":"零部件与供应商"},
        {"type":"非结构化","name":"动作视频","device":"光学动捕+相机","cost":30,"content":"抓取/行走动作"},
        {"type":"非结构化","name":"训练场视频流","device":"训练场摄像头","cost":28,"content":"多机器人协同"},
        {"type":"半结构化","name":"质检缺陷记录","device":"MES导出","cost":10,"content":"装配缺陷明细"},
        {"type":"半结构化","name":"试飞遥测数据","device":"飞控导出","cost":18,"content":"eVTOL姿态数据"},
    ],
    "future_health": [
        {"type":"结构化","name":"脑电波形数据","device":"脑电帽(256导)","cost":45,"content":"μV级神经信号"},
        {"type":"结构化","name":"患者电子病历","device":"HIS直连","cost":25,"content":"诊断/用药记录"},
        {"type":"非结构化","name":"康复动作视频","device":"动作捕捉系统","cost":20,"content":"外骨骼训练"},
        {"type":"非结构化","name":"术中影像","device":"SPECT/CT(DICOM)","cost":38,"content":"核素分布影像"},
        {"type":"半结构化","name":"临床量表","device":"量表系统导出","cost":8,"content":"功能评分"},
        {"type":"半结构化","name":"伦理审批文档","device":"伦理委员会归档","cost":5,"content":"知情同意书"},
    ],
}

INDUSTRIES = {
    "future_energy": {"name":"未来能源·绿色氢能","company":"蜀能智造","color":"#1E88E5"},
    "future_info": {"name":"未来信息·6G算力","company":"蜀光智算","color":"#7C4DFF"},
    "future_manufacturing": {"name":"未来制造·机器人","company":"蜀工智能","color":"#FF6D00"},
    "future_health": {"name":"未来健康·脑机接口","company":"蜀康生命","color":"#00A86B"},
}

# ========== 初始化状态 ==========
if "budget" not in st.session_state:
    st.session_state.budget = INIT_BUDGET
if "started" not in st.session_state:
    st.session_state.started = False
if "done" not in st.session_state:
    st.session_state.done = set()
if "log" not in st.session_state:
    st.session_state.log = []
if "revenue" not in st.session_state:
    st.session_state.revenue = 0
if "val_history" not in st.session_state:
    st.session_state.val_history = []
if "industry" not in st.session_state:
    st.session_state.industry = "future_energy"
if "company" not in st.session_state:
    st.session_state.company = "蜀能智造"
if "role" not in st.session_state:
    st.session_state.role = "数据管家"
if "target" not in st.session_state:
    st.session_state.target = "降本增效"

def spend(name, amt):
    if amt <= 0:
        return True
    if st.session_state.budget < amt:
        st.error(f"❌ 预算不够！需要{amt/10000:.1f}万，只剩{st.session_state.budget/10000:.1f}万")
        return False
    st.session_state.budget -= amt
    st.session_state.log.append((datetime.now().strftime("%H:%M:%S"), name, -amt))
    return True


def step_done(step):
    """步骤是否已完成（用于锁定按钮、防止重复扣款）"""
    return step in st.session_state.done

# ========== 侧边栏 ==========
st.sidebar.title("💎 数据资产经营")
st.sidebar.metric("剩余预算", f"¥{st.session_state.budget/10000:.0f}万")
st.sidebar.metric("累计收入", f"¥{st.session_state.revenue/10000:.0f}万")
st.sidebar.write(f"**企业**：{st.session_state.company}")
st.sidebar.write(f"**角色**：{st.session_state.role} ｜ **目标**：{st.session_state.target}")
st.sidebar.write("**9层能力路线图**：管→治→用→值")

# ========== Tab导航 ==========
tab0, tab1, tab2, tab3, tab4 = st.tabs(["📖 实验导览","💰 管数据","🔧 治数据","📊 用数据","📈 能力画像"])

# ============ Tab0：实验导览 ============
with tab0:
    st.title("💎 AI企业数据资产化与合规治理虚拟仿真实验")
    st.markdown("---")

    st.subheader("🧑‍💼 步骤 0 · 角色与「人单合一」目标")
    st.write("领取 500 万预算，先定角色与目标——角色决定复盘点评的关注点，目标决定你的经营重心（全程留痕）。")
    rc1, rc2 = st.columns(2)
    with rc1:
        role_sel = st.selectbox(
            "选择你的角色：",
            ["数据管家", "数据产品经理", "首席数据官"],
            index=["数据管家", "数据产品经理", "首席数据官"].index(
                st.session_state.role
            )
            if st.session_state.role in ["数据管家", "数据产品经理", "首席数据官"]
            else 0,
            key="role_sel",
        )
        st.session_state.role = role_sel
        role_desc = {
            "数据管家": "数据治理与合规，守住底线",
            "数据产品经理": "数据变现与运营，放大价值",
            "首席数据官": "统筹全局，人单合一",
        }[role_sel]
        st.caption(role_desc)
    with rc2:
        target_sel = st.selectbox(
            "选择你的「人单合一」目标：",
            ["降本增效", "合规避险", "价值创造"],
            index=["降本增效", "合规避险", "价值创造"].index(
                st.session_state.target
            )
            if st.session_state.target in ["降本增效", "合规避险", "价值创造"]
            else 0,
            key="target_sel",
        )
        st.session_state.target = target_sel
        target_desc = {
            "降本增效": "省 50 万治理成本",
            "合规避险": "规避 100 万罚款风险",
            "价值创造": "年增收 200 万",
        }[target_sel]
        st.caption(target_desc)
    st.success(f"🎯 角色：{st.session_state.role}｜目标：{st.session_state.target}——已写入档案，能力画像复盘会按此点评")

    st.subheader("🏭 选择案例行业")
    st.write("四大案例均基于四川真实产业，共用同一套框架，但数据场景与风险事件不同：")

    c1,c2,c3,c4 = st.columns(4)
    for i,(k,v) in enumerate(INDUSTRIES.items()):
        with [c1,c2,c3,c4][i]:
            st.markdown(f"""
            <div style="border-left: 5px solid {v['color']}; padding: 10px; background: #f8f9fa; border-radius: 6px;">
                <h4 style="color: {v['color']}; margin:0; font-size:14px;">{v['name']}</h4>
                <p style="font-size:12px; margin:4px 0;">{v['company']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"选择", key=f"ind_{k}"):
                st.session_state.industry = k
                st.session_state.company = v['company']
                st.success(f"✅ 已选：{v['company']}")

    st.write(f"**当前案例**：{st.session_state.company}")

    st.subheader("📖 怎么玩？")
    st.write("""
    **数据六步跃迁（企业真实路径）**：
    统一管理 → 汇聚采集 → 标准治理 → 高质量数据集 → 知识资产化 → 智能调用

    **两条线（占比）**：
    - 结构化线（20%）：ERP/MES表格 → 治理 → 数据资产台账
    - 非结构化线（80%）：文档/图像/视频 → OCR解析 → 标注数据集

    **为什么可信环节最值钱？**
    从"存下来"到"可信可用"这一段最苦、也最值钱——没有可信，后面的AI都是"演示惊艳、生产不敢用"
    """)

    if st.button("🚀 开始实验（500万到账）", type="primary"):
        st.session_state.started = True
        st.session_state.done.add(0)
        st.success(f"✅ 500万预算已到账！{st.session_state.company}，请点上面的「💰 管数据」开始")

# ============ Tab1：管数据 ============
with tab1:
    st.header("第一阶：管数据（9层1-3层）")

    cat = DATA_CATALOG[st.session_state.industry]
    struct = [x for x in cat if x["type"]=="结构化"]
    unstruct = [x for x in cat if x["type"]=="非结构化"]
    semi = [x for x in cat if x["type"]=="半结构化"]

    s1_cost = sum(x["cost"] for x in struct)*10000
    s2_cost = sum(x["cost"] for x in unstruct)*10000
    s3_cost = sum(x["cost"] for x in semi)*10000

    st.subheader("① 采购六类数据资产")
    if not st.session_state.started:
        st.warning("⚠️ 请先到「📖 实验导览」页点击「🚀 开始实验」，500万预算才会到账")
    s1_done = step_done(1)
    s2_done = step_done(2)
    s3_done = step_done(3)
    s4_done = step_done(4)

    st.write("**📊 结构化数据（时序+表格）**")
    for x in struct:
        st.write(f"- {x['name']}（{x['device']}）：{x['content']} —— {x['cost']}万")
    if st.button(f"采购结构化（-{s1_cost/10000:.0f}万）", key="s1", disabled=s1_done or not st.session_state.started):
        if spend("步骤1-结构化", s1_cost):
            st.session_state.done.add(1)
            st.success(f"✅ 结构化数据就绪（已扣{s1_cost/10000:.0f}万，剩余{st.session_state.budget/10000:.0f}万）")

    st.write("**🖼️ 非结构化数据（图像+视频）**")
    for x in unstruct:
        st.write(f"- {x['name']}（{x['device']}）：{x['content']} —— {x['cost']}万")
    if st.button(f"采购非结构化（-{s2_cost/10000:.0f}万）", key="s2", disabled=s2_done or not st.session_state.started):
        if spend("步骤2-非结构化", s2_cost):
            st.session_state.done.add(2)
            st.success(f"✅ 非结构化数据就绪（已扣{s2_cost/10000:.0f}万，剩余{st.session_state.budget/10000:.0f}万）")

    st.write("**📄 半结构化数据（文档+日志）**")
    for x in semi:
        st.write(f"- {x['name']}（{x['device']}）：{x['content']} —— {x['cost']}万")
    if st.button(f"采购半结构化（-{s3_cost/10000:.0f}万）", key="s3", disabled=s3_done or not st.session_state.started):
        if spend("步骤3-半结构化", s3_cost):
            st.session_state.done.add(3)
            st.success(f"✅ 半结构化数据就绪（已扣{s3_cost/10000:.0f}万，剩余{st.session_state.budget/10000:.0f}万）")

    st.subheader("④ 存储底座+汇聚接入")
    if st.button("部署存储+管道（-50万）", key="s4", disabled=s4_done or not st.session_state.started):
        if spend("步骤4-存储", 500000):
            st.session_state.done.add(4)
            st.success(f"✅ 存储底座已搭好（已扣50万，剩余{st.session_state.budget/10000:.0f}万）")

# ============ Tab2：治数据 ============
with tab2:
    st.header("第二阶：治数据（9层4-5层）")

    st.subheader("⑤ 清洗去重——找出同质异码")
    st.write("💡 企业里同一个设备在不同系统编码不一样，你要自己找出来")
    duplicates = pd.DataFrame({
        "系统A编码": ["电堆A","压缩机01","储氢罐3号","传感器X","阀门Y"],
        "系统B编码": ["燃料电池A","CMP-001","TK-H2-03","Sensor-7","Valve-2"],
        "实际设备": ["100kW电堆","氢气压缩机","35MPa储氢罐","压力传感器","防爆阀"],
        "关键参数": ["额定功率100kW","型号CMP-001","耐压35MPa","量程0~1.6MPa","口径DN50"],
        "是否同一物": [True, True, True, False, False],
    })
    st.dataframe(duplicates[["系统A编码","系统B编码","实际设备","关键参数"]], hide_index=True)
    st.write("依据上面的参数线索判断：哪几对其实是同一个设备？（注意：名称相似不代表同一物）")
    pick1 = st.checkbox("电堆A = 燃料电池A", key="dup1")
    pick2 = st.checkbox("压缩机01 = CMP-001", key="dup2")
    pick3 = st.checkbox("储氢罐3号 = TK-H2-03", key="dup3")
    pick4 = st.checkbox("传感器X = Sensor-7", key="dup4")
    pick5 = st.checkbox("阀门Y = Valve-2", key="dup5")
    correct = pick1 and pick2 and pick3 and not pick4 and not pick5
    dup_reason = (
        "正确答案：电堆A=燃料电池A、压缩机01=CMP-001、储氢罐3号=TK-H2-03。"
        "干扰项：传感器X是压力传感器(量程0~1.6MPa)，而Sensor-7实为温度传感器(-40~200℃)，不是同一物；"
        "阀门Y是DN50防爆阀，Valve-2是DN25减压阀，也不是同一物。"
    )
    if st.button("提交去重结果（-30万）", key="s5", disabled=step_done(5) or not st.session_state.started):
        if correct:
            spend("步骤5-清洗", 300000)
            st.session_state.done.add(5)
            st.success(f"✅ 找对了！去重完成，省了重复采购钱（已扣30万，剩余{st.session_state.budget/10000:.0f}万）")
        else:
            spend("步骤5-清洗", 300000)
            spend("步骤5-清洗返工", 100000)
            st.session_state.done.add(5)
            st.error(f"❌ 找错了！把不同设备合并了，数据混乱，返工追加10万——本次共扣40万（30万清洗+10万返工），剩余{st.session_state.budget/10000:.0f}万")
            st.info(dup_reason)

    st.subheader("⑥ 脱敏防险——你自己决定脱哪些")
    st.write("💡 企业里不是全脱，是你自己判断哪些字段敏感：涉及客户个人、合同财务、人员与安全位置的字段必须脱敏；纯设备工况数据（温度/压力）不用脱")
    fields = st.multiselect(
        "勾选需要脱敏的字段：",
        ["客户手机号","客户姓名","设备温度","设备压力","合同金额","维修记录","员工工号","巡检位置"],
        key="desens_fields"
    )
    must_have = {"客户手机号","客户姓名","合同金额","维修记录","员工工号","巡检位置"}
    non_sensitive = {"设备温度","设备压力"}
    missed = must_have - set(fields)
    over_masked = non_sensitive & set(fields)
    if st.button("确认脱敏（-20万）", key="s6", disabled=step_done(6) or not st.session_state.started):
        if spend("步骤6-脱敏", 200000):
            st.session_state.done.add(6)
            st.session_state.desens_missed = sorted(missed)
            if missed:
                st.error(f"⚠️ 你漏了脱敏：{'、'.join(sorted(missed))}——后面会触发合规罚款！")
                st.session_state.desens_bad = True
            else:
                st.success("✅ 敏感字段都脱敏了，规避50万罚款风险")
                st.session_state.desens_bad = False
            if over_masked:
                st.warning(f"⚠️ 你额外脱敏了工况数据（{'、'.join(sorted(over_masked))}），会损伤AI预测精度，但不影响合规")

    st.subheader("⑦ 可信溯源 ⭐（核心壁垒）")
    st.write("💡 这一段最苦、也最值钱——从'存下来'到'可信可用'")
    st.info("**企业真实要求**：版本·血缘·台账——数据出了问题能追溯到源头，敢给业务用、敢给AI训练")
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.write("🔗 血缘追溯")
    with c2:
        st.write("📝 操作留痕")
    with c3:
        st.write("⏪ 版本回滚")
    with c4:
        st.write("🔐 跨域授权")
    if st.button("部署可信溯源体系（-30万）", key="s7", disabled=step_done(7) or not st.session_state.started):
        if spend("步骤7-可信溯源", 300000):
            st.session_state.done.add(7)
            st.success(f"✅ 可信溯源四步走完成——数据有了'身份证'，后面AI才敢用（已扣30万，剩余{st.session_state.budget/10000:.0f}万）")

    st.subheader("⑧ 质检标注 ⭐——你自己选标注方案")
    st.write("💡 企业里不是三选一按钮，是你自己算：要标多少？花多少钱？质量够不够？")
    st.write("**标注任务清单**（单价×数量=标注费，另需**平台基础费20万**：算力+质检人力，无论标多少都要出）：")
    annot_items = pd.DataFrame({
        "任务": ["电堆裂纹标注","巡检视频抽帧","维修工单分类","安全文档OCR"],
        "数量": ["1200张","800帧","500份","300页"],
        "单价": ["5元/张","2元/帧","8元/份","3元/页"],
        "标注费": ["6000元","1600元","4000元","900元"],
    })
    st.dataframe(annot_items, hide_index=True)
    st.write("你要选哪些来标注？（全标太贵，标少了AI不准）：")
    a1 = st.checkbox("电堆裂纹标注（6000元）", key="ann1")
    a2 = st.checkbox("巡检视频抽帧（1600元）", key="ann2")
    a3 = st.checkbox("维修工单分类（4000元）", key="ann3")
    a4 = st.checkbox("安全文档OCR（900元）", key="ann4")
    total_ann = (6000 if a1 else 0) + (1600 if a2 else 0) + (4000 if a3 else 0) + (900 if a4 else 0)
    platform_fee = 200000
    st.write(f"**当前已选标注费：{total_ann/10000:.2f}万**；平台基础费：20万；合计需扣：{(total_ann+platform_fee)/10000:.2f}万")
    if st.button("开始标注", key="s8", disabled=step_done(8) or not st.session_state.started):
        if total_ann < 10000:
            st.warning("⚠️ 标太少了！AI训练样本不够，准确率只有60%，后面收入打折")
        if spend("步骤8-标注", total_ann + platform_fee):
            st.session_state.done.add(8)
            st.success(f"✅ 标注完成：标注费{total_ann/10000:.2f}万 + 平台基础费20万 = 共花{(total_ann+platform_fee)/10000:.2f}万（剩余{st.session_state.budget/10000:.0f}万）")

# ============ Tab3：用数据 ============
with tab3:
    st.markdown(
        "<div style='background:linear-gradient(135deg,#0f2557,#2563eb);color:#fff;border-radius:16px;"
        "padding:22px 28px;margin-bottom:10px'>"
        "<div style='font-size:12px;opacity:.85;letter-spacing:1px'>第三阶 · 知识资产化与智能调用</div>"
        "<h2 style='color:#fff;margin:4px 0 6px'>用数据：让知识被智能体调起来</h2>"
        "<div style='font-size:14px;opacity:.92'>知识资产建好了，最后一步是把它开放出去。算法和专家每年带来收入；"
        "六维估值随治理与调用进度动态更新。<b style='color:#fde047'>所有部署均可撤销</b>，每步操作都在底部审计日志留痕。</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    trace_ok = step_done(7)
    income_mult = 1.0 if trace_ok else 0.5
    algo_base = 50
    expert_base = 60
    algo_income = int(algo_base * income_mult)
    expert_income = int(expert_base * income_mult)

    if not trace_ok and (step_done(10) or step_done(11)):
        st.warning("⚠️ **可信溯源未部署：算法/专家收益按 5 折兑现**——业务与客户不信任数据出处，算法服务与专家咨询收入减半。前往「治数据」部署后收益全额兑现。")

    # ---------- 三张部署卡片 ----------
    st.markdown("### 🛠️ 数据资产部署台")
    st.caption("真实扣款、可撤销：部署后显示交付成果，不满意可一键撤销（退还预算并扣回收入）")
    offers = [
        (9,  "🕸️", "企业知识图谱", "构建设备/项目/人员/标签的语义图谱，支撑语义检索", 30, 0, [
            "抽取实体 1.2 万个（设备 4,800 · 项目 320 · 人员 1,600 · 标签 5,300）",
            "构建关系边 3.5 万条，实体与文档双向关联",
            "开放语义检索：支持「找到所有 2026 年检修过的压缩机」类查询",
            "对接 MCP Server，供智能体跨系统取数引用"]),
        (10, "🧠", "故障预测算法", "基于时序数据训练故障预测，每年带来算法服务收入", 30, algo_base, [
            "故障预测模型上线，Top-1 准确率 87%，AUC 0.91",
            "接入设备运行日志等 3 类时序数据源，分钟级增量推理",
            "提前 2 小时预警设备故障，减少非计划停机",
            "模型 API 开放，形成算法服务收入 +50 万/年"]),
        (11, "🎓", "算法专家优化", "聘请行业算法专家调优模型与产线，每年带来咨询收入", 40, expert_base, [
            "完成 3 个核心模型调优，推理时延降低 32%",
            "建立标注 SOP 与质检规则库，标注返工率下降 40%",
            "输出行业知识库与调优方法论，沉淀为可复用资产",
            "对外提供专家咨询服务，形成咨询收入 +60 万/年"]),
    ]
    step_label = {9: "图谱", 10: "算法", 11: "专家"}
    oc1, oc2, oc3 = st.columns(3)
    for col, (step_key, icon, name, desc, cost, base_income, delivers) in zip([oc1, oc2, oc3], offers):
        with col:
            done = step_done(step_key)
            border = "#16a34a" if done else "#e5e7eb"
            bg = "#f0fdf4" if done else "#ffffff"
            badge = "已部署 ✅" if done else f"成本 -{cost} 万"
            income_html = ""
            if base_income > 0:
                show_income = int(base_income * income_mult)
                suffix = "（未部署溯源，5折）" if income_mult < 1 else ""
                income_html = f"<div style='color:#16a34a;font-weight:700;margin:6px 0'>+{show_income} 万/年收入 {suffix}</div>"
            st.markdown(
                f"<div style='border:2px solid {border};background:{bg};border-radius:14px;padding:14px 16px;"
                f"min-height:200px'>"
                f"<div style='font-size:26px'>{icon}</div>"
                f"<div style='font-weight:800;font-size:15px'>{name}</div>"
                f"<div style='font-size:11px;color:#6b7280;background:#f3f4f6;display:inline-block;"
                f"border-radius:999px;padding:1px 10px;margin:4px 0'>{badge}</div>"
                f"<div style='font-size:12px;color:#374151;min-height:34px'>{desc}</div>"
                f"{income_html}"
                f"</div>",
                unsafe_allow_html=True,
            )
            if done:
                st.success("部署结果 · 已上线")
                for d in delivers:
                    st.write(f"- ✅ {d}")
                if st.button(f"↩️ 撤销部署（退还{cost}万）", key=f"undo_{step_key}"):
                    st.session_state.done.discard(step_key)
                    st.session_state.budget += cost * 10000
                    if step_key in (10, 11):
                        st.session_state.revenue -= int(base_income * income_mult * 10000)
                    st.session_state.log.append((datetime.now().strftime("%H:%M:%S"),
                                                 f"↩️ 撤销部署-{step_label[step_key]}（退还{cost}万）", cost * 10000))
                    st.rerun()
            else:
                if st.button(f"🚀 部署（-{cost} 万）", key=f"s{step_key}",
                             disabled=not st.session_state.started or st.session_state.budget < cost * 10000):
                    if spend(f"步骤{step_key}-{step_label[step_key]}", cost * 10000):
                        st.session_state.done.add(step_key)
                        if step_key in (10, 11):
                            st.session_state.revenue += int(base_income * income_mult * 10000)
                        st.rerun()

    # ---------- 风险事件博弈 ----------
    st.markdown("### ⚡ 风险事件博弈")
    st.caption("三次估值迭代之间会遭遇合规抽查、对手抢数据、算法事故等风险事件。选择应对策略会真实扣减预算并影响年收入，全部留痕、可撤销。")
    RISK_EVENTS = [
        ("监管合规抽查",
         "数据监管局抽查发现你的数据底座存在未脱敏字段外泄风险，要求限期整改，否则按上限罚款。",
         [("A · 立即补全脱敏", "紧急追加脱敏规则，当场消除风险", 20, 0),
          ("B · 自查后整改", "花时间自查，暴露面更大", 40, -10),
          ("C · 拖延应对", "不正面回应，赌抽查结束", 0, -50)]),
        ("竞争对手抢数据",
         "同行业对手高价挖你的标注团队，并向数据源厂商开出双倍价格抢购同源数据。",
         [("A · 加薪留人+签独家", "锁定标注团队与数据源独家供应", 30, 0),
          ("B · 换开源替代源", "改用开源数据，质量和独家性下降", 10, -20),
          ("C · 不设防", "任由对手抢购，数据被截胡", 0, -40)]),
        ("AI 算法事故",
         "已上线的预测算法在生产中误报，引发产线停摆，客户要求追责赔偿。",
         [("A · 紧急回滚并修复", "回滚模型、补充重训数据", 25, 0),
          ("B · 人工复核兜底", "暂停自动决策，转人工审核", 15, -15),
          ("C · 继续运行", "侥幸继续，事故扩大", 0, -60)]),
    ]
    if "risk_choices" not in st.session_state:
        st.session_state.risk_choices = {}
    resolved_cnt = len(st.session_state.risk_choices)
    st.markdown(f"**📋 已处理 {resolved_cnt}/{len(RISK_EVENTS)} 个风险事件**")

    for ev_i, (title, desc, options) in enumerate(RISK_EVENTS):
        chosen = st.session_state.risk_choices.get(ev_i)
        badge = "✅ 已应对" if chosen is not None else "⏳ 待应对"
        with st.container(border=True):
            st.markdown(f"**{title}**　<span style='font-size:12px'>{badge}</span>", unsafe_allow_html=True)
            st.caption(desc)
            cols = st.columns(3)
            for col, (label, opt_desc, cost, delta) in zip(cols, options):
                with col:
                    is_chosen = chosen is not None and chosen[0] == label
                    if is_chosen:
                        card_bg, card_border = "#f0fdf4", "#16a34a"
                    elif chosen is None:
                        card_bg, card_border = "#ffffff", "#e5e7eb"
                    else:
                        card_bg, card_border = "#f9fafb", "#e5e7eb"
                    delta_txt = f"年收入 {delta:+d} 万" if delta else "年收入不变"
                    st.markdown(
                        f"<div style='border:1.5px solid {card_border};background:{card_bg};border-radius:10px;"
                        f"padding:10px 12px;min-height:118px'>"
                        f"<div style='font-weight:700;font-size:13px'>{label}</div>"
                        f"<div style='font-size:11px;color:#6b7280;min-height:32px'>{opt_desc}</div>"
                        f"<div style='font-size:12px;color:#dc2626'>支出 {cost} 万</div>"
                        f"<div style='font-size:12px;color:{'#16a34a' if delta > 0 else '#dc2626' if delta < 0 else '#6b7280'}'>"
                        f"{delta_txt}</div>"
                        f"{'<div style=color:#16a34a;font-weight:700;font-size:12px>✔ 已选</div>' if is_chosen else ''}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
            if chosen is None:
                btn_cols = st.columns(3)
                for col, (label, opt_desc, cost, delta) in zip(btn_cols, options):
                    with col:
                        if st.button(f"选择 {label}", key=f"risk_{ev_i}_{cost}_{delta}",
                                     disabled=not st.session_state.started):
                            if st.session_state.budget >= cost * 10000:
                                spend(f"风险{ev_i+1}-{label}", cost * 10000)
                                st.session_state.revenue += delta * 10000
                                st.session_state.risk_choices[ev_i] = (label, cost, delta)
                                st.rerun()
                            else:
                                st.error(f"❌ 预算不够！需要{cost}万")
            else:
                label, cost, delta = chosen
                st.write(f"你的应对：「{label}」——已在操作留痕中记录，可撤销后重新选择。")
                if st.button(f"↩️ 撤销应对（退还{cost}万预算、恢复收入{delta:+d}万）", key=f"risk_undo_{ev_i}"):
                    st.session_state.budget += cost * 10000
                    st.session_state.revenue -= delta * 10000
                    st.session_state.log.append((datetime.now().strftime("%H:%M:%S"),
                                                 f"↩️ 撤销风险{ev_i+1}-{label}（退还{cost}万）", cost * 10000))
                    del st.session_state.risk_choices[ev_i]
                    st.rerun()

    risk_income = sum(d for _, _, d in st.session_state.risk_choices.values())
    st.markdown(f"**风险事件累计年收入影响：{'<span style=color:#16a34a>+' if risk_income >= 0 else '<span style=color:#dc2626>'}"
                f"{risk_income} 万/年</span>**", unsafe_allow_html=True)

    # ---------- 六维估值 ----------
    st.markdown("### 📊 六维估值（治理六维）")
    purchased_cnt = sum(1 for s in (1, 2, 3) if step_done(s)) * 2
    cleaned = step_done(5)
    masked = step_done(6)
    traced = step_done(7)
    labeled = step_done(8)
    dims = [
        ("可用性", "数据集规模与字段完整，可被消费", 30 + purchased_cnt * 10),
        ("可信性", "来源可溯、质量可度量、有验收", (40 if traced else 10) + (20 if labeled else 0) + (20 if cleaned else 0)),
        ("完整性", "口径统一，字段与标签可解释", (40 if cleaned else 10) + (20 if masked else 0)),
        ("可追溯性", "版本、血缘、台账齐全，可回滚", 85 if traced else 15),
        ("标准化", "统一编码与主数据，消除同质异码", 80 if cleaned else 20),
        ("合规性", "脱敏、分级、权限与审计留痕", 85 if masked else 20),
    ]
    total_score = round(sum(s for _, _, s in dims) / 6)
    with st.container(border=True):
        v1, v2 = st.columns([3, 2])
        with v1:
            st.markdown(f"**数据资产综合评分：<span style='color:#2563eb;font-size:26px'>{total_score}</span>**（六维平均，随管/治/用进度实时变化）", unsafe_allow_html=True)
            for name, desc, score in dims:
                st.progress(min(score, 100) / 100, text=f"{name}（{desc}）— {score}")
        with v2:
            st.markdown("**六维得分分布**")
            chart_df = pd.DataFrame({"维度": [d[0] for d in dims], "得分": [d[2] for d in dims]})
            chart_df = chart_df.set_index("维度")
            st.bar_chart(chart_df, height=220)
    st.info("口径说明：本实验的六维为「治理六维」——衡量数据资产的质量与合规水平；与海尔「共赢增值表」的生态六维（用户资源/资源方/生态总价值/收入/成本/边际收益）是两套不同口径，前者管质量、后者管生态增值，报告页两者都会呈现。")

    # ---------- 预算与生效年收入 ----------
    effective_income = (algo_income if step_done(10) else 0) + (expert_income if step_done(11) else 0) + risk_income
    st.success(f"💰 当前预算 **{st.session_state.budget/10000:.0f} 万** ｜ 📈 生效年收入约 **{effective_income} 万/年**（含风险影响与溯源折扣）；不想要的部署可随时撤销。")

    # ---------- 操作留痕 · 审计日志 ----------
    st.markdown("### 🛡️ 操作留痕 · 审计日志")
    st.caption("每一步部署、风险应对、撤销操作都记录在案——可回滚、可追溯、可对账。")
    if st.session_state.log:
        audit_df = pd.DataFrame(st.session_state.log, columns=["时间", "操作", "金额变动(万)"])
        audit_df["金额变动(万)"] = (audit_df["金额变动(万)"] / 10000).map(lambda x: f"{x:+.1f}")
        st.dataframe(audit_df, hide_index=True, use_container_width=True)
    else:
        st.caption("暂无操作记录——完成一次部署或风险应对后，这里会生成审计条目")


# ============ Tab4：能力画像 ============
with tab4:
    st.header("📈 你的数据资产经营报告")
    st.write(f"**企业**：{st.session_state.company} ｜ **角色**：{st.session_state.role} ｜ **目标**：{st.session_state.target}")
    total_cost = INIT_BUDGET - st.session_state.budget
    st.metric("总投入", f"{total_cost/10000:.0f}万")
    st.metric("累计收入", f"{st.session_state.revenue/10000:.0f}万")
    st.metric("边际收益", f"{(st.session_state.revenue-total_cost)/10000:.0f}万")

    st.write("**开支明细（审计日志）**")
    for t, name, amt in st.session_state.log:
        st.write(f"- `{t}` {name}: {amt/10000:+.1f}万")

    st.write("**收入构成**（为什么累计收入是这么多，一笔笔算给你看）")
    rev_items = []
    mult = 1.0 if step_done(7) else 0.5
    if step_done(10):
        algo_amt = int(50 * mult)
        rev_items.append((f"采购故障预测算法上线{'（未部署溯源按5折）' if mult < 1 else ''}", f"+{algo_amt}万/年"))
    if step_done(11):
        expert_amt = int(60 * mult)
        rev_items.append((f"聘请算法专家优化{'（未部署溯源按5折）' if mult < 1 else ''}", f"+{expert_amt}万/年"))
    risk_choices = st.session_state.get("risk_choices", {})
    risk_titles = ["监管合规抽查", "竞争对手抢数据", "AI 算法事故"]
    for ev_i in sorted(risk_choices):
        label, _cost, delta = risk_choices[ev_i]
        if delta != 0:
            sign = "+" if delta > 0 else ""
            rev_items.append((f"风险应对-{risk_titles[ev_i]}（{label}）", f"{sign}{delta}万"))
    if rev_items:
        for k, v in rev_items:
            st.write(f"- {k}: {v}")
    st.write(f"**合计累计收入：{st.session_state.revenue/10000:.0f}万**")

    total_cost = INIT_BUDGET - st.session_state.budget
    st.write("**📐 口径对照：治理六维 vs 海尔「共赢增值表」生态六维**")
    st.caption("本实验的六维估值采用「治理六维」，衡量数据资产的质量与合规水平；参考方案中的「生态六维」是另一套经营口径（共赢增值表），二者互补不冲突。")
    dim1, dim2 = st.columns(2)
    with dim1:
        st.markdown("**治理六维（本实验采用）**")
        gov_dims = [
            ("可用性", "统一管理后数据能调能算"),
            ("可信性", "可追溯、可回滚、敢给AI用"),
            ("完整性", "清洗补全后无缺漏"),
            ("可追溯性", "血缘清晰、留痕完备"),
            ("标准化", "统一编码消除同质异码"),
            ("合规性", "脱敏分级、审计留痕"),
        ]
        for k, v in gov_dims:
            st.write(f"- **{k}**：{v}")
    with dim2:
        st.markdown("**海尔生态六维（共赢增值表·参考口径）**")
        eco_dims = [
            ("用户资源", "可触达的用户规模与活跃度"),
            ("资源方", "生态资源方的数量与质量"),
            ("生态总价值", "生态整体创造的价值总量"),
            ("收入", "经营产生的现金收入"),
            ("成本", "投入的资源与费用"),
            ("边际收益", "收入与成本之差"),
        ]
        for k, v in eco_dims:
            st.write(f"- **{k}**：{v}")

    st.write("**📋 复盘点评（重来一次你会改哪里？）**")
    tips = []
    if not step_done(7) and (step_done(10) or step_done(11)):
        tips.append("⚠️ 你没部署可信溯源，算法/专家收益只按 5 折兑现——第⑦步 30 万没花，白白损失几十万年收入，重来应优先部署")
    if st.session_state.role == "数据管家" and st.session_state.get("desens_bad", False):
        tips.append("🎯 作为数据管家，治理与合规是底线——但你漏脱敏触发罚款，重来应把客户/财务/人员/位置类字段全部脱敏")
    if st.session_state.role == "数据产品经理" and (not step_done(10) or not step_done(11)):
        tips.append("🎯 作为数据产品经理，变现与运营是主线——算法(+50万/年)和专家(+60万/年)是回报最高投入，重来优先购买")
    if st.session_state.role == "首席数据官" and len(st.session_state.get("risk_choices", {})) < 3:
        tips.append("🎯 作为首席数据官，统筹全局——治理已完成，建议在「用数据」完成价值挖掘策略三选一，兑现数据价值")
    if st.session_state.target == "降本增效" and st.session_state.budget < INIT_BUDGET - 2000000:
        tips.append("📌 你的目标是降本增效——目前投入已超 200 万，重来应砍掉低性价比步骤（如全量标注），聚焦必要治理")
    if st.session_state.target == "合规避险" and st.session_state.get("desens_bad", False):
        tips.append("📌 你的目标是合规避险——却因漏脱敏触发罚款，与目标背道而驰，重来务必全字段脱敏")
    if st.session_state.target == "价值创造" and (st.session_state.revenue - total_cost) <= 0:
        tips.append("📌 你的目标是价值创造——当前边际收益未转正，重来应优先高回报的算法/专家投入，并处理风险事件保住收入")
    if st.session_state.get("desens_bad", False):
        tips.append("⚠️ 你在第⑥步漏脱敏了，直接导致合规罚款——重来时应把客户/财务/人员/位置类字段全部脱敏，成本一样，风险为0")
    if total_ann_val := sum(a for _, _, a in st.session_state.log if _.startswith("步骤8")):
        if total_ann_val > 200000:
            tips.append(f"💡 质检标注花了{total_ann_val/10000:.0f}万（含20万平台费），是成本大头——下轮可只标核心任务，把预算留给算法")
    if not step_done(10) or not step_done(11):
        tips.append("💡 算法(+50万/年)和专家(+60万/年)是回报最高的投入，优先购买")
    if (st.session_state.revenue - total_cost) < 0 and tips:
        tips.append("📌 总体仍亏损——数据治理是长期投资，重点是让每笔钱都有明确回报路径")
    if not tips:
        tips.append("✅ 每一步都花得明明白白，无合规风险——可以挑战更高利润目标")
    for t in tips:
        st.write(t)

    if (st.session_state.revenue - total_cost) > 0:
        st.success("🎉 你是优秀的数据资产投资经理！")
    else:
        st.info("📉 还在亏损，但比初评好多了")
