import { useState } from 'react';
import type { MaterialSummary } from '../types/api';
import { EmptyState } from './EmptyState';
import { ErrorState } from './ErrorState';
import { LoadingState } from './LoadingState';

interface MaterialsTableProps {
  materials: MaterialSummary[];
  loading: boolean;
  error: string | null;
  deletingFilename: string | null;
  updatingFilename: string | null;
  suggestingFilename: string | null;
  onRefresh: () => Promise<void>;
  onDelete: (filename: string) => Promise<void>;
  onUpdateMetadata: (filename: string, payload: { subject: string; grade: string; topic: string }) => Promise<void>;
  onSuggestMetadata: (filename: string) => Promise<void>;
}

export function MaterialsTable({
  materials,
  loading,
  error,
  deletingFilename,
  updatingFilename,
  suggestingFilename,
  onRefresh,
  onDelete,
  onUpdateMetadata,
  onSuggestMetadata,
}: MaterialsTableProps) {
  const [editingFilename, setEditingFilename] = useState<string | null>(null);
  const [draft, setDraft] = useState({ subject: '', grade: '', topic: '' });

  const handleEdit = (material: MaterialSummary) => {
    setEditingFilename(material.filename);
    setDraft({
      subject: material.subject,
      grade: material.grade,
      topic: material.topic,
    });
  };

  const renderTagCell = (
    value: string,
    suggestedValue: string,
    source: 'manual' | 'ai' | 'empty',
    _field: 'subject' | 'grade' | 'topic',
  ) => {
    if (!value) {
      return <span className="text-slate-400">-</span>;
    }

    const isAi = source === 'ai';

    return (
      <div className="flex flex-col gap-1">
        <span>{value}</span>
        {isAi && suggestedValue ? <span className="text-xs text-blue-600">AI 建议</span> : null}
      </div>
    );
  };

  return (
    <section className="panel p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="panel-title">资料列表</h3>
          <p className="mt-1 text-sm leading-6 text-slate-600">在这里整理资料、修正标签和删除无关文件。</p>
        </div>
        <button type="button" className="btn-secondary px-3 py-2 text-sm" onClick={onRefresh} disabled={loading}>
          刷新列表
        </button>
      </div>

      <div className="mt-4">
        {loading ? <LoadingState text="正在加载资料列表..." /> : null}
        {!loading && error ? <ErrorState message={error} /> : null}
        {!loading && !error && materials.length === 0 ? (
          <EmptyState title="暂无资料" description="先上传资料并建立索引，这里会展示当前已接入的资料文件。" />
        ) : null}
        {!loading && !error && materials.length > 0 ? (
          <div className="overflow-hidden rounded-[22px] border border-slate-200 bg-white">
            <table className="min-w-full text-sm">
              <thead className="bg-[#f6fafb] text-left text-slate-500">
                <tr>
                  <th className="px-4 py-3 font-medium">文件名</th>
                  <th className="px-4 py-3 font-medium">类型</th>
                  <th className="px-4 py-3 font-medium">学科</th>
                  <th className="px-4 py-3 font-medium">年级</th>
                  <th className="px-4 py-3 font-medium">专题</th>
                  <th className="px-4 py-3 font-medium">解析器</th>
                  <th className="px-4 py-3 font-medium">Chunk</th>
                  <th className="px-4 py-3 font-medium">OCR</th>
                  <th className="px-4 py-3 font-medium">操作</th>
                </tr>
              </thead>
              <tbody className="bg-white">
                {materials.map((material) => (
                  <tr key={material.id} className="border-t border-slate-100">
                    <td className="px-4 py-3.5 text-slate-700">{material.filename}</td>
                    <td className="px-4 py-3 text-slate-600">{material.source_type}</td>
                    <td className="px-4 py-3 text-slate-600">
                      {editingFilename === material.filename ? (
                        <input
                          className="input-base py-2"
                          value={draft.subject}
                          onChange={(event) => setDraft((current) => ({ ...current, subject: event.target.value }))}
                        />
                      ) : (
                        renderTagCell(material.subject, material.suggested_subject, material.subject_source, 'subject')
                      )}
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {editingFilename === material.filename ? (
                        <input
                          className="input-base py-2"
                          value={draft.grade}
                          onChange={(event) => setDraft((current) => ({ ...current, grade: event.target.value }))}
                        />
                      ) : (
                        renderTagCell(material.grade, material.suggested_grade, material.grade_source, 'grade')
                      )}
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {editingFilename === material.filename ? (
                        <input
                          className="input-base py-2"
                          value={draft.topic}
                          onChange={(event) => setDraft((current) => ({ ...current, topic: event.target.value }))}
                        />
                      ) : (
                        renderTagCell(material.topic, material.suggested_topic, material.topic_source, 'topic')
                      )}
                    </td>
                    <td className="px-4 py-3 text-slate-600">{material.parser_name}</td>
                    <td className="px-4 py-3 text-slate-600">{material.chunk_count}</td>
                    <td className="px-4 py-3 text-slate-600">{material.is_ocr ? '是' : '否'}</td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-2">
                        {editingFilename === material.filename ? (
                          <>
                            <button
                              type="button"
                              className="btn-secondary px-3 py-2 text-sm"
                              onClick={async () => {
                                await onUpdateMetadata(material.filename, draft);
                                setEditingFilename(null);
                              }}
                              disabled={updatingFilename === material.filename}
                            >
                              {updatingFilename === material.filename ? '保存中...' : '保存'}
                            </button>
                            <button
                              type="button"
                              className="btn-secondary px-3 py-2 text-sm"
                              onClick={() => setEditingFilename(null)}
                            >
                              取消
                            </button>
                          </>
                        ) : (
                          <>
                            <button type="button" className="btn-secondary px-3 py-2 text-sm" onClick={() => handleEdit(material)}>
                              编辑
                            </button>
                            <button
                              type="button"
                              className="btn-secondary px-3 py-2 text-sm"
                              onClick={() => onSuggestMetadata(material.filename)}
                              disabled={suggestingFilename === material.filename}
                            >
                              {suggestingFilename === material.filename ? '识别中...' : 'AI识别'}
                            </button>
                            {(material.suggested_subject || material.suggested_grade || material.suggested_topic) ? (
                              <button
                                type="button"
                                className="btn-secondary px-3 py-2 text-sm"
                                onClick={() =>
                                  onUpdateMetadata(material.filename, {
                                    subject: material.suggested_subject || material.subject,
                                    grade: material.suggested_grade || material.grade,
                                    topic: material.suggested_topic || material.topic,
                                  })
                                }
                                disabled={updatingFilename === material.filename || suggestingFilename === material.filename}
                              >
                                采用建议
                              </button>
                            ) : null}
                          </>
                        )}
                        <button
                          type="button"
                          className="btn-secondary px-3 py-2 text-sm"
                          onClick={() => onDelete(material.filename)}
                          disabled={deletingFilename === material.filename || updatingFilename === material.filename}
                        >
                          {deletingFilename === material.filename ? '删除中...' : '删除'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </div>
    </section>
  );
}
