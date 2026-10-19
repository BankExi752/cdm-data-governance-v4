# 用 streamlit.testing.v1.AppTest 做端到端流程验证（v2.0）
import sys, json
sys.path.insert(0, r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab")
from streamlit.testing.v1 import AppTest

def run_and_collect(at, tag):
    at.run(timeout=30)
    if at.exception:
        return {"tag": tag, "status": "EXCEPTION", "exc": str(at.exception[0].value)}
    return {"tag": tag, "status": "OK", "exc": ""}

results = []
at = AppTest.from_file(r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab\main_app.py", default_timeout=30)
results.append(run_and_collect(at, "initial"))

# 点击开始实验（按钮组：第一个 primary 是开始）
at.button[0].click()
results.append(run_and_collect(at, "start_clicked"))

# ---- S1 组阁：6 必选默认勾选，直接点锁定 ----
def click_btn(at, label_contains):
    for i, b in enumerate(at.button):
        if label_contains in (b.label or ""):
            b.click()
            return i
    return None

click_btn(at, "锁定组阁")
results.append(run_and_collect(at, "S1_lock"))

# ---- 导航到下一步：找"下一步"按钮 ----
click_btn(at, "下一步")
results.append(run_and_collect(at, "nav_to_S2"))

# ---- S2 盘点 ----
click_btn(at, "确认盘点完成")
results.append(run_and_collect(at, "S2_done"))
click_btn(at, "下一步")
results.append(run_and_collect(at, "nav_to_S3"))

# ---- S3 战略 ----
click_btn(at, "锁定三年战略")
results.append(run_and_collect(at, "S3_done"))
click_btn(at, "下一步")
results.append(run_and_collect(at, "nav_to_S4"))

# ---- S4 预算（默认合计100万，在预算内） ----
click_btn(at, "确认编制预算")
results.append(run_and_collect(at, "S4_done"))
click_btn(at, "下一步")
results.append(run_and_collect(at, "nav_to_S5"))

# ---- S5 数据源（默认内部30TB，30万） ----
click_btn(at, "确认数据源")
results.append(run_and_collect(at, "S5_done"))
click_btn(at, "下一步")
results.append(run_and_collect(at, "nav_to_S6"))

# ---- S6 合同 ----
click_btn(at, "确认合同条款")
results.append(run_and_collect(at, "S6_done"))
click_btn(at, "下一步")
results.append(run_and_collect(at, "nav_to_S7"))

# ---- S7 存储（湖仓一体35万） ----
click_btn(at, "确认存储方案")
results.append(run_and_collect(at, "S7_done"))
click_btn(at, "下一步")
results.append(run_and_collect(at, "nav_to_S8"))

# ---- S8 确权 ----
click_btn(at, "完成确权登记并签字")
results.append(run_and_collect(at, "S8_done"))
click_btn(at, "下一步")
results.append(run_and_collect(at, "nav_to_S9"))

# ---- S9 标准 ----
click_btn(at, "确认标准投入")
results.append(run_and_collect(at, "S9_done"))
click_btn(at, "下一步")
results.append(run_and_collect(at, "nav_to_S10"))

# ---- S10 稽核（看按钮文本） ----
labels10 = [b.label for b in at.button if b.label]
results.append({"tag": "S10_buttons", "status": "OK", "exc": json.dumps(labels10, ensure_ascii=False)[:400]})

open(r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab\apptest_results.json", "w", encoding="utf-8").write(json.dumps(results, ensure_ascii=False, indent=1))
print("DONE", len(results))
