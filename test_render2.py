# -*- coding: utf-8 -*-
import streamlit as st
import textwrap

def md_html(s):
    lines = [ln.strip() for ln in s.splitlines()]
    return st.markdown("\n".join(lines), unsafe_allow_html=True)

PHASES = [
    {"name": "投入篇", "steps": [1, 2, 3, 4], "aim": "定好团队与预算——开局底子"},
    {"name": "采集篇", "steps": [5, 6, 7, 8], "aim": "拿到数据并安全存好——原料入仓"},
]

st.markdown("## X1: main_app flow_html 结构复刻")
flow_html = """
<div style="display:flex;gap:10px;flex-wrap:nowrap;overflow-x:auto;padding:6px 0">
{phases}
</div>
<div style="margin-top:8px;font-size:13px;color:#37474F;background:#ECEFF1;border-radius:10px;padding:10px 14px">
💡 <b>逻辑主线</b>：先把「数据当资产」的<b>底子</b>打好（投入→采集→治理），再把「资产变钱」的<b>变现</b>跑通（赋能→变现→经营估值）。前 12 步决定 Q/C/H 的底子，后 12 步决定现金流的来源——两边都做好，V 才会高。
</div>
"""
phase_blocks = []
for ph in PHASES:
    phase_blocks.append(f"""
    <div style="flex:1;min-width:150px;background:#F5F9FF;border:1px solid #BBDEFB;border-radius:12px;padding:12px">
    <div style="font-weight:700;color:#0D47A1;font-size:15px">{ph['name']}</div>
    <div style="font-size:12px;color:#1565C0;margin-top:4px">步骤 {ph['steps'][0]}-{ph['steps'][-1]}</div>
    <div style="font-size:12px;color:#455A64;margin-top:6px">{ph['aim']}</div>
    </div>
    """)
md_html(flow_html.format(phases="".join(phase_blocks)))

st.markdown("## X2: 无 f-string 占位、纯静态块")
static_blocks = ""
for ph in PHASES:
    static_blocks += """
    <div style="flex:1;min-width:150px;background:#F5F9FF;border:1px solid #BBDEFB;border-radius:12px;padding:12px">STATIC-{name}</div>
    """.format(name=ph["name"])
md_html(flow_html.format(phases=static_blocks))

st.markdown("## X3: 单行拼接（无换行）")
one_line = "<div style=\"flex:1;min-width:150px;background:#F5F9FF;border:1px solid #BBDEFB;border-radius:12px;padding:12px\">ONELINE</div>"
md_html(flow_html.format(phases=one_line))
