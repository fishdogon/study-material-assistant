import { useState } from 'react';
import type { MaterialSummary, TextModeResponse } from '../types/api';
import { EmptyState } from './EmptyState';
import { ErrorState } from './ErrorState';
import { LoadingState } from './LoadingState';
import { MarkdownContent } from './MarkdownContent';
import { MaterialScopeFilter } from './MaterialScopeFilter';
import { RetrievedChunksList } from './RetrievedChunksList';
import { SourceSummaryCard } from './SourceSummaryCard';

interface ExplainPanelProps {
  value: string;
  teachingMode: string;
  explanationDepth: string;
  loading: boolean;
  error: string | null;
  result: TextModeResponse | null;
  materials: MaterialSummary[];
  selectedSourceNames: string[];
  subject: string;
  grade: string;
  topic: string;
  excludeOcr: boolean;
  onChange: (value: string) => void;
  onTeachingModeChange: (value: string) => void;
  onExplanationDepthChange: (value: string) => void;
  onToggleSourceName: (filename: string) => void;
  onSubjectChange: (value: string) => void;
  onGradeChange: (value: string) => void;
  onTopicChange: (value: string) => void;
  onExcludeOcrChange: (value: boolean) => void;
  onClearFilters: () => void;
  onSubmit: () => Promise<void>;
  onContinueToExercise: () => void;
}

const quickPrompts = [
  '这份资料应该怎么给孩子讲，才能更容易听懂？',
  '请用更适合家长转述的方式解释这份资料的核心思路。',
  '这类题最容易错在哪里？讲的时候应该重点提醒什么？',
];

export function ExplainPanel({
  value,
  teachingMode,
  explanationDepth,
  loading,
  error,
  result,
  materials,
  selectedSourceNames,
  subject,
  grade,
  topic,
  excludeOcr,
  onChange,
  onTeachingModeChange,
  onExplanationDepthChange,
  onToggleSourceName,
  onSubjectChange,
  onGradeChange,
  onTopicChange,
  onExcludeOcrChange,
  onClearFilters,
  onSubmit,
  onContinueToExercise,
}: ExplainPanelProps) {
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
        <div>
          <h3 className="panel-title">先把这份资料讲懂</h3>
          <p className="mt-1 text-sm leading-6 text-slate-600">
            先把重点讲清楚，再继续生成同专题练习，孩子会更容易跟上。
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            {quickPrompts.map((prompt) => (
              <button
                key={prompt}
                type="button"
                className="tag transition hover:border-blue-300 hover:bg-blue-50/80"
                onClick={() => onChange(prompt)}
              >
                {prompt}
              </button>
            ))}
          </div>
          <div className="panel-soft-area mt-4 space-y-4">
            <div className="grid gap-3 sm:grid-cols-2">
              <select className="input-base" value={teachingMode} onChange={(event) => onTeachingModeChange(event.target.value)}>
                <option value="">自动判断讲解场景</option>
                <option value="parent">更适合家长辅导</option>
                <option value="teacher">更适合老师讲课</option>
                <option value="general">通用讲解</option>
              </select>
              <select className="input-base" value={explanationDepth} onChange={(event) => onExplanationDepthChange(event.target.value)}>
                <option value="">自动判断详略</option>
                <option value="brief">简洁一点</option>
                <option value="standard">标准展开</option>
                <option value="detailed">详细展开</option>
              </select>
            </div>
            <textarea
              className="input-base min-h-36 resize-y"
              value={value}
              onChange={(event) => onChange(event.target.value)}
              placeholder="例如：这份资料应该怎么给孩子讲，才能更容易听懂？"
            />
            <div className="flex flex-col gap-3 sm:flex-row">
              <button type="button" className="btn-primary w-full sm:w-auto" onClick={onSubmit} disabled={loading || !value.trim()}>
                生成讲解
              </button>
              <button
                type="button"
                className="btn-secondary w-full px-4 py-2.5 sm:w-auto"
                onClick={onContinueToExercise}
                disabled={!materials.length}
              >
                讲解后继续生成练习
              </button>
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

      {loading ? <LoadingState text="正在生成讲解..." /> : null}
      {!loading && error ? <ErrorState message={error} /> : null}

      {!loading && !error && result ? (
        <div className="space-y-6">
          <section className="result-card">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <div className="text-sm text-slate-500">当前讲解问题</div>
                <div className="mt-2 text-sm leading-6 text-slate-700">{result.query}</div>
              </div>
              <div className="flex flex-col gap-3 sm:flex-row">
                <button type="button" className="btn-secondary w-full px-3 py-2 text-sm sm:w-auto" onClick={handleCopy}>
                  {copied ? '已复制' : '复制讲解'}
                </button>
                <button type="button" className="btn-primary w-full sm:w-auto" onClick={onContinueToExercise}>
                  继续生成练习
                </button>
              </div>
            </div>
            <div className="mt-5 text-sm text-slate-800">
              <MarkdownContent content={result.answer} />
            </div>
          </section>
          <SourceSummaryCard summary={result.source_summary} />
          <RetrievedChunksList chunks={result.retrieved_chunks} />
        </div>
      ) : null}

      {!loading && !error && !result ? (
        <EmptyState title="等待生成讲解" description="先选好资料范围，再提出“应该怎么讲”的问题，系统会把资料转成更容易转述和理解的讲解内容。" />
      ) : null}
    </div>
  );
}
