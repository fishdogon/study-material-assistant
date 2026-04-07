import type { SourceSummary } from '../types/api';

interface SourceSummaryCardProps {
  summary: SourceSummary;
}

export function SourceSummaryCard({ summary }: SourceSummaryCardProps) {
  return (
    <section className="panel p-6">
      <h3 className="panel-title">来源摘要</h3>
      <p className="mt-1 text-sm leading-6 text-slate-600">这里会告诉你本次内容主要参考了哪些资料，方便判断是否贴合当前专题。</p>
      <div className="mt-4 flex flex-wrap gap-2">
        <span className="tag">主来源：{summary.primary_source_type}</span>
        <span className="tag">来源类型：{summary.source_types.join(' / ') || '未知'}</span>
        <span className="tag">{summary.contains_ocr ? '包含 OCR 结果' : '纯文本来源'}</span>
      </div>
      <p className="mt-4 rounded-[18px] border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-600">
        {summary.note}
      </p>
    </section>
  );
}
