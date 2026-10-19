# 打印三轮估值明细（数值合理性检查）
import sys, json
sys.path.insert(0, r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab")
from streamlit.testing.v1 import AppTest

def click_btn(at, txt):
    for b in at.button:
        if txt in (b.label or ""):
            b.click(); return True
    return False

def step(at, btn_text):
    click_btn(at, btn_text); at.run(timeout=30)
    click_btn(at, "下一步"); at.run(timeout=30)

def find_radio(at, label_prefix):
    for r in at.radio:
        if r.label and label_prefix in r.label:
            return r
    return None

def find_text(at, label_prefix):
    for t in at.text_input:
        if t.label and label_prefix in t.label:
            return t
    return None

def find_area(at, label_prefix):
    for a in at.text_area:
        if a.label and label_prefix in a.label:
            return a
    return None

def run_round(at):
    step(at, "锁定组阁")
    step(at, "确认盘点完成")
    step(at, "锁定三年战略")
    step(at, "确认编制预算")
    step(at, "确认数据源")
    step(at, "确认合同条款")
    step(at, "确认存储方案")
    step(at, "完成确权登记并签字")
    step(at, "确认标准投入")
    step(at, "确认稽核投入")
    rq = find_radio(at, "Q1：脱敏")
    if rq:
        rq.set_value(rq.options[1]); at.run(timeout=30)
    step(at, "确认脱敏方案")
    step(at, "确认上架")
    emp_r = find_area(at, "为什么选这个方案")
    if emp_r:
        emp_r.set_value("B 方案均衡"); at.run(timeout=30)
    click_btn(at, "锁定 B 方案"); at.run(timeout=30)
    click_btn(at, "下一步"); at.run(timeout=30)
    step(at, "确认建模投入")
    step(at, "确认推广策略")
    step(at, "确认效果度量")
    step(at, "确认产品化")
    step(at, "确认定价")
    pa = find_text(at, "甲方（数据提供方）")
    pb = find_text(at, "乙方（数据购买方）")
    pu = find_text(at, "用途限制")
    if pa: pa.set_value("蜀能智造实验组")
    if pb: pb.set_value("蜀光智算买方")
    if pu: pu.set_value("行业数据分析与预测报告")
    at.run(timeout=30)
    step(at, "签署合同")
    step(at, "确认 SLA")
    step(at, "投放激励方案")
    step(at, "确认出表方式")
    click_btn(at, "触发估值引擎"); at.run(timeout=30)
    click_btn(at, "下一步"); at.run(timeout=30)
    click_btn(at, "提交答辩记录"); at.run(timeout=30)
    click_btn(at, "完成本轮（结算锁定）"); at.run(timeout=30)

at = AppTest.from_file(r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab\main_app.py", default_timeout=30)
at.run(timeout=30)
at.button[0].click(); at.run(timeout=30)
run_round(at)
click_btn(at, "开放第 2 轮（开始新决策）"); at.run(timeout=30)
run_round(at)
click_btn(at, "开放第 3 轮（开始新决策）"); at.run(timeout=30)
run_round(at)

# 从 session_state 拿估值明细
ss = at.session_state
try:
    full = ss.to_dict()
except Exception as e:
    full = {"ERR": str(e)}
lines = []
lines.append("SS_KEYS:" + ",".join(sorted(full.keys())))
vh = full.get("val_history", [])
lines.append("VH_LEN:" + str(len(vh)))
lines.append("ROUND|V|PV|Q|C|H|D|T|EMP|EVENTS|DROP")
for v in vh:
    lines.append("|".join(str(x) for x in [
        v.get("round"), v.get("v"), v.get("pv"), v.get("q"), v.get("c"),
        v.get("h"), v.get("d"), v.get("t_score"), v.get("empower"),
        ",".join(v.get("events", [])), ",".join(v.get("drop_paths", []))
    ]))
lines.append("TEAM:" + (json.dumps(full.get("team", {}), ensure_ascii=False)))
if vh:
    lines.append("T_DETAIL:" + json.dumps(vh[-1].get("t_detail", {}), ensure_ascii=False))
    lines.append("H_DETAIL:" + json.dumps(vh[-1].get("h_detail", {}), ensure_ascii=False))
    lines.append("Q_DETAIL:" + json.dumps(vh[-1].get("q_detail", {}), ensure_ascii=False))
    lines.append("DECI_SRC:" + json.dumps(full.get("decisions", {}).get("source"), ensure_ascii=False))
    lines.append("DECI_TB:" + str(full.get("decisions", {}).get("source_tb")))
    lines.append("DECI_SAL:" + str(full.get("decisions", {}).get("team_salary")))
    lines.append("DECI_STO:" + json.dumps(full.get("decisions", {}).get("storage"), ensure_ascii=False))
    lines.append("DECI_EMP:" + json.dumps(full.get("decisions", {}).get("empower"), ensure_ascii=False))
lines.append("BUDGET_R3:" + str(full.get("budget", "NA")))
lines.append("CONTRACT:" + (json.dumps(full.get("decisions", {}).get("contract_filled", {}), ensure_ascii=False)))
open(r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab\val_detail.txt", "w", encoding="utf-8").write("\n".join(lines))
print("DONE", len(vh))
