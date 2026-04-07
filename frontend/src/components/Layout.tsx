import { useState, type ReactNode } from 'react';
import { classNames } from '../lib/classNames';

interface LayoutProps {
  sidebar: (helpers: { closeMobileSidebar: () => void }) => ReactNode;
  children: ReactNode;
}

export function Layout({ sidebar, children }: LayoutProps) {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-canvas px-2 py-2 sm:px-4 sm:py-4 lg:px-4">
      {mobileSidebarOpen ? (
        <button
          type="button"
          aria-label="关闭导航"
          className="fixed inset-0 z-30 bg-slate-950/30 backdrop-blur-[2px] lg:hidden"
          onClick={() => setMobileSidebarOpen(false)}
        />
      ) : null}

      <div className="mx-auto flex min-h-[calc(100vh-16px)] max-w-[1660px] flex-col overflow-hidden rounded-[28px] border border-slate-200/80 bg-white shadow-[0_16px_36px_rgba(15,23,42,0.03)] lg:rounded-[32px] lg:flex-row">
        <aside
          className={classNames(
            'fixed inset-y-2 left-2 z-40 w-[286px] overflow-y-auto rounded-[28px] border border-slate-200 bg-[linear-gradient(180deg,#3e73d8_0%,#5a97f4_100%)] px-4 py-6 text-white shadow-[0_18px_40px_rgba(15,23,42,0.14)] transition-transform duration-200 lg:static lg:inset-auto lg:w-[292px] lg:translate-x-0 lg:rounded-none lg:border-0 lg:border-r lg:border-slate-200 lg:shadow-none',
            mobileSidebarOpen ? 'translate-x-0' : '-translate-x-[120%]',
          )}
        >
          {sidebar({ closeMobileSidebar: () => setMobileSidebarOpen(false) })}
        </aside>
        <main className="flex-1 bg-[#f2f5f8] px-4 py-6 sm:px-6 lg:px-7 lg:py-8">
          <div className="mb-4 flex items-center justify-between rounded-[22px] border border-slate-200 bg-white px-4 py-3 lg:hidden">
            <div>
              <div className="text-sm font-semibold text-slate-900">学习资料智能助手</div>
            </div>
            <button type="button" className="btn-secondary px-3 py-2 text-sm" onClick={() => setMobileSidebarOpen(true)}>
              菜单
            </button>
          </div>
          {children}
        </main>
      </div>
    </div>
  );
}
