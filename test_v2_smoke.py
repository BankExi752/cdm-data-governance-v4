# v2.0 估值引擎冒烟测试（纯函数，不依赖 st.session_state）
import importlib.util, sys, types

# 用 stub 替换 streamlit 后再 import main_app 的函数
stub = types.ModuleType("streamlit")
def _noop(*a, **k): return None
def _noop_context(*a, **k):
    class Ctx:
        def __enter__(self): return self
        def __exit__(self, *a): return False
    return Ctx()
stub.__getattr__ = lambda name: _noop
for name in ["markdown", "caption", "info", "warning", "error", "success",
             "button", "checkbox", "radio", "selectbox", "multiselect",
             "number_input", "text_input", "text_area", "metric", "dataframe",
             "line_chart", "bar_chart", "progress", "divider", "columns",
             "expander", "rerun", "stop", "session_state", "sidebar", "tab",
             "set_page_config", "spinner", "container", "html", "tabs",
             "write", "header", "subheader", "empty", "toggle", "popover",
             "status", "chat_message", "code", "latex", "download_button",
             "form", "form_submit_button", "column_config", "data_editor"]:
    setattr(stub, name, _noop)
stub.columns = lambda *a, **k: [_noop_context() for _ in (a[0] if a and isinstance(a[0], (list, tuple)) else range(2))]
stub.tabs = lambda *a, **k: [_noop_context() for _ in range(len(a[0]) if a and isinstance(a[0], (list, tuple)) else 3)]
stub.expander = _noop_context
stub.sidebar = _noop_context()
class SS:
    def __init__(self): self._d = {}
    def __contains__(self, k): return k in self._d
    def __getitem__(self, k): return self._d[k]
    def __setitem__(self, k, v): self._d[k] = v
    def __getattr__(self, k):
        if k.startswith("_"): raise AttributeError(k)
        return self._d.get(k)
    def __setattr__(self, k, v):
        if k.startswith("_"): object.__setattr__(self, k, v)
        else: self._d[k] = v
stub.session_state = SS()
sys.modules["streamlit"] = stub

spec = importlib.util.spec_from_file_location("main_app", r"C:\Users\孔鑫璇\Doubao\chats\2026-10-19\new-chat\data-asset-lab\main_app.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# ---- 1. calc_t ----
d1 = {"source": "内部", "register": True, "audit_trail": True}
t1, det1 = mod.calc_t(d1)
assert t1 == 100, f"内部+签字+审计 应 100, got {t1}"
d2 = {"source": "爬取", "register": False, "audit_trail": False}
t2, det2 = mod.calc_t(d2)
assert t2 == 10, f"爬取全不 应 10, got {t2}"
d3 = {"source": "第三方", "register": True, "audit_trail": False}
t3, _ = mod.calc_t(d3)
assert t3 == 55, f"第三方+签字 应 55, got {t3}"
print("calc_t OK:", t1, t2, t3)

# ---- 2. calc_h（年薪计入 + 越限） ----
h1, hd1 = mod.calc_h("制造", {"storage": "湖仓一体", "source": "内部", "source_tb": 30, "team_salary": 92}, 1, [])
print("calc_h 内部30TB+湖仓+92年薪:", h1, hd1)
assert abs(hd1["salary"] - 92) < 0.01, "年薪应计入"
# 内部超限 40TB
h2, hd2 = mod.calc_h("制造", {"storage": "数仓", "source": "内部", "source_tb": 40, "team_salary": 0}, 1, [])
print("calc_h 内部超限40TB:", h2, hd2)
assert hd2["over_cost"] > 0, "越限应有追加成本"

# ---- 3. calc_q（赋能加成） ----
q1, qd1 = mod.calc_q("制造", {"mask": "全量脱敏", "standard": True, "qc": True, "catalog": True, "storage": "湖仓一体", "empower_plan": "C"})
q0, qd0 = mod.calc_q("制造", {"mask": "全量脱敏", "standard": True, "qc": True, "catalog": True, "storage": "湖仓一体"})
print("calc_q 赋能C:", q0, "->", q1)
assert q1 >= q0, "赋能应提升 Q"

# ---- 4. calc_c（爬取超限 C=0.3） ----
c1 = mod.calc_c("制造", {"source": "爬取", "source_over_limit": True, "mask": "全量脱敏"}, 1, [])
c2 = mod.calc_c("制造", {"source": "爬取", "source_over_limit": False, "mask": "全量脱敏"}, 1, [])
print("calc_c 爬取未超限:", c2, "超限:", c1)
assert c1 <= 0.3 and c2 > c1, "爬取超限 C 应 ≤0.3"

# ---- 5. calc_cash（赋能乘数） ----
cash_a = mod.calc_cash("制造", {"scenes": list(mod.INDUSTRIES["制造"]["scenes"].keys())[:2], "strategy": "对外优先", "empower_plan": "A"}, 1, [])
cash_n = mod.calc_cash("制造", {"scenes": list(mod.INDUSTRIES["制造"]["scenes"].keys())[:2], "strategy": "对外优先"}, 1, [])
print("calc_cash 无赋能:", cash_n, "赋能A:", cash_a)

# ---- 6. 数据定义完整性 ----
assert len(mod.ROLE_TEAM) == 8
assert len(mod.INCENTIVES) == 5
assert len(mod.SOURCE_TYPES) == 3
assert len(mod.EMPOWER_PLANS) == 3
assert len(mod.MASK_METHODS) == 4
assert len(mod.DATA_TYPE_INVENTORY) == 5
assert len(mod.DATA_KINDS_CLASS) == 3
assert len(mod.CONTRACT_CLAUSES) == 9
for inc in mod.INCENTIVES:
    assert all(k in inc for k in ["id", "name", "type", "cost", "effect", "hidden", "ref"])
print("数据定义完整性 OK")
print("ALL SMOKE TESTS PASSED")
