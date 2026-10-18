"""
V4.1 新14步版评分系统
S1课前选角色 S2数据源 S3存储 S4汇聚血缘 S5同质异码 S6脱敏
S7可信评估(血缘回滚)🔑 S8分类分级 S9标注质检 S10语义图谱
S11 RAG问答 S12 MCP边界 S13估值三次递进🔑 S14智能体+反思
满分100；S7=10分(可信核心)，S13=15分(价值核心)
"""
from dataclasses import dataclass
from typing import Dict, List
import pandas as pd


@dataclass
class ScoringRule:
    step_no: int
    max_score: float
    deduct_on: List[str]
    deduct_amount: float = 1.5
    min_score: float = 0.0


# 新14步，满分100
STEP_SCORING_RULES: Dict[int, ScoringRule] = {
    1:  ScoringRule(1, 3.0,  ["未选角色"]),
    2:  ScoringRule(2, 5.0,  ["漏选关键数据源"]),
    3:  ScoringRule(3, 5.0,  ["选错存储方案"]),
    4:  ScoringRule(4, 6.0,  ["未看血缘"]),
    5:  ScoringRule(5, 8.0,  ["映射错误", "漏并同质异码"], deduct_amount=2.0),
    6:  ScoringRule(6, 7.0,  ["未脱敏PII"], deduct_amount=2.0),
    7:  ScoringRule(7, 10.0, ["未回滚测试", "忽视可信标识", "跳过血缘追溯"], deduct_amount=3.0),
    8:  ScoringRule(8, 6.0,  ["分级错误"]),
    9:  ScoringRule(9, 6.0,  ["标注不合格"]),
    10: ScoringRule(10, 5.0, ["未做语义切分"]),
    11: ScoringRule(11, 5.0, ["未看引用溯源"]),
    12: ScoringRule(12, 6.0, ["越权放行"], deduct_amount=2.5),
    13: ScoringRule(13, 15.0, ["未做调整", "估值初评后直接终评", "未填归因"], deduct_amount=4.0),
    14: ScoringRule(14, 13.0, ["越权放行", "未导出"], deduct_amount=3.0),
}


@dataclass
class StepScore:
    step_no: int
    action: str
    raw_score: float
    deductions: List[tuple]
    final_score: float
    max_score: float


@dataclass
class SessionScore:
    session_id: str
    step_scores: List[StepScore]
    total_raw: float
    total_deductions: float
    total_final: float
    total_max: float
    percentage: float


@dataclass
class Abilities:
    data_quality: float
    compliance: float
    asset_operation: float
    emergency_response: float

    def to_dict(self) -> dict:
        return {
            "data_quality": round(self.data_quality, 1),
            "compliance": round(self.compliance, 1),
            "asset_operation": round(self.asset_operation, 1),
            "emergency_response": round(self.emergency_response, 1),
        }

    @staticmethod
    def _grade(score: float) -> str:
        if score >= 90: return "S"
        if score >= 80: return "A"
        if score >= 70: return "B"
        if score >= 60: return "C"
        return "D"

    def grades(self) -> dict:
        return {
            "data_quality": self._grade(self.data_quality),
            "compliance": self._grade(self.compliance),
            "asset_operation": self._grade(self.asset_operation),
            "emergency_response": self._grade(self.emergency_response),
        }


def score_session(audit_df: pd.DataFrame, session_id: str = None) -> SessionScore:
    if session_id is None and not audit_df.empty:
        session_id = audit_df.iloc[0].get("session_id", "unknown")

    step_scores = []
    total_raw = total_deductions = total_max = 0.0
    steps_df = audit_df[audit_df["type"] == "step"].copy() if "type" in audit_df.columns else pd.DataFrame()

    for step_no in sorted(STEP_SCORING_RULES.keys()):
        rule = STEP_SCORING_RULES[step_no]
        step_events = steps_df[steps_df["step_no"] == step_no] if not steps_df.empty else pd.DataFrame()
        raw_score = rule.max_score
        deductions = []
        if not step_events.empty:
            for _, event in step_events.iterrows():
                action_desc = str(event.get("action", ""))
                params = event.get("params", {})
                result = event.get("result", {})
                for keyword in rule.deduct_on:
                    if (keyword in action_desc or keyword in str(params) or keyword in str(result)):
                        deductions.append((keyword, rule.deduct_amount))
                        raw_score -= rule.deduct_amount
        else:
            deductions.append(("未执行", rule.max_score))
            raw_score = 0.0
        final_score = max(raw_score, rule.min_score)
        total_raw += rule.max_score
        total_deductions += rule.max_score - final_score
        total_max += rule.max_score
        step_scores.append(StepScore(
            step_no=step_no,
            action=step_events.iloc[0].get("action", "未执行") if not step_events.empty else "未执行",
            raw_score=rule.max_score, deductions=deductions,
            final_score=final_score, max_score=rule.max_score,
        ))

    total_final = sum(s.final_score for s in step_scores)
    percentage = (total_final / total_max * 100) if total_max > 0 else 0.0
    return SessionScore(
        session_id=session_id or "unknown", step_scores=step_scores,
        total_raw=total_raw, total_deductions=total_deductions,
        total_final=total_final, total_max=total_max, percentage=percentage,
    )


def compute_abilities(score: SessionScore, audit_df: pd.DataFrame = None) -> Abilities:
    step_map = {s.step_no: s for s in score.step_scores}
    dq = [5, 7, 8, 9]
    comp = [6, 10, 12, 14]
    ao = [11, 13]
    er = [7, 13, 14]
    def _calc(steps):
        total = sum(step_map[s].max_score for s in steps if s in step_map)
        earned = sum(step_map[s].final_score for s in steps if s in step_map)
        return (earned / total * 100) if total > 0 else 0.0
    return Abilities(
        data_quality=_calc(dq),
        compliance=_calc(comp),
        asset_operation=_calc(ao),
        emergency_response=_calc(er),
    )
