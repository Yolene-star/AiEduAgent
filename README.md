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

## 阶段 3 模型适配层

阶段 3 将模型调用封装到 `backend/app/providers/`：

- `ModelProvider`：统一 `generate(request) -> response` 接口。
- `FakeModelProvider`：默认离线演示和测试 provider，不需要密钥。
- `RealModelProvider`：读取环境变量并调用 OpenAI-compatible `/chat/completions` 接口。
- `FakeModelProvider` 失败注入：`fake_timeout`、`fake_rate_limit`、`fake_invalid_json`。
- 验收证据：`artifacts/stage-03/results.txt`

默认不配置密钥即可运行：

```bash
MODEL_PROVIDER=fake python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

真实模型只通过环境变量切换，前端不用改：

```bash
MODEL_PROVIDER=real
LLM_MODEL=deepseek-v4-flash
LLM_API_KEY=replace_me
LLM_BASE_URL=https://api.deepseek.com
LLM_TIMEOUT_SECONDS=20
```

注意：真实密钥只能写入本地 `.env` 或终端环境变量，不能提交到 Git。

阶段 3 后端测试：

```bash
conda run -n aieduagent-py312 python -m pytest backend/tests -q
```

DeepSeek 兼容性检查，不会打印密钥：

```bash
MODEL_PROVIDER=real \
LLM_MODEL=deepseek-v4-flash \
LLM_API_KEY=你的DeepSeek密钥 \
LLM_BASE_URL=https://api.deepseek.com \
LLM_TIMEOUT_SECONDS=20 \
conda run -n aieduagent-py312 python scripts/check_model_provider.py
```

## 阶段 4 U1 知识卡与可追溯回答

阶段 4 增加 U1“机器怎样看见世界”的五张知识卡：

- `U1-C01`：像素
- `U1-C02`：标签
- `U1-C03`：训练数据
- `U1-C04`：图像分类
- `U1-C05`：训练集、验证集和测试集

内容文件：

- `content/cards/u1/*.yaml`
- `content/aliases.yml`
- `evals/stage4_golden_cases.json`

后端启动时会校验知识卡 Schema、别名表和 golden cases。`/api/v1/chat` 会先用确定性规则检索卡片，再把合法 `card_id` 映射为来源标题和链接。模型或 FakeProvider 只能返回 `used_card_ids`，不能生成最终来源 URL。

阶段 4 检查：

```bash
conda run -n aieduagent-py312 python -m pytest backend/tests -q
cd frontend
corepack pnpm test
corepack pnpm build
```

课程外问题会返回边界提示，不会伪造知识卡或来源。

## 阶段 5 四学段适配与状态机

阶段 5 增加配置化学段规则和显式教学状态机：

- `backend/app/stage_policy.py`：四学段 `StagePolicy`、格式校验、四学段基准输出。
- `backend/app/lesson_state.py`：`LessonState`、`LessonEvent` 和允许迁移表。
- `evals/stage5_virtual_students.json`：低龄动物兴趣、高中编程兴趣两个虚拟学生。
- `artifacts/stage-05/four-stage-snapshot.md`：同一问题四学段并排输出。
- `artifacts/stage-05/results.txt`：阶段 5 验收结果。

程序负责状态迁移，模型只生成当前状态需要的结构化内容。非法状态迁移会返回 `409`，例如不能从 `WELCOME` 直接跳到 `RECOMMEND`。

## 阶段 6 游戏化练习与学习事件

阶段 6 增加“讲解—作答—反馈—记录”的最小闭环：

- 固定题库：`content/quizzes/u1_stage6.json`
- 题目数量：5 个 U1 概念 × 4 个学段 = 20 道
- 题型：选择、判断、排序
- 列表接口：`GET /api/v1/quizzes?stage=lower_primary`
- 提交接口：`POST /api/v1/quiz/{quiz_id}/submit`
- 学习事件：`data/demo/learning_events.jsonl`
- 重置脚本：`scripts/reset_demo.ps1`

学习事件包含正确性、提示次数、耗时、错因、回看卡片和幂等键。`data/demo/` 是本地演示进度，不提交到 Git；固定题库属于教学内容，会提交。

阶段 6 后端检查：

```bash
conda run -n aieduagent-py312 python -m pytest backend/tests -q
```

阶段 6 前端检查：

```bash
cd frontend
corepack pnpm test
corepack pnpm build
```

Windows PowerShell 重置演示数据：

```powershell
.\scripts\reset_demo.ps1
```

## 课程资源添加接口

当前已预留教师/内容侧资源添加接口，但新资源只进入本地草稿区，不会直接进入学生问答知识库。后续需要经过来源、许可证、年龄适配和内容安全审核后，才能转成 `content/cards/`、`content/quizzes/` 或阶段 7 多模态资源。

- 添加资源：`POST /api/v1/resources`
- 查看草稿：`GET /api/v1/resources`
- 本地草稿文件：`data/demo/course_resources.jsonl`
- 前端预留方法：`addResource()`、`fetchResources()`

示例请求：

```json
{
  "title": "图像分类补充阅读",
  "resource_type": "link",
  "stage": "middle_school",
  "unit": "U1",
  "topic": "图像分类",
  "source_url": "https://example.edu/image-classification",
  "license": "teacher-reviewed-demo",
  "description": "后续可审核进入课程库的补充链接。",
  "card_ids": ["U1-C04"],
  "created_by": "demo-teacher"
}
```

注意：`data/demo/` 是本地运行进度和草稿缓存，不提交到 Git；已经审核过的正式教学内容才提交到 `content/`。

## 阶段 7 动画、绘本与语音模板

阶段 7 增加模板化多模态能力，不依赖现场实时生成视频：

- 动画规格：`content/multimodal/animation_u1_image_classification.json`
- 绘本规格：`content/multimodal/storybook_u1_lower_primary.json`
- 资源许可证台账：`content/multimodal/asset_licenses.md`
- 绘本图片：`frontend/public/assets/storybook/*.svg`
- 动画组件：`frontend/src/components/AnimationPanel.vue`
- 绘本组件：`frontend/src/components/StorybookPanel.vue`
- 语音组件：`frontend/src/components/SpeechControls.vue`

后端接口：

```text
GET /api/v1/multimodal/animation/u1-image-classification
GET /api/v1/multimodal/storybook/u1-lower-primary
```

安全边界：

- 前端只解析白名单字段和固定 `visual` 名称，不执行模型生成脚本。
- 绘本使用本地已审查 SVG 图片，并在 JSON 中提供替代文本。
- 语音使用浏览器 `speechSynthesis`，会等待 `voiceschanged` 并优先选择中文 voice；不录音、不保存真实学生声音。
- 图片或语音失败时，文本和字幕仍然可用。
- 动画使用固定 16:9 HTML 舞台和百分比坐标，窗口尺寸变化时元素保持相对位置。

调研参考：

- MDN Web Speech 示例：采用 `getVoices()`、`voiceschanged`、语速和音调控制的浏览器 TTS 模式。
- sherpa-onnx：可作为后续离线 TTS/WASM 方案，但模型和运行时更重，当前阶段不直接集成。
- Motion / Remotion / HyperFrames 思路：采用数据驱动时间轴和固定画布组合；本项目只实现网页动态效果，不做视频导出。

### 离线中文语音 sherpa-onnx

当前已预留 sherpa-onnx WebAssembly TTS 适配层：

- 适配层：`frontend/src/speech/sherpaOfflineTts.ts`
- 运行时目录：`frontend/public/vendor/sherpa-onnx-tts/`
- 资产检查：`python scripts/check_sherpa_tts_assets.py`

需要把 sherpa-onnx `wasm/tts` 构建产物复制到运行时目录，至少包括：

```text
sherpa-onnx-tts.worker.js
sherpa-onnx-tts.js
sherpa-onnx-wasm-main-tts.js
sherpa-onnx-wasm-main-tts.wasm
```

以及对应 TTS 模型/data 资产。官方文档说明 sherpa-onnx TTS 支持 WebAssembly，并提供中文预训练模型，例如 `matcha-icefall-zh-baker`、`vits-melo-tts-zh_en`、`aishell3` 等。大模型和 wasm 文件默认被 `.gitignore` 忽略，避免仓库体积失控；演示机本地放置即可。

页面语音模式：

- `自动`：优先探测 sherpa-onnx 离线 TTS，失败后回退浏览器语音。
- `离线中文`：只使用 sherpa-onnx，缺资产时显示错误。
- `浏览器语音`：只使用系统/浏览器 `speechSynthesis`。

阶段 7 检查：

```bash
conda run -n aieduagent-py312 python -m pytest backend/tests -q
cd frontend
corepack pnpm test
corepack pnpm build
python ../scripts/check_sherpa_tts_assets.py
```

## Git 使用

当前运行环境使用分离 Git 目录 `.repo/`。常用命令如下：

```bash
git --git-dir=.repo --work-tree=. status --short --branch
git --git-dir=.repo --work-tree=. add .
git --git-dir=.repo --work-tree=. diff --cached
git --git-dir=.repo --work-tree=. commit -m "chore: complete stage 0 safety baseline"
```

提交前必须检查暂存内容，确认没有 `.env`、密钥、数据库、依赖目录或构建产物。
