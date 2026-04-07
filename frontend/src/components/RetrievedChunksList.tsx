import { useMemo, useState } from 'react';
import type { RetrievedChunk } from '../types/api';

interface RetrievedChunksListProps {
  chunks: RetrievedChunk[];
}

export function RetrievedChunksList({ chunks }: RetrievedChunksListProps) {
  const [expandedKeys, setExpandedKeys] = useState<Record<string, boolean>>({});
  const [selectedSourceType, setSelectedSourceType] = useState<string>('all');
  const [selectedSource, setSelectedSource] = useState<string>('all');
  const [onlyOcr, setOnlyOcr] = useState(false);
  const [highRelevanceOnly, setHighRelevanceOnly] = useState(false);

  const toggleExpanded = (key: string) => {
    setExpandedKeys((current) => ({
      ...current,
      [key]: !current[key],
    }));
  };

  const sourceTypes = useMemo(
    () => ['all', ...Array.from(new Set(chunks.map((chunk) => chunk.source_type)))],
    [chunks],
  );

  const sources = useMemo(
    () => ['all', ...Array.from(new Set(chunks.map((chunk) => chunk.source)))],
    [chunks],
  );

  const filteredChunks = useMemo(() => {
    return chunks.filter((chunk, index) => {
      if (selectedSourceType !== 'all' && chunk.source_type !== selectedSourceType) {
        return false;
      }

      if (selectedSource !== 'all' && chunk.source !== selectedSource) {
        return false;
      }

      if (onlyOcr && !chunk.is_ocr) {
        return false;
      }

      if (highRelevanceOnly) {
        const keywordScore = chunk.keyword_score ?? 0;
        if (keywordScore < 4 && index >= 2) {
          return false;
        }
      }

      return true;
    });
  }, [chunks, selectedSourceType, selectedSource, onlyOcr, highRelevanceOnly]);

  return (
    <section className="panel p-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="panel-title">检索片段</h3>
        </div>
        <span className="text-sm text-slate-500">
          {filteredChunks.length} / {chunks.length} 条
        </span>
      </div>

      {chunks.length === 0 ? (
        <div className="mt-4 rounded-[22px] border border-dashed border-slate-300 px-4 py-8 text-center text-sm text-slate-500">
          暂无检索片段。
        </div>
      ) : (
        <div className="mt-4 space-y-4">
          <div className="grid gap-3 lg:grid-cols-[1fr_1fr_auto_auto]">
            <select
              className="input-base"
              value={selectedSourceType}
              onChange={(event) => setSelectedSourceType(event.target.value)}
            >
              {sourceTypes.map((type) => (
                <option key={type} value={type}>
                  {type === 'all' ? '全部来源类型' : `来源类型：${type}`}
                </option>
              ))}
            </select>
            <select className="input-base" value={selectedSource} onChange={(event) => setSelectedSource(event.target.value)}>
              {sources.map((source) => (
                <option key={source} value={source}>
                  {source === 'all' ? '全部来源文件' : source}
                </option>
              ))}
            </select>
            <label className="panel-subtle flex items-center gap-2">
              <input type="checkbox" checked={onlyOcr} onChange={(event) => setOnlyOcr(event.target.checked)} />
              仅看 OCR
            </label>
            <label className="panel-subtle flex items-center gap-2">
              <input
                type="checkbox"
                checked={highRelevanceOnly}
                onChange={(event) => setHighRelevanceOnly(event.target.checked)}
              />
              高相关优先
            </label>
          </div>

          {highRelevanceOnly ? (
            <div className="panel-subtle">
              当前已优先保留关键词分数更高的片段，并默认保留排序前两条结果，帮助减少无关资料干扰。
            </div>
          ) : null}

          {filteredChunks.length === 0 ? (
            <div className="rounded-[18px] border border-slate-200 bg-slate-50 px-5 py-8 text-center text-sm text-slate-500">
              当前筛选条件下没有可展示的片段，请放宽筛选条件。
            </div>
          ) : null}

          {filteredChunks.map((chunk, index) => (
            <article key={`${chunk.id}-${index}`} className="rounded-[20px] border border-slate-200 bg-white p-4">
              <div className="flex flex-wrap gap-2">
                <span className="tag">来源：{chunk.source}</span>
                <span className="tag">类型：{chunk.source_type}</span>
                <span className="tag">解析器：{chunk.parser_name}</span>
                <span className="tag">{chunk.is_ocr ? 'OCR' : '非 OCR'}</span>
                <span className="tag">距离：{chunk.distance.toFixed(3)}</span>
                {chunk.keyword_score !== undefined ? <span className="tag">关键词分数：{chunk.keyword_score}</span> : null}
              </div>
              <p
                className={
                  expandedKeys[`${chunk.id}-${index}`]
                    ? 'mt-4 whitespace-pre-wrap break-words text-sm leading-6 text-slate-700'
                    : 'mt-4 line-clamp-4 whitespace-pre-wrap break-words text-sm leading-6 text-slate-700'
                }
              >
                {chunk.content}
              </p>
              <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
                <span>{chunk.is_ocr ? '该片段来自 OCR 结果，阅读时请注意识别误差。' : '该片段来自非 OCR 文本资料。'}</span>
                <button
                  type="button"
                  className="btn-secondary px-3 py-1.5 text-xs"
                  onClick={() => toggleExpanded(`${chunk.id}-${index}`)}
                >
                  {expandedKeys[`${chunk.id}-${index}`] ? '收起' : '展开全文'}
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
