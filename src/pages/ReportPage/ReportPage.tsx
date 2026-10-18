// 能力画像页：数据资产经营报告（图文并茂版）
import { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import { AlertCircle, Lightbulb, TrendingUp, Wallet } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Image } from '@/components/ui/image';
import { CASES, RISK_EVENTS, ROLE_OPTIONS, TARGET_OPTIONS, USAGE_OFFERS, VALUATION_DIMS } from '@/data/lab';
import { useLab } from '@/store/lab-context';

// 与主题变量 --chart-1..5 严格一致的 hex 字面量
const CHART_COLORS = ['#1D49AF', '#1C8779', '#F59F0A', '#65758B', '#B897ED'];

const BASE = (import.meta.env.MIAODA_CLIENT_BASE_PATH || '').replace(/\/$/, '') + '/';

// 海尔「共赢增值表」生态六维（口径对照用）
const ECO_DIMS = [
  { name: '用户资源', desc: '可触达的用户规模与活跃度' },
  { name: '资源方', desc: '生态资源方的数量与质量' },
  { name: '生态总价值', desc: '生态整体创造的价值总量' },
  { name: '收入', desc: '直接经营收入' },
  { name: '成本', desc: '投入与运营成本' },
  { name: '边际收益', desc: '收入 − 成本的动态边际' },
];

