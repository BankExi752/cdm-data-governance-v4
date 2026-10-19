# 诊断 R1 全流程 + 结算（带每步页面信息日志）
import sys, json
sys.path.insert(0, r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab")
from streamlit.testing.v1 import AppTest

log = []
def page_sig(at):
    md = [m.value for m in at.markdown if m.value]
    sig = ""
    for m in md:
        if "第 1 轮 · 步骤" in m or "第 2 轮 · 步骤" in m or "第 3 轮 · 步骤" in m:
            sig = m[:40]
            break
    return sig

def step(at, btn_text, tag):
    hit = [b.label for b in at.button if btn_text in (b.label or "")]
    log.append({"tag": tag, "page": page_sig(at), "btn_hit": len(hit) > 0, "radios": len(at.radio), "texts": len(at.text_input), "areas": len(at.text_area), "exc": (str(at.exception[0].value)[:200] if at.exception else "")})
    for b in at.button:
        if btn_text in (b.label or ""):
            b.click()
            at.run(timeout=30)
            log.append({"tag": tag + "_after", "page": page_sig(at), "exc": (str(at.exception[0].value)[:200] if at.exception else "")})
            return True
    return False

at = AppTest.from_file(r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab\main_app.py", default_timeout=30)
at.run(timeout=30)
at.button[0].click(); at.run(timeout=30)
log.append({"tag": "start", "page": page_sig(at)})

step(at, "锁定组阁", "S1")
step(at, "确认盘点完成", "S2")
step(at, "锁定三年战略", "S3")
step(at, "确认编制预算", "S4")
step(at, "确认数据源", "S5")
step(at, "确认合同条款", "S6")
step(at, "确认存储方案", "S7")
step(at, "完成确权登记并签字", "S8")
step(at, "确认标准投入", "S9")
step(at, "确认稽核投入", "S10")
# S11 测验
log.append({"tag": "S11_pre", "page": page_sig(at), "radios": len(at.radio)})
if at.radio:
    at.radio[0].set_value(at.radio[0].options[1])
    at.run(timeout=30)
step(at, "确认脱敏方案", "S11")
step(at, "确认上架", "S12")
# S13 填原因
if at.text_area:
    at.text_area[0].set_value("B 方案均衡")
    at.run(timeout=30)
step(at, "锁定 B 方案", "S13")
step(at, "确认建模投入", "S14")
step(at, "确认推广策略", "S15")
step(at, "确认效果度量", "S16")
step(at, "确认产品化", "S17")
step(at, "确认定价", "S18")
# S19 填表
if len(at.text_input) >= 3:
    at.text_input[0].set_value("甲方实验组")
    at.text_input[1].set_value("乙方买方")
    at.text_input[2].set_value("行业分析报告用途")
    at.run(timeout=30)
step(at, "签署合同", "S19")
step(at, "确认 SLA", "S20")
step(at, "投放激励方案", "S21")
step(at, "确认出表方式", "S22")
step(at, "触发估值引擎", "S23")
step(at, "提交答辩记录", "S24")
step(at, "完成本轮（结算锁定）", "SETTLE")
step(at, "开放第 2 轮（开始新决策）", "OPEN_R2")
# R2S1
step(at, "锁定组阁", "R2S1")

open(r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab\apptest_diag.json", "w", encoding="utf-8").write(json.dumps(log, ensure_ascii=False, indent=1))
print("LOG_LEN", len(log))
