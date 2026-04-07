# Study Material Assistant

一个面向家教老师 / 备课场景的学习资料智能助手。

项目目标是：把本地的 `txt` / `pdf` / 图片 OCR 学习资料转成一个可以进行**问答、讲解、出题**的智能辅助系统，帮助老师更快查资料、整理教学思路、生成练习题。

## 当前能力

- 上传学习资料
- 重建资料索引
- 资料问答
- 教学讲解
- 练习题生成
- 支持 `txt` / `pdf` / `image(OCR)` 资料接入
- 返回检索来源、来源类型、OCR 标记等信息

## 项目结构

```text
study-material-assistant/
├── app/                        # 后端 FastAPI 与业务逻辑
├── data/                       # 原始资料与预留处理数据
├── frontend/                   # React + TypeScript + Vite 前端
├── notes/                      # 项目笔记与前端记忆文件
├── qdrant_storage/             # 本地向量库数据
├── .env                        # 后端环境变量
├── README.md
└── requirements.txt
```

## 技术栈

### 后端

- FastAPI
- sentence-transformers
- Qdrant / Chroma
- MiniMax（OpenAI 兼容接口）

### 前端

- React
- TypeScript
- Vite
- Tailwind CSS

## 后端环境变量

在项目根目录创建 `.env`：

```bash
OPENAI_API_KEY=你的MiniMax_API_Key
OPENAI_BASE_URL=https://api.minimaxi.com/v1
OPENAI_MODEL=MiniMax-M2.5-highspeed
```

## 安装依赖

### 后端依赖

```bash
pip install -r requirements.txt
```

### 前端依赖

```bash
cd frontend
npm install
```

## 启动方式

### 1. 启动后端 API

```bash
uvicorn app.api:app --host 127.0.0.1 --port 8000
```

后端启动后可通过 [http://127.0.0.1:8000/](http://127.0.0.1:8000/) 检查健康状态。

### 2. 配置前端环境变量

在 `frontend/.env` 中配置：

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 3. 启动前端

```bash
cd frontend
npm run dev
```

前端默认运行在 [http://127.0.0.1:5173/](http://127.0.0.1:5173/)。

## 前后端联调顺序

推荐按这个顺序使用：

1. 启动后端 API
2. 启动前端
3. 在“资料管理”中上传文件
4. 保持“上传后自动重建索引”开启，或手动点击“重建索引”
5. 再使用“资料问答”“教学讲解”“练习题生成”

说明：
- 当前后端 `POST /materials/upload` 只负责保存文件
- 真正的建索引逻辑在 `POST /materials/index`
- 前端已经默认支持“上传成功后自动重建索引”

## Web 前端说明

`frontend/` 已实现一个可运行的单页应用，包含：

- 资料管理
- 资料问答
- 教学讲解
- 练习题生成

前端特性包括：

- Markdown 结果渲染
- 检索片段筛选
- 上传后自动重建索引
- 移动端抽屉导航
- 一键复制回答 / 题目

更多前端细节可查看仓库中的 `frontend/README.md`。

## 示例问题

### 资料问答

- 和倍问题的基本思路是什么？
- 平行线专题的常见易错点是什么？

### 教学讲解

- 和倍问题应该怎么给三年级学生讲？
- 平行线专题应该怎么循序渐进地讲？

### 练习题生成

- 给我出几个和倍问题的题目
- 出一道适合三年级学生的和倍练习题
- 给我一道平行线基础判断题

## 当前已知问题

- 检索结果仍可能混入少量无关片段
- OCR 图片资料可能带来识别误差
- 练习题生成结果仍有继续提高专题纯度的空间

## 下一步建议

- 优化检索相关性，减少无关 chunk
- 增加资料标签（年级 / 专题 / 难度）
- 支持更强的 PDF 与 OCR 解析能力
- 增加更细粒度的来源过滤与结果导出能力