export default function ReportPage() {
  const { audit, caseId, started, budget, algorithmBought, expertHired, cleaned, masked, traced, labeled, graphBuilt, purchased, role, target, risks } = useLab();

  const report = useMemo(() => {
    // 只统计未回滚的条目
    const valid = audit.filter((a) => !a.rolledBack);
    const totalInvest = valid.filter((a) => a.amount < 0).reduce((sum, a) => sum - a.amount, 0);

    // 收益联动：未部署可信溯源 → 算法/专家收益打 5 折（V8.1 核心壁垒联动）
    const incomeMultiplier = traced ? 1 : 0.5;
    const baseIncome =
      ((algorithmBought ? USAGE_OFFERS.find((o) => o.id === 'u-algo')?.incomePerYear ?? 0 : 0) +
        (expertHired ? USAGE_OFFERS.find((o) => o.id === 'u-expert')?.incomePerYear ?? 0 : 0)) *
      incomeMultiplier;
    // 风险事件对年收入的影响（正=增收，负=减收）
    const riskIncome = risks
      .filter((r) => r.resolved && r.choiceIndex !== null)
      .reduce((sum, r) => {
        const event = RISK_EVENTS.find((e) => e.id === r.eventId);
        const choice = event?.options[r.choiceIndex ?? 0];
        return sum + (choice?.incomeDelta ?? 0);
      }, 0);
    const yearlyIncome = baseIncome + riskIncome;
    const margin = yearlyIncome - totalInvest;

    // 开支明细（按类别，含风险事件支出）
    const spendByKind = [
      { name: '数据采购', value: valid.filter((a) => a.kind === 'purchase').reduce((s, a) => s - a.amount, 0) },
      { name: '治理与标注', value: valid.filter((a) => a.kind === 'govern').reduce((s, a) => s - a.amount, 0) },
      { name: '智能调用', value: valid.filter((a) => a.kind === 'usage').reduce((s, a) => s - a.amount, 0) },
      { name: '风险应对', value: valid.filter((a) => a.kind === 'risk').reduce((s, a) => s - a.amount, 0) },
    ].filter((x) => x.value > 0);

    const incomeParts: { name: string; value: number }[] = [];
    if (algorithmBought) incomeParts.push({ name: '故障预测算法服务', value: Math.round((USAGE_OFFERS.find((o) => o.id === 'u-algo')?.incomePerYear ?? 0) * incomeMultiplier) });
    if (expertHired) incomeParts.push({ name: '算法专家咨询', value: Math.round((USAGE_OFFERS.find((o) => o.id === 'u-expert')?.incomePerYear ?? 0) * incomeMultiplier) });
    for (const r of risks) {
      if (!r.resolved || r.choiceIndex === null) continue;
      const event = RISK_EVENTS.find((e) => e.id === r.eventId);
      const choice = event?.options[r.choiceIndex];
      if (choice && choice.incomeDelta !== 0) {
        incomeParts.push({ name: `风险·${event?.title ?? ''}`, value: choice.incomeDelta });
      }
    }

    // 六维估值（与用数据页同一套计算口径）
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

    // 复盘点评（含角色 / 目标 / 风险事件核验）
    const tips: string[] = [];
    if (!started) tips.push('尚未开始实验：前往「实验导览」选择角色、目标与案例行业，500 万预算即刻到账。');
    if (started && purchased.length === 0) tips.push('还没有采购任何数据资产：先去「管数据」把三类数据源归集起来。');
    if (cleaned && !masked) tips.push('已完成同质异码清洗，建议继续做字段脱敏，补上合规短板。');
    if (!cleaned) tips.push('未做同质异码清洗：口径不统一会让 AI 一问三种答案，建议优先治理。');
    if (!traced) tips.push('未部署可信溯源：数据出了事无法回滚，业务不敢用——这是「核心壁垒」，且算法/专家收益按 5 折兑现。');
    if (traced && (algorithmBought || expertHired)) tips.push('可信溯源已部署，算法与专家收益全额兑现——「可信是收益生效的前提」得到验证。');
    if (labeled && !graphBuilt) tips.push('数据已标注入库，可以建知识图谱，把数据升维成知识资产。');
    if (!algorithmBought) tips.push('算法（+50 万/年）是回报最高的投入之一，优先购买。');
    if (!expertHired) tips.push('专家（+60 万/年）回报最高，优先聘请。');
    if (algorithmBought && expertHired) tips.push('算法 + 专家均已部署，模型与产线双重加持，边际收益为正。');
    const unresolvedRisks = risks.filter((r) => !r.resolved).length;
    if (unresolvedRisks > 0) tips.push(`还有 ${unresolvedRisks} 个风险事件未应对：合规抽查、对手抢数据、算法事故会真实影响预算与年收入，建议到「用数据」页尽快处理。`);
    if (target === 'cost' && totalInvest < 50) tips.push('你的目标是「降本增效」：当前总投入未超过 50 万阈值，继续以最小成本完成治理闭环。');
    if (target === 'compliance' && !masked) tips.push('你的目标是「合规避险」：尚未完成脱敏，存在最高 100 万罚款敞口，优先补齐。');
    if (target === 'value' && margin <= 0) tips.push('你的目标是「价值创造」（年增收 200 万）：当前边际收益为负，需部署算法/专家并处理好风险事件。');
    if (role === 'steward' && !traced) tips.push('作为数据管家，可信溯源是你的本分——未部署前业务数据无法放心上产线。');
    if (role === 'pm' && !algorithmBought && !expertHired) tips.push('作为数据产品经理，变现才是关键——算法与专家尚未部署，收入仍为零。');
    if (role === 'cdo' && (masked || cleaned) && !graphBuilt) tips.push('作为首席数据官，应统筹全局——治理已完成，建议推进知识图谱与智能调用，兑现数据价值。');
    if (incomeParts.length > 0 && margin <= 0) tips.push('当前年收入尚不能覆盖总投入，需继续扩大调用场景或等待收益累积。');

    const maxSpend = Math.max(1, ...spendByKind.map((x) => x.value));
    return { totalInvest, yearlyIncome, margin, spendByKind, incomeParts, tips, maxSpend, dimScores, totalScore, incomeMultiplier, riskIncome };
  }, [audit, algorithmBought, expertHired, started, purchased.length, cleaned, masked, traced, labeled, graphBuilt, role, target, risks]);

  // 六维估值雷达图
  const radarOption = useMemo(
    () => ({
      color: [CHART_COLORS[0]],
      tooltip: { trigger: 'item' },
      radar: {
        indicator: VALUATION_DIMS.map((dim) => ({ name: dim.name, max: 100 })),
        radius: '68%',
        splitArea: { areaStyle: { color: ['rgba(29,73,175,0.02)', 'rgba(29,73,175,0.05)'] } },
        axisName: { color: '#4B5563', fontSize: 12 },
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              value: VALUATION_DIMS.map((dim) => report.dimScores[dim.id]),
              name: '数据资产能力',
              areaStyle: { color: 'rgba(29,73,175,0.2)' },
              lineStyle: { color: CHART_COLORS[0], width: 2 },
              symbolSize: 4,
            },
          ],
        },
      ],
    }),
    [report.dimScores],
  );

  // 开支构成环形图
  const spendPieOption = useMemo(
    () => ({
      color: CHART_COLORS,
      tooltip: { trigger: 'item', formatter: '{b}：{c} 万（{d}%）' },
      legend: { bottom: 0, textStyle: { fontSize: 12 } },
      series: [
        {
          name: '开支构成',
          type: 'pie',
          radius: ['42%', '68%'],
          center: ['50%', '44%'],
          avoidLabelOverlap: true,
          itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
          label: { show: true, formatter: '{b}\n{c} 万' },
          data: report.spendByKind.map((item) => ({ name: item.name, value: item.value })),
        },
      ],
    }),
    [report.spendByKind],
  );

  // 收入构成柱状图
  const incomeBarOption = useMemo(
    () => ({
      color: [CHART_COLORS[1]],
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: 40, right: 16, top: 24, bottom: 32 },
      xAxis: {
        type: 'category',
        data: report.incomeParts.length > 0 ? report.incomeParts.map((item) => item.name) : ['暂无收入'],
        axisLabel: { fontSize: 11, color: '#4B5563', interval: 0 },
      },
      yAxis: { type: 'value', name: '万/年', nameTextStyle: { color: '#9CA3AF' }, axisLabel: { color: '#9CA3AF' } },
      series: [
        {
          name: '年收入',
          type: 'bar',
          barWidth: 42,
          itemStyle: { borderRadius: [6, 6, 0, 0] },
          label: { show: true, position: 'top', formatter: '{c} 万/年', color: '#374151', fontSize: 11 },
          data: report.incomeParts.length > 0 ? report.incomeParts.map((item) => item.value) : [0],
        },
      ],
    }),
    [report.incomeParts],
  );

  const caseName = CASES.find((c) => c.id === caseId)?.name ?? '未选择';
  const roleLabel = ROLE_OPTIONS.find((r) => r.id === role)?.label ?? '未选择';
  const targetLabel = TARGET_OPTIONS.find((t) => t.id === target)?.label ?? '未选择';

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-1">
        <Badge variant="secondary" className="w-fit">数据资产经营报告</Badge>
        <h1 className="text-2xl font-bold tracking-tight">能力画像</h1>
        <p className="max-w-3xl text-muted-foreground">
          数据资产回答「我们有什么」；知识资产回答「我们知道什么」。总投入、累计收入与边际收益一笔笔算给你看。
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Badge variant="outline">案例：{caseName}</Badge>
        <Badge variant="outline">角色：{roleLabel}</Badge>
        <Badge variant="outline">目标：{targetLabel}</Badge>
        {started && <Badge variant="secondary">剩余预算 {budget} 万</Badge>}
      </div>

      {/* 主题横幅主图：数据六步跃迁 */}
      <Card className="overflow-hidden">
        <Image
          src={`${BASE}images/report-hero.png`}
          alt="数据六步跃迁：统一管理 → 汇聚采集 → 标准治理 → 高质量数据集 → 知识资产化 → 智能调用"
          className="aspect-[16/7] w-full object-cover"
        />
      </Card>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-1.5">
              <Wallet className="h-4 w-4" />
              总投入
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{report.totalInvest}</div>
            <div className="text-sm text-muted-foreground">万（未回滚的支出合计）</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-1.5">
              <TrendingUp className="h-4 w-4" />
              累计年收入
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-success">{report.yearlyIncome}</div>
            <div className="text-sm text-muted-foreground">
              万/年（算法 + 专家{report.incomeMultiplier < 1 ? '，未部署溯源按 5 折' : ''} + 风险影响 {report.riskIncome >= 0 ? '+' : ''}
              {report.riskIncome}）
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-1.5">
              <Lightbulb className="h-4 w-4" />
              边际收益
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className={`text-3xl font-bold ${report.margin >= 0 ? 'text-success' : 'text-destructive'}`}>
              {report.margin >= 0 ? '+' : ''}
              {report.margin}
            </div>
            <div className="text-sm text-muted-foreground">万（年收入 − 总投入）</div>
          </CardContent>
        </Card>
      </div>

      {/* 六维估值雷达图 */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between gap-2">
            <CardTitle className="text-base">六维估值 · 能力雷达</CardTitle>
            <Badge variant="secondary">
              数据资产综合评分
              <span className="ml-1 text-base font-bold text-primary">{report.totalScore}</span>
            </Badge>
          </div>
          <CardDescription>六个维度随管、治、用进度实时变化：采集越多越可用，治理越全越可信。</CardDescription>
        </CardHeader>
        <CardContent>
          <ReactECharts option={radarOption} style={{ height: 320 }} notMerge />
        </CardContent>
      </Card>

      {/* 口径说明：治理六维 vs 海尔生态六维 */}
      <Card className="border-dashed">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
            口径对照：治理六维 vs 海尔「共赢增值表」生态六维
          </CardTitle>
          <CardDescription>
            本实验的六维估值采用「治理六维」（上图雷达），衡量数据资产的质量与合规水平；参考方案中的「生态六维」是另一套经营口径，二者互补不冲突。
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 lg:grid-cols-2">
            <div className="rounded-lg border bg-card p-4">
              <h3 className="text-sm font-semibold text-primary">治理六维（本实验采用）</h3>
              <ul className="mt-3 flex flex-col gap-2">
                {VALUATION_DIMS.map((dim) => (
                  <li key={dim.id} className="flex items-start gap-2 text-sm">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                    <span>
                      <span className="font-medium">{dim.name}</span>
                      <span className="text-muted-foreground"> —— {dim.desc}；当前得分 {report.dimScores[dim.id]}</span>
                    </span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="rounded-lg border bg-card p-4">
              <h3 className="text-sm font-semibold text-success">海尔生态六维（共赢增值表，参考口径）</h3>
              <ul className="mt-3 flex flex-col gap-2">
                {ECO_DIMS.map((dim) => (
                  <li key={dim.name} className="flex items-start gap-2 text-sm">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-success" />
                    <span>
                      <span className="font-medium">{dim.name}</span>
                      <span className="text-muted-foreground"> —— {dim.desc}</span>
                    </span>
                  </li>
                ))}
              </ul>
              <p className="mt-3 text-xs text-muted-foreground">
                本实验的「累计年收入 − 总投入 = 边际收益」即对应生态六维的边际收益口径：收入覆盖成本后转正，就是「数据管理是利润中心」的实证。
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">开支构成</CardTitle>
            <CardDescription>按阶段统计，回滚过的支出已剔除</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            {report.spendByKind.length === 0 ? (
              <p className="text-sm text-muted-foreground">暂无开支，去「管数据」采购数据资产开始吧。</p>
            ) : (
              <>
                <ReactECharts option={spendPieOption} style={{ height: 240 }} notMerge />
                <div className="flex flex-col gap-1.5">
                  {report.spendByKind.map((item, index) => (
                    <div key={item.name} className="flex items-center justify-between text-sm">
                      <span className="flex items-center gap-2">
                        <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }} />
                        {item.name}
                      </span>
                      <span className="font-semibold">{item.value} 万</span>
                    </div>
                  ))}
                  <div className="mt-2 flex items-center justify-between rounded-lg border border-dashed px-3 py-2 text-sm">
                    <span className="text-muted-foreground">当前预算余额</span>
                    <span className="font-bold">{budget} 万</span>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">收入构成（为什么累计收入是这么多）</CardTitle>
            <CardDescription>一笔笔算给你看</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            {report.incomeParts.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                暂无收入来源。部署「故障预测算法」（+50 万/年）与「算法专家」（+60 万/年）后这里会出现明细。
              </p>
            ) : (
              <>
                <ReactECharts option={incomeBarOption} style={{ height: 240 }} notMerge />
                <div className="flex flex-col gap-2">
                  {report.incomeParts.map((item) => (
                    <div key={item.name} className="flex items-center justify-between rounded-lg border bg-card px-3 py-2 text-sm">
                      <span>{item.name}</span>
                      <span className="font-semibold text-success">+{item.value} 万/年</span>
                    </div>
                  ))}
                  <div className="flex items-center justify-between rounded-lg border border-dashed px-3 py-2 text-sm">
                    <span className="text-muted-foreground">合计累计收入</span>
                    <span className="font-bold text-success">{report.yearlyIncome} 万/年</span>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between gap-2">
            <CardTitle className="text-base">复盘点评（重来一次你会改哪里？）</CardTitle>
            <Badge variant="secondary">案例：{caseName}</Badge>
          </div>
          <CardDescription>基于你的实际进度生成的改进建议</CardDescription>
        </CardHeader>
        <CardContent>
          {report.tips.length === 0 ? (
            <p className="text-sm text-muted-foreground">暂无建议。</p>
          ) : (
            <ul className="flex flex-col gap-2">
              {report.tips.map((tip, index) => (
                <li key={index} className="flex items-start gap-2 text-sm">
                  {tip.startsWith('未') || tip.startsWith('尚未') || tip.startsWith('没有') ? (
                    <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-warning" />
                  ) : (
                    <TrendingUp className="mt-0.5 h-4 w-4 shrink-0 text-success" />
                  )}
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
