# -*- coding: utf-8 -*-
import streamlit as st
import textwrap

def md_html(s):
    return st.markdown(textwrap.dedent(s), unsafe_allow_html=True)

st.markdown("## A: 直接 st.markdown 横幅（原格式）")
st.markdown("""
    <div style="background:linear-gradient(135deg,#0F2B46,#1E88E5 55%,#64B5F6);padding:26px 30px;border-radius:14px;color:#fff">
    <h1 style="margin:0;color:#fff">A 横幅测试</h1>
    </div>
    """, unsafe_allow_html=True)

st.markdown("## B: md_html dedent")
md_html("""
    <div style="background:#E8F5E9;border:1px solid #43A047;border-radius:12px;padding:12px">
    <b>B dedent 测试</b>
    </div>
    """)

st.markdown("## C: md_html + format 拼接")
inner = """
        <div style="flex:1;min-width:150px;background:#F5F9FF;border:1px solid #BBDEFB;border-radius:12px;padding:12px">C 内嵌块</div>
        """
full = """
    <div style="display:flex;gap:10px">{phases}</div>
    """.format(phases=inner)
md_html(full)

st.markdown("## D: 单行 inline HTML")
st.markdown('<span style="background:#FFF3E0;border-radius:8px;padding:2px 8px">D inline 测试</span>', unsafe_allow_html=True)
