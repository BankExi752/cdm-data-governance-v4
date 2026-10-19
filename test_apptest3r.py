# v2.0 三轮全流程 AppTest（streamlit.testing.v1）
import sys, json
sys.path.insert(0, r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab")
from streamlit.testing.v1 import AppTest

results = []
def rec(tag, at):
    if at.exception:
        results.append({"tag": tag, "status": "EXCEPTION", "exc": str(at.exception[0].value)[:500]})
    else:
        results.append({"tag": tag, "status": "OK", "exc": ""})

def click_btn(at, label_contains):
    for b in at.button:
        if label_contains in (b.label or ""):
            b.click()
            return True
    return False

at = AppTest.from_file(r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab\main_app.py", default_timeout=30)
at.run(timeout=30); rec("initial", at)

# 开始实验
at.button[0].click(); at.run(timeout=30); rec("start", at)

def step_commit(at, btn_text, tag):
    ok = click_btn(at, btn_text)
    at.run(timeout=30); rec(tag, at)
    ok2 = click_btn(at, "下一步")
    at.run(timeout=30); rec(tag + "_nav", at)
    return ok and ok2

# R1 S1-S9
step_commit(at, "锁定组阁", "R1S1")
step_commit(at, "确认盘点完成", "R1S2")
step_commit(at, "锁定三年战略", "R1S3")
step_commit(at, "确认编制预算", "R1S4")
step_commit(at, "确认数据源", "R1S5")
step_commit(at, "确认合同条款", "R1S6")
step_commit(at, "确认存储方案", "R1S7")
step_commit(at, "完成确权登记并签字", "R1S8")
step_commit(at, "确认标准投入", "R1S9")
step_commit(at, "确认稽核投入", "R1S10")

# S11：先答测验 Q1→B（index 1），Q2 默认 A（index 0）
at.radio[0].set_value(at.radio[0].options[1])
at.run(timeout=30); rec("R1S11_quiz", at)
click_btn(at, "确认脱敏方案"); at.run(timeout=30); rec("R1S11", at)
click_btn(at, "下一步"); at.run(timeout=30); rec("R1S11_nav", at)

# S12
step_commit(at, "确认上架", "R1S12")

# S13：填原因 + 锁定（radio 默认 B）
if at.text_area:
    at.text_area[0].set_value("B 方案均衡，风险收益比最好，团队预算可承受")
at.run(timeout=30)
click_btn(at, "锁定 B 方案") or click_btn(at, "方案（开支-")
at.run(timeout=30); rec("R1S13", at)
click_btn(at, "下一步"); at.run(timeout=30); rec("R1S13_nav", at)

# S14-S18
step_commit(at, "确认建模投入", "R1S14")
step_commit(at, "确认推广策略", "R1S15")
step_commit(at, "确认效果度量", "R1S16")
step_commit(at, "确认产品化", "R1S17")
step_commit(at, "确认定价", "R1S18")

# S19：填合同表（默认值大多可用；用途/甲乙方需填）
# text_input 顺序：ca, cb, cu
if len(at.text_input) >= 3:
    at.text_input[0].set_value("蜀能智造（实验组）")
    at.text_input[1].set_value("蜀光智算（买方）")
    at.text_input[2].set_value("行业数据分析与预测报告")
at.run(timeout=30)
click_btn(at, "签署合同"); at.run(timeout=30); rec("R1S19", at)
click_btn(at, "下一步"); at.run(timeout=30); rec("R1S19_nav", at)

# S20
step_commit(at, "确认 SLA", "R1S20")

# S21：激励（默认全不选，can_go=True）
click_btn(at, "投放激励方案"); at.run(timeout=30); rec("R1S21", at)
click_btn(at, "下一步"); at.run(timeout=30); rec("R1S21_nav", at)

# S22-S24
step_commit(at, "确认出表方式", "R1S22")
click_btn(at, "触发估值引擎"); at.run(timeout=30); rec("R1S23_valu", at)
click_btn(at, "下一步"); at.run(timeout=30); rec("R1S23_nav", at)
step_commit(at, "提交答辩记录", "R1S24")

# 结算 R1 → 开 R2
click_btn(at, "完成本轮（结算锁定）"); at.run(timeout=30); rec("R1_settle", at)
click_btn(at, "开放第 2 轮（开始新决策）"); at.run(timeout=30); rec("R2_open", at)

# ---- R2 走 S1-S24 ----
step_commit(at, "锁定组阁", "R2S1")
step_commit(at, "确认盘点完成", "R2S2")
step_commit(at, "锁定三年战略", "R2S3")
step_commit(at, "确认编制预算", "R2S4")
step_commit(at, "确认数据源", "R2S5")
step_commit(at, "确认合同条款", "R2S6")
step_commit(at, "确认存储方案", "R2S7")
step_commit(at, "完成确权登记并签字", "R2S8")
step_commit(at, "确认标准投入", "R2S9")
step_commit(at, "确认稽核投入", "R2S10")
at.radio[0].set_value(at.radio[0].options[1])
at.run(timeout=30)
click_btn(at, "确认脱敏方案"); at.run(timeout=30); rec("R2S11", at)
click_btn(at, "下一步"); at.run(timeout=30)
step_commit(at, "确认上架", "R2S12")
if at.text_area:
    at.text_area[0].set_value("继续 B 方案，保持均衡投入")
at.run(timeout=30)
click_btn(at, "锁定 B 方案") or click_btn(at, "方案（开支-")
at.run(timeout=30); rec("R2S13", at)
click_btn(at, "下一步"); at.run(timeout=30)
step_commit(at, "确认建模投入", "R2S14")
step_commit(at, "确认推广策略", "R2S15")
step_commit(at, "确认效果度量", "R2S16")
step_commit(at, "确认产品化", "R2S17")
step_commit(at, "确认定价", "R2S18")
if len(at.text_input) >= 3:
    at.text_input[0].set_value("蜀能智造（实验组）")
    at.text_input[1].set_value("蜀光智算（买方）")
    at.text_input[2].set_value("行业数据分析与预测报告")
at.run(timeout=30)
click_btn(at, "签署合同"); at.run(timeout=30); rec("R2S19", at)
click_btn(at, "下一步"); at.run(timeout=30)
step_commit(at, "确认 SLA", "R2S20")
click_btn(at, "投放激励方案"); at.run(timeout=30); rec("R2S21", at)
click_btn(at, "下一步"); at.run(timeout=30)
step_commit(at, "确认出表方式", "R2S22")
click_btn(at, "触发估值引擎"); at.run(timeout=30); rec("R2S23_valu", at)
click_btn(at, "下一步"); at.run(timeout=30)
step_commit(at, "提交答辩记录", "R2S24")
click_btn(at, "完成本轮（结算锁定）"); at.run(timeout=30); rec("R2_settle", at)
click_btn(at, "开放第 3 轮（开始新决策）"); at.run(timeout=30); rec("R3_open", at)

# ---- R3 走 S1-S24 ----
step_commit(at, "锁定组阁", "R3S1")
step_commit(at, "确认盘点完成", "R3S2")
step_commit(at, "锁定三年战略", "R3S3")
step_commit(at, "确认编制预算", "R3S4")
step_commit(at, "确认数据源", "R3S5")
step_commit(at, "确认合同条款", "R3S6")
step_commit(at, "确认存储方案", "R3S7")
step_commit(at, "完成确权登记并签字", "R3S8")
step_commit(at, "确认标准投入", "R3S9")
step_commit(at, "确认稽核投入", "R3S10")
at.radio[0].set_value(at.radio[0].options[1])
at.run(timeout=30)
click_btn(at, "确认脱敏方案"); at.run(timeout=30); rec("R3S11", at)
click_btn(at, "下一步"); at.run(timeout=30)
step_commit(at, "确认上架", "R3S12")
if at.text_area:
    at.text_area[0].set_value("第三轮维持 B 方案")
at.run(timeout=30)
click_btn(at, "锁定 B 方案") or click_btn(at, "方案（开支-")
at.run(timeout=30); rec("R3S13", at)
click_btn(at, "下一步"); at.run(timeout=30)
step_commit(at, "确认建模投入", "R3S14")
step_commit(at, "确认推广策略", "R3S15")
step_commit(at, "确认效果度量", "R3S16")
step_commit(at, "确认产品化", "R3S17")
step_commit(at, "确认定价", "R3S18")
if len(at.text_input) >= 3:
    at.text_input[0].set_value("蜀能智造（实验组）")
    at.text_input[1].set_value("蜀光智算（买方）")
    at.text_input[2].set_value("行业数据分析与预测报告")
at.run(timeout=30)
click_btn(at, "签署合同"); at.run(timeout=30); rec("R3S19", at)
click_btn(at, "下一步"); at.run(timeout=30)
step_commit(at, "确认 SLA", "R3S20")
click_btn(at, "投放激励方案"); at.run(timeout=30); rec("R3S21", at)
click_btn(at, "下一步"); at.run(timeout=30)
step_commit(at, "确认出表方式", "R3S22")
click_btn(at, "触发估值引擎"); at.run(timeout=30); rec("R3S23_valu", at)
click_btn(at, "下一步"); at.run(timeout=30)
step_commit(at, "提交答辩记录", "R3S24")
click_btn(at, "完成本轮（结算锁定）"); at.run(timeout=30); rec("R3_settle", at)

# 终局：教师端六维评分（切到教师端 tab 逻辑通过 button 文本触发）
# AppTest 下 tab 切换：at.tabs 存在，直接调 compute_eval 相关按钮
click_btn(at, "计算终局六维评分"); at.run(timeout=30); rec("final_eval", at)

ok_count = sum(1 for r in results if r["status"] == "OK")
exc_count = sum(1 for r in results if r["status"] == "EXCEPTION")
print("OK:", ok_count, "EXC:", exc_count)
open(r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab\apptest3r.json", "w", encoding="utf-8").write(json.dumps(results, ensure_ascii=False, indent=1))
for r in results:
    if r["status"] == "EXCEPTION":
        print("EXC at", r["tag"], r["exc"][:300])
