# 数学教育类 RAG 具体改造方案

## 目标

把当前“学习资料智能助手”从通用资料问答原型，升级成一个更适合数学教育场景的高相关性 RAG 系统。

本方案重点解决：

- 检索结果混入相近但错误的题型
- 数学资料中的公式、题目、讲解结构没有被充分利用
- OCR 与 PDF 内容质量不稳定时，检索精度下降
- 当前只有 dense + 简单字符级重排，缺少真正的 hybrid retrieval 与 rerank

---

## 当前系统现状

### 已有能力

- FastAPI 后端，支持上传资料、重建索引、资料问答、教学讲解、练习题生成
- 支持 `txt / pdf / image(OCR)` 三类资料接入
- 使用 Qdrant 作为主要向量库
- 使用 `sentence-transformers/all-MiniLM-L6-v2` 生成向量
- 使用 React + TypeScript + Vite + Tailwind 构建独立前端
- 已支持资料元信息：
  - `subject`
  - `grade`
  - `topic`
- 已支持按资料范围过滤：
  - 指定文件
  - 学科
  - 年级
  - 专题
  - 排除 OCR
- 已支持 AI 标签建议：
  - 上传后自动生成建议标签
  - 对已有资料手动触发 `AI识别`
  - 人工确认后可采用建议

### 当前相关性判断逻辑

核心代码：

- [app/retriever.py](/Users/long/Downloads/workSpace/study-material-assistant/app/retriever.py)
- [app/vectorstores/qdrant_store.py](/Users/long/Downloads/workSpace/study-material-assistant/app/vectorstores/qdrant_store.py)

当前流程：

1. 用户问题做 embedding
2. Qdrant 向量召回候选 chunk
3. 按资料范围和 OCR 开关过滤
4. 用字符级 `keyword_score` 做简单重排
5. 返回 top-k 给生成模型

当前短板：

- 只有 dense 检索，没有 sparse/BM25 路径
- 字符级关键词命中过于粗糙
- 对数学题型、公式、题干/讲解结构没有单独建模
- OCR 结果缺少更细粒度的质量控制
- 缺少真正 reranker

---

## 总体改造原则

### 1. 先做结构化解析，再做检索升级

数学教育资料的关键不是先换模型，而是先把“题目、讲解、公式、易错点”正确抽出来。

### 2. 先做混合检索，再做复杂生成

如果召回错了，再强的生成模型也只会基于错误上下文回答。

### 3. 元信息过滤必须深入到题型层

对数学教育资料，`subject / grade / topic` 还不够，必须增加题型和教学角色。

### 4. AI 标注要默认可人工确认

不要让模型直接覆盖正式标签，避免后续检索范围被错误标签带偏。

---

## 推荐技术路线

## 阶段一：把检索从“dense only”升级到“hybrid + rerank”

优先级：最高

### 目标

显著减少“和倍问题”召回“差倍问题”这类错误。

### 后端改造点

#### 1. dense 模型升级

推荐路线二选一：

- 快速落地：`BAAI/bge-m3`
- 中文效果优先：`Qwen/Qwen3-Embedding-*`

推荐理由：

- `bge-m3` 同时支持 dense / sparse / multi-vector，适合直接做 hybrid
- `Qwen3-Embedding` 更适合中文产品化场景，后续与 `Qwen3-Reranker` 搭配更自然

建议：

- 第一阶段先上 `bge-m3`
- 如果后面追求更高中文效果，再切 `Qwen3-Embedding`

#### 2. 引入 sparse / BM25 路径

可选方案：

- 方案 A：Qdrant hybrid query
- 方案 B：Pyserini 维护一份 BM25 索引，再做结果融合

更推荐：

- 先直接走 Qdrant hybrid，工程复杂度更低

#### 3. 增加 reranker

推荐：

- `Qwen3-Reranker`
- 或 `BGE reranker`

召回流程建议改成：

1. dense + sparse 同时召回 top 30~50
2. 做融合
3. reranker 重排
4. 取 top 5~8 给生成

#### 4. 替换当前字符级 keyword_score

