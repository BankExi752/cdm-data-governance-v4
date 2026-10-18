// 治数据页：第二阶，清洗去重 / 脱敏 / 可信溯源 / 质检标注
import { useState } from 'react';
import type { ReactNode } from 'react';
import {
  AlertTriangle,
  Check,
  CheckCircle2,
  Eye,
  GitBranch,
  ScanSearch,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import { toast } from 'sonner';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ANNO_TASKS, CODE_PAIRS, MASK_FIELDS, MAX_PLATFORM_FEE } from '@/data/lab';
import { useLab } from '@/store/lab-context';
import { cn } from '@/lib/utils';

function SectionCard({
  step,
  title,
  desc,
  done,
  results,
  children,
}: {
  step: string;
  title: string;
  desc: string;
  done?: boolean;
  results?: string[];
  children: ReactNode;
}) {
  return (
    <Card className={cn(done && 'border-success/60 bg-success/5')}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">
              {step}
            </span>
            <CardTitle className="text-base">{title}</CardTitle>
          </div>
          {done && (
            <Badge className="bg-success">
              <Check className="mr-0.5 h-3 w-3" />
              已完成
            </Badge>
          )}
        </div>
        <CardDescription>{desc}</CardDescription>
      </CardHeader>
      <CardContent>
        {done && results && results.length > 0 && (
          <div className="mb-3 flex flex-col gap-2">
            <div className="flex items-center gap-1.5 text-sm font-medium text-success">
              <CheckCircle2 className="h-4 w-4" />
              治理结果
            </div>
            <ul className="flex flex-col gap-1.5 rounded-lg border bg-muted/40 p-3">
              {results.map((item, index) => (
                <li key={index} className="flex items-start gap-1.5 text-xs leading-relaxed text-muted-foreground">
                  <Check className="mt-0.5 h-3 w-3 shrink-0 text-success" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}
        {children}
      </CardContent>
    </Card>
  );
}

export default function GovernPage() {
  const { cleaned, masked, traced, labeled, submitCleanCheck, submitMaskCheck, deployTrace, submitLabel, budget, started } = useLab();

  // 同质异码判定
  const [cleanPicks, setCleanPicks] = useState<string[]>([]);
  // 脱敏勾选
  const [maskPicks, setMaskPicks] = useState<string[]>([]);
  // 质检标注数量
  const [quantities, setQuantities] = useState<Record<string, string>>({});

  const togglePick = (list: string[], setList: (v: string[]) => void, id: string) => {
    if (list.includes(id)) {
      setList(list.filter((x) => x !== id));
    } else {
      setList([...list, id]);
    }
  };

  const handleClean = () => {
    const result = submitCleanCheck(cleanPicks);
    if (result.ok) {
      toast.success(result.message);
    } else {
      toast.error(result.message);
    }
  };

  const handleMask = () => {
    const result = submitMaskCheck(maskPicks);
    if (result.ok) {
      toast.success(result.message);
    } else {
      toast.error(result.message);
    }
  };

  const handleTrace = () => {
    const result = deployTrace();
    if (result.ok) {
      toast.success(result.message);
    } else {
      toast.error(result.message);
    }
  };

  const totalLabelCost = Object.entries(quantities).reduce((sum, [id, v]) => {
    const task = ANNO_TASKS.find((t) => t.id === id);
    const qty = Number(v) || 0;
    return sum + qty * (task?.unitPrice ?? 0);
  }, MAX_PLATFORM_FEE);

  const handleLabel = () => {
    const parsed: Record<string, number> = {};
    for (const task of ANNO_TASKS) {
      parsed[task.id] = Number(quantities[task.id]) || 0;
    }
    const result = submitLabel(parsed);
    if (result.ok) {
      toast.success(result.message);
    } else {
      toast.error(result.message);
    }
  };

  const cleanOk = CODE_PAIRS.filter((p) => p.same).map((p) => p.id);
  const cleanHint = `提示：共 ${cleanOk.length} 对是同一设备（名称相似不代表同一物，参数线索才是依据）`;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-1">
        <Badge variant="secondary" className="w-fit">第二阶 · 标准治理</Badge>
        <h1 className="text-2xl font-bold tracking-tight">治数据：从“存下来”到“可信可用”</h1>
        <p className="max-w-3xl text-muted-foreground">
          治理不是一次性搬运，而是把「持续供数」做成可运维的产线。每一步都有校验：判定错误会即时提示并留痕，可重新判定；扣费操作可一键撤销。
        </p>
      </div>

      {!started && (
        <div className="flex items-center gap-2 rounded-lg border border-destructive/40 bg-destructive/5 px-4 py-3 text-sm text-destructive">
          <AlertTriangle className="h-4 w-4" />
          实验未开始，请先到「实验导览」页选择案例并开始实验。
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <SectionCard
          step="⑤"
          title="清洗去重 · 找出同质异码"
          desc={cleanHint}
          done={cleaned}
          results={cleaned ? [
            '识别 3 对同质异码并统一编码：电堆A=燃料电池A、压缩机01=CMP-001、储氢罐3号=TK-H2-03',
            '主数据台账已建立，冗余编码停用并冻结入口，杜绝重复采购与库存虚高',
            '消除口径失真：AI 对同一设备的回答从「三种答案」收敛为一种',
          ] : undefined}
        >
          <div className="flex flex-col gap-2">
            {CODE_PAIRS.map((pair) => {
              const picked = cleanPicks.includes(pair.id);
              return (
                <button
                  key={pair.id}
                  type="button"
                  disabled={cleaned}
                  onClick={() => togglePick(cleanPicks, setCleanPicks, pair.id)}
                  className={cn(
                    'flex flex-col gap-1 rounded-lg border px-3 py-2.5 text-left transition-colors',
                    picked
                      ? 'border-primary bg-primary/5'
                      : 'bg-card hover:bg-muted',
                    cleaned && 'cursor-default opacity-70',
                  )}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-medium">
                      {pair.a} <span className="text-muted-foreground">=</span> {pair.b}
                    </span>
                    <span className={cn('text-xs', picked ? 'text-primary' : 'text-muted-foreground')}>
                      {picked ? '✓ 判定为同一设备' : '点击判定为同一设备'}
                    </span>
                  </div>
                  <span className="text-xs text-muted-foreground">线索：{pair.hint}</span>
                </button>
              );
            })}
            <Button className="mt-1 gap-2" disabled={cleaned || !started} onClick={handleClean}>
              <ScanSearch className="h-4 w-4" />
              提交判定
            </Button>
          </div>
        </SectionCard>

        <SectionCard
          step="⑥"
          title="数据脱敏 · 勾选敏感字段"
          desc="涉及客户个人、合同财务、人员位置的字段必须脱敏；纯设备工况（温度/压力）不用脱。勾选并确认，费用 20 万。"
          done={masked}
          results={masked ? [
            '5 个敏感字段完成脱敏：客户姓名、客户身份证号、银行账号、合同金额、人员定位',
            '敏感信息命中即阻断并隔离，全过程留痕可追溯',
            '合规性维度提升：数据可放心用于 AI 训练与业务分析',
          ] : undefined}
        >
          <div className="grid grid-cols-2 gap-2">
            {MASK_FIELDS.map((field) => {
              const picked = maskPicks.includes(field.id);
              return (
                <button
                  key={field.id}
                  type="button"
                  disabled={masked}
                  onClick={() => togglePick(maskPicks, setMaskPicks, field.id)}
                  className={cn(
                    'flex items-center justify-between gap-2 rounded-lg border px-3 py-2 text-sm transition-colors',
                    picked ? 'border-primary bg-primary/5' : 'bg-card hover:bg-muted',
                    masked && 'cursor-default opacity-70',
                  )}
                >
                  <span>{field.name}</span>
                  <Badge variant={field.sensitive ? 'default' : 'outline'} className="text-[10px]">
                    {field.sensitive ? '敏感' : '非敏感'}
                  </Badge>
                </button>
              );
            })}
          </div>
          <Button className="mt-3 w-full gap-2" disabled={masked || !started} onClick={handleMask}>
            <Eye className="h-4 w-4" />
            确认脱敏（-20 万）
          </Button>
        </SectionCard>

        <SectionCard
          step="⑦"
          title="可信溯源 ⭐ 核心壁垒"
          desc="版本 · 血缘 · 台账——数据出了问题能追溯到源头，敢给业务用、敢给 AI 训练。部署后可随时回滚任意操作，费用 30 万。"
          done={traced}
          results={traced ? [
            '血缘追溯上线：任一字段可回溯到源系统，全程记录「数据从哪来、被谁改过」',
            '操作留痕上线：所有操作可审计、可复核，异常 30 分钟内可恢复',
            '版本回滚上线：保留回滚脚本，业务敢把生产数据交给 AI 产线',
          ] : undefined}
        >
          <div className="grid grid-cols-2 gap-2">
            {[
              { icon: GitBranch, label: '血缘追溯' },
              { icon: ScanSearch, label: '操作留痕' },
              { icon: Sparkles, label: '版本回滚' },
              { icon: ShieldCheck, label: '跨域授权' },
            ].map(({ icon: Icon, label }) => (
              <div key={label} className="flex items-center gap-2 rounded-lg border bg-card px-3 py-2 text-sm">
                <Icon className="h-4 w-4 text-primary" />
                {label}
              </div>
            ))}
          </div>
          <Button className="mt-3 w-full gap-2" disabled={traced || !started || budget < 30} onClick={handleTrace}>
            <ShieldCheck className="h-4 w-4" />
            部署可信溯源体系（-30 万）
          </Button>
        </SectionCard>

        <SectionCard
          step="⑧"
          title="质检标注 · 自己算标注方案"
          desc="单价 × 数量 = 标注费，另需平台基础费 20 万（算力+质检人力，无论标多少都要出）。预算不足会拦截并提示。"
          done={labeled}
          results={
            labeled
              ? (() => {
                  const parts: string[] = [];
                  for (const task of ANNO_TASKS) {
                    const qty = Number(quantities[task.id]) || 0;
                    if (qty > 0) {
                      const total = qty * task.unitPrice;
                      parts.push(`${task.name} ${qty} ${task.unit}：产出 ${qty} 条标注样本，费用 ${Math.round(total * 100) / 100} 万`);
                    }
                  }
                  parts.push(`平台基础费 ${MAX_PLATFORM_FEE} 万（算力+质检人力），标注成果已验收、可训练可评测`);
                  return parts;
                })()
              : undefined
          }
        >
          <div className="flex flex-col gap-3">
            {ANNO_TASKS.map((task) => (
              <div key={task.id} className="flex items-center gap-3 rounded-lg border bg-card px-3 py-2.5">
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-medium">{task.name}</div>
                  <div className="truncate text-xs text-muted-foreground">
                    {task.desc} · {task.unitPrice} 万/{task.unit}
                  </div>
                </div>
                <div className="flex w-28 items-center gap-1">
                  <Input
                    type="number"
                    min={0}
                    disabled={labeled}
                    value={quantities[task.id] ?? ''}
                    placeholder="数量"
                    onChange={(e) => setQuantities((prev) => ({ ...prev, [task.id]: e.target.value }))}
                  />
                </div>
              </div>
            ))}
            <div className="flex items-center justify-between rounded-lg border border-dashed px-3 py-2 text-sm">
              <span className="text-muted-foreground">标注费用合计（含平台费 {MAX_PLATFORM_FEE} 万）</span>
              <span className="font-bold">{Math.round(totalLabelCost * 100) / 100} 万</span>
            </div>
            <Button className="w-full gap-2" disabled={labeled || !started} onClick={handleLabel}>
              <Check className="h-4 w-4" />
              提交标注方案并付款
            </Button>
          </div>
        </SectionCard>
      </div>

      <div className="flex items-center gap-2 rounded-lg border bg-card px-4 py-3 text-sm text-muted-foreground">
        <Label className="text-muted-foreground">当前预算</Label>
        <span className="font-bold text-foreground">{budget}</span>
        <span className="text-muted-foreground">万</span>
        <span className="ml-auto text-xs">填错不必重来：打开右上角「操作留痕」，可撤销最近一次扣费操作。</span>
      </div>
    </div>
  );
}
