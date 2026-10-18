// 实验全局状态：Provider 与全部业务操作（采购 / 治理 / 标注 / 估值 / 风险 / 回滚）
import { useCallback, useState } from 'react';
import type { ReactNode } from 'react';
import { toast } from 'sonner';
import { LabContext } from '@/store/lab-context';
import type { ICheckResult, ILabCtx } from '@/store/lab-context';
import type { IAuditEntry, IAuditKind, ILabState, IRiskState } from '@/data/lab';
import {
  ANNO_TASKS,
  CODE_PAIRS,
  getAssets,
  INITIAL_BUDGET,
  MASK_FIELDS,
  MAX_PLATFORM_FEE,
  RISK_EVENTS,
  ROLE_OPTIONS,
  TARGET_OPTIONS,
  USAGE_OFFERS,
} from '@/data/lab';

const NS = 'data-asset-lab';

const EMPTY_STATE: ILabState = {
  caseId: null,
  budget: INITIAL_BUDGET,
  started: false,
  role: null,
  target: null,
  purchased: [],
  cleaned: false,
  masked: false,
  traced: false,
  labeled: false,
  graphBuilt: false,
  algorithmBought: false,
  expertHired: false,
  risks: [],
  audit: [],
};

function loadState(): ILabState {
  try {
    const raw = localStorage.getItem(`${NS}:state`);
    if (!raw) return EMPTY_STATE;
    const parsed = JSON.parse(raw) as ILabState;
    const merged = { ...EMPTY_STATE, ...parsed };
    // 旧存档兼容：已开始实验但缺少风险事件状态时，补齐待处理事件
    if (merged.started && (!merged.risks || merged.risks.length === 0)) {
      merged.risks = RISK_EVENTS.map((ev) => ({ eventId: ev.id, resolved: false, choiceIndex: null }));
    }
    return merged;
  } catch {
    return EMPTY_STATE;
  }
}

