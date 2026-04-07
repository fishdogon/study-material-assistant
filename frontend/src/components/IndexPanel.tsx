import type { IndexResponse } from '../types/api';
import { EmptyState } from './EmptyState';
import { ErrorState } from './ErrorState';
import { LoadingState } from './LoadingState';

interface IndexPanelProps {
  loading: boolean;
  error: string | null;
  result: IndexResponse | null;
  onBuildIndex: () => Promise<void>;
}

export function IndexPanel({ loading, error, result, onBuildIndex }: IndexPanelProps) {
  return (
    <section className="panel p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="panel-title">资料准备状态</h3>
          <p className="mt-1 text-sm leading-6 text-slate-600">这是后台准备区。上传新资料后可以手动更新索引，确保后续讲解和练习基于最新内容生成。</p>
        </div>
        <button type="button" className="btn-primary" onClick={onBuildIndex} disabled={loading}>
          更新资料准备
        </button>
      </div>

      <div className="mt-4">
        {loading ? <LoadingState text="正在构建索引..." /> : null}
        {!loading && error ? <ErrorState message={error} /> : null}
        {!loading && !error && result ? (
          <div className="space-y-4">
            <div className="grid gap-3 md:grid-cols-2">
              <div className="soft-card px-4 py-4">
                <div className="text-xs uppercase tracking-[0.18em] text-slate-400">准备状态</div>
                <div className="mt-2 text-sm font-medium text-slate-800">{result.message}</div>
              </div>
              <div className="soft-card px-4 py-4">
                <div className="text-xs uppercase tracking-[0.18em] text-slate-400">可检索文本块</div>
                <div className="mt-2 text-2xl font-semibold tracking-tight text-slate-900">{result.chunk_count}</div>
              </div>
            </div>
            <div>
              <div className="mb-2 text-sm font-medium text-slate-700">来源统计</div>
              <div className="info-table">
                <table className="min-w-full divide-y divide-line text-sm">
                  <thead className="bg-blue-50 text-left text-slate-500">
                    <tr>
                      <th className="px-4 py-3 font-medium">来源文件</th>
                      <th className="px-4 py-3 font-medium">Chunk 数量</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-line bg-white">
                    {Object.entries(result.source_count).map(([source, count]) => (
                      <tr key={source}>
                        <td className="px-4 py-3 text-slate-700">{source}</td>
                        <td className="px-4 py-3 text-slate-600">{count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : null}
        {!loading && !error && !result ? (
          <EmptyState title="尚未完成资料准备" description="上传资料后可点击“更新资料准备”，或保持自动重建开启。" />
        ) : null}
      </div>
    </section>
  );
}
