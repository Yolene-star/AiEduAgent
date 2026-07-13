# AiEduAgent

多模态 K12 人工智能通识课教学助手项目工作区。

当前仓库已清空到“阶段 0：项目控制面与安全基线”。这里暂不保留前端、后端、数据库、Docker、测试或模型接入代码，后续将严格按照 `K12_AI_Tutor_Staged_Practice_Harness.md` 分阶段重建。

## 当前保留内容

- `K12_AI_Tutor_Staged_Practice_Harness.md`：分阶段实践步骤与 Harness 手册。
- `多模态K12人工智能教学助手项目开发与开源成果借鉴计划书.docx`：项目规划与开源成果借鉴材料。
- `.gitignore`：密钥、依赖、缓存、数据库和构建产物忽略规则。
- `.env.example`：环境变量占位模板，不包含真实密钥。
- `docs/decisions.md`：阶段 0 技术选型和安全边界记录。
- `artifacts/stage-00/versions.txt`：阶段 0 工具版本证据。

## 阶段顺序

1. 阶段 0：项目控制面与安全基线。
2. 阶段 1：FastAPI `/health` 最小后端。
3. 阶段 2：前后端最小垂直切片。
4. 阶段 3：模型适配层，先 Fake 模型，再真实 API。
5. 阶段 4：U1 五张知识卡、检索与来源追踪。
6. 阶段 5 以后：四学段适配、练习、多模态模板、掌握度、部署演示。

每次只进入一个阶段。上一个阶段的退出闸门全部通过后，再开始下一个阶段。

## 阶段 0 当前状态

- 已保存工具版本到 `artifacts/stage-00/versions.txt`。
- 已确认当前仓库没有真实 `.env`。
- 已创建 `docs/decisions.md`。
- 已保留分离 Git 目录 `.repo/`。
- 已创建 Python 3.12 conda 环境：`aieduagent-py312`。
- 待你在 GitHub 网页确认远程仓库为 Private。

阶段 0 完成后，再进入阶段 1：FastAPI `/health` 最小后端。

## Python 环境

手册要求使用 Python 3.12。本机系统 `python3` 是 3.10.19，因此项目使用专用 conda 环境：

```bash
conda activate aieduagent-py312
python --version
```

预期输出：

```text
Python 3.12.13
```

## 阶段 1 后端启动

阶段 1 只实现最小 FastAPI 后端：

- 健康检查：`GET /health`
- 接口文档：`GET /docs`
- 测试文件：`backend/tests/test_health.py`
- 固定启动脚本：`scripts/dev-backend.ps1`
- 验收证据：`artifacts/stage-01/results.txt`

在仓库根目录运行：

```bash
conda activate aieduagent-py312
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

或使用 PowerShell 脚本：

```powershell
.\scripts\dev-backend.ps1
```

运行测试：

```bash
conda run -n aieduagent-py312 python -m pytest backend/tests/test_health.py -q
```

说明：当前环境中 Starlette `TestClient` 会在后台 portal 初始化时卡住，因此阶段 1 测试使用 `httpx.ASGITransport` 直接调用真实 ASGI app。它仍然会经过 FastAPI 路由和中间件，不是测试假函数。

## 阶段 2 前后端垂直切片

阶段 2 增加最小聊天链路：

- 后端接口：`POST /api/v1/chat`
- 固定输入：`{"stage":"lower_primary","message":"AI怎么认识小猫？"}`
- 固定假回答：由 `FakeModelProvider` 返回
- 前端页面：学段选择、问题输入、发送、回答、来源占位、错误提示
- 验收证据：`artifacts/stage-02/results.txt`

后端启动：

```bash
conda activate aieduagent-py312
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

前端启动：

```bash
cd frontend
corepack pnpm install
corepack pnpm dev
```

前端检查：

```bash
cd frontend
corepack pnpm test
corepack pnpm build
```

后端检查：

```bash
conda run -n aieduagent-py312 python -m pytest backend/tests -q
```

说明：本机 `npm install` 在解析依赖树时多次超时，阶段 2 改用 Corepack 管理的 pnpm，并提交 `pnpm-lock.yaml`。

## Git 使用

当前运行环境使用分离 Git 目录 `.repo/`。常用命令如下：

```bash
git --git-dir=.repo --work-tree=. status --short --branch
git --git-dir=.repo --work-tree=. add .
git --git-dir=.repo --work-tree=. diff --cached
git --git-dir=.repo --work-tree=. commit -m "chore: complete stage 0 safety baseline"
```

提交前必须检查暂存内容，确认没有 `.env`、密钥、数据库、依赖目录或构建产物。
