// 用数据页：第三阶，建图谱 / 买算法 / 请专家 / 风险博弈 / 六维估值
import { useState } from 'react';
import { AlertTriangle, Brain, Check, CheckCircle2, Database, Gauge, GraduationCap, Network, ShieldAlert } from 'lucide-react';
import { toast } from 'sonner';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { RISK_EVENTS, USAGE_OFFERS, VALUATION_DIMS } from '@/data/lab';
import { useLab } from '@/store/lab-context';
import { cn } from '@/lib/utils';

export default function UsePage() {
  const { started, budget, graphBuilt, algorithmBought, expertHired, cleaned, masked, traced, labeled, buildGraph, buyAlgorithm, hireExpert, purchased, risks, resolveRisk } = useLab();
  const [busy, setBusy] = useState<string | null>(null);

  const handleDeploy = (id: string, fn: () => { ok: boolean; message: string }) => {
    if (busy) return;
    setBusy(id);
    window.setTimeout(() => {
      const result = fn();
      if (result.ok) {
        toast.success(result.message);
      } else {
        toast.error(result.message);
      }
      setBusy(null);
    }, 300);
  };

  // 六维估值：依据已完成的阶段计算
  const dimScores: Record<string, number> = {
    'd-usable': 30 + purchased.length * 10,
    'd-trust': (traced ? 40 : 10) + (labeled ? 20 : 0) + (cleaned ? 20 : 0),
    'd-complete': (cleaned ? 40 : 10) + (masked ? 20 : 0),
    'd-trace': traced ? 85 : 15,
    'd-std': cleaned ? 80 : 20,
    'd-compliance': masked ? 85 : 20,
  };
  const totalScore = Math.round(
    VALUATION_DIMS.reduce((sum, dim) => sum + dimScores[dim.id], 0) / VALUATION_DIMS.length,
  );

  // 收益联动：未部署可信溯源 → 算法/专家收益打 5 折
  const incomeMultiplier = traced ? 1 : 0.5;
  const algoIncome = algorithmBought ? (USAGE_OFFERS.find((o) => o.id === 'u-algo')?.incomePerYear ?? 0) * incomeMultiplier : 0;
  const expertIncome = expertHired ? (USAGE_OFFERS.find((o) => o.id === 'u-expert')?.incomePerYear ?? 0) * incomeMultiplier : 0;
  const riskIncome = risks
    .filter((r) => r.resolved && r.choiceIndex !== null)
    .reduce((sum, r) => {
      const event = RISK_EVENTS.find((e) => e.id === r.eventId);
      const choice = event?.options[r.choiceIndex ?? 0];
      return sum + (choice?.incomeDelta ?? 0);
    }, 0);
  const effectiveIncome = algoIncome + expertIncome + riskIncome;

  const offerMeta: Record<string, { icon: typeof Network; done: boolean }> = {
    'u-graph': { icon: Network, done: graphBuilt },
    'u-algo': { icon: Brain, done: algorithmBought },
    'u-expert': { icon: GraduationCap, done: expertHired },
  };

  const handleFn: Record<string, () => { ok: boolean; message: string }> = {
    'u-graph': buildGraph,
    'u-algo': buyAlgorithm,
    'u-expert': hireExpert,
  };

  const handleRisk = (eventId: string, choiceIndex: number) => {
    const result = resolveRisk(eventId, choiceIndex);
    if (result.ok) {
      toast.success(result.message);
    } else {
      toast.error(result.message);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-1">
        <Badge variant="secondary" className="w-fit">第三阶 · 知识资产化与智能调用</Badge>
        <h1 className="text-2xl font-bold tracking-tight">用数据：让知识被智能体调起来</h1>
        <p className="max-w-3xl text-muted-foreground">
          知识资产建好了，最后一步是把它开放出去。算法和专家每年带来收入；六维估值随治理与调用进度动态更新。所有部署均可撤销。
        </p>
      </div>

      {!traced && (algorithmBought || expertHired) && (
        <div className="flex items-start gap-2 rounded-lg border border-warning/40 bg-warning/5 px-4 py-3 text-sm text-warning">
          <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0" />
          <div>
            <p className="font-medium">可信溯源未部署：算法/专家收益按 5 折兑现</p>
            <p className="text-xs text-muted-foreground">
              未部署「可信溯源」时，业务与客户不信任数据出处，算法服务与专家咨询收入减半。前往「治数据」部署后收益全额兑现。
            </p>
          </div>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-3">
        {USAGE_OFFERS.map((offer) => {
          const meta = offerMeta[offer.id];
          const Icon = meta.icon;
          const showIncome = offer.incomePerYear > 0 ? Math.round(offer.incomePerYear * incomeMultiplier) : 0;
          return (
            <Card key={offer.id} className={meta.done ? 'border-success/60 bg-success/5' : ''}>
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
                    <Icon className="h-5 w-5 text-primary" />
                  </div>
                  <Badge variant={meta.done ? 'default' : 'outline'} className={meta.done ? 'bg-success' : ''}>
                    {meta.done ? '已部署' : `-${offer.cost} 万`}
                  </Badge>
                </div>
                <CardTitle className="text-base">{offer.name}</CardTitle>
                <CardDescription>{offer.desc}</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col gap-3">
                {offer.incomePerYear > 0 && (
                  <div className="flex items-center gap-1.5 text-sm">
                    <Gauge className="h-4 w-4 text-success" />
                    <span className="text-success">
                      +{showIncome} 万/年收入{incomeMultiplier < 1 && <span className="text-muted-foreground">（未部署溯源，5折）</span>}
                    </span>
                  </div>
                )}
                {meta.done ? (
                  <div className="flex flex-col gap-2">
                    <div className="flex items-center gap-1.5 text-sm font-medium text-success">
                      <CheckCircle2 className="h-4 w-4" />
                      部署结果 · 已上线
                    </div>
                    <ul className="flex flex-col gap-1.5 rounded-lg border bg-muted/40 p-3">
                      {offer.deliverables.map((item, index) => (
                        <li key={index} className="flex items-start gap-1.5 text-xs leading-relaxed text-muted-foreground">
                          <Check className="mt-0.5 h-3 w-3 shrink-0 text-success" />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : (
                  <Button
                    variant="default"
                    size="sm"
                    className="w-full gap-2"
                    disabled={!started || budget < offer.cost}
                    onClick={() => handleDeploy(offer.id, handleFn[offer.id])}
                  >
                    <Database className="h-4 w-4" />
                    部署（-{offer.cost} 万）
                  </Button>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* 风险事件博弈（步骤12 的初评 → 风险 → 调整） */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between gap-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <AlertTriangle className="h-4 w-4 text-warning" />
              风险事件博弈 ⭐
            </CardTitle>
            <Badge variant="secondary">
              已处理 {risks.filter((r) => r.resolved).length}/{RISK_EVENTS.length}
            </Badge>
          </div>
          <CardDescription>
            三次估值迭代之间会遭遇合规抽查、对手抢数据、算法事故等风险事件。选择应对策略会真实扣减预算并影响年收入，全部留痕、可撤销。
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          {RISK_EVENTS.map((event) => {
            const state = risks.find((r) => r.eventId === event.id);
            const resolved = state?.resolved ?? false;
            const chosen = state?.choiceIndex ?? null;
            return (
              <div key={event.id} className={cn('rounded-lg border p-4', resolved ? 'border-success/60 bg-success/5' : 'bg-card')}>
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <ShieldAlert className={cn('h-4 w-4', resolved ? 'text-success' : 'text-warning')} />
                    <span className="text-sm font-semibold">{event.title}</span>
                  </div>
                  <Badge variant={resolved ? 'default' : 'outline'} className={resolved ? 'bg-success' : ''}>
                    {resolved ? '已应对' : '待应对'}
                  </Badge>
                </div>
                <p className="mt-2 text-sm text-muted-foreground">{event.desc}</p>
                <div className="mt-3 grid gap-2 sm:grid-cols-3">
                  {event.options.map((option, index) => {
                    const isChosen = chosen === index;
                    return (
                      <button
                        key={option.label}
                        type="button"
                        disabled={resolved}
                        onClick={() => handleRisk(event.id, index)}
                        className={cn(
                          'flex flex-col gap-1 rounded-lg border px-3 py-2.5 text-left transition-colors',
                          isChosen
                            ? 'border-success bg-success/5'
                            : resolved
                              ? 'cursor-default opacity-60'
                              : 'bg-card hover:bg-muted',
                        )}
                      >
                        <span className="text-sm font-medium">{option.label}</span>
                        <span className="text-xs text-muted-foreground">{option.desc}</span>
                        <span className="text-xs font-semibold">
                          支出 {option.cost} 万
                          {option.incomeDelta !== 0 && (
                            <span className={option.incomeDelta > 0 ? 'text-success' : 'text-destructive'}>
                              {' · 年收入' + (option.incomeDelta > 0 ? '+' : '') + option.incomeDelta + ' 万'}
                            </span>
                          )}
                        </span>
                      </button>
                    );
                  })}
                </div>
                {resolved && chosen !== null && (
                  <p className="mt-3 rounded-lg border border-dashed px-3 py-2 text-xs text-muted-foreground">
                    你的应对：「{event.options[chosen].label}」—— 已在操作留痕中记录，可撤销后重新选择。
                  </p>
                )}
              </div>
            );
          })}
          <div className="flex items-center justify-between rounded-lg border border-dashed px-3 py-2 text-sm">
            <span className="text-muted-foreground">风险事件累计年收入影响</span>
            <span className={cn('font-bold', riskIncome >= 0 ? 'text-success' : 'text-destructive')}>
              {riskIncome >= 0 ? '+' : ''}
              {riskIncome} 万/年
            </span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between gap-2">
            <CardTitle className="text-base">六维估值 ⭐</CardTitle>
            <Badge variant="secondary">
              数据资产综合评分
              <span className="ml-1 text-base font-bold text-primary">{totalScore}</span>
            </Badge>
          </div>
          <CardDescription>
            六个维度随你的管、治、用进度实时变化：采集越多越可用，治理越全越可信。口径为「治理六维」（可用性/可信性/完整性/可追溯性/标准化/合规性）。
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {VALUATION_DIMS.map((dim) => {
              const score = dimScores[dim.id];
              return (
                <div key={dim.id} className="rounded-lg border bg-card p-3">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-medium">{dim.name}</span>
                    <span className="text-sm font-bold text-primary">{score}</span>
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">{dim.desc}</p>
                  <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-muted">
                    <div
                      className="h-full rounded-full bg-primary transition-all"
                      style={{ width: `${score}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
          <div className="mt-3 flex items-start gap-2 rounded-lg border border-dashed px-3 py-2 text-xs text-muted-foreground">
            <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
            <span>
              口径说明：本实验的六维为「治理六维」——衡量数据资产的质量与合规水平；与海尔「共赢增值表」的生态六维（用户资源/资源方/生态总价值/收入/成本/边际收益）是两套不同口径，前者管质量、后者管生态增值，报告页两者都会呈现。
            </span>
          </div>
        </CardContent>
      </Card>

      <div className="flex items-center gap-2 rounded-lg border bg-card px-4 py-3 text-sm text-muted-foreground">
        <span>当前预算</span>
        <span className="font-bold text-foreground">{budget}</span>
        <span className="text-muted-foreground">万</span>
        <span className="ml-auto text-xs">
          生效年收入约 {effectiveIncome} 万/年（含风险影响与溯源折扣）；不想要的部署可随时撤销。
        </span>
      </div>
    </div>
  );
}
