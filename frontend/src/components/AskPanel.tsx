import type { MaterialSummary, TextModeResponse } from '../types/api';
import { useState } from 'react';
import { EmptyState } from './EmptyState';
import { ErrorState } from './ErrorState';
import { LoadingState } from './LoadingState';
import { MarkdownContent } from './MarkdownContent';
import { MaterialScopeFilter } from './MaterialScopeFilter';
import { RetrievedChunksList } from './RetrievedChunksList';
import { SourceSummaryCard } from './SourceSummaryCard';

interface AskPanelProps {
  title: string;
  description: string;
  placeholder: string;
  value: string;
  loading: boolean;
  error: string | null;
  result: TextModeResponse | null;
  submitLabel: string;
  materials: MaterialSummary[];
  selectedSourceNames: string[];
  subject: string;
  grade: string;
  topic: string;
  excludeOcr: boolean;
  onChange: (value: string) => void;
  onToggleSourceName: (filename: string) => void;
  onSubjectChange: (value: string) => void;
  onGradeChange: (value: string) => void;
  onTopicChange: (value: string) => void;
  onExcludeOcrChange: (value: boolean) => void;
  onClearFilters: () => void;
  onSubmit: () => Promise<void>;
}

export function AskPanel({
  title,
  description,
  placeholder,
  value,
  loading,
  error,
  result,
  submitLabel,
  materials,
  selectedSourceNames,
  subject,
  grade,
  topic,
  excludeOcr,
  onChange,
  onToggleSourceName,
  onSubjectChange,
  onGradeChange,
  onTopicChange,
  onExcludeOcrChange,
  onClearFilters,
  onSubmit,
}: AskPanelProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!result?.answer) {
      return;
    }

    try {
      await navigator.clipboard.writeText(result.answer);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className="space-y-6">
      <section className="panel p-6">
        <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr] lg:items-start">
          <div>
            <h3 className="panel-title">{title}</h3>
            <p className="mt-1 text-sm text-slate-600">{description}</p>
            <div className="panel-soft-area mt-4 space-y-4">
              <textarea
                className="input-base min-h-32 resize-y"
                value={value}
                onChange={(event) => onChange(event.target.value)}
                placeholder={placeholder}
              />
              <button type="button" className="btn-primary w-full sm:w-auto" onClick={onSubmit} disabled={loading || !value.trim()}>
                {submitLabel}
              </button>
            </div>
          </div>

          <div className="space-y-3">
            <div className="soft-card px-5 py-5">
              <div className="text-sm font-medium text-slate-900">这个页面更适合什么时候用</div>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                当你已经看过讲解，但还想补充查某个知识点、结论或来源片段时，可以在这里继续追问。
              </p>
            </div>
            <div className="soft-card px-5 py-5">
              <div className="text-sm font-medium text-slate-900">推荐追问示例</div>
              <div className="mt-3 space-y-2">
                {[
                  '这份资料的核心思路是什么？',
                  '最容易出错的地方在哪里？',
                  '这个结论主要来自哪份资料？',
                ].map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    className="block w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-left text-sm leading-6 text-slate-600 transition hover:border-blue-300 hover:bg-blue-50/60"
                    onClick={() => onChange(prompt)}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <MaterialScopeFilter
        materials={materials}
        selectedSourceNames={selectedSourceNames}
        subject={subject}
        grade={grade}
        topic={topic}
        excludeOcr={excludeOcr}
        disabled={loading}
        onToggleSourceName={onToggleSourceName}
        onSubjectChange={onSubjectChange}
        onGradeChange={onGradeChange}
        onTopicChange={onTopicChange}
        onExcludeOcrChange={onExcludeOcrChange}
        onClear={onClearFilters}
      />

      {loading ? <LoadingState text="正在请求后端生成结果..." /> : null}
      {!loading && error ? <ErrorState message={error} /> : null}

      {!loading && !error && result ? (
        <div className="space-y-6">
          <section className="result-card">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <div className="text-sm text-slate-500">问题</div>
              </div>
              <button type="button" className="btn-secondary w-full px-3 py-2 text-sm sm:w-auto" onClick={handleCopy}>
                {copied ? '已复制' : '复制回答'}
              </button>
            </div>
            <div className="mt-2 text-sm leading-6 text-slate-700">{result.query}</div>
            <div className="mt-5 text-sm text-slate-500">回答</div>
            <div className="mt-3 text-sm text-slate-800">
              <MarkdownContent content={result.answer} />
            </div>
          </section>
          <SourceSummaryCard summary={result.source_summary} />
          <RetrievedChunksList chunks={result.retrieved_chunks} />
        </div>
      ) : null}
      {!loading && !error && !result ? (
        <EmptyState title="等待补充查询" description="如果你想继续查某个知识点、结论或来源片段，可以在这里补充提问。" />
      ) : null}
    </div>
  );
}
