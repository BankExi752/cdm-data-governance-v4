// 实验导览页：选择角色与目标、案例行业、开始实验、六步跃迁总览
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Check, Play } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { CASES, ROLE_OPTIONS, TARGET_OPTIONS } from '@/data/lab';
import { useLab } from '@/store/lab-context';
import { cn } from '@/lib/utils';

const STEPS = [
  { name: '统一管理', desc: '存得下 · 管得住' },
  { name: '汇聚采集', desc: '多源异构归集' },
  { name: '标准治理', desc: '去重 · 定标 · 补全' },
  { name: '高质量数据集', desc: '可用 · 可信 · 可交付' },
  { name: '知识资产化', desc: '语义化 · 可检索' },
  { name: '智能调用', desc: 'MCP · 智能体' },
];

export default function OverviewPage() {
  const { started, caseId, role, target, startExperiment, resetAll } = useLab();
  const navigate = useNavigate();
  const [pickedCase, setPickedCase] = useState<string | null>(null);
  const [pickedRole, setPickedRole] = useState<string>('steward');
  const [pickedTarget, setPickedTarget] = useState<string>('cost');

  const handleStart = (id: string) => {
    if (started) {
      startExperiment(id, role ?? 'steward', target ?? 'cost');
      navigate('/manage');
      return;
    }
    setPickedCase(id);
    if (id && pickedRole && pickedTarget) {
      startExperiment(id, pickedRole, pickedTarget);
      navigate('/manage');
    }
  };

  const roleLabel = ROLE_OPTIONS.find((r) => r.id === role)?.label ?? '未选择';
  const targetLabel = TARGET_OPTIONS.find((t) => t.id === target)?.label ?? '未选择';

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2">
          <Badge variant="secondary">AI 企业数据资产化与合规治理仿真实验</Badge>
        </div>
        <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">从散落数据到可调用的知识资产</h1>
        <p className="max-w-3xl text-muted-foreground">
          参考《企业智能：数据治理到高质量数据集的知识资产化构建》的框架，沿着「数据六步跃迁」完成管数据、治数据、用数据三个阶段的实验。
          每个按钮都真实生效：预算实时扣减、判定即时校验、操作全程留痕、填错一键回溯。
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-6">
        {STEPS.map((step, index) => (
          <div key={step.name} className="flex flex-col gap-1 rounded-lg border bg-card p-3">
            <span className="text-xs font-semibold text-primary">0{index + 1}</span>
            <span className="text-sm font-medium">{step.name}</span>
            <span className="text-xs text-muted-foreground">{step.desc}</span>
          </div>
        ))}
      </div>

      {!started && (
        <div className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <h2 className="text-lg font-semibold">步骤 0 · 角色与资金</h2>
            <p className="text-sm text-muted-foreground">
              领取 500 万预算，选择你的角色与「人单合一」目标，再选案例行业开始实验。角色与目标会全程留痕并影响复盘点评。
            </p>
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">选择你的角色</CardTitle>
                <CardDescription>不同角色在复盘点评中的关注点不同</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col gap-2">
                {ROLE_OPTIONS.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setPickedRole(item.id)}
                    className={cn(
                      'flex items-center justify-between gap-2 rounded-lg border px-3 py-2.5 text-left transition-colors',
                      pickedRole === item.id ? 'border-primary bg-primary/5' : 'bg-card hover:bg-muted',
                    )}
                  >
                    <span>
                      <span className="block text-sm font-medium">{item.label}</span>
                      <span className="block text-xs text-muted-foreground">{item.desc}</span>
                    </span>
                    {pickedRole === item.id && <Check className="h-4 w-4 shrink-0 text-primary" />}
                  </button>
                ))}
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">选择「人单合一」目标</CardTitle>
                <CardDescription>目标决定你的经营重心，会在复盘点评中被核验</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col gap-2">
                {TARGET_OPTIONS.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setPickedTarget(item.id)}
                    className={cn(
                      'flex items-center justify-between gap-2 rounded-lg border px-3 py-2.5 text-left transition-colors',
                      pickedTarget === item.id ? 'border-primary bg-primary/5' : 'bg-card hover:bg-muted',
                    )}
                  >
                    <span>
                      <span className="block text-sm font-medium">{item.label}</span>
                      <span className="block text-xs text-muted-foreground">{item.desc}</span>
                    </span>
                    {pickedTarget === item.id && <Check className="h-4 w-4 shrink-0 text-primary" />}
                  </button>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      <div className="flex flex-col gap-4">
        <h2 className="text-lg font-semibold">选择案例行业</h2>
        {!started && (
          <p className="text-sm text-muted-foreground">
            四大案例均基于四川真实产业，数据资产与风险事件随行业切换。点击「开始实验」，500 万预算即刻到账。
          </p>
        )}
        <div className="grid gap-4 sm:grid-cols-2">
          {CASES.map((item) => {
            const isCurrent = started && caseId === item.id;
            const isPicked = pickedCase === item.id;
            return (
              <Card key={item.id} className={cn((isCurrent || isPicked) && 'border-primary ring-1 ring-primary')}>
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <CardTitle className="text-lg">{item.name}</CardTitle>
                      <CardDescription>{item.sector}</CardDescription>
                    </div>
                    {isCurrent && (
                      <Badge className="gap-1">
                        <Check className="h-3 w-3" />
                        当前案例
                      </Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="flex flex-col gap-3">
                  <p className="text-sm text-muted-foreground">{item.desc}</p>
                  <div className="flex flex-wrap gap-1.5">
                    {item.scenes.map((scene) => (
                      <Badge key={scene} variant="outline" className="font-normal">
                        {scene}
                      </Badge>
                    ))}
                  </div>
                  {started ? (
                    <Button
                      variant={isCurrent ? 'outline' : 'default'}
                      className="gap-2"
                      disabled={isCurrent}
                      onClick={() => handleStart(item.id)}
                    >
                      {isCurrent ? '正在实验此案例' : '切换到此案例'}
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  ) : (
                    <Button className="gap-2" onClick={() => handleStart(item.id)}>
                      <Play className="h-4 w-4" />
                      开始实验
                    </Button>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
        {started && (
          <div className="flex flex-col gap-2 rounded-lg border border-dashed bg-card p-4">
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
              <span>
                当前实验案例：<span className="font-medium">{CASES.find((c) => c.id === caseId)?.name}</span>
              </span>
              <span>
                角色：<span className="font-medium">{roleLabel}</span>
              </span>
              <span>
                目标：<span className="font-medium">{targetLabel}</span>
              </span>
            </div>
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm text-muted-foreground">
                —— 已开始，预算 500 万到账，风险事件已就位。前往「管数据」采购数据资产。
              </p>
              <Button variant="outline" size="sm" onClick={resetAll}>
                重置实验
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
