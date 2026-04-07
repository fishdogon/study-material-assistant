import { useEffect, useState } from 'react';
import {
  askQuestion,
  buildIndex,
  deleteMaterial,
  explainTeaching,
  generateExercises,
  getHealth,
  getMaterials,
  suggestMaterialMetadata,
  updateMaterialMetadata,
  uploadMaterial,
} from './lib/api';
import { Layout } from './components/Layout';
import { Sidebar, type AppSection } from './components/Sidebar';
import { PageHeader } from './components/PageHeader';
import { HomePage } from './components/HomePage';
import { FileUploadPanel } from './components/FileUploadPanel';
import { IndexPanel } from './components/IndexPanel';
import { MaterialsTable } from './components/MaterialsTable';
import { AskPanel } from './components/AskPanel';
import { ExplainPanel } from './components/ExplainPanel';
import { ExercisePanel } from './components/ExercisePanel';
import type {
  ExerciseResponse,
  HealthResponse,
  IndexResponse,
  MaterialSummary,
  TextModeResponse,
  UploadResponse,
} from './types/api';

export default function App() {
  const [activeSection, setActiveSection] = useState<AppSection>('home');

  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);

  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const [autoIndexHint, setAutoIndexHint] = useState<string | null>('上传后系统会自动准备资料，完成后即可生成讲解和练习。');

  const [indexLoading, setIndexLoading] = useState(false);
  const [indexError, setIndexError] = useState<string | null>(null);
  const [indexResult, setIndexResult] = useState<IndexResponse | null>(null);

  const [materials, setMaterials] = useState<MaterialSummary[]>([]);
  const [materialsLoading, setMaterialsLoading] = useState(false);
  const [materialsError, setMaterialsError] = useState<string | null>(null);
  const [deletingFilename, setDeletingFilename] = useState<string | null>(null);
  const [updatingFilename, setUpdatingFilename] = useState<string | null>(null);
  const [suggestingFilename, setSuggestingFilename] = useState<string | null>(null);

  const [qaQuery, setQaQuery] = useState('');
  const [qaLoading, setQaLoading] = useState(false);
  const [qaError, setQaError] = useState<string | null>(null);
  const [qaResult, setQaResult] = useState<TextModeResponse | null>(null);
  const [qaSelectedSourceNames, setQaSelectedSourceNames] = useState<string[]>([]);
  const [qaSubject, setQaSubject] = useState('');
  const [qaGrade, setQaGrade] = useState('');
  const [qaTopic, setQaTopic] = useState('');
  const [qaExcludeOcr, setQaExcludeOcr] = useState(false);

  const [teachingQuery, setTeachingQuery] = useState('');
  const [teachingMode, setTeachingMode] = useState('');
  const [teachingDepth, setTeachingDepth] = useState('');
  const [teachingLoading, setTeachingLoading] = useState(false);
  const [teachingError, setTeachingError] = useState<string | null>(null);
  const [teachingResult, setTeachingResult] = useState<TextModeResponse | null>(null);
  const [teachingSelectedSourceNames, setTeachingSelectedSourceNames] = useState<string[]>([]);
  const [teachingSubject, setTeachingSubject] = useState('');
  const [teachingGrade, setTeachingGrade] = useState('');
  const [teachingTopic, setTeachingTopic] = useState('');
  const [teachingExcludeOcr, setTeachingExcludeOcr] = useState(false);

  const [exerciseQuery, setExerciseQuery] = useState('');
  const [exerciseStyle, setExerciseStyle] = useState<'1' | '2' | '3'>('1');
  const [exerciseDifficulty, setExerciseDifficulty] = useState('');
  const [exerciseExpectedCount, setExerciseExpectedCount] = useState(0);
  const [exerciseLoading, setExerciseLoading] = useState(false);
  const [exerciseError, setExerciseError] = useState<string | null>(null);
  const [exerciseResult, setExerciseResult] = useState<ExerciseResponse | null>(null);
  const [exerciseSelectedSourceNames, setExerciseSelectedSourceNames] = useState<string[]>([]);
  const [exerciseSubject, setExerciseSubject] = useState('');
  const [exerciseGrade, setExerciseGrade] = useState('');
  const [exerciseTopic, setExerciseTopic] = useState('');
  const [exerciseExcludeOcr, setExerciseExcludeOcr] = useState(false);

  useEffect(() => {
    async function loadHealth() {
      try {
        const response = await getHealth();
        setHealth(response);
        setHealthError(null);
      } catch (error) {
        setHealthError(error instanceof Error ? error.message : '后端连接失败');
      }
    }

    void loadHealth();
    void loadMaterials();
  }, []);

  const loadMaterials = async () => {
    setMaterialsLoading(true);
    setMaterialsError(null);

    try {
      const response = await getMaterials();
      setMaterials(response.materials);
    } catch (error) {
      setMaterialsError(error instanceof Error ? error.message : '资料列表加载失败');
    } finally {
      setMaterialsLoading(false);
    }
  };

  const healthOnline = Boolean(health && !healthError);
  const hasMaterials = materials.length > 0;
  const sectionSummary: Record<AppSection, { eyebrow: string; note: string }> = {
    home: {
      eyebrow: '首页',
      note: '从孩子当前资料开始，先生成讲解，再继续做练习。',
    },
    materials: {
      eyebrow: '资料管理',
      note: '先上传孩子当前讲义、题单或作业，这是后续讲解和练习的基础。',
    },
    teaching: {
      eyebrow: '教学讲解',
      note: '默认先走这一步，把资料讲懂，再决定要不要继续生成练习。',
    },
    exercise: {
      eyebrow: '练习题生成',
      note: '围绕当前资料继续巩固，生成适合孩子练习的题目。',
    },
    qa: {
      eyebrow: '资料问答',
      note: '需要补充查知识点、结论或来源片段时，再使用问答。',
    },
  };

  const runBuildIndex = async () => {
    setIndexLoading(true);
    setIndexError(null);

    try {
      const response = await buildIndex();
      setIndexResult(response);
      return response;
    } catch (error) {
      setIndexResult(null);
      const message = error instanceof Error ? error.message : '索引构建失败';
      setIndexError(message);
      throw new Error(message);
    } finally {
      setIndexLoading(false);
    }
  };

  const handleUpload = async (file: File) => {
    setUploadLoading(true);
    setUploadError(null);
    setAutoIndexHint(null);

    try {
      const response = await uploadMaterial(file);
      setUploadResult(response);
      if (response.suggested_metadata && Object.values(response.suggested_metadata).some(Boolean)) {
        setAutoIndexHint(
          `资料已上传，系统初步识别为：${[response.suggested_metadata.subject, response.suggested_metadata.grade, response.suggested_metadata.topic]
            .filter(Boolean)
            .join(' / ')}`,
        );
      }

      setAutoIndexHint('资料已上传，正在自动准备后续讲解与练习所需的内容...');
      try {
        const indexResponse = await runBuildIndex();
        setAutoIndexHint(`资料已经准备完成，现在可以先生成讲解，也可以继续生成练习。当前共生成 ${indexResponse.chunk_count} 个文本块。`);
      } catch {
        setAutoIndexHint('资料已上传，但自动准备失败。你仍可在资料管理里手动更新资料准备。');
      }
      await loadMaterials();
      return true;
    } catch (error) {
      const message = error instanceof Error ? error.message : '上传失败';
      setUploadResult(null);
      setUploadError(message);
      setAutoIndexHint('上传流程未完成，资料还没有准备好。');
      return false;
    } finally {
      setUploadLoading(false);
    }
  };

  const handleBuildIndex = async () => {
    try {
      const response = await runBuildIndex();
      setAutoIndexHint(`索引已手动重建，共生成 ${response.chunk_count} 个文本块。`);
      await loadMaterials();
    } catch {
      setAutoIndexHint('手动重建索引失败，请检查后端日志或资料内容后重试。');
    }
  };

  const handleDeleteMaterial = async (filename: string) => {
    setDeletingFilename(filename);
    setMaterialsError(null);

    try {
      await deleteMaterial(filename);
      setAutoIndexHint(`资料 ${filename} 已删除，索引已同步更新。`);
      await loadMaterials();
    } catch (error) {
      setMaterialsError(error instanceof Error ? error.message : '删除资料失败');
    } finally {
      setDeletingFilename(null);
    }
  };

  const handleUpdateMaterialMetadata = async (
    filename: string,
    payload: { subject: string; grade: string; topic: string },
  ) => {
    setUpdatingFilename(filename);
    setMaterialsError(null);

    try {
      await updateMaterialMetadata(filename, payload);
      await loadMaterials();
    } catch (error) {
      setMaterialsError(error instanceof Error ? error.message : '资料元信息更新失败');
    } finally {
      setUpdatingFilename(null);
    }
  };

  const handleSuggestMaterialMetadata = async (filename: string) => {
    setSuggestingFilename(filename);
    setMaterialsError(null);

    try {
      await suggestMaterialMetadata(filename);
      await loadMaterials();
    } catch (error) {
      setMaterialsError(error instanceof Error ? error.message : 'AI 标签识别失败');
    } finally {
      setSuggestingFilename(null);
    }
  };

  const toggleSelectedSourceName = (
    filename: string,
    current: string[],
    setter: (value: string[]) => void,
  ) => {
    setter(current.includes(filename) ? current.filter((item) => item !== filename) : [...current, filename]);
  };

  const latestContext = {
    filename: uploadResult?.filename ?? '',
    subject: uploadResult?.suggested_metadata?.subject ?? '',
    grade: uploadResult?.suggested_metadata?.grade ?? '',
    topic: uploadResult?.suggested_metadata?.topic ?? '',
  };

  const openTeachingFlow = () => {
    if (latestContext.filename) {
      setTeachingSelectedSourceNames([latestContext.filename]);
    }
    if (latestContext.subject) {
      setTeachingSubject(latestContext.subject);
    }
    if (latestContext.grade) {
      setTeachingGrade(latestContext.grade);
    }
    if (latestContext.topic) {
      setTeachingTopic(latestContext.topic);
    }
    if (!teachingQuery.trim()) {
      const topicText = latestContext.topic || '这份资料';
      const gradeText = latestContext.grade ? `${latestContext.grade}孩子` : '孩子';
      setTeachingQuery(`${topicText}应该怎么给${gradeText}讲，才能更容易听懂？`);
    }
    setActiveSection('teaching');
  };

  const openExerciseFlow = () => {
    if (latestContext.filename) {
      setExerciseSelectedSourceNames([latestContext.filename]);
    }
    if (latestContext.subject) {
      setExerciseSubject(latestContext.subject);
    }
    if (latestContext.grade) {
      setExerciseGrade(latestContext.grade);
    }
    if (latestContext.topic) {
      setExerciseTopic(latestContext.topic);
    }
    if (!exerciseQuery.trim()) {
      const topicText = latestContext.topic || '当前资料内容';
      const gradeText = latestContext.grade || '当前阶段';
      setExerciseQuery(`请围绕${topicText}出 3 道适合${gradeText}练习的题目`);
    }
    setActiveSection('exercise');
  };

  const continueFromTeachingToExercise = () => {
    if (teachingSelectedSourceNames.length > 0) {
      setExerciseSelectedSourceNames(teachingSelectedSourceNames);
    }
    if (teachingSubject) {
      setExerciseSubject(teachingSubject);
    }
    if (teachingGrade) {
      setExerciseGrade(teachingGrade);
    }
    if (teachingTopic) {
      setExerciseTopic(teachingTopic);
    }
    if (teachingQuery.trim() && !exerciseQuery.trim()) {
      const topicText = teachingTopic || latestContext.topic || '当前资料内容';
      const gradeText = teachingGrade || latestContext.grade || '当前阶段';
      setExerciseQuery(`请围绕${topicText}出 3 道适合${gradeText}继续巩固的题目，并附简短答案`);
    }
    setActiveSection('exercise');
  };

  const handleAsk = async () => {
    setQaLoading(true);
    setQaError(null);

    try {
      const response = await askQuestion({
        query: qaQuery.trim(),
        source_names: qaSelectedSourceNames,
        subject: qaSubject,
        grade: qaGrade,
        topic: qaTopic,
        exclude_ocr: qaExcludeOcr,
      });
      setQaResult(response);
    } catch (error) {
      setQaResult(null);
      setQaError(error instanceof Error ? error.message : '问答失败');
    } finally {
      setQaLoading(false);
    }
  };

  const handleExplain = async () => {
    setTeachingLoading(true);
    setTeachingError(null);

    try {
      const response = await explainTeaching({
        query: teachingQuery.trim(),
        source_names: teachingSelectedSourceNames,
        subject: teachingSubject,
        grade: teachingGrade,
        topic: teachingTopic,
        exclude_ocr: teachingExcludeOcr,
        teaching_mode: teachingMode,
        explanation_depth: teachingDepth,
      });
      setTeachingResult(response);
    } catch (error) {
      setTeachingResult(null);
      setTeachingError(error instanceof Error ? error.message : '讲解生成失败');
    } finally {
      setTeachingLoading(false);
    }
  };

  const handleGenerateExercises = async () => {
    setExerciseLoading(true);
    setExerciseError(null);

    try {
      const response = await generateExercises({
        query: exerciseQuery.trim(),
        style: exerciseStyle,
        source_names: exerciseSelectedSourceNames,
        subject: exerciseSubject,
        grade: exerciseGrade,
        topic: exerciseTopic,
        exclude_ocr: exerciseExcludeOcr,
        difficulty: exerciseDifficulty,
        expected_count: exerciseExpectedCount,
      });
      setExerciseResult(response);
    } catch (error) {
      setExerciseResult(null);
      setExerciseError(error instanceof Error ? error.message : '练习题生成失败');
    } finally {
      setExerciseLoading(false);
    }
  };

  const renderContent = () => {
    switch (activeSection) {
      case 'home':
        return (
          <HomePage
            uploadLoading={uploadLoading}
            uploadError={uploadError}
            uploadResult={uploadResult}
            autoIndexHint={autoIndexHint}
            onUpload={handleUpload}
            materials={materials}
            materialsLoading={materialsLoading}
            latestFilename={latestContext.filename}
            latestSubject={latestContext.subject}
            latestGrade={latestContext.grade}
            latestTopic={latestContext.topic}
            indexResult={indexResult}
            onOpenTeaching={openTeachingFlow}
            onOpenExercise={openExerciseFlow}
            onOpenMaterials={() => setActiveSection('materials')}
          />
        );

      case 'materials':
        return (
          <div className="space-y-6">
            <PageHeader
              title="资料管理"
              description="这里负责资料上传、标签整理和后台准备。资料准备完成后，建议优先去“教学讲解”，再继续生成练习。"
              rightSlot={
                <div className="rounded-xl border border-line bg-white px-4 py-3 text-sm text-slate-600">
                  <div className="font-medium text-slate-800">后端状态</div>
                  <div className="mt-1">{health?.message ?? healthError ?? '检测中...'}</div>
                </div>
              }
            />
            <section className="panel p-6">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <h3 className="panel-title">推荐下一步</h3>
                  <p className="mt-1 text-sm leading-6 text-slate-600">
                    资料准备完成后，建议先生成讲解，把内容讲懂；再继续生成练习，帮助孩子围绕当前资料做巩固。
                  </p>
                </div>
                <div className="flex flex-col gap-3 sm:flex-row">
                  <button type="button" className="btn-primary w-full sm:w-auto" onClick={openTeachingFlow} disabled={!hasMaterials}>
                    先生成讲解
                  </button>
                  <button type="button" className="btn-secondary w-full px-4 py-2.5 sm:w-auto" onClick={openExerciseFlow} disabled={!hasMaterials}>
                    再生成练习
                  </button>
                </div>
              </div>
              {!hasMaterials ? (
                <div className="panel-subtle mt-4">请先上传资料并完成准备，系统才能围绕当前内容生成讲解和练习。</div>
              ) : null}
              {latestContext.filename ? (
                <div className="mt-4 flex flex-wrap gap-2">
                  <span className="tag">当前资料：{latestContext.filename}</span>
                  {latestContext.topic ? <span className="tag">专题：{latestContext.topic}</span> : null}
                  {latestContext.grade ? <span className="tag">年级：{latestContext.grade}</span> : null}
                </div>
              ) : null}
            </section>
            <div className="grid gap-6 xl:grid-cols-2">
              <FileUploadPanel
                loading={uploadLoading}
                error={uploadError}
                result={uploadResult}
                autoIndexHint={autoIndexHint}
                onUpload={handleUpload}
              />
              <IndexPanel
                loading={indexLoading}
                error={indexError}
                result={indexResult}
                onBuildIndex={handleBuildIndex}
              />
            </div>
            <MaterialsTable
              materials={materials}
              loading={materialsLoading}
              error={materialsError}
              deletingFilename={deletingFilename}
              updatingFilename={updatingFilename}
              suggestingFilename={suggestingFilename}
              onRefresh={loadMaterials}
              onDelete={handleDeleteMaterial}
              onUpdateMetadata={handleUpdateMaterialMetadata}
              onSuggestMetadata={handleSuggestMaterialMetadata}
            />
          </div>
        );

      case 'qa':
        return (
          <>
            <PageHeader
              title="资料问答"
              description="这是补充查询页。适合在看过讲解后，继续查某个知识点、结论或来源片段。"
            />
            <AskPanel
              title="提问"
              description="适合查资料重点、知识点定义、易错点与结论。"
              placeholder="例如：和倍问题的基本思路是什么？"
              value={qaQuery}
              loading={qaLoading}
              error={qaError}
              result={qaResult}
              submitLabel="开始问答"
              materials={materials}
              selectedSourceNames={qaSelectedSourceNames}
              subject={qaSubject}
              grade={qaGrade}
              topic={qaTopic}
              excludeOcr={qaExcludeOcr}
              onChange={setQaQuery}
              onToggleSourceName={(filename) =>
                toggleSelectedSourceName(filename, qaSelectedSourceNames, setQaSelectedSourceNames)
              }
              onSubjectChange={setQaSubject}
              onGradeChange={setQaGrade}
              onTopicChange={setQaTopic}
              onExcludeOcrChange={setQaExcludeOcr}
              onClearFilters={() => {
                setQaSelectedSourceNames([]);
                setQaSubject('');
                setQaGrade('');
                setQaTopic('');
                setQaExcludeOcr(false);
              }}
              onSubmit={handleAsk}
            />
          </>
        );

      case 'teaching':
        return (
          <>
            <PageHeader
              title="教学讲解"
              description="这是默认推荐的第一步。围绕孩子当前资料生成更容易讲清楚的解释，帮助你先把内容讲懂。"
            />
            <ExplainPanel
              value={teachingQuery}
              teachingMode={teachingMode}
              explanationDepth={teachingDepth}
              loading={teachingLoading}
              error={teachingError}
              result={teachingResult}
              materials={materials}
              selectedSourceNames={teachingSelectedSourceNames}
              subject={teachingSubject}
              grade={teachingGrade}
              topic={teachingTopic}
              excludeOcr={teachingExcludeOcr}
              onChange={setTeachingQuery}
              onTeachingModeChange={setTeachingMode}
              onExplanationDepthChange={setTeachingDepth}
              onToggleSourceName={(filename) =>
                toggleSelectedSourceName(filename, teachingSelectedSourceNames, setTeachingSelectedSourceNames)
              }
              onSubjectChange={setTeachingSubject}
              onGradeChange={setTeachingGrade}
              onTopicChange={setTeachingTopic}
              onExcludeOcrChange={setTeachingExcludeOcr}
              onClearFilters={() => {
                setTeachingSelectedSourceNames([]);
                setTeachingSubject('');
                setTeachingGrade('');
                setTeachingTopic('');
                setTeachingExcludeOcr(false);
                setTeachingMode('');
                setTeachingDepth('');
              }}
              onSubmit={handleExplain}
              onContinueToExercise={continueFromTeachingToExercise}
            />
          </>
        );

      case 'exercise':
        return (
          <>
            <PageHeader
              title="练习题生成"
              description="在讲解之后继续生成同专题练习，帮助孩子围绕当前资料做巩固。"
            />
            <ExercisePanel
              query={exerciseQuery}
              style={exerciseStyle}
              difficulty={exerciseDifficulty}
              expectedCount={exerciseExpectedCount}
              loading={exerciseLoading}
              error={exerciseError}
              result={exerciseResult}
              materials={materials}
              selectedSourceNames={exerciseSelectedSourceNames}
              subject={exerciseSubject}
              grade={exerciseGrade}
              topic={exerciseTopic}
              excludeOcr={exerciseExcludeOcr}
              onQueryChange={setExerciseQuery}
              onStyleChange={setExerciseStyle}
              onDifficultyChange={setExerciseDifficulty}
              onExpectedCountChange={setExerciseExpectedCount}
              onToggleSourceName={(filename) =>
                toggleSelectedSourceName(filename, exerciseSelectedSourceNames, setExerciseSelectedSourceNames)
              }
              onSubjectChange={setExerciseSubject}
              onGradeChange={setExerciseGrade}
              onTopicChange={setExerciseTopic}
              onExcludeOcrChange={setExerciseExcludeOcr}
              onClearFilters={() => {
                setExerciseSelectedSourceNames([]);
                setExerciseSubject('');
                setExerciseGrade('');
                setExerciseTopic('');
                setExerciseExcludeOcr(false);
                setExerciseDifficulty('');
                setExerciseExpectedCount(0);
              }}
              onSubmit={handleGenerateExercises}
            />
          </>
        );

      default:
        return null;
    }
  };

  return (
    <Layout
      sidebar={({ closeMobileSidebar }) => (
        <Sidebar
          activeSection={activeSection}
          onSelect={setActiveSection}
          onNavigate={closeMobileSidebar}
        />
      )}
    >
      <div className="space-y-6">
        {activeSection !== 'home' ? (
          <section className="panel px-6 py-5">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <div className="text-sm font-medium text-slate-500">围绕孩子当前资料的数学辅导助手</div>
                <div className="mt-2 text-[28px] font-semibold tracking-tight text-slate-900">{itemsLabel(activeSection)}</div>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">{sectionSummary[activeSection].note}</p>
              </div>
              <div className="text-sm leading-6 text-slate-500">
                {healthOnline ? health?.message : healthError ?? '检测中...'}
              </div>
            </div>
          </section>
        ) : null}
        {renderContent()}
      </div>
    </Layout>
  );
}

function itemsLabel(section: AppSection) {
  if (section === 'home') {
    return '首页';
  }

  if (section === 'materials') {
    return '资料管理';
  }

  if (section === 'qa') {
    return '资料问答';
  }

  if (section === 'teaching') {
    return '教学讲解';
  }

  return '练习题生成';
}
