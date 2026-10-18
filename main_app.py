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
    st.session_state.log.append((name, amt))
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
    st.header("第三阶：用数据（9层6-9层）")

    st.subheader("⑨ 建知识图谱")
    if st.button("构建知识图谱（-30万）", key="s9", disabled=step_done(9) or not st.session_state.started):
        if spend("步骤9-图谱", 300000):
            st.session_state.done.add(9)
            st.success(f"✅ 知识图谱已建（已扣30万，剩余{st.session_state.budget/10000:.0f}万）")

    st.subheader("⑩ 买算法")
    trace_ok = step_done(7)
    income_mult = 1.0 if trace_ok else 0.5
    if not trace_ok:
        st.warning("⚠️ 未部署可信溯源：算法与专家收益按 **5 折** 兑现——可信是收益生效的前提（去「治数据」部署第⑦步）")
    algo_income = int(500000 * income_mult)
    expert_income = int(600000 * income_mult)
    if st.button("采购故障预测算法（-30万）", key="s10", disabled=step_done(10) or not st.session_state.started):
        if spend("步骤10-算法", 300000):
            st.session_state.done.add(10)
            st.session_state.revenue += algo_income
            note = f"（未部署溯源按5折：+{algo_income/10000:.0f}万/年）" if income_mult < 1 else ""
            st.success(f"✅ 算法上线，年省{algo_income/10000:.0f}万{note}（已扣30万，剩余{st.session_state.budget/10000:.0f}万）")

    st.subheader("⑪ 请专家优化")
    if st.button("聘请算法专家（-40万）", key="s11", disabled=step_done(11) or not st.session_state.started):
        if spend("步骤11-专家", 400000):
            st.session_state.done.add(11)
            st.session_state.revenue += expert_income
            note = f"（未部署溯源按5折：+{expert_income/10000:.0f}万/年）" if income_mult < 1 else ""
            st.success(f"✅ 专家到位，年省再增{expert_income/10000:.0f}万{note}（已扣40万，剩余{st.session_state.budget/10000:.0f}万）")

    # 步骤12：六维估值
    st.subheader("⑫ 六维估值 ⭐")

    if "s12_phase" not in st.session_state:
        st.session_state.s12_phase = "initial"
    if "s12_e1" not in st.session_state:
        st.session_state.s12_e1 = None
    if "s12_e2" not in st.session_state:
        st.session_state.s12_e2 = None
    if "s12_e3" not in st.session_state:
        st.session_state.s12_e3 = None
    if "s12_strategy" not in st.session_state:
        st.session_state.s12_strategy = None

    if st.session_state.s12_phase == "initial":
        total_cost = (INIT_BUDGET - st.session_state.budget)
        marginal = st.session_state.revenue - total_cost
        st.dataframe(pd.DataFrame({
            "六维": ["用户资源","资源方","生态总价值","收入","成本","边际收益"],
            "初评值": ["60","45","180",
                      f"{st.session_state.revenue/10000:.0f}万", f"{total_cost/10000:.0f}万",
                      f"{marginal/10000:.0f}万"],
        }), hide_index=True)
        st.warning(f"📉 初评边际收益{marginal/10000:.0f}万——光花钱不赚钱！")
        if st.button("确认初评，进入调整", key="s12a"):
            st.session_state.val_history.append(("初评", total_cost, st.session_state.revenue, marginal))
            st.session_state.s12_phase = "adjust"
            st.rerun()

    elif st.session_state.s12_phase == "adjust":
        if st.session_state.s12_e1 is None:
            desens_bad = st.session_state.get("desens_bad", False)
            desens_missed = st.session_state.get("desens_missed", [])
            if desens_bad:
                st.write("**🎲 风险事件1：合规罚款**")
                st.error(f"⚠️ 监管抽查发现数据脱敏不彻底！——就是你在第⑥步漏脱敏了：{'、'.join(desens_missed) or '敏感字段'}，被监管部门抽查出来")
                cA,cB,cC = st.columns(3)
                with cA:
                    if st.button("A 全面整改(-20万，罚款10万)", key="e1a"):
                        spend("合规整改", 200000)
                        st.session_state.revenue -= 100000
                        st.session_state.s12_e1 = "A"
                        st.rerun()
                with cB:
                    if st.button("B 硬扛申诉(0万，罚款50万)", key="e1b"):
                        st.session_state.revenue -= 500000
                        st.session_state.s12_e1 = "B"
                        st.rerun()
                with cC:
                    if st.button("C 部分整改(-10万，罚款25万)", key="e1c"):
                        spend("部分整改", 100000)
                        st.session_state.revenue -= 250000
                        st.session_state.s12_e1 = "C"
                        st.rerun()
            else:
                st.write("**🎲 监管抽查**")
                st.success("✅ 监管抽查未发现合规问题——第⑥步脱敏做得很完整，罚款风险为0，直接进入下一环节")
                st.session_state.s12_e1 = "OK"
                st.rerun()
        elif st.session_state.s12_e2 is None:
            st.success(f"✅ 合规事件已处理")
            st.write("**🎲 风险事件2：竞争对手抢数据**")
            st.error("⚠️ 竞争对手挖角数据分析师！")
            cA,cB,cC = st.columns(3)
            with cA:
                if st.button("A 法律维权(-15万，追回数据)", key="e2a"):
                    spend("法律维权", 150000)
                    st.session_state.s12_e2 = "A"
                    st.rerun()
            with cB:
                if st.button("B 技术加固(-20万，阻止泄露)", key="e2b"):
                    spend("技术加固", 200000)
                    st.session_state.s12_e2 = "B"
                    st.rerun()
            with cC:
                if st.button("C 被动接受(0万，用户流失)", key="e2c"):
                    st.session_state.revenue -= 100000
                    st.session_state.s12_e2 = "C"
                    st.rerun()
        elif st.session_state.s12_e3 is None:
            st.success("✅ 两个风险事件已处理")
            st.write("**🎲 风险事件3：AI 算法事故**")
            st.error("⚠️ 已上线的预测算法在生产中误报，引发产线停摆，客户要求追责赔偿！")
            cA,cB,cC = st.columns(3)
            with cA:
                if st.button("A 紧急回滚并修复(-25万，收入不变)", key="e3a"):
                    spend("AI事故-回滚修复", 250000)
                    st.session_state.s12_e3 = "A"
                    st.rerun()
            with cB:
                if st.button("B 人工复核兜底(-15万，收入-15万)", key="e3b"):
                    spend("AI事故-人工兜底", 150000)
                    st.session_state.revenue -= 150000
                    st.session_state.s12_e3 = "B"
                    st.rerun()
            with cC:
                if st.button("C 继续运行(0万，收入-60万)", key="e3c"):
                    st.session_state.revenue -= 600000
                    st.session_state.s12_e3 = "C"
                    st.rerun()
        else:
            st.success(f"✅ 三个风险事件已处理")
            st.write("**📈 价值挖掘策略三选一**（点击下方按钮选择你的变现策略）")
            cA,cB,cC = st.columns(3)
            with cA:
                if st.button("拓展场景服务(-20万，收入+45万)", key="str1", type="primary"):
                    spend("场景服务", 200000)
                    st.session_state.revenue += 450000
                    st.session_state.s12_strategy = "场景服务"
                    st.session_state.s12_phase = "final"
                    st.rerun()
            with cB:
                if st.button("优化算法变现(-15万，收入+35万)", key="str2", type="primary"):
                    spend("算法优化", 150000)
                    st.session_state.revenue += 350000
                    st.session_state.s12_strategy = "算法优化"
                    st.session_state.s12_phase = "final"
                    st.rerun()
            with cC:
                if st.button("生态伙伴共建(-25万，收入+40万)", key="str3", type="primary"):
                    spend("生态共建", 250000)
                    st.session_state.revenue += 400000
                    st.session_state.s12_strategy = "生态共建"
                    st.session_state.s12_phase = "final"
                    st.rerun()

    elif st.session_state.s12_phase == "final":
        st.success("✅ 估值完成")
        total_cost = (INIT_BUDGET - st.session_state.budget)
        marginal = st.session_state.revenue - total_cost
        st.session_state.val_history.append(("终评", total_cost, st.session_state.revenue, marginal))
        st.session_state.done.add(12)

        cmp_df = pd.DataFrame(st.session_state.val_history, columns=["阶段","成本(万)","收入(万)","边际收益(万)"])
        cmp_df["成本(万)"] = cmp_df["成本(万)"]/10000
        cmp_df["收入(万)"] = cmp_df["收入(万)"]/10000
        cmp_df["边际收益(万)"] = cmp_df["边际收益(万)"]/10000
        st.dataframe(cmp_df, hide_index=True)
        st.metric("最终边际收益", f"{marginal/10000:.0f} 万")

