// 管数据页：第一阶，采购三类六项数据资产（随行业差异化）
import { useMemo, useState } from 'react';
import { CheckCircle2, ShoppingCart, Wallet } from 'lucide-react';
import { toast } from 'sonner';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { getAssets } from '@/data/lab';
import type { IAssetCategory, IDataAsset } from '@/data/lab';
import { useLab } from '@/store/lab-context';

const CATEGORY_META: Record<IAssetCategory, { label: string; desc: string }> = {
  structured: { label: '结构化数据', desc: '库表直连：业务库表、订单、日志' },
  unstructured: { label: '非结构化数据', desc: '文件纳管：图像、视频、影像' },
  semi: { label: '半结构化数据', desc: '文档+日志：合同、操作日志' },
};

export default function ManagePage() {
  const { started, budget, purchased, purchaseAsset, caseId } = useLab();
  const [purchasing, setPurchasing] = useState<string | null>(null);

  const assets = useMemo(() => getAssets(caseId), [caseId]);

  const grouped = useMemo(() => {
    const order: IAssetCategory[] = ['structured', 'unstructured', 'semi'];
    return order.map((category) => ({
      category,
      assets: assets.filter((a) => a.category === category),
    }));
  }, [assets]);

  const handlePurchase = (asset: IDataAsset) => {
    if (purchasing) return;
    setPurchasing(asset.id);
    window.setTimeout(() => {
      const result = purchaseAsset(asset.id);
      if (result.ok) {
        toast.success(result.message);
      } else {
        toast.error(result.message);
      }
      setPurchasing(null);
    }, 300);
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-1">
        <Badge variant="secondary" className="w-fit">第一阶 · 汇聚采集</Badge>
        <h1 className="text-2xl font-bold tracking-tight">管数据：采购数据资产</h1>
        <p className="max-w-3xl text-muted-foreground">
          从数据源归集到统一底座。两类手法完全不同，但共用一套规范标准、一个知识资产出口。采购后预算实时扣减，操作自动留痕，可随时在「操作留痕」中撤销。
        </p>
      </div>

      <div className="flex items-center gap-2 rounded-lg border bg-card px-4 py-3">
        <Wallet className="h-5 w-5 text-primary" />
        <span className="text-sm text-muted-foreground">当前预算</span>
        <span className="text-lg font-bold">{budget}</span>
        <span className="text-sm text-muted-foreground">万</span>
        {!started && (
          <Badge variant="destructive" className="ml-2">未开始实验，请先到实验导览</Badge>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {grouped.map(({ category, assets }) => (
          <div key={category} className="flex flex-col gap-3">
            <div>
              <h2 className="text-base font-semibold">{CATEGORY_META[category].label}</h2>
              <p className="text-sm text-muted-foreground">{CATEGORY_META[category].desc}</p>
            </div>
            <div className="flex flex-col gap-3">
              {assets.map((asset) => {
                const owned = purchased.includes(asset.id);
                return (
                  <Card key={asset.id} className={owned ? 'border-success/60 bg-success/5' : ''}>
                    <CardHeader className="pb-2">
                      <div className="flex items-start justify-between gap-2">
                        <CardTitle className="text-base">{asset.name}</CardTitle>
                        <Badge variant={owned ? 'default' : 'outline'} className={owned ? 'bg-success' : ''}>
                          {owned ? '已采购' : `${asset.price} 万`}
                        </Badge>
                      </div>
                      <CardDescription>{asset.desc}</CardDescription>
                    </CardHeader>
                    <CardContent className="flex flex-col gap-3">
                      {owned ? (
                        <div className="flex flex-col gap-2">
                          <div className="flex items-center gap-1.5 text-sm font-medium text-success">
                            <CheckCircle2 className="h-4 w-4" />
                            入库结果
                          </div>
                          <p className="rounded-lg border bg-muted/40 px-3 py-2 text-xs leading-relaxed text-muted-foreground">
                            {asset.result}
                          </p>
                        </div>
                      ) : (
                        <Button
                          variant="default"
                          size="sm"
                          className="w-full gap-2"
                          disabled={!started || budget < asset.price}
                          onClick={() => handlePurchase(asset)}
                        >
                          <ShoppingCart className="h-4 w-4" />
                          采购（-{asset.price} 万）
                        </Button>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
