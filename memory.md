# Project Memory

## 项目概览

- 项目名称：学习资料智能助手
- 项目定位：面向数学辅导与教学场景的教育类 RAG 产品，当前对外更偏家长辅导叙事，底层能力按老师标准打磨
- 当前形态：FastAPI 后端 + React Web 前端 + Qdrant 向量库
- 当前重点方向：从“资料问答原型”走向“数学教育垂类 RAG”，主流程强调“上传资料 -> 先讲懂 -> 再练习”

---

## 当前系统架构

### 后端

- FastAPI 提供 API
- 资料支持：
  - `txt`
  - `pdf`
  - `image(OCR)`
- 主要能力：
  - 文件上传
  - 重建索引
  - 资料问答
  - 教学讲解
  - 练习题生成
  - 资料列表
  - 删除资料
  - 资料元信息编辑
  - AI 建议标签生成

### 前端

- 目录：`frontend/`
- 技术栈：
  - React
  - TypeScript
  - Vite
  - Tailwind CSS
- 当前已形成可演示单页应用

### 向量检索

- 当前主要向量库：Qdrant
- embedding：`all-MiniLM-L6-v2`
- 检索逻辑：dense 检索 + 简单后处理

---

## 已完成的功能建设

## 1. 独立前端工程建设

已完成：

- 初始化 `frontend/`
- 配置 Vite + React + TypeScript + Tailwind
- 建立 API 封装与 TypeScript 类型
- 实现左侧导航 + 右侧内容区单页布局

已实现页面：

- 资料管理
- 资料问答
- 教学讲解
- 练习题生成

已实现组件：

- `Layout`
- `Sidebar`
- `PageHeader`
- `FileUploadPanel`
- `IndexPanel`
- `AskPanel`
- `ExplainPanel`
- `ExercisePanel`
- `SourceSummaryCard`
- `RetrievedChunksList`
- `ExerciseCard`
- `LoadingState`
- `ErrorState`
- `EmptyState`
- `MarkdownContent`
- `MaterialsTable`
- `MaterialScopeFilter`

---

## 2. 前端交互与产品化优化

已完成：

- 上传后自动重建索引
- Markdown 渲染支持
- 复制回答 / 复制题目
- 移动端抽屉侧栏
- 资料范围过滤
- 检索片段筛选
- 空状态 / 错误状态 / loading 状态
- 中文化文案清理
- 去除面向开发者的英文装饰标题与接口暴露文案

视觉方向调整过：

- 初版工具型布局
- 后续改成更接近教育类产品的界面
- 再做了降饱和与细节统一

---

## 3. 前后端联调与真实问题修复

### 已完成真实联调

已验证：

- `GET /`
- `POST /materials/upload`
- `POST /materials/index`
- `POST /qa/ask`
- `POST /teaching/explain`
- `POST /exercises/generate`

### 已修复的重要问题

#### 上传链路问题

- 上传本身成功，但上传后自动重建索引可能失败
- 修复了：
  - 模型加载优先使用本地 Hugging Face 缓存
  - 索引构建失败时返回更明确错误
- 重启电脑后补启动 Qdrant 容器，恢复索引能力

#### 移动端抽屉问题

- 切换模块后侧栏不会自动关闭
- 已修复

#### 上传失败重试问题

- 上传失败后文件状态被错误清空
- 同文件无法直接重试
- 已修复

#### 过滤逻辑问题

- 有筛选条件但无匹配资料时，系统曾错误回退到全库检索
- 已修复为显式返回 `未找到符合筛选条件的资料`

---

## 4. 资料管理能力升级

已完成：

- `GET /materials`
- `DELETE /materials/{filename}`
- `PATCH /materials/{filename}`

资料列表支持：

- 文件名
- 类型
- 解析器
- chunk 数量
- OCR 标记
- 学科 / 年级 / 专题

前端支持：

- 删除资料
- 手动编辑元信息
- 刷新资料列表

---

## 5. 检索过滤能力升级

已完成：

- 按文件名过滤
- 按学科过滤
- 按年级过滤
- 按专题过滤
- 排除 OCR

相关接口已支持：

- `/qa/ask`
- `/teaching/explain`
- `/exercises/generate`

这使系统从“全库盲搜”走向“资料范围可控”。

---

## 6. 讲解与练习生成质量升级

已完成：

- 教学讲解从“普通回答”升级为“结构化辅导稿”
- 讲解支持自动判断：
  - 家长辅导场景
  - 老师备课 / 课堂讲解场景
  - 通用辅导场景
- 讲解支持控制详略：
  - 简洁
  - 标准
  - 详细
- 讲解 prompt 强制输出稳定的 Markdown 结构：
  - 这份资料主要在讲什么
  - 核心思路
  - 分步骤讲解 / 课堂讲解顺序
  - 可以直接对孩子说的话
  - 常见易错点
  - 辅导提醒 / 教学提醒

练习题生成已完成：

- `style=1/2/3` 不再只是前端裁字段，而是真正影响生成
- 支持自动识别或显式控制：
  - 题量
  - 难度
- 支持数学专题纯度守卫：
  - 例如和倍问题不会再轻易混入差倍、和差、倍差
