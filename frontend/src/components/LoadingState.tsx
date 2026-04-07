interface LoadingStateProps {
  text?: string;
}

export function LoadingState({ text = '处理中，请稍候...' }: LoadingStateProps) {
  return (
    <div className="panel flex min-h-28 items-center justify-center gap-3 px-6 py-7 text-sm text-slate-600">
      <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-blue-600/80" />
      {text}
    </div>
  );
}
