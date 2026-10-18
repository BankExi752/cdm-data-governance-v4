// 全局布局：顶部导航 + 预算徽章 + 角色/目标 + 操作留痕入口
import { NavLink, Outlet } from 'react-router-dom';
import { Database, FlaskConical, LineChart, Settings2, UserRound, Wallet, Target } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import AuditPanel from '@/components/AuditPanel';
import { ROLE_OPTIONS, TARGET_OPTIONS } from '@/data/lab';
import { useLab } from '@/store/lab-context';

const NAV_ITEMS = [
  { path: '/', label: '实验导览', icon: FlaskConical, end: true },
  { path: '/manage', label: '管数据', icon: Database, end: false },
  { path: '/govern', label: '治数据', icon: Settings2, end: false },
  { path: '/use', label: '用数据', icon: LineChart, end: false },
  { path: '/report', label: '能力画像', icon: Wallet, end: false },
];

export function Layout() {
  const { budget, started, role, target } = useLab();
  const roleLabel = ROLE_OPTIONS.find((r) => r.id === role)?.label;
  const targetLabel = TARGET_OPTIONS.find((t) => t.id === target)?.label;

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80">
        <div className="mx-auto flex h-14 w-full max-w-6xl items-center justify-between gap-4 px-4">
          <div className="flex items-center gap-6">
            <NavLink to="/" className="flex items-center gap-2 font-semibold">
              <span className="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-primary-foreground">
                <Database className="h-4 w-4" />
              </span>
              <span className="hidden sm:inline">数据资产化与知识资产化仿真实验</span>
            </NavLink>
            <nav className="flex items-center gap-1">
              {NAV_ITEMS.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end={item.end}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm transition-colors',
                      isActive
                        ? 'bg-primary/10 font-medium text-primary'
                        : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                    )
                  }
                >
                  <item.icon className="h-4 w-4" />
                  <span className="hidden md:inline">{item.label}</span>
                </NavLink>
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-3">
            {started && (
              <>
                <div className="hidden items-center gap-1.5 rounded-full border bg-card px-3 py-1.5 text-xs text-muted-foreground sm:flex">
                  <UserRound className="h-3.5 w-3.5 text-primary" />
                  {roleLabel}
                </div>
                <div className="hidden items-center gap-1.5 rounded-full border bg-card px-3 py-1.5 text-xs text-muted-foreground md:flex">
                  <Target className="h-3.5 w-3.5 text-primary" />
                  {targetLabel}
                </div>
              </>
            )}
            <div className="flex items-center gap-1.5 rounded-full border bg-card px-3 py-1.5 text-sm">
              <Wallet className="h-4 w-4 text-primary" />
              <span className="font-semibold">{budget}</span>
              <span className="text-muted-foreground">万</span>
              {!started && <Badge variant="secondary" className="ml-1">未开始</Badge>}
            </div>
            <AuditPanel />
          </div>
        </div>
      </header>
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