let seq = 0;
function makeEntry(
  kind: IAuditKind,
  label: string,
  detail: string,
  amount: number,
  undoable: boolean,
): IAuditEntry {
  seq += 1;
  const now = new Date();
  const time = `${now.getMonth() + 1}/${now.getDate()} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
  return { id: `audit-${Date.now()}-${seq}`, time, kind, label, detail, amount, undoable, rolledBack: false };
}

export default function LabProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<ILabState>(loadState);

  const persist = useCallback((next: ILabState) => {
    try {
      localStorage.setItem(`${NS}:state`, JSON.stringify(next));
    } catch {
      /* 隐私模式静默降级 */
    }
  }, []);

  const startExperiment = useCallback(
    (caseId: string, role: string, target: string) => {
      setState((prev) => {
        const roleLabel = ROLE_OPTIONS.find((r) => r.id === role)?.label ?? role;
        const targetLabel = TARGET_OPTIONS.find((t) => t.id === target)?.label ?? target;
        const entry = makeEntry(
          'system',
          '开始实验',
          `选定案例「${caseId}」、角色「${roleLabel}」、目标「${targetLabel}」，${INITIAL_BUDGET} 万预算到账`,
          INITIAL_BUDGET,
          false,
        );
        const next: ILabState = {
          ...prev,
          caseId,
          role,
          target,
          started: true,
          budget: prev.started ? prev.budget : INITIAL_BUDGET,
          // 开始实验即进入风险事件博弈：三个事件全部待处理
          risks: RISK_EVENTS.map((ev) => ({ eventId: ev.id, resolved: false, choiceIndex: null })),
          audit: [...prev.audit, entry],
        };
        persist(next);
        return next;
      });
      toast.success('实验开始，500 万预算已到账，风险事件已就位');
    },
    [persist],
  );

  const purchaseAsset = useCallback(
    (assetId: string): ICheckResult => {
      const result: ICheckResult = { ok: true, message: '' };
      setState((prev) => {
        const asset = getAssets(prev.caseId).find((a) => a.id === assetId);
        if (!asset) {
          result.ok = false;
          result.message = '未找到该资产';
          return prev;
        }
        result.message = `已采购「${asset.name}」，支出 ${asset.price} 万`;
        if (!prev.started) {
          result.ok = false;
          result.message = '请先到实验导览页开始实验';
          return prev;
        }
        if (prev.purchased.includes(assetId)) {
          result.ok = false;
          result.message = `「${asset.name}」已采购，请勿重复购买`;
          return prev;
        }
        if (prev.budget < asset.price) {
          result.ok = false;
          result.message = `预算不足：需 ${asset.price} 万，当前仅剩 ${prev.budget} 万`;
          return prev;
        }
        const entry = makeEntry('purchase', `采购 ${asset.name}`, `${asset.result}｜支出 ${asset.price} 万`, -asset.price, true);
        const next: ILabState = {
          ...prev,
          budget: prev.budget - asset.price,
          purchased: [...prev.purchased, assetId],
          audit: [...prev.audit, entry],
        };
        persist(next);
        return next;
      });
      return result;
    },
    [persist],
  );

  const submitCleanCheck = useCallback(
    (sameIds: string[]): ICheckResult => {
      const correct = CODE_PAIRS.filter((p) => p.same).map((p) => p.id);
    const wrongSame = CODE_PAIRS.filter((p) => !p.same).map((p) => p.id);
    const pickedWrong = sameIds.filter((id) => wrongSame.includes(id));
    const missedRight = correct.filter((id) => !sameIds.includes(id));
    if (pickedWrong.length === 0 && missedRight.length === 0) {
      setState((prev) => {
        const entry = makeEntry('govern', '同质异码清洗', '识别 3 对同质异码并统一编码：电堆A=燃料电池A、压缩机01=CMP-001、储氢罐3号=TK-H2-03；冗余编码停用', 0, false);
        const next: ILabState = { ...prev, cleaned: true, audit: [...prev.audit, entry] };
        persist(next);
        return next;
      });
      return { ok: true, message: '判定全部正确，同质异码清洗完成' };
    }
    const parts: string[] = [];
    if (missedRight.length > 0) {
      parts.push(`漏判同质异码 ${missedRight.length} 对`);
    }
    if (pickedWrong.length > 0) {
      parts.push(`误判 ${pickedWrong.length} 对（名称相似≠同一物）`);
    }
    setState((prev) => {
      const entry = makeEntry('error', '同质异码判定失败', parts.join('；') + '——已留痕，可重新判定', 0, false);
      const next: ILabState = { ...prev, audit: [...prev.audit, entry] };
      persist(next);
      return next;
    });
    return { ok: false, message: parts.join('；') + '，请重新判定' };
    },
    [persist],
  );

  const submitMaskCheck = useCallback(
    (selectedIds: string[]): ICheckResult => {
      const mustMask = MASK_FIELDS.filter((f) => f.sensitive).map((f) => f.id);
      const mustNot = MASK_FIELDS.filter((f) => !f.sensitive).map((f) => f.id);
      const missed = mustMask.filter((id) => !selectedIds.includes(id));
      const over = selectedIds.filter((id) => mustNot.includes(id));
      if (missed.length > 0 || over.length > 0) {
        const parts: string[] = [];
        if (missed.length > 0) parts.push(`漏选 ${missed.length} 个敏感字段`);
        if (over.length > 0) parts.push(`多选 ${over.length} 个非敏感字段`);
        setState((prev) => {
          const entry = makeEntry('error', '脱敏方案校验失败', parts.join('；') + '——已留痕，可重新选择', 0, false);
          const next: ILabState = { ...prev, audit: [...prev.audit, entry] };
          persist(next);
          return next;
        });
        return { ok: false, message: parts.join('；') + '，请重新勾选' };
      }
      setState((prev) => {
        if (prev.budget < 20) {
          return prev;
        }
        const entry = makeEntry('govern', '数据脱敏', '5 个敏感字段脱敏完成（客户姓名/身份证号/银行账号/合同金额/人员定位），命中即阻断隔离，支出 20 万', -20, true);
        const next: ILabState = {
          ...prev,
          budget: prev.budget - 20,
          masked: true,
          audit: [...prev.audit, entry],
        };
        persist(next);
        return next;
      });
      return { ok: true, message: '脱敏方案校验通过，支出 20 万' };
    },
    [persist],
  );

  const deployTrace = useCallback((): ICheckResult => {
    const result: ICheckResult = { ok: true, message: '可信溯源体系已部署，支出 30 万' };
    setState((prev) => {
      if (prev.traced) {
        result.ok = false;
        result.message = '可信溯源体系已部署，请勿重复部署';
        return prev;
      }
      if (prev.budget < 30) {
        result.ok = false;
        result.message = `预算不足：需 30 万，当前仅剩 ${prev.budget} 万`;
        return prev;
      }
      const entry = makeEntry('govern', '部署可信溯源', '血缘追溯 + 操作留痕 + 版本回滚 + 跨域授权四件套上线，异常 30 分钟内可恢复，支出 30 万', -30, true);
      const next: ILabState = {
        ...prev,
        budget: prev.budget - 30,
        traced: true,
        audit: [...prev.audit, entry],
      };
      persist(next);
      return next;
    });
    return result;
  }, [persist]);

  const submitLabel = useCallback(
    (quantities: Record<string, number>): ICheckResult => {
      const total = Object.entries(quantities).reduce((sum, [, qty]) => sum + qty, 0);
      if (total <= 0) {
        return { ok: false, message: '请至少选择一个标注任务并填写数量' };
      }
      let cost = MAX_PLATFORM_FEE;
      for (const task of ANNO_TASKS) {
        cost += (quantities[task.id] ?? 0) * task.unitPrice;
      }
      const costRounded = Math.round(cost * 100) / 100;
      const result: ICheckResult = { ok: true, message: `标注费用合计 ${costRounded} 万（含平台费 ${MAX_PLATFORM_FEE} 万）` };
      setState((prev) => {
        if (prev.labeled) {
          result.ok = false;
          result.message = '质检标注已完成，请勿重复提交';
          return prev;
        }
        if (prev.budget < costRounded) {
          result.ok = false;
          result.message = `预算不足：标注需 ${costRounded} 万，当前仅剩 ${prev.budget} 万`;
          return prev;
        }
        const qtyText = Object.entries(quantities)
          .filter(([, q]) => q > 0)
          .map(([id, q]) => `${id === 't-box' ? '图像框选' : id === 't-text' ? '文本标注' : '语音转写'}×${q}`)
          .join('、');
        const entry = makeEntry('govern', '质检标注', `任务：${qtyText}；产出标注样本已验收可训练，合计 ${costRounded} 万`, -costRounded, true);
        const next: ILabState = {
          ...prev,
          budget: prev.budget - costRounded,
          labeled: true,
          audit: [...prev.audit, entry],
        };
        persist(next);
        return next;
      });
      return result;
    },
    [persist],
  );

  const buyUsage = useCallback(
    (offerId: string): ICheckResult => {
      const offer = USAGE_OFFERS.find((o) => o.id === offerId);
      if (!offer) return { ok: false, message: '未找到该能力项' };
      const result: ICheckResult = { ok: true, message: `已构建「${offer.name}」，支出 ${offer.cost} 万` };
      setState((prev) => {
        const already =
          (offerId === 'u-graph' && prev.graphBuilt) ||
          (offerId === 'u-algo' && prev.algorithmBought) ||
          (offerId === 'u-expert' && prev.expertHired);
        if (already) {
          result.ok = false;
          result.message = `「${offer.name}」已部署，请勿重复购买`;
          return prev;
        }
        if (prev.budget < offer.cost) {
          result.ok = false;
          result.message = `预算不足：需 ${offer.cost} 万，当前仅剩 ${prev.budget} 万`;
          return prev;
        }
        const incomeText = offer.incomePerYear > 0 ? `，每年带来 ${offer.incomePerYear} 万收入` : '';
        const deliverText = offer.deliverables[0] ?? '';
        const entry = makeEntry('usage', `部署 ${offer.name}`, `${deliverText}${incomeText}，支出 ${offer.cost} 万`, -offer.cost, true);
        const next: ILabState = {
          ...prev,
          budget: prev.budget - offer.cost,
          graphBuilt: prev.graphBuilt || offerId === 'u-graph',
          algorithmBought: prev.algorithmBought || offerId === 'u-algo',
          expertHired: prev.expertHired || offerId === 'u-expert',
          audit: [...prev.audit, entry],
        };
        persist(next);
        return next;
      });
      return result;
    },
    [persist],
  );

  const resolveRisk = useCallback(
    (eventId: string, choiceIndex: number): ICheckResult => {
      const result: ICheckResult = { ok: true, message: '' };
      setState((prev) => {
        const event = RISK_EVENTS.find((e) => e.id === eventId);
        const existing = prev.risks.find((r) => r.eventId === eventId);
        if (!event) {
          result.ok = false;
          result.message = '未找到该风险事件';
          return prev;
        }
        if (!existing || existing.resolved) {
          result.ok = false;
          result.message = `「${event.title}」已处理，请勿重复选择`;
          return prev;
        }
        const choice = event.options[choiceIndex];
        if (!choice) {
          result.ok = false;
          result.message = '无效的应对选项';
          return prev;
        }
        if (prev.budget < choice.cost) {
          result.ok = false;
          result.message = `预算不足：应对需 ${choice.cost} 万，当前仅剩 ${prev.budget} 万`;
          return prev;
        }
        const incomeText = choice.incomeDelta !== 0
          ? `，年收入${choice.incomeDelta > 0 ? '+' : ''}${choice.incomeDelta} 万`
          : '';
        const entry = makeEntry(
          'risk',
          `应对风险：${event.title}`,
          `选择「${choice.label}」：${choice.desc}｜支出 ${choice.cost} 万${incomeText}`,
          -choice.cost,
          true,
        );
        const nextRisk: IRiskState = { eventId, resolved: true, choiceIndex };
        const next: ILabState = {
          ...prev,
          budget: prev.budget - choice.cost,
          risks: prev.risks.map((r) => (r.eventId === eventId ? nextRisk : r)),
          audit: [...prev.audit, entry],
        };
        persist(next);
        result.message = `已选择「${choice.label}」，支出 ${choice.cost} 万${incomeText}，已留痕`;
        return next;
      });
      return result;
    },
    [persist],
  );

  const rollback = useCallback(
    (auditId: string): ICheckResult => {
      const result: ICheckResult = { ok: true, message: '已回滚该操作' };
      setState((prev) => {
        const target = prev.audit.find((a) => a.id === auditId);
        if (!target || !target.undoable || target.rolledBack) {
          result.ok = false;
          result.message = '该操作不可回滚或已回滚';
          return prev;
        }
        const refund = -target.amount;
        let next: ILabState = { ...prev, budget: prev.budget + refund };
        if (target.kind === 'purchase') {
          const assetId = getAssets(prev.caseId).find((a) => a.name === target.label.replace('采购 ', ''))?.id;
          if (assetId) {
            next = { ...next, purchased: next.purchased.filter((id) => id !== assetId) };
          }
        } else if (target.kind === 'govern') {
          if (target.label === '数据脱敏') next = { ...next, masked: false };
          if (target.label === '部署可信溯源') next = { ...next, traced: false };
          if (target.label === '质检标注') next = { ...next, labeled: false };
          if (target.label === '同质异码清洗') next = { ...next, cleaned: false };
        } else if (target.kind === 'usage') {
          if (target.label.includes('企业知识图谱')) next = { ...next, graphBuilt: false };
          if (target.label.includes('故障预测算法')) next = { ...next, algorithmBought: false };
          if (target.label.includes('算法专家')) next = { ...next, expertHired: false };
        } else if (target.kind === 'risk') {
          // 回滚风险事件：恢复对应事件为未处理状态，年收入增量随之失效
          const event = RISK_EVENTS.find((e) => `应对风险：${e.title}` === target.label);
          if (event) {
            next = {
              ...next,
              risks: next.risks.map((r) => (r.eventId === event.id ? { ...r, resolved: false, choiceIndex: null } : r)),
            };
          }
        }
        const rollEntry = makeEntry('system', '回滚操作', `撤销「${target.label}」，退回 ${refund} 万`, refund, false);
        next = {
          ...next,
          audit: [...next.audit.map((a) => (a.id === auditId ? { ...a, rolledBack: true } : a)), rollEntry],
        };
        persist(next);
        return next;
      });
      return result;
    },
    [persist],
  );

  const resetAll = useCallback(() => {
    setState(() => {
      const entry = makeEntry('system', '重置实验', '清空全部进度与留痕，恢复初始预算', 0, false);
      const next: ILabState = { ...EMPTY_STATE, audit: [entry] };
      persist(next);
      return next;
    });
    toast.info('实验已重置');
  }, [persist]);

  const value: ILabCtx = {
    ...state,
    startExperiment,
    purchaseAsset,
    submitCleanCheck,
    submitMaskCheck,
    deployTrace,
    submitLabel,
    buildGraph: () => buyUsage('u-graph'),
    buyAlgorithm: () => buyUsage('u-algo'),
    hireExpert: () => buyUsage('u-expert'),
    resolveRisk,
    rollback,
    resetAll,
  };

  return <LabContext.Provider value={value}>{children}</LabContext.Provider>;
}