- 练习题支持分层生成：
  - 基础巩固
  - 同类变式
  - 略提高
  - 或提高场景下的铺垫题 / 变式题 / 提高题
- 后端已对练习结果做后处理，把层次标签真正写回题目标题与意图
- 前端结果区已显式展示练习结构摘要

相关核心文件：

- [app/prompt_utils.py](/Users/long/Downloads/workSpace/study-material-assistant/app/prompt_utils.py)
- [app/explainer.py](/Users/long/Downloads/workSpace/study-material-assistant/app/explainer.py)
- [app/exercise_generator.py](/Users/long/Downloads/workSpace/study-material-assistant/app/exercise_generator.py)
- [app/retriever.py](/Users/long/Downloads/workSpace/study-material-assistant/app/retriever.py)
- [frontend/src/components/ExplainPanel.tsx](/Users/long/Downloads/workSpace/study-material-assistant/frontend/src/components/ExplainPanel.tsx)
- [frontend/src/components/ExercisePanel.tsx](/Users/long/Downloads/workSpace/study-material-assistant/frontend/src/components/ExercisePanel.tsx)
- [frontend/src/components/ExerciseCard.tsx](/Users/long/Downloads/workSpace/study-material-assistant/frontend/src/components/ExerciseCard.tsx)

---

## 7. AI 标签建议能力

已完成：

- 上传资料后自动生成 AI 建议标签
- 为已有资料手动触发 `AI识别`
- 资料列表中展示 AI 建议标签
- 支持“一键采用建议”
- 保留人工最终确认机制，不直接强覆盖正式标签

后端新增：

- [app/material_tagger.py](/Users/long/Downloads/workSpace/study-material-assistant/app/material_tagger.py)
- `POST /materials/{filename}/suggest-metadata`

当前标签体系：

- 正式标签：
  - `subject`
  - `grade`
  - `topic`
- AI 建议标签：
  - `suggested_subject`
  - `suggested_grade`
  - `suggested_topic`

---

## 当前技术债与已知短板

### 检索相关性

- 当前仍是 dense 检索为主
- 仍未引入真正 hybrid retrieval
- 仍未引入 reranker
- 关键词重排已比初版更强，但仍不是正式 rerank

### 数学场景能力

- 题型纯度约束已补第一版，但元信息标签还不够细
- 没有 `problem_type`
- 没有 `pedagogical_role`
- 数学公式与题目结构解析仍偏弱
- 讲解和练习结果虽然更结构化，但还没有导出链路

### 文档解析

- PDF 解析仍偏基础
- OCR 主要依赖外部脚本
- 尚未使用数学更友好的结构化解析工具

---

## 当前最重要的下一步

### 产品方向

把项目从“通用学习资料助手”升级为“围绕孩子当前资料的数学辅导助手”，并保留老师可用的专业底层能力。

### 产品策略补充

- 对外主叙事用户：家长
- 底层能力打磨用户：家教老师 / 数学老师
- 首页默认主流程：
  1. 上传资料
  2. 先生成讲解
  3. 再生成练习
- 未来高价值交付物：
  - 讲解稿
  - 练习单
  - 小测卷
  - PDF / Word 导出

### 技术优先级

1. hybrid retrieval
2. reranker
3. `problem_type / pedagogical_role` 标签
4. 数学语义切块
5. 导出能力

---

## 简历 / 面试问答可提炼点

### 可描述的项目亮点

#### 1. 从后端原型补成可演示产品

- 为已有 FastAPI 后端独立搭建 React + TypeScript + Vite + Tailwind 前端
- 形成资料管理、问答、教学讲解、练习题生成完整闭环

#### 2. 设计并实现资料范围可控的 RAG 查询

- 从全库盲检索升级为按文件、学科、年级、专题、OCR 条件过滤
- 修复“筛选为空时错误回退全库”的逻辑漏洞

#### 3. 解决上传后自动索引的真实稳定性问题

- 定位并修复索引链路中模型加载与向量库依赖问题
- 将 embedding 模型加载改成本地缓存优先，提升离线环境稳定性

#### 4. 建立 AI 标签建议机制

- 为资料自动提取 `学科 / 年级 / 专题`
- 设计“AI 建议 + 人工确认”的产品机制，平衡自动化与准确性

#### 5. 从产品层明确主流程

- 将产品链路从“文件问答”转向“上传资料 -> 先讲懂 -> 再练习”
- 明确家长是对外主叙事用户，老师是底层能力打磨用户

#### 6. 把生成结果从“普通回答”升级成“教学产物”

- 让教学讲解稳定输出成结构化辅导稿
- 让练习题生成支持题量、难度和分层练习
- 让前端结果区能直接体现“基础巩固 -> 变式 -> 提高”的教学节奏

---

## 当前运行约定

- 前端地址：
  - [http://127.0.0.1:5173/](http://127.0.0.1:5173/)
- 后端地址：
  - [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Qdrant：
  - [http://127.0.0.1:6333/](http://127.0.0.1:6333/)

---

## 备注

- `notes/frontend_memory.md` 保留为前端专项记忆
- 本文件 `memory.md` 作为项目级长期回溯文件
- 后续如果继续开发，优先更新本文件和 `product_prd_mvp.md`
