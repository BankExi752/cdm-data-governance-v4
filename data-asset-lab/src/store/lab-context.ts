// 实验全局状态：Context 定义、hook 与操作签名
// EXPORTS: ILabCtx, LabContext, useLab
import { createContext, useContext } from 'react';
import type { IAuditEntry, ILabState } from '@/data/lab';

export interface ICheckResult {
  ok: boolean;
  message: string;
}

export interface ILabCtx extends ILabState {
  startExperiment: (caseId: string, role: string, target: string) => void;
  purchaseAsset: (assetId: string) => ICheckResult;
  submitCleanCheck: (sameIds: string[]) => ICheckResult;
  submitMaskCheck: (selectedIds: string[]) => ICheckResult;
  deployTrace: () => ICheckResult;
  submitLabel: (quantities: Record<string, number>) => ICheckResult;
  buildGraph: () => ICheckResult;
  buyAlgorithm: () => ICheckResult;
  hireExpert: () => ICheckResult;
  resolveRisk: (eventId: string, choiceIndex: number) => ICheckResult;
  rollback: (auditId: string) => ICheckResult;
  resetAll: () => void;
  audit: IAuditEntry[];
}

export const LabContext = createContext<ILabCtx | null>(null);

export function useLab(): ILabCtx {
  const ctx = useContext(LabContext);
  if (!ctx) {
    throw new Error('useLab must be used within LabProvider');
  }
  return ctx;
}