# ============ Tab4：能力画像 ============
with tab4:
    st.header("📈 你的数据资产经营报告")
    st.write(f"**企业**：{st.session_state.company} ｜ **角色**：{st.session_state.role} ｜ **目标**：{st.session_state.target}")
    total_cost = INIT_BUDGET - st.session_state.budget
    st.metric("总投入", f"{total_cost/10000:.0f}万")
    st.metric("累计收入", f"{st.session_state.revenue/10000:.0f}万")
    st.metric("边际收益", f"{(st.session_state.revenue-total_cost)/10000:.0f}万")

    st.write("**开支明细**")
    for name, amt in st.session_state.log:
        st.write(f"- {name}: -{amt/10000:.1f}万")

    st.write("**收入构成**（为什么累计收入是这么多，一笔笔算给你看）")
    rev_items = []
    mult = 1.0 if step_done(7) else 0.5
    if step_done(10):
        algo_amt = int(50 * mult)
        rev_items.append((f"采购故障预测算法上线{'（未部署溯源按5折）' if mult < 1 else ''}", f"+{algo_amt}万/年"))
    if step_done(11):
        expert_amt = int(60 * mult)
        rev_items.append((f"聘请算法专家优化{'（未部署溯源按5折）' if mult < 1 else ''}", f"+{expert_amt}万/年"))
    strat = st.session_state.get("s12_strategy")
    if strat == "场景服务":
        rev_items.append(("拓展场景服务", "+45万"))
    elif strat == "算法优化":
        rev_items.append(("优化算法变现", "+35万"))
    elif strat == "生态共建":
        rev_items.append(("生态伙伴共建", "+40万"))
    e1 = st.session_state.get("s12_e1")
    if e1 == "A":
        rev_items.append(("合规整改罚款", "-10万"))
    elif e1 == "B":
        rev_items.append(("合规硬扛罚款", "-50万"))
    elif e1 == "C":
        rev_items.append(("合规部分整改罚款", "-25万"))
    if st.session_state.get("s12_e2") == "C":
        rev_items.append(("被动接受致用户流失", "-10万"))
    e3 = st.session_state.get("s12_e3")
    if e3 == "B":
        rev_items.append(("AI事故-人工兜底减收", "-15万"))
    elif e3 == "C":
        rev_items.append(("AI事故-继续运行减收", "-60万"))
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
    if st.session_state.role == "首席数据官" and st.session_state.get("s12_strategy") is None:
        tips.append("🎯 作为首席数据官，统筹全局——治理已完成，建议在「用数据」完成价值挖掘策略三选一，兑现数据价值")
    if st.session_state.target == "降本增效" and st.session_state.budget < INIT_BUDGET - 2000000:
        tips.append("📌 你的目标是降本增效——目前投入已超 200 万，重来应砍掉低性价比步骤（如全量标注），聚焦必要治理")
    if st.session_state.target == "合规避险" and st.session_state.get("desens_bad", False):
        tips.append("📌 你的目标是合规避险——却因漏脱敏触发罚款，与目标背道而驰，重来务必全字段脱敏")
    if st.session_state.target == "价值创造" and (st.session_state.revenue - total_cost) <= 0:
        tips.append("📌 你的目标是价值创造——当前边际收益未转正，重来应优先高回报的算法/专家投入，并处理风险事件保住收入")
    if st.session_state.get("desens_bad", False):
        tips.append("⚠️ 你在第⑥步漏脱敏了，直接导致合规罚款——重来时应把客户/财务/人员/位置类字段全部脱敏，成本一样，风险为0")
    if total_ann_val := sum(a for _, a in st.session_state.log if _.startswith("步骤8")):
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
