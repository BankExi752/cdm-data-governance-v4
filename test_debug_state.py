# 分段调试：每轮结束后打印状态
import sys, json
sys.path.insert(0, r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab")
from streamlit.testing.v1 import AppTest

out = []
def click_btn(at, txt):
    for b in at.button:
        if txt in (b.label or ""):
            b.click(); return True
    return False

def step(at, btn_text):
    click_btn(at, btn_text); at.run(timeout=30)
    click_btn(at, "下一步"); at.run(timeout=30)

def find_radio(at, lp):
    for r in at.radio:
        if r.label and lp in r.label: return r
    return None
def find_text(at, lp):
    for t in at.text_input:
        if t.label and lp in t.label: return t
    return None
def find_area(at, lp):
    for a in at.text_area:
        if a.label and lp in a.label: return a
    return None

def snap(at, tag):
    try:
        f = at.session_state.to_dict()
        out.append({"tag": tag, "round": f.get("round"), "step": f.get("step"),
                    "done": sorted(f.get("done", [])), "settled": sorted(f.get("settled", [])),
                    "closed": sorted(f.get("closed_round", [])), "vh": len(f.get("val_history", [])),
                    "contract_filled": bool(f.get("contract_filled", {}))})
    except Exception as e:
        out.append({"tag": tag, "err": str(e)})

def run_round(at, tag):
    step(at, "锁定组阁"); snap(at, tag + "S1")
    step(at, "确认盘点完成"); snap(at, tag + "S2")
    step(at, "锁定三年战略"); snap(at, tag + "S3")
    step(at, "确认编制预算"); snap(at, tag + "S4")
    step(at, "确认数据源"); snap(at, tag + "S5")
    step(at, "确认合同条款"); snap(at, tag + "S6")
    step(at, "确认存储方案"); snap(at, tag + "S7")
    step(at, "完成确权登记并签字"); snap(at, tag + "S8")
    step(at, "确认标准投入"); snap(at, tag + "S9")
    step(at, "确认稽核投入"); snap(at, tag + "S10")
    rq = find_radio(at, "Q1：脱敏")
    if rq:
        rq.set_value(rq.options[1]); at.run(timeout=30)
    step(at, "确认脱敏方案"); snap(at, tag + "S11")
    step(at, "确认上架"); snap(at, tag + "S12")
    emp_r = find_area(at, "为什么选这个方案")
    if emp_r:
        emp_r.set_value("B 方案均衡"); at.run(timeout=30)
    click_btn(at, "锁定 B 方案"); at.run(timeout=30)
    click_btn(at, "下一步"); at.run(timeout=30)
    snap(at, tag + "S13")
    step(at, "确认建模投入"); snap(at, tag + "S14")
    step(at, "确认推广策略"); snap(at, tag + "S15")
    step(at, "确认效果度量"); snap(at, tag + "S16")
    step(at, "确认产品化"); snap(at, tag + "S17")
    step(at, "确认定价"); snap(at, tag + "S18")
    pa = find_text(at, "甲方（数据提供方）")
    pb = find_text(at, "乙方（数据购买方）")
    pu = find_text(at, "用途限制")
    if pa: pa.set_value("蜀能智造实验组")
    if pb: pb.set_value("蜀光智算买方")
    if pu: pu.set_value("行业数据分析与预测报告")
    at.run(timeout=30)
    step(at, "签署合同"); snap(at, tag + "S19")
    step(at, "确认 SLA"); snap(at, tag + "S20")
    step(at, "投放激励方案"); snap(at, tag + "S21")
    step(at, "确认出表方式"); snap(at, tag + "S22")
    okv = click_btn(at, "触发估值引擎"); at.run(timeout=30); snap(at, tag + "S23v")
    out.append({"tag": tag + "S23btn", "found": okv})
    click_btn(at, "下一步"); at.run(timeout=30)
    click_btn(at, "提交答辩记录"); at.run(timeout=30); snap(at, tag + "S24")
    okc = click_btn(at, "完成本轮（结算锁定）"); at.run(timeout=30); snap(at, tag + "SETTLE")
    out.append({"tag": tag + "settlebtn", "found": okc})

at = AppTest.from_file(r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab\main_app.py", default_timeout=30)
at.run(timeout=30)
at.button[0].click(); at.run(timeout=30)
run_round(at, "R1")
oko = click_btn(at, "开放第 2 轮（开始新决策）"); at.run(timeout=30); snap(at, "R2OPEN")
out.append({"tag": "openR2btn", "found": oko})
run_round(at, "R2")
oko2 = click_btn(at, "开放第 3 轮（开始新决策）"); at.run(timeout=30); snap(at, "R3OPEN")
out.append({"tag": "openR3btn", "found": oko2})
run_round(at, "R3")

open(r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab\debug_state.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
print("DONE", len(out))
