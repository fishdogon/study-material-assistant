import { classNames } from '../lib/classNames';

export type AppSection = 'home' | 'materials' | 'qa' | 'teaching' | 'exercise';

interface SidebarItem {
  key: AppSection;
  label: string;
}

interface SidebarProps {
  activeSection: AppSection;
  onSelect: (section: AppSection) => void;
  onNavigate?: () => void;
}

const items: SidebarItem[] = [
  { key: 'home', label: '首页' },
  { key: 'materials', label: '资料管理' },
  { key: 'teaching', label: '教学讲解' },
  { key: 'exercise', label: '练习题生成' },
  { key: 'qa', label: '资料问答' },
];

export function Sidebar({ activeSection, onSelect, onNavigate }: SidebarProps) {
  return (
    <div className="flex h-full flex-col">
      <div>
        <h1 className="mt-3 text-[28px] font-semibold tracking-tight text-white">学习资料智能助手</h1>
        <p className="mt-3 text-sm leading-6 text-slate-200/80">先讲懂，再练习。</p>
      </div>

      <nav className="mt-7 space-y-2">
        {items.map((item, index) => (
          <button
            key={item.key}
            type="button"
            onClick={() => {
              onSelect(item.key);
              onNavigate?.();
            }}
            className={classNames(
              'w-full rounded-[22px] px-4 py-3.5 text-left transition',
              activeSection === item.key
                ? 'bg-white text-slate-900 shadow-[0_10px_24px_rgba(15,23,42,0.12)]'
                : 'bg-white/5 text-slate-100 hover:bg-white/9',
            )}
          >
            <div className="flex items-center justify-between gap-3">
              <div className="text-sm font-medium">{item.label}</div>
              <span className={classNames('text-xs', activeSection === item.key ? 'text-slate-500' : 'text-slate-300/55')}>0{index + 1}</span>
            </div>
          </button>
        ))}
      </nav>

      <div className="mt-auto border-t border-white/10 pt-5">
        <p className="text-sm leading-6 text-slate-300/72">先上传资料，再进入讲解和练习。</p>
      </div>
    </div>
  );
}
