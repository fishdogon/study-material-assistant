import { useState } from 'react';
import type { ExerciseResponse, MaterialSummary } from '../types/api';
import { EmptyState } from './EmptyState';
import { ErrorState } from './ErrorState';
import { ExerciseCard } from './ExerciseCard';
import { LoadingState } from './LoadingState';
import { MaterialScopeFilter } from './MaterialScopeFilter';
import { RetrievedChunksList } from './RetrievedChunksList';
import { SourceSummaryCard } from './SourceSummaryCard';

interface ExercisePanelProps {
  query: string;
  style: '1' | '2' | '3';
  difficulty: string;
  expectedCount: number;
  loading: boolean;
  error: string | null;
  result: ExerciseResponse | null;
  materials: MaterialSummary[];
  selectedSourceNames: string[];
  subject: string;
  grade: string;
  topic: string;
  excludeOcr: boolean;
  onQueryChange: (value: string) => void;
  onStyleChange: (value: '1' | '2' | '3') => void;
  onDifficultyChange: (value: string) => void;
  onExpectedCountChange: (value: number) => void;
  onToggleSourceName: (filename: string) => void;
  onSubjectChange: (value: string) => void;
  onGradeChange: (value: string) => void;
  onTopicChange: (value: string) => void;
  onExcludeOcrChange: (value: boolean) => void;
  onClearFilters: () => void;
  onSubmit: () => Promise<void>;
}

export function ExercisePanel({
  query,
  style,
  difficulty,
  expectedCount,
  loading,
  error,
  result,
  materials,
  selectedSourceNames,
  subject,
  grade,
  topic,
  excludeOcr,
  onQueryChange,
  onStyleChange,
  onDifficultyChange,
  onExpectedCountChange,
  onToggleSourceName,
  onSubjectChange,
  onGradeChange,
  onTopicChange,
  onExcludeOcrChange,
  onClearFilters,
  onSubmit,
}: ExercisePanelProps) {
  const [copied, setCopied] = useState(false);

  const stageSummary = result
    ? result.answer.exercises
        .map((exercise) => exercise.title.split('｜')[0]?.trim())
        .filter((item, index, array) => item && array.indexOf(item) === index)
    : [];

  const handleCopy = async () => {
    if (!result) {
      return;
    }

    const text = result.answer.exercises
      .map((exercise, index) => {
        return [`${index + 1}. ${exercise.title}`, exercise.problem, exercise.answer, exercise.explanation]
          .filter(Boolean)
          .join('\n');
      })
      .join('\n\n');

    try {
      await navigator.clipboard.writeText(text);
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
          <h3 className="panel-title">围绕当前资料继续练习</h3>
          <p className="mt-1 text-sm leading-6 text-slate-600">
            讲解之后继续巩固最合适。先出几道同类型题，再根据孩子情况补答案或讲解。
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            {[
              '请围绕这份资料出 3 道基础练习题',
              '请出一组适合当前年级巩固的同类题，并附答案',
              '请出题并带简短讲解，方便我带着孩子一起看',
            ].map((preset) => (
              <button
                key={preset}
                type="button"
                className="tag transition hover:border-blue-300 hover:bg-blue-50/80"
                onClick={() => onQueryChange(preset)}
              >
                {preset}
              </button>
            ))}
          </div>
          <div className="panel-soft-area mt-4 grid gap-4 lg:grid-cols-[1fr_240px]">
            <textarea
              className="input-base min-h-36 resize-y"
              value={query}
              onChange={(event) => onQueryChange(event.target.value)}
              placeholder="例如：请围绕这份资料出 3 道适合孩子练习的题目"
            />
            <div className="space-y-4">
              <select className="input-base" value={difficulty} onChange={(event) => onDifficultyChange(event.target.value)}>
                <option value="">自动判断难度</option>
                <option value="基础">基础巩固</option>
                <option value="标准">标准练习</option>
                <option value="提高">略有提高</option>
              </select>
              <select
                className="input-base"
                value={expectedCount}
                onChange={(event) => onExpectedCountChange(Number(event.target.value))}
              >
                <option value={0}>自动判断题量</option>
                <option value={2}>2 道题</option>
                <option value={3}>3 道题</option>
                <option value={4}>4 道题</option>
                <option value={5}>5 道题</option>
              </select>
              <select
                className="input-base"
                value={style}
                onChange={(event) => onStyleChange(event.target.value as '1' | '2' | '3')}
              >
                <option value="1">1. 只出题</option>
                <option value="2">2. 出题 + 答案</option>
                <option value="3">3. 出题 + 讲解</option>
              </select>
              <button type="button" className="btn-primary w-full" onClick={onSubmit} disabled={loading || !query.trim()}>
                生成练习题
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

      {loading ? <LoadingState text="正在生成练习题..." /> : null}
      {!loading && error ? <ErrorState message={error} /> : null}

      {!loading && !error && result ? (
        <div className="space-y-6">
          <section className="result-card">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <div className="text-sm text-slate-500">当前练习单</div>
                <div className="flex flex-wrap gap-2">
                  <span className="tag">主题：{result.answer.topic}</span>
                  <span className="tag">适合年级：{result.answer.grade}</span>
                  <span className="tag">题目数量：{result.answer.exercises.length}</span>
                  {result.answer.difficulty ? <span className="tag">难度：{result.answer.difficulty}</span> : null}
                </div>
                {stageSummary.length > 0 ? (
                  <div className="mt-3 text-sm leading-6 text-slate-600">
                    本组练习结构：{stageSummary.join(' -> ')}
                  </div>
                ) : null}
              </div>
              <button type="button" className="btn-secondary w-full px-3 py-2 text-sm sm:w-auto" onClick={handleCopy}>
                {copied ? '已复制' : '复制题目'}
              </button>
            </div>
            <div className="mt-5 space-y-4">
              {result.answer.exercises.map((exercise, index) => (
                <ExerciseCard key={`${exercise.title}-${index}`} exercise={exercise} index={index} style={result.style} />
              ))}
            </div>
          </section>
          <SourceSummaryCard summary={result.source_summary} />
          <RetrievedChunksList chunks={result.retrieved_chunks} />
        </div>
      ) : null}
      {!loading && !error && !result ? (
        <EmptyState title="等待生成练习题" description="输入出题需求并选择风格后，系统会返回结构化练习题和对应来源信息。" />
      ) : null}
    </div>
  );
}
