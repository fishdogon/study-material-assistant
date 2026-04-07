# Frontend

学习资料智能助手的 Web 前端，基于 React + TypeScript + Vite + Tailwind CSS。

## 安装依赖

```bash
cd frontend
npm install
```

## 配置后端地址

在 `frontend/` 目录下创建 `.env` 文件：

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

如果后端运行在其他地址或端口，请替换为实际值。

## 启动开发环境

```bash
cd frontend
npm run dev
```

默认开发地址为 `http://127.0.0.1:5173`。

## 构建生产版本

```bash
cd frontend
npm run build
```

构建产物会输出到 `frontend/dist/`。
