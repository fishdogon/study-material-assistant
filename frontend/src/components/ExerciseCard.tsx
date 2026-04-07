import type { ExerciseItem } from '../types/api';
import { MarkdownContent } from './MarkdownContent';

interface ExerciseCardProps {
  exercise: ExerciseItem;
  index: number;
  style: '1' | '2' | '3';
}

function parseExerciseTitle(title: string) {
  const [stage, rest] = title.split('｜');

  if (rest) {
    return {
      stage: stage.trim(),
      title: rest.trim(),
    };
  }

  return {
    stage: '',
    title: title,
  };
}

export function ExerciseCard({ exercise, index, style }: ExerciseCardProps) {
  const parsed = parseExerciseTitle(exercise.title);

  return (
    <article className="result-card">
      <div className="flex items-center justify-between gap-4">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            {parsed.stage ? <span className="tag">{parsed.stage}</span> : null}
            <span className="tag">样式 {style}</span>
          </div>
          <h4 className="mt-2 text-[15px] font-semibold text-slate-800 sm:text-base">
            {index + 1}. {parsed.title}
          </h4>
        </div>
      </div>
      <div className="mt-4 space-y-3.5 text-sm leading-6 text-slate-700">
        <div>
          <div className="font-medium text-slate-900">题目</div>
          <div className="mt-1">
            <MarkdownContent content={exercise.problem} />
          </div>
        </div>
        <div>
          <div className="font-medium text-slate-900">出题意图</div>
          <div className="mt-1">
            <MarkdownContent content={exercise.intent} />
          </div>
        </div>
        <div>
          <div className="font-medium text-slate-900">提示</div>
          <div className="mt-1">
            <MarkdownContent content={exercise.hint} />
          </div>
        </div>
        {style !== '1' && exercise.answer ? (
          <div>
            <div className="font-medium text-slate-900">参考答案</div>
            <div className="mt-1">
              <MarkdownContent content={exercise.answer} />
            </div>
          </div>
        ) : null}
        {style === '3' && exercise.explanation ? (
          <div>
            <div className="font-medium text-slate-900">讲解思路</div>
            <div className="mt-1">
              <MarkdownContent content={exercise.explanation} />
            </div>
          </div>
        ) : null}
      </div>
    </article>
  );
}
