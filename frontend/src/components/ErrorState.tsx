interface ErrorStateProps {
  message: string;
}

export function ErrorState({ message }: ErrorStateProps) {
  return (
    <div className="rounded-[18px] border border-rose-200 bg-rose-50/85 px-4 py-3 text-sm text-rose-700">
      {message}
    </div>
  );
}
