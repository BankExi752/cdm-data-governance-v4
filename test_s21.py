# -*- coding: utf-8 -*-
# 第21步修复单测：INCENTIVES 列表 + id 索引
INCENTIVES = [
    {"id": "money", "name": "绩效奖金", "type": "金钱", "cost": 150000, "effect": {"mot": 15}},
    {"id": "train", "name": "培训进修", "type": "非金钱", "cost": 80000, "effect": {"cap": 10}},
    {"id": "auth", "name": "授权放权", "type": "非金钱", "cost": 0, "effect": {"mot": 12}},
    {"id": "honor", "name": "荣誉表彰", "type": "非金钱", "cost": 0, "effect": {"ret": 8}},
    {"id": "equity", "name": "股权/分红", "type": "金钱", "cost": 200000, "effect": {"ret": 15, "mot": 5}},
    {"id": "rotate", "name": "岗位轮换", "type": "非金钱", "cost": 50000, "effect": {"cap": -5}},
]
INC_BY_ID = {x["id"]: x for x in INCENTIVES}

def money_only(chosen):
    return all(INC_BY_ID[i]["type"] == "金钱" for i in chosen) and len(chosen) > 0

cases = [[], ["money"], ["train"], ["auth", "honor"], ["money", "equity"], ["money", "train"]]
for c in cases:
    print(c, "->", money_only(c))
print("OK")
