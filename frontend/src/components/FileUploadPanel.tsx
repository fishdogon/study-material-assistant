import { useRef, useState, type FormEvent } from 'react';
import type { UploadResponse } from '../types/api';
import { ErrorState } from './ErrorState';
import { LoadingState } from './LoadingState';

interface FileUploadPanelProps {
  loading: boolean;
  error: string | null;
  result: UploadResponse | null;
  autoIndexHint: string | null;
  onUpload: (file: File) => Promise<boolean>;
}

export function FileUploadPanel({
  loading,
  error,
  result,
  autoIndexHint,
  onUpload,
}: FileUploadPanelProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedFile) {
      return;
    }

    const success = await onUpload(selectedFile);
    if (success) {
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <section className="panel p-6">
      <div>
        <h3 className="panel-title">上传资料</h3>
        <p className="mt-1 text-sm leading-6 text-slate-600">上传孩子当前讲义、题单、作业或拍照题，后续就可以围绕这些资料生成讲解和练习。</p>
      </div>

      <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
        <label className="block rounded-[24px] border-2 border-dashed border-slate-200 bg-slate-50 px-5 py-6 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-white text-lg text-slate-700 shadow-sm">
            ↑
          </div>
          <div className="mt-4 text-sm font-medium text-slate-800">选择孩子当前正在学的资料</div>
          <div className="mt-1 text-sm text-slate-500">支持 txt / pdf / 图片资料</div>
          <input
            ref={fileInputRef}
            className="input-base mt-4 file:mr-4 file:rounded-lg file:border-0 file:bg-slate-100 file:px-3 file:py-2 file:text-sm file:font-medium file:text-slate-700"
            type="file"
            onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
            accept=".txt,.pdf,image/*"
          />
        </label>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <button type="submit" className="btn-primary w-full sm:w-auto" disabled={loading || !selectedFile}>
            上传孩子资料
          </button>
          {selectedFile ? <span className="text-sm text-slate-500">{selectedFile.name}</span> : null}
        </div>
      </form>

      <div className="mt-4">
        {loading ? <LoadingState text="正在上传文件..." /> : null}
        {!loading && error ? <ErrorState message={error} /> : null}
        {!loading && !error && result ? (
          <div className="rounded-[22px] border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
            <div>{result.message}</div>
            <div className="mt-1">文件名：{result.filename}</div>
          </div>
        ) : null}
        {!loading && autoIndexHint ? (
          <div className="panel-subtle mt-3">{autoIndexHint}</div>
        ) : null}
      </div>
    </section>
  );
}
