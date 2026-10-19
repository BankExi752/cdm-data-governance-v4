# 打印 AppTest 当前 widget 详情（诊断）
import sys, json
sys.path.insert(0, r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab")
from streamlit.testing.v1 import AppTest

out = []
at = AppTest.from_file(r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab\main_app.py", default_timeout=30)
at.run(timeout=30)
at.button[0].click(); at.run(timeout=30)

def sig():
    md = [m.value for m in at.markdown if m.value]
    for m in md:
        if "步骤" in m and "第 1 轮" in m:
            return m[:50]
    return "?"

def click_and_run(btn_text):
    for b in at.button:
        if btn_text in (b.label or ""):
            b.click(); at.run(timeout=30); return True
    return False

out.append({"step": sig(), "radios": [(r.label, r.disabled) for r in at.radio], "texts": [t.label for t in at.text_input], "areas": [a.label for a in at.text_area]})

for t, tag in [("锁定组阁","S1"),("确认盘点完成","S2"),("锁定三年战略","S3"),("确认编制预算","S4"),("确认数据源","S5"),("确认合同条款","S6"),("确认存储方案","S7"),("完成确权登记并签字","S8"),("确认标准投入","S9"),("确认稽核投入","S10")]:
    click_and_run(t)
    out.append({"step": sig(), "tag": tag, "radios": [(r.label, r.disabled) for r in at.radio], "texts": [t.label for t in at.text_input], "areas": [a.label for a in at.text_area]})

open(r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab\widget_diag.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
print("DONE")