现有的字符级命中只适合作为临时策略，不适合作为数学教育场景的长期方案。

建议替换为：

- BM25 分数
- 标准分词后的关键词命中
- 元信息权重

### 代码改造建议

- [app/retriever.py](/Users/long/Downloads/workSpace/study-material-assistant/app/retriever.py)
  - 抽成三层：
    - `dense_retrieve`
    - `sparse_retrieve`
    - `rerank_candidates`
- [app/vectorstores/qdrant_store.py](/Users/long/Downloads/workSpace/study-material-assistant/app/vectorstores/qdrant_store.py)
  - 增加 hybrid 查询支持
- 新增：
  - `app/reranker.py`
  - `app/sparse_retriever.py`

### 预期收益

- 明显减少同类题型误召回
- 相关性不再过分依赖向量相似度
- 中文短问句与题型词的匹配会更稳

---

## 阶段二：重做数学资料解析与切块

优先级：最高

### 目标

让检索对象从“普通文本块”升级成“题目块 / 讲解块 / 方法块 / 易错点块”。

### 推荐开源技术

- `Docling`
- `Marker`
- 数学公式图片增强时可补：
  - `Pix2Text`

### 目标数据结构

每份资料解析后，建议统一成这样的结构：

```json
{
  "source": "文件名",
  "source_type": "pdf",
  "grade": "三年级",
  "subject": "数学",
  "topic": "和倍问题",
  "problem_type": "和倍问题",
  "pedagogical_role": "example",
  "content": "文本内容",
  "formula_latex": ["..."],
  "section_title": "例题1",
  "page": 3
}
```

### 切块策略

不要继续只按长度切。

建议改成：

- 题目块
- 题目 + 答案块
- 例题 + 讲解块
- 方法总结块
- 易错点块

双层 chunk 方案：

- 小块：高精度检索
- 大块：生成时补上下文

### 代码改造建议

- [app/loader.py](/Users/long/Downloads/workSpace/study-material-assistant/app/loader.py)
- [app/chunker.py](/Users/long/Downloads/workSpace/study-material-assistant/app/chunker.py)
- [app/ingestion/pdf_parser.py](/Users/long/Downloads/workSpace/study-material-assistant/app/ingestion/pdf_parser.py)
- [app/ingestion/ocr_parser.py](/Users/long/Downloads/workSpace/study-material-assistant/app/ingestion/ocr_parser.py)

新增建议：

- `app/structure_parser.py`
- `app/math_chunker.py`

### 预期收益

- 召回结果更像“题目”而不是“随便一段文字”
- 生成结果更容易基于正确教学片段回答
- 数学题型误召回概率下降

---

## 阶段三：把标签体系从 topic 扩展到数学题型层

优先级：高

### 当前已有

- `subject`
- `grade`
- `topic`

### 建议新增

- `problem_type`
  - 和倍问题
  - 差倍问题
  - 和差问题
  - 植树问题
  - 归一问题
  - 追及问题
- `pedagogical_role`
  - 例题
  - 练习题
  - 方法总结
  - 易错点
  - 讲解
- `difficulty`
  - 基础
  - 提升
  - 拔高
- `is_answer_material`
- `is_explanation_material`

### 为什么重要

对数学教育 RAG，题型和教学角色比普通主题词更关键。

例如：

- “给三年级学生讲和倍问题”
- “出几道同类型题”
- “只找易错点”

这些请求如果没有结构化标签，最终只能靠向量碰运气。

### 代码改造建议

- [app/material_tagger.py](/Users/long/Downloads/workSpace/study-material-assistant/app/material_tagger.py)
  - 扩展 AI 标签生成逻辑
- [app/material_metadata.py](/Users/long/Downloads/workSpace/study-material-assistant/app/material_metadata.py)
  - 增加新字段
- [frontend/src/components/MaterialsTable.tsx](/Users/long/Downloads/workSpace/study-material-assistant/frontend/src/components/MaterialsTable.tsx)
  - 展示和编辑新字段

### 前端改造建议

- 筛选器支持：
  - 按题型筛选
  - 按教学角色筛选
  - 按难度筛选

