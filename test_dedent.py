# -*- coding: utf-8 -*-
import textwrap
s = """
    <div style="display:flex;gap:10px">
    TEST
    </div>
    """
print(repr(textwrap.dedent(s)))
print("---")
# 模拟 phase_blocks 内嵌
inner = """
        <div style="flex:1;min-width:150px">投入篇</div>
        """
full = """
    <div style="display:flex">{phases}</div>
    """.format(phases=inner)
print(repr(textwrap.dedent(full)))
