// 操作留痕面板：审计日志时间线 + 可回滚操作
import { useState } from 'react';
import { History, RotateCcw, Wallet, CheckCircle2, AlertTriangle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import { useLab } from '@/store/lab-context';
import type { IAuditEntry, IAuditKind } from '@/data/lab';

const KIND_META: Record<IAuditKind, { label: string; variant: 'default' | 'outline' | 'secondary' | 'destructive' }> = {
  system: { label: '系统', variant: 'secondary' },
  purchase: { label: '采购', variant: 'default' },
  govern: { label: '治理', variant: 'outline' },
  usage: { label: '调用', variant: 'outline' },
  income: { label: '收入', variant: 'default' },
  error: { label: '异常', variant: 'destructive' },
  risk: { label: '风险', variant: 'destructive' },
};

export default function AuditPanel() {
  const { audit, rollback, budget } = useLab();
  const [open, setOpen] = useState(false);

  const handleRollback = (entry: IAuditEntry) => {
    const result = rollback(entry.id);
    if (result.ok) {
      setOpen(false);
    }
  };

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <History className="h-4 w-4" />
          操作留痕
          <Badge variant="secondary" className="ml-0.5">{audit.length}</Badge>
        </Button>
      </SheetTrigger>
      <SheetContent className="w-full sm:max-w-md">
        <SheetHeader>
          <SheetTitle>操作留痕 · 审计日志</SheetTitle>
          <SheetDescription>
            每一次采购、治理、调用与校验失败都被记录。可回滚的操作支持一键撤销，真正实现“填错可回溯”。
          </SheetDescription>
        </SheetHeader>
        <div className="mt-4 flex flex-col gap-3 overflow-y-auto pr-1">
          {audit.length === 0 && (
            <p className="text-sm text-muted-foreground">暂无操作记录，开始实验后这里会逐步留下审计痕迹。</p>
          )}
          {[...audit].reverse().map((entry) => {
            const meta = KIND_META[entry.kind];
            return (
              <div key={entry.id} className="rounded-lg border bg-card p-3">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <Badge variant={meta.variant}>{meta.label}</Badge>
                    <span className="text-sm font-medium">{entry.label}</span>
                  </div>
                  {(entry.kind === 'error' || entry.kind === 'risk') && <AlertTriangle className="h-4 w-4 text-destructive" />}
                  {entry.amount !== 0 && (
                    <span className={`text-sm font-semibold ${entry.amount > 0 ? 'text-success' : 'text-destructive'}`}>
                      {entry.amount > 0 ? '+' : ''}
                      {entry.amount} 万
                    </span>
                  )}
                </div>
                <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">{entry.detail}</p>
                <div className="mt-2 flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">{entry.time}</span>
                  {entry.undoable && !entry.rolledBack && (
                    <Button variant="outline" size="sm" className="h-7 gap-1 text-xs" onClick={() => handleRollback(entry)}>
                      <RotateCcw className="h-3 w-3" />
                      撤销此操作
                    </Button>
                  )}
                  {entry.rolledBack && (
                    <span className="flex items-center gap-1 text-xs text-muted-foreground">
                      <CheckCircle2 className="h-3 w-3" />
                      已回滚
                    </span>
                  )}
                </div>
              </div>
            );
          })}
          {audit.length > 0 && (
            <div className="mt-2 flex items-center justify-between rounded-lg border border-dashed p-3 text-sm">
              <span className="flex items-center gap-2 text-muted-foreground">
                <Wallet className="h-4 w-4" />
                当前预算
              </span>
              <span className="font-semibold">{budget} 万</span>
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
