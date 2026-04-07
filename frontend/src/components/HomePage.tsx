import type { IndexResponse, MaterialSummary, UploadResponse } from '../types/api';
import { FileUploadPanel } from './FileUploadPanel';

interface HomePageProps {
  uploadLoading: boolean;
  uploadError: string | null;
  uploadResult: UploadResponse | null;
  autoIndexHint: string | null;
  onUpload: (file: File) => Promise<boolean>;
  materials: MaterialSummary[];
  materialsLoading: boolean;
  latestFilename: string;
  latestSubject: string;
  latestGrade: string;
  latestTopic: string;
  indexResult: IndexResponse | null;
  onOpenTeaching: () => void;
  onOpenExercise: () => void;
  onOpenMaterials: () => void;
}

export function HomePage({
  uploadLoading,
  uploadError,
  uploadResult,
  autoIndexHint,
  onUpload,
  materials,
  materialsLoading,
  latestFilename,
  latestSubject,
  latestGrade,
  latestTopic,
  indexResult,
  onOpenTeaching,
  onOpenExercise,
  onOpenMaterials,
}: HomePageProps) {
  const latestMaterial = materials.find((item) => item.filename === latestFilename) ?? materials[0] ?? null;
  const readyText = latestMaterial ? '资料已准备好，可以继续讲解或练习。' : '先上传一份资料开始。';

  return (
    <div className="space-y-6">
      <section className="rounded-[26px] border border-slate-200 bg-[linear-gradient(180deg,#fdfefe_0%,#f3f8ff_100%)] px-5 py-7 sm:px-6 sm:py-8">
        <div className="max-w-3xl">
          <div className="text-sm font-medium text-blue-700">数学辅导助手</div>
          <h1 className="mt-3 text-[32px] font-semibold tracking-tight text-slate-900 sm:text-[40px]">上传资料，先讲懂，再练习</h1>
          <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-600 sm:text-[15px]">
            把孩子当前的讲义、题单和作业变成更容易转述的讲解，再围绕这些内容继续练习。
          </p>
          <div className="mt-6 flex flex-col gap-3 sm:flex-row">
            <button type="button" className="btn-primary min-w-[148px] w-full sm:w-auto" onClick={onOpenTeaching} disabled={!materials.length}>
              先生成讲解
            </button>
            <button type="button" className="btn-secondary min-w-[148px] w-full px-4 py-2.5 sm:w-auto" onClick={onOpenExercise} disabled={!materials.length}>
              再生成练习
            </button>
          </div>
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[1.22fr_0.78fr]">
        <FileUploadPanel
          loading={uploadLoading}
          error={uploadError}
          result={uploadResult}
          autoIndexHint={autoIndexHint}
          onUpload={onUpload}
        />

        <section className="panel p-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h3 className="panel-title">下一步</h3>
              <p className="mt-1 text-sm leading-6 text-slate-600">{readyText}</p>
            </div>
            <button type="button" className="btn-secondary px-4 py-2.5 text-sm" onClick={onOpenMaterials}>
              资料管理
            </button>
          </div>

          <div className="mt-5 rounded-[22px] border border-slate-200 bg-[#f8fbfc] px-4 py-4">
            {latestMaterial ? (
              <div>
                <div className="text-xs font-medium tracking-[0.16em] text-slate-400">当前资料</div>
                <div className="mt-2 text-sm font-medium text-slate-900">{latestMaterial.filename}</div>
                <div className="mt-3 flex flex-wrap gap-2">
                  {latestTopic ? <span className="tag">{latestTopic}</span> : null}
                  {latestGrade ? <span className="tag">{latestGrade}</span> : null}
                  {latestSubject ? <span className="tag">{latestSubject}</span> : null}
                </div>
                {indexResult ? <div className="mt-3 text-sm text-slate-500">最近一次准备已完成，共生成 {indexResult.chunk_count} 个文本块。</div> : null}
              </div>
            ) : (
              <div className="text-sm leading-6 text-slate-600">上传后这里会显示当前正在使用的资料。</div>
            )}

            <div className="mt-4 grid gap-3">
              <button
                type="button"
                className="soft-card block w-full px-4 py-3.5 text-left transition hover:border-blue-300"
                onClick={onOpenTeaching}
                disabled={!materials.length || materialsLoading}
              >
                <div className="text-sm font-medium text-slate-900">先生成讲解</div>
                <div className="mt-1 text-sm leading-6 text-slate-600">先看怎么讲，再决定怎么练。</div>
              </button>
              <button
                type="button"
                className="soft-card block w-full px-4 py-3.5 text-left transition hover:border-blue-300"
                onClick={onOpenExercise}
                disabled={!materials.length || materialsLoading}
              >
                <div className="text-sm font-medium text-slate-900">再生成练习</div>
                <div className="mt-1 text-sm leading-6 text-slate-600">围绕当前资料继续巩固。</div>
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
