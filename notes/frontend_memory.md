# Frontend Memory

## 项目定位

- 项目名称：学习资料智能助手
- 前端目录固定在仓库根目录 `frontend/`
- 前端目标：为现有后端 API 提供最小可用、界面干净专业的 Web 前端
- 前端原则：优先保证接口跑通、页面清楚好用，不做过度设计

## 明确约束

- 尽量不改后端 Python 代码
- 如前后端联调必须，允许做最小改动
- 前端技术栈固定：
  - React
  - TypeScript
  - Vite
  - Tailwind CSS
- 页面风格：
  - 简约高级
  - 专业、干净、轻量
  - 偏工具型产品界面
  - 不使用花哨动画
- 状态管理先使用本地 state + hooks，不引入 Redux 等复杂状态库
- 所有后端请求地址必须通过 `VITE_API_BASE_URL` 配置
- 界面文案以中文为主

## 当前前端实现状态

- 已创建独立前端工程：`frontend/`
- 已完成 Vite + React + TypeScript + Tailwind 基础配置
- 已实现单页应用结构：左侧导航 + 右侧内容区
- 已完成四个主功能区：
  - 资料管理
  - 资料问答
  - 教学讲解
  - 练习题生成
- 已实现 API 请求封装：`frontend/src/lib/api.ts`
- 已实现类型定义：`frontend/src/types/api.ts`
- 已补充 `frontend/README.md`
- 已执行 `npm run build`，构建通过

## 当前组件约定

- 已实现组件：
  - `Layout`
  - `Sidebar`
  - `PageHeader`
  - `FileUploadPanel`
  - `IndexPanel`
  - `AskPanel`
  - `ExercisePanel`
  - `SourceSummaryCard`
  - `RetrievedChunksList`
  - `ExerciseCard`
  - `LoadingState`
  - `ErrorState`
- 当前“教学讲解”复用了 `AskPanel`
- 用户最初期望中提到 `ExplainPanel`
- 如果后续需要更清晰的组件边界，可以新增 `ExplainPanel`，但当前 MVP 复用 `AskPanel` 是有意的，属于简化实现，不影响功能

## 后端接口约定

- `GET /`
  - 用于健康检查
- `POST /materials/upload`
  - 表单字段：`file`
- `POST /materials/index`
  - 无请求体
  - 返回索引构建结果、chunk 数量、来源统计
- `POST /qa/ask`
  - 请求体：`{ query: string }`
  - 返回文本回答、来源摘要、检索片段
- `POST /teaching/explain`
  - 请求体：`{ query: string }`
  - 返回结构与问答模式基本一致
- `POST /exercises/generate`
  - 请求体：`{ query: string, style: "1" | "2" | "3" }`
  - 返回结构化练习题结果

## 当前后端联调改动

- 为支持本地前端开发联调，已在 `app/api.py` 增加最小 CORS 配置
- 当前允许来源：
  - `http://localhost:5173`
  - `http://127.0.0.1:5173`
- 这属于联调必需的小改动，尽量不要继续扩大后端改动范围

## 当前前端页面行为

### 资料管理

- 支持文件上传
- 支持重建索引
- 展示上传状态、索引状态、错误信息
- 展示索引结果：
  - `message`
  - `chunk_count`
  - `source_count`

### 资料问答

- 输入问题后调用 `/qa/ask`
- 展示：
  - `answer`
  - `source_summary.note`
  - `retrieved_chunks`

### 教学讲解

- 输入问题后调用 `/teaching/explain`
- 展示：
  - `answer`
  - `source_summary.note`
  - `retrieved_chunks`

### 练习题生成

- 输入出题需求
- 选择 `style`
- 调用 `/exercises/generate`
- 展示：
  - `topic`
  - `grade`
  - `exercises`
  - `source_summary.note`
  - `retrieved_chunks`
- 题目显示规则：
  - `style=1`：显示 `title` / `problem` / `intent` / `hint`
  - `style=2`：额外显示 `answer`
  - `style=3`：额外显示 `answer` + `explanation`

## 后续迭代建议

- 若要继续增强，可优先考虑：
  - 补空状态占位的细节文案
  - 增加接口成功后的轻量提示
  - 增加移动端导航体验优化
  - 为 `ExplainPanel` 做独立组件拆分
  - 增加来源类型筛选或折叠检索片段
- 暂不建议：
  - 引入复杂状态管理库
  - 过早做视觉特效
  - 将前端嵌入后端目录结构

## 本地运行约定

- 前端环境变量文件：`frontend/.env`
- 当前默认值：
  - `VITE_API_BASE_URL=http://127.0.0.1:8000`
- 常用命令：
  - `cd frontend && npm install`
  - `cd frontend && npm run dev`
  - `cd frontend && npm run build`
