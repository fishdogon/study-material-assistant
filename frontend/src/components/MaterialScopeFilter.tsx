import type { MaterialSummary } from '../types/api';

interface MaterialScopeFilterProps {
  materials: MaterialSummary[];
  selectedSourceNames: string[];
  subject: string;
  grade: string;
  topic: string;
  excludeOcr: boolean;
  disabled?: boolean;
  onToggleSourceName: (filename: string) => void;
  onSubjectChange: (value: string) => void;
  onGradeChange: (value: string) => void;
  onTopicChange: (value: string) => void;
  onExcludeOcrChange: (value: boolean) => void;
  onClear: () => void;
}

export function MaterialScopeFilter({
  materials,
  selectedSourceNames,
  subject,
  grade,
  topic,
  excludeOcr,
  disabled = false,
  onToggleSourceName,
  onSubjectChange,
  onGradeChange,
  onTopicChange,
  onExcludeOcrChange,
  onClear,
}: MaterialScopeFilterProps) {
  const subjects = Array.from(new Set(materials.map((material) => material.subject).filter(Boolean)));
  const grades = Array.from(new Set(materials.map((material) => material.grade).filter(Boolean)));
  const topics = Array.from(new Set(materials.map((material) => material.topic).filter(Boolean)));

  return (
    <section className="panel p-6">
      <h3 className="panel-title">资料范围</h3>
      <p className="mt-1 text-sm leading-6 text-slate-600">需要时可限定资料范围，避免混入无关内容。</p>

      <div className="mt-4 space-y-4">
        <div className="panel-soft-area">
          <div className="grid gap-3 md:grid-cols-3">
            <select className="input-base" value={subject} disabled={disabled} onChange={(event) => onSubjectChange(event.target.value)}>
              <option value="">全部学科</option>
              {subjects.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
            <select className="input-base" value={grade} disabled={disabled} onChange={(event) => onGradeChange(event.target.value)}>
              <option value="">全部年级</option>
              {grades.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
            <select className="input-base" value={topic} disabled={disabled} onChange={(event) => onTopicChange(event.target.value)}>
              <option value="">全部专题</option>
              {topics.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </div>
          <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-sm font-medium text-slate-800">选择资料</div>
            <button type="button" className="btn-secondary px-3 py-2 text-sm" onClick={onClear} disabled={disabled}>
              清空选择
            </button>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {materials.length === 0 ? (
              <span className="text-sm text-slate-500">当前没有可用资料，请先上传并建立索引。</span>
            ) : (
              materials.map((material) => {
                const active = selectedSourceNames.includes(material.filename);
                return (
                  <button
                    key={material.id}
                    type="button"
                    disabled={disabled}
                    onClick={() => onToggleSourceName(material.filename)}
                    className={
                      active
                        ? 'rounded-full border border-slate-300 bg-slate-900 px-3 py-1.5 text-xs font-medium text-white'
                        : 'rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600'
                    }
                  >
                    {material.filename}
                  </button>
                );
              })
            )}
          </div>
        </div>

        <label className="panel-subtle flex items-center gap-2">
          <input
            type="checkbox"
            checked={excludeOcr}
            disabled={disabled}
            onChange={(event) => onExcludeOcrChange(event.target.checked)}
          />
          排除 OCR 图片资料
        </label>
      </div>
    </section>
  );
}