---

## 阶段四：增加数学场景的 query rewrite

优先级：中高

### 目标

把用户自然语言请求拆成“检索目标”和“生成目标”。

### 例子

用户问题：

“和倍问题应该怎么给三年级学生讲？”

拆解后：

- 检索 query：
  - `和倍问题 三年级 讲解 方法 易错点`
- 生成任务：
  - 产出适合老师课堂讲解的表达

### 推荐做法

增加一个轻量 query planner，输出：

```json
{
  "retrieval_query": "和倍问题 三年级 方法 易错点",
  "intent": "teaching",
  "grade": "三年级",
  "topic": "和倍问题",
  "pedagogical_role": ["讲解", "方法总结", "易错点"]
}
```

### 代码改造建议

新增：

- `app/query_planner.py`

在：

- [app/api.py](/Users/long/Downloads/workSpace/study-material-assistant/app/api.py)
- [app/pipeline.py](/Users/long/Downloads/workSpace/study-material-assistant/app/pipeline.py)

中接入 query rewrite。

### 预期收益

- 提高复杂教学问题的检索精度
- 让“问答 / 讲解 / 出题”三条链路走向不同的检索策略

---

## 阶段五：建立评测体系

优先级：高

### 目标

不要靠主观感觉调相关性，要有评测集。

### 建议评测维度

- Top-3 是否召回正确资料
- 是否召回正确题型
- 是否混入错误年级内容
- 是否引用了 OCR 错误内容
- 讲解是否基于正确资料

### 数据集建议

至少整理 50~100 条真实样本：

- 用户问题
- 标准答案
- 正确来源文件
- 正确题型
- 年级
- 是否允许 OCR

### 工具建议

- `Ragas`

### 输出指标建议

- Recall@3
- Recall@5
- Top-1 题型命中率
- 元信息过滤正确率
- Answer groundedness

---

## 推荐实施顺序

### 第一阶段，1~2 周

- 替换字符级 `keyword_score`
- 引入 hybrid retrieval
- 增加 reranker
- 保持现有 chunk 逻辑不动

### 第二阶段，1~2 周

- 引入结构化解析
- 重做数学语义切块
- 为题型和教学角色建标签

### 第三阶段，1 周

- 增加 query rewrite
- 打通题型级过滤
- 做评测集与离线评测

### 第四阶段，持续迭代

- 优化 OCR 数学公式识别
- 调整 reranker
- 做面向题库的定制化微调或蒸馏

---

## 针对当前仓库的最小可执行改造包

如果只做当前最值得的一轮，我建议优先完成下面 5 项：

1. 用 `bge-m3` 或 `Qwen3-Embedding` 替换当前 embedding
2. 在 Qdrant 中实现 dense + sparse hybrid
3. 增加 reranker 层
4. 新增 `problem_type` 和 `pedagogical_role`
5. 把当前 chunk 改为“题目/讲解/易错点”语义切块

这是当前从“能用”走向“数学教育专业化”的关键一步。

---

## 开源技术清单

- BGE-M3
  - [https://huggingface.co/BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3)
- Qwen3 Embedding
  - [https://huggingface.co/papers/2506.05176](https://huggingface.co/papers/2506.05176)
- Qdrant Hybrid Search
  - [https://qdrant.tech/documentation/advanced-tutorials/reranking-hybrid-search/](https://qdrant.tech/documentation/advanced-tutorials/reranking-hybrid-search/)
- Pyserini
  - [https://github.com/castorini/pyserini](https://github.com/castorini/pyserini)
- ColBERTv2
  - [https://huggingface.co/papers/2112.01488](https://huggingface.co/papers/2112.01488)
- Docling
  - [https://github.com/docling-project/docling](https://github.com/docling-project/docling)
- Marker
  - [https://github.com/datalab-to/marker](https://github.com/datalab-to/marker)
- Pix2Text
  - [https://github.com/breezedeus/Pix2Text](https://github.com/breezedeus/Pix2Text)
- Ragas
  - [https://docs.ragas.io/](https://docs.ragas.io/)

