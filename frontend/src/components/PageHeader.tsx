import type { ReactNode } from 'react';

interface PageHeaderProps {
  title: string;
  description: string;
  rightSlot?: ReactNode;
}

export function PageHeader({ title, description, rightSlot }: PageHeaderProps) {
  return (
    <div className="mb-5 flex flex-col gap-4 rounded-[24px] border border-slate-200 bg-white px-6 py-5 text-slate-900 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <h2 className="text-[30px] font-semibold tracking-tight text-slate-900">{title}</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">{description}</p>
      </div>
      {rightSlot ? <div className="shrink-0">{rightSlot}</div> : null}
    </div>
  );
}
