# v2.0 三轮全流程 AppTest（修正版：提交后点“下一步”推进）
import sys, json
sys.path.insert(0, r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab")
from streamlit.testing.v1 import AppTest

results = []
def rec(tag, at):
    results.append({"tag": tag, "status": "OK" if not at.exception else "EXCEPTION",
                    "exc": (str(at.exception[0].value)[:400] if at.exception else "")})

def sig(at):
    for m in at.markdown:
        v = m.value or ""
        if "轮 · 步骤" in v:
            return v.strip().replace("#", "")[:30]
    return "?"

def click_btn(at, txt):
    for b in at.button:
        if txt in (b.label or ""):
            b.click()
            return True
    return False

def step(at, btn_text, tag):
    """提交当前步 + 点下一步推进"""
    ok = click_btn(at, btn_text)
    at.run(timeout=30)
    rec(tag, at)
    ok2 = click_btn(at, "下一步")
    at.run(timeout=30)
    rec(tag + "_nav", at)
    return ok and ok2

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

def run_round(at, tag):
    step(at, "锁定组阁", tag + "S1")
    step(at, "确认盘点完成", tag + "S2")
    step(at, "锁定三年战略", tag + "S3")
    step(at, "确认编制预算", tag + "S4")
    step(at, "确认数据源", tag + "S5")
    step(at, "确认合同条款", tag + "S6")
    step(at, "确认存储方案", tag + "S7")
    step(at, "完成确权登记并签字", tag + "S8")
    step(at, "确认标准投入", tag + "S9")
    step(at, "确认稽核投入", tag + "S10")
    # S11 脱敏测验
    rq = find_radio(at, "Q1：脱敏")
    if rq:
        rq.set_value(rq.options[1])
        at.run(timeout=30)
    step(at, "确认脱敏方案", tag + "S11")
    step(at, "确认上架", tag + "S12")
    # S13 赋能：radio 默认 B，填原因
    emp_r = find_area(at, "为什么选这个方案")
    if emp_r:
        emp_r.set_value("B 方案均衡，风险收益比最优，团队预算可承受")
        at.run(timeout=30)
    click_btn(at, "锁定 B 方案")
    at.run(timeout=30)
    rec(tag + "S13", at)
    click_btn(at, "下一步"); at.run(timeout=30)
    step(at, "确认建模投入", tag + "S14")
    step(at, "确认推广策略", tag + "S15")
    step(at, "确认效果度量", tag + "S16")
    step(at, "确认产品化", tag + "S17")
    step(at, "确认定价", tag + "S18")
    # S19 合同：填甲乙方/用途（其余默认合规）
    pa = find_text(at, "甲方（数据提供方）")
    pb = find_text(at, "乙方（数据购买方）")
    pu = find_text(at, "用途限制")
    if pa: pa.set_value("蜀能智造实验组")
    if pb: pb.set_value("蜀光智算买方")
    if pu: pu.set_value("行业数据分析与预测报告")
    at.run(timeout=30)
    step(at, "签署合同", tag + "S19")
    step(at, "确认 SLA", tag + "S20")
    step(at, "投放激励方案", tag + "S21")
    step(at, "确认出表方式", tag + "S22")
    click_btn(at, "触发估值引擎"); at.run(timeout=30); rec(tag + "S23_valu", at)
    click_btn(at, "下一步"); at.run(timeout=30)
    ok = click_btn(at, "提交答辩记录"); at.run(timeout=30)
    rec(tag + "S24", at)
    if ok:
        click_btn(at, "完成本轮（结算锁定）"); at.run(timeout=30); rec(tag + "_settle", at)

at = AppTest.from_file(r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab\main_app.py", default_timeout=30)
at.run(timeout=30); rec("initial", at)
at.button[0].click(); at.run(timeout=30); rec("start", at)

run_round(at, "R1")
click_btn(at, "开放第 2 轮（开始新决策）"); at.run(timeout=30); rec("R2_open", at)
run_round(at, "R2")
click_btn(at, "开放第 3 轮（开始新决策）"); at.run(timeout=30); rec("R3_open", at)
run_round(at, "R3")
click_btn(at, "计算终局六维评分"); at.run(timeout=30); rec("final_eval", at)

ok_count = sum(1 for r in results if r["status"] == "OK")
exc_list = [r["tag"] for r in results if r["status"] == "EXCEPTION"]
print("OK:", ok_count, "EXC:", exc_list)
open(r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab\apptest3r2.json", "w", encoding="utf-8").write(json.dumps(results, ensure_ascii=False, indent=1))
for r in results:
    if r["status"] == "EXCEPTION":
        print("EXC:", r["tag"], "::", r["exc"][:250])
