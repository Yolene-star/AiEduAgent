# AiEduAgent

多模态 K12 人工智能通识课教学助手。当前版本先实现可运行 MVP 闭环：

1. 学生选择学段。
2. 进入“人工智能如何学会分类”课程。
3. 发起教学对话。
4. 获得适龄回答与来源。
5. 生成并提交练习。
6. 更新掌握度。
7. 获得下一步推荐。
8. 对关键文本执行 Mock TTS 回环测试。

## 技术栈

- Frontend: Next.js + React + TypeScript
- Backend: FastAPI + Python 3.10
- Persistence: SQLite during local development
- AI/RAG: Dify API adapter with local fallback
- Tests: backend unittest/pytest-compatible layout, frontend Vitest, behavior tests with Playwright
- TTS: Mock loopback first, real provider later

## 后端启动

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

如果当前环境已安装 FastAPI，也可以直接运行：

```bash
cd backend
python3 -m unittest discover -s tests
```

后端会在 `backend/aieduagent.db` 创建本地 SQLite 数据库。该文件是运行产物，不会进入 Git。

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

默认读取 `NEXT_PUBLIC_API_BASE_URL`，未设置时使用 `http://localhost:8000`。

## 测试

后端：

```bash
cd backend
python3 -m unittest discover -s tests
```

前端：

```bash
cd frontend
npm test
```

行为测试：

```bash
cd frontend
npm run test:e2e
```

## Dify 配置

后端通过 `/api/chat` 统一代理 Dify，前端不接触密钥。在 `.env` 中配置：

```bash
DIFY_BASE_URL=https://api.dify.ai/v1
DIFY_API_KEY=你的 Dify 应用 API Key
```

未配置 API Key、网络失败、代理缺依赖或 Dify 返回空答案时，系统会自动降级为本地适龄教学回答，保证演示链路不中断。

## Judge0 配置

在线编程通过 `/api/code/run` 统一代理。开发期未配置 Judge0 时使用安全 fallback，不会在本机直接执行学生代码。

```bash
JUDGE0_BASE_URL=https://your-judge0-host
JUDGE0_API_KEY=可选
```

## Git 使用说明

当前运行环境会把 `.git` 特殊挂载为只读目录，因此本项目使用分离 Git 目录 `.repo/`。初始化命令：

```bash
git --git-dir=/home/yjm/AiEduAgent/.repo --work-tree=/home/yjm/AiEduAgent init
```

查看状态：

```bash
git --git-dir=/home/yjm/AiEduAgent/.repo --work-tree=/home/yjm/AiEduAgent status --short
```

提交：

```bash
git --git-dir=/home/yjm/AiEduAgent/.repo --work-tree=/home/yjm/AiEduAgent add .
git --git-dir=/home/yjm/AiEduAgent/.repo --work-tree=/home/yjm/AiEduAgent commit -m "feat: bootstrap ai education assistant mvp"
```

## 开源参考

详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
