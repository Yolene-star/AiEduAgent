# K12 AI 教学助手：分阶段实践步骤与工程 Harness 手册

**适用项目：** JBGS-2026-02 多模态 K12 人工智能通识课教学助手对话智能体  
**适用团队：** 4 人；2026-07-13 至 2026-08-12 主要由 1 人开发  
**使用方式：** 每次只进入一个阶段；上一个阶段的“退出闸门”全部通过后，才能进入下一阶段  
**默认环境：** Windows 11 + PowerShell + VS Code；后端 Python/FastAPI，前端 Vue 3/TypeScript  
**版本日期：** 2026-07-13

> 本手册中的日期是内部倒排计划，不是官方截止日期。官方赛程公布后，应保留阶段顺序，只调整每阶段工期。

---

## 0. 先理解什么是“实践 Harness”

这里的 Harness 不是某一个框架，而是让一次实践可以被**重复运行、观察、验收和回归**的整套工作台。

如果只写了一个接口，打开浏览器看起来能用，这叫“做出了功能”；如果同一个功能还具备固定输入、预期输出、假模型、测试命令、日志、重置脚本和证据文件，才叫“进入 Harness”。

本项目的标准 Harness 包含八部分：

| 部分 | 作用 | 首版实现 |
|---|---|---|
| 固定入口 | 所有人用同样方式启动 | `scripts/dev.ps1` |
| 固定数据 | 每次测试使用相同账号和知识卡 | `scripts/seed_demo.py`、`fixtures/` |
| 可替换依赖 | 不依赖真实模型也能测试 | `FakeModelProvider` |
| 自动检查 | 一条命令检查格式、测试和构建 | `scripts/check.ps1` |
| 可观测性 | 知道请求走到哪里、为何失败 | 结构化日志、`request_id`、耗时 |
| 可重置性 | 数据损坏后能恢复演示状态 | `scripts/reset_demo.ps1` |
| 退出闸门 | 不靠“感觉差不多”判断完成 | 每阶段验收清单 |
| 证据归档 | 为报告、答辩和排错留证据 | `artifacts/stage-XX/` |

### 0.1 最终 Harness 目录

```text
k12-ai-tutor/
├─ frontend/
├─ backend/
│  ├─ app/
│  └─ tests/
│     ├─ unit/
│     ├─ integration/
│     └─ fixtures/
├─ content/
│  ├─ cards/u1/
│  ├─ quizzes/
│  └─ sources.yml
├─ evals/
│  ├─ golden_cases.json
│  ├─ stage_cases.json
│  └─ safety_cases.json
├─ scripts/
│  ├─ dev.ps1
│  ├─ check.ps1
│  ├─ reset_demo.ps1
│  └─ seed_demo.py
├─ artifacts/
│  ├─ stage-00/
│  ├─ stage-01/
│  └─ ...
├─ docs/
├─ .env.example
├─ .gitignore
├─ docker-compose.yml
└─ README.md
```

### 0.2 每阶段都要执行的固定循环

```text
读本阶段目的
  → 建立或补充 Harness
  → 只实现最小功能
  → 执行自动检查
  → 人工走一遍主路径
  → 保存截图/日志/测试结果
  → 对照退出闸门
  → Git 提交并打阶段标签
```

### 0.3 你和 Codex 的固定分工

**你负责：** 决定阶段目标；执行命令；亲自体验；保存完整报错；判断教学内容是否符合项目意图；确认是否通过退出闸门；管理密钥和最终提交。

**Codex 负责：** 阅读限定文件；按任务卡修改代码；补测试；运行检查；解释变更；指出风险；维护 README 和 Harness 脚本。

**每次给 Codex 的任务不应跨越阶段。** 例如阶段 1 时，禁止顺手加入向量数据库、动画或登录系统。

---

# 阶段 0：项目控制面与安全基线

**建议时间：** 2026-07-13，半天至 1 天  
**参与者：** 你  
**实现目的：** 建立不会轻易丢代码、泄露密钥或被 AI 大范围误改的安全工作区。

## 0.1 本阶段要理解的工程常识

1. 文件夹不是 Git 仓库；只有初始化并提交后，才有可回退历史。
2. GitHub 私有仓库是远程备份，不等于本地代码自动上传。
3. `.env` 保存真实密钥，`.env.example` 只保存变量名和假值。
4. 一次提交应对应一个明确目标，提交前必须看 `git diff`。
5. Codex 修改的是文件；你必须通过测试和运行结果判断修改是否正确。

## 0.2 实践 Harness

本阶段建立“仓库安全 Harness”：

- `.gitignore`：排除 `.env`、`.venv/`、`node_modules/`、数据库、日志、构建产物。
- `.env.example`：只写 `LLM_API_KEY=replace_me` 等占位值。
- `README.md`：记录当前阶段、启动前提和空白的验收章节。
- `docs/decisions.md`：记录为什么选择 Vue、FastAPI、SQLite 和 YAML。
- `artifacts/stage-00/versions.txt`：保存工具版本。

## 0.3 具体实践步骤

1. 安装 Git、Python 3.12、Node.js LTS、VS Code。
2. 在 PowerShell 中确认：

```powershell
git --version
py --version
node --version
npm --version
```

3. 新建私有 GitHub 仓库，克隆到本地。
4. 创建顶层目录和安全文件。
5. 运行：

```powershell
git status
git diff
git add .
git diff --cached
git commit -m "chore: initialize safe project workspace"
```

6. 在 GitHub 网页确认仓库中不存在 `.env`、密钥、数据库和日志。
7. 在一个临时空目录重新克隆，确认 README 可以看到。

## 0.4 退出闸门

- [ ] 四个版本命令都有输出，并保存到 `artifacts/stage-00/versions.txt`。
- [ ] GitHub 仓库为 Private。
- [ ] `.env` 不在 `git status` 和 GitHub 中。
- [ ] 本地至少有一个可识别的提交。
- [ ] 重新克隆成功。
- [ ] 你能用自己的话解释工作区、暂存区、本地提交和远程仓库的区别。

## 0.5 给 Codex 的任务卡

```text
当前处于阶段 0，只建立项目安全基线。
请检查仓库现状，创建合理的 .gitignore、.env.example、README.md 和 docs/decisions.md。
禁止安装依赖、实现业务功能、写入任何真实密钥。
完成后请列出新增文件、每个文件用途，并给出我需要手动执行的 Git 检查命令。
```

## 0.6 参考资料

- [Git 官方入门](https://git-scm.com/book/zh/v2/起步-Git-基础)
- [GitHub：忽略文件](https://docs.github.com/en/get-started/getting-started-with-git/ignoring-files)
- [Python 虚拟环境](https://docs.python.org/3/library/venv.html)

---

# 阶段 1：后端最小可运行 Harness

**建议时间：** 2026-07-14  
**参与者：** 你  
**实现目的：** 建立能启动、能访问、能测试、能看懂错误的 FastAPI 后端。

## 1.1 学习目标

只掌握五个概念：进程、端口、HTTP 方法、JSON、状态码。暂时不学习微服务、异步任务、鉴权和数据库优化。

## 1.2 实践 Harness

- 固定启动入口：`scripts/dev-backend.ps1`。
- 固定健康检查：`GET /health`。
- 固定测试：`backend/tests/test_health.py`。
- 固定日志字段：时间、级别、路径、状态码、耗时、`request_id`。
- 固定失败演练：占用 8000 端口、访问不存在路径、传入错误 JSON。

## 1.3 具体实践步骤

1. 创建虚拟环境：

```powershell
py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install "fastapi[standard]" pytest httpx
```

2. 创建 `backend/app/main.py`，只实现 `/health`。
3. 创建 `backend/tests/test_health.py`，断言状态码为 200，JSON 为 `{"status":"ok"}`。
4. 启动开发服务器：

```powershell
fastapi dev backend/app/main.py
```

5. 访问 `http://127.0.0.1:8000/health` 和 `/docs`。
6. 运行测试：

```powershell
pytest backend/tests/test_health.py -q
```

7. 故意把返回值改错，确认测试会失败；再恢复正确实现。

## 1.4 退出闸门

- [ ] `/health` 返回 200 和规定 JSON。
- [ ] `/docs` 能看到接口。
- [ ] 关闭服务器后访问会失败，你能解释原因。
- [ ] 测试在正确代码上通过，在故意错误代码上失败。
- [ ] 从新终端启动不依赖 VS Code 的“神秘状态”。
- [ ] 将启动命令写入 README。

## 1.5 常见失败

| 现象 | 优先检查 |
|---|---|
| `python` 找不到 | 是否使用 `py`；Python 是否加入 PATH |
| 无法运行激活脚本 | 当前进程是否执行 `Set-ExecutionPolicy` |
| 8000 端口占用 | 是否已有 FastAPI 进程；换端口验证 |
| 导入模块失败 | 当前目录、包路径、`__init__.py` |
| 测试“通过但接口打不开” | 测试是否只测了假函数而非 TestClient |

## 1.6 给 Codex 的任务卡

```text
当前处于阶段 1。请实现 FastAPI /health 接口、对应 pytest 测试和 PowerShell 启动脚本。
只允许修改 backend/、scripts/dev-backend.ps1 和 README.md。
验收：pytest 通过；响应严格为 {"status":"ok"}；启动脚本在仓库根目录可运行。
禁止数据库、模型 API、登录、多模态功能。
```

## 1.7 参考资料

- [FastAPI 官方逐步教程](https://fastapi.tiangolo.com/tutorial/)
- [FastAPI 测试](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest Get Started](https://docs.pytest.org/en/stable/getting-started.html)

---

# 阶段 2：前后端最小垂直切片

**建议时间：** 2026-07-15 至 2026-07-16  
**参与者：** 你  
**实现目的：** 完成“浏览器输入问题—后端接收—返回假答案—页面显示”的第一条完整链路。

## 2.1 为什么先用假答案

如果一开始就接模型 API，页面错误、网络错误、密钥错误和模型错误会混在一起。先用 `FakeModelProvider`，可以证明前后端链路本身正确。

## 2.2 实践 Harness

- 固定请求：`POST /api/v1/chat`。
- 固定输入：`{"stage":"lower_primary","message":"AI怎么认识小猫？"}`。
- 固定假输出：答案、检查题、卡片 ID、下一步动作。
- 前端三态：加载、成功、失败。
- 网络观察：浏览器 DevTools 的 Network 面板。
- 契约文件：Pydantic 请求/响应模型与 TypeScript 类型保持一致。

## 2.3 具体实践步骤

1. 创建 Vue 项目：

```powershell
npm create vue@latest
```

建议选择 TypeScript、Vue Router、Vitest、ESLint、Prettier；暂时不选 Pinia 和端到端测试框架。

2. 安装并启动：

```powershell
cd frontend
npm install
npm run dev
```

3. 创建四个组件：`StageSelector`、`ChatInput`、`AnswerCard`、`SourceList`。
4. 后端创建 `ChatRequest`、`ChatResponse`。
5. 实现 `FakeModelProvider`，永远返回固定结构。
6. 配置 CORS，仅允许本地前端地址。
7. 前端调用 `/api/v1/chat`，显示加载、成功、失败。
8. 断开后端，确认前端显示人类可理解的错误，而不是空白页面。

## 2.4 契约 Harness

建议固定响应：

```json
{
  "answer": "它会从许多带有名字的小猫图片中学习共同特点。",
  "check_question": "图片旁边写着‘小猫’，这个名字在训练中叫什么？",
  "used_card_ids": ["U1-C02", "U1-C04"],
  "next_actions": ["answer_check", "open_storybook"]
}
```

后端测试不仅检查 200，还要检查四个字段存在、类型正确、卡片 ID 为数组。

## 2.5 退出闸门

- [ ] 四个学段可以选择并随请求发送。
- [ ] 固定问题能得到固定假回答。
- [ ] 请求体错误时后端返回 422，前端有提示。
- [ ] 后端关闭时，前端不会一直转圈。
- [ ] 浏览器中看不到任何 API 密钥。
- [ ] `npm run build` 和后端测试均通过。

## 2.6 给 Codex 的任务卡

```text
当前处于阶段 2。请建立 Vue 到 FastAPI 的最小垂直切片。
必须使用 FakeModelProvider；不要接真实模型。
页面只需要学段选择、问题输入、提交、回答、来源占位和错误提示。
请同步定义 Pydantic 与 TypeScript 类型，并补后端契约测试和前端核心组件测试。
完成后给出启动两个终端的准确命令和人工验收路径。
```

## 2.7 参考资料

- [Vue 官方 Quick Start](https://vuejs.org/guide/quick-start.html)
- [Vue TypeScript 指南](https://vuejs.org/guide/typescript/overview.html)
- [MDN：使用 Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)
- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)

---

# 阶段 3：模型适配层与可控调用

**建议时间：** 2026-07-17 至 2026-07-19  
**参与者：** 你  
**实现目的：** 接入一个真实大模型 API，但保证测试、业务代码和页面不绑定某个模型供应商。

## 3.1 实践 Harness

- `ModelProvider` 接口：统一 `generate(request) -> response`。
- `FakeModelProvider`：测试和离线演示。
- `RealModelProvider`：读取环境变量后调用真实 API。
- 结构化输出：模型必须返回规定字段。
- 失败注入：假超时、假限流、假无效 JSON。
- 调用日志：供应商、模型别名、耗时、结果状态、请求 ID；不记录密钥。

## 3.2 具体实践步骤

1. 在 `.env.example` 加入：

```text
MODEL_PROVIDER=fake
LLM_MODEL=replace_me
LLM_API_KEY=replace_me
LLM_TIMEOUT_SECONDS=20
```

2. 定义模型无关的 `TutorGenerationRequest` 和 `TutorGenerationResponse`。
3. 把原先聊天接口中的假答案移到 `FakeModelProvider`。
4. 实现真实提供者；API 调用只能出现在 `backend/app/providers/`。
5. 设置超时；只对可重试错误重试一次。
6. 结构验证失败时，不把原始乱码直接返回前端。
7. 实现降级：真实模型失败 → 固定知识卡摘要或友好提示。
8. 用环境变量切换 fake/real，前端完全不改。

## 3.3 测试矩阵

| 场景 | 预期 |
|---|---|
| Fake 正常 | 200、结构正确 |
| Real 正常 | 200、结构正确、无密钥泄漏 |
| 超时 | 规定时间内结束并降级 |
| 限流 | 最多重试一次，不无限循环 |
| 非法 JSON | 捕获并返回受控错误 |
| 空答案 | 视为失败，不显示空卡片 |

## 3.4 退出闸门

- [ ] 不配置密钥时，Fake 模式仍可完整运行。
- [ ] 配置真实密钥后，只改环境变量即可切换。
- [ ] 仓库搜索不到真实密钥。
- [ ] 测试全程使用 Fake，不产生 API 费用。
- [ ] 三种失败注入均有自动测试。
- [ ] 真实模型输出由 Pydantic 验证。

## 3.5 给 Codex 的任务卡

```text
当前处于阶段 3。请把模型调用封装为 ModelProvider，保留 Fake 和 Real 两个实现。
业务接口不能直接导入具体供应商 SDK。
加入超时、一次受控重试、结构化输出验证和固定降级。
测试必须通过 FakeProvider 覆盖成功、超时、限流、非法结构。
不得在日志、测试、README 中写真实密钥。
```

## 3.6 参考资料

- [OpenAI 文本生成指南](https://developers.openai.com/api/docs/guides/text)
- [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/)
- 其他供应商接入时，只阅读其官方 API 文档；不要默认“兼容 OpenAI”就完全兼容所有接口。

---

# 阶段 4：U1 知识卡、检索与可追溯回答

**建议时间：** 2026-07-20 至 2026-07-26  
**参与者：** 你  
**实现目的：** 让回答以五张可核验知识卡为事实边界，并展示真实来源。

## 4.1 U1 范围

1. U1-C01：像素。
2. U1-C02：标签。
3. U1-C03：训练数据。
4. U1-C04：图像分类。
5. U1-C05：训练集、验证集和测试集。

## 4.2 实践 Harness

- 五张 YAML 卡及 Schema 校验。
- 概念别名表：例如“识图、辨认图片、分类器”指向 U1-C04。
- 20 条固定问句，保存期望卡片 ID。
- 来源白名单：链接由后端从卡片映射，不由模型生成。
- 无答案测试：课程外问题不能伪造知识卡。
- 内容状态：`draft`、`source_verified`、`model_checked`、`peer_reviewed`、`demo_published`。

## 4.3 具体实践步骤

1. 为每个概念查找两个权威来源。
2. 写 `canonical_claims`，每条只表达一个可验证事实。
3. 写 `misconceptions`，用于补救讲解和测试。
4. 写先修关系和关键词，不先写长篇课程。
5. 创建 YAML Schema 或 Pydantic 模型，启动时一次性校验全部卡片。
6. 实现确定性检索：概念 ID → 别名 → 关键词评分。
7. 将检索卡片和学段要求发送给模型。
8. 模型只返回 `used_card_ids`；后端过滤不存在的 ID，并映射来源。
9. 建立 20 条黄金问句，逐条记录期望卡片和关键事实。

## 4.4 内容 Harness 的证据审计

对每张卡执行两个独立审查提示：

**证据审计：** 检查每条事实是否被来源支持，指出推断、过度概括、缺失条件和不可靠来源。

**反驳审计：** 以挑剔评审身份寻找年龄不适配、错误比喻、安全问题、事实混淆和可能导致误学的表达。

模型审查只能把状态推进到 `model_checked`。没有教师审稿时，不能标记“专家审核通过”。

## 4.5 退出闸门

- [ ] 五张卡启动校验全部通过。
- [ ] 每张卡至少有两个来源或明确说明只有一个来源。
- [ ] 20 条固定问句的卡片命中率达到内部目标。
- [ ] 页面展示来源标题和链接。
- [ ] 模型无法把不存在的 URL 混入来源区。
- [ ] 对课程外问题有明确边界和返回策略。
- [ ] 每张卡有状态、版本和审查记录。

## 4.6 给 Codex 的任务卡

```text
当前处于阶段 4。请实现五张 U1 YAML 知识卡的加载、Schema 校验、确定性检索和来源映射。
模型不能生成最终来源链接；后端只能根据合法 card_id 映射 sources。
请用 20 条固定问句建立参数化测试，输出每条的期望卡片和实际卡片。
禁止引入向量数据库；五张卡先用透明规则完成。
```

## 4.7 参考资料

- [AI4K12](https://ai4k12.org/)
- [Google 监督学习入门](https://developers.google.com/machine-learning/intro-to-ml/supervised)
- [Google ML Glossary](https://developers.google.com/machine-learning/glossary)
- [TensorFlow 图像分类](https://www.tensorflow.org/tutorials/images/classification)
- [OpenCV 图像基础操作](https://docs.opencv.org/4.x/d3/df2/tutorial_py_basic_ops.html)
- [scikit-learn train_test_split](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html)

---

# 阶段 5：四学段适配与主动教学状态机

**建议时间：** 2026-07-27 至 2026-08-02  
**参与者：** 你  
**实现目的：** 把“同一事实、四种教法”变成可执行、可测试的规则，并让系统主动推进教学。

## 5.1 实践 Harness

- `StagePolicy`：字数、术语数、例子类型、公式、代码和互动形式。
- 5 个概念 × 4 学段 = 20 个基准输出要求。
- 状态机事件表和非法迁移测试。
- 两个虚拟学生：低龄动物兴趣、高中编程兴趣。
- 快照检查：同一问题四个版本并排保存。

## 5.2 学段策略

| 学段 | 输出长度 | 教学形式 | 限制 |
|---|---:|---|---|
| 小学低年级 | 80～150 字 | 故事、语音、图片选择 | 一次只引入 1 个新词 |
| 小学高年级 | 150～250 字 | 图示、小游戏、简单步骤 | 术语后立即解释 |
| 初中 | 250～400 字 | 流程、动画、伪代码 | 给反例和因果 |
| 高中 | 350～600 字 | 算法、代码、实验、伦理 | 给限制和验证方法 |

## 5.3 状态机

```text
WELCOME
 → DIAGNOSE
 → EXPLAIN
 → CHECK_UNDERSTANDING
     ├─ 正确 → PRACTICE → REFLECT → RECOMMEND
     └─ 错误 → REMEDIATE → CHECK_UNDERSTANDING
```

## 5.4 具体实践步骤

1. 将学段策略写为后端配置，不放在提示词散文中。
2. `PromptBuilder` 同时接收知识卡和 `StagePolicy`。
3. 写格式校验器：字数、新术语、一次问题数量、公式/代码许可。
4. 定义状态、事件、允许迁移和每个状态的输出类型。
5. 程序决定状态迁移，模型只生成该状态需要的内容。
6. 错误后进入 `REMEDIATE`，强制换例子或换模态。
7. 保存四学段同题输出到 `artifacts/stage-05/`，人工并排检查。

## 5.5 退出闸门

- [ ] 同一问题四个版本肉眼可明显区分。
- [ ] 规则测试能发现超字数、术语过多和非法公式。
- [ ] 模型不能从 `WELCOME` 直接跳到 `RECOMMEND`。
- [ ] 做错题后进入补救，补救后重新检查。
- [ ] `CHECK_UNDERSTANDING` 一次只问规定数量的问题。
- [ ] 两个虚拟学生的示例、形式和后续动作不同。

## 5.6 给 Codex 的任务卡

```text
当前处于阶段 5。请实现配置化 StagePolicy 和显式 LessonStateMachine。
程序负责状态迁移，模型只能生成当前状态所需的结构化内容。
请建立四学段格式检查和非法状态迁移测试，并生成同题四版本的测试证据。
禁止引入 LangGraph；先用 Python Enum 和纯函数实现。
```

## 5.7 参考资料

- [Python Enum](https://docs.python.org/3/library/enum.html)
- [Pydantic Validators](https://docs.pydantic.dev/latest/concepts/validators/)
- [IBM Machine Learning for Kids 开源仓库](https://github.com/IBM/taxinomitis)

---

# 阶段 6：游戏化练习与学习事件

**建议时间：** 2026-08-03 至 2026-08-05  
**参与者：** 你  
**实现目的：** 完成“讲解—作答—反馈—记录”的最小闭环。

## 6.1 实践 Harness

- 20 道固定题：5 个概念 × 4 学段。
- 题目、答案、错因、反馈和回看卡片 ID 均固定。
- `learning_events` 记录正确性、提示次数、耗时和错误类型。
- 重复提交测试、非法选项测试、断线重试测试。
- 演示数据重置脚本。

## 6.2 具体实践步骤

1. 先完成选择、判断、排序三种题型，不做复杂小游戏引擎。
2. 题目生成只作为离线草稿；演示题必须先进入固定题库。
3. `POST /quiz/{id}/submit` 返回是否正确、解释、错因和下一动作。
4. 前端即时显示反馈，但最终判分以后端为准。
5. 写入学习事件；相同提交使用幂等键避免重复计分。
6. `reset_demo.ps1` 删除演示进度并重新播种两个虚拟学生。

## 6.3 退出闸门

- [ ] 20 道题的确定性批改测试全部通过。
- [ ] 错误反馈不是只有“答错了”，而是说明误区。
- [ ] 重复点击提交不会重复计分。
- [ ] 刷新页面后学习事件仍存在。
- [ ] 一条命令可以重置演示数据。

## 6.4 给 Codex 的任务卡

```text
当前处于阶段 6。请实现固定题库、确定性批改和 learning_events 写入。
先支持选择、判断和排序；不要生成实时随机题。
要求幂等提交、错误类型、回看 card_id、20 道题参数化测试和演示数据重置脚本。
```

---

# 阶段 7：动画、绘本与语音的模板化多模态

**建议时间：** 2026-08-06 至 2026-08-09  
**参与者：** 你；如队友提前加入，可让 B 协助前端  
**实现目的：** 用稳定模板完成至少三种多模态能力，不依赖现场实时生成视频。

## 7.1 实践 Harness

- 一套 `AnimationSpec` JSON 样例和 Schema。
- 一套六页绘本 JSON、固定图片、字幕和替代文本。
- 浏览器语音播放开关；无语音权限时文本仍可用。
- 低速网络测试、图片丢失测试、静音测试。
- 预生成资源清单和版权台账。

## 7.2 动画实践

1. 只实现“图像分类过程”模板。
2. 五个固定步骤：图片进入、像素网格、特征提示、类别分数、最终标签。
3. 模型只填写标题、旁白、示例和步骤参数。
4. 前端只解析白名单字段，不执行模型生成的 JavaScript。
5. 加暂停、重新播放、上一步、下一步和字幕。

## 7.3 绘本实践

1. 固定角色、配色和六页图片。
2. 每页结构：标题、图片、旁白、角色台词、互动问题、替代文本。
3. 小学低年级默认绘本；高中默认不推荐绘本，除非学生选择。
4. 现场只生成/切换文本，图片提前审查并缓存。

## 7.4 语音实践

1. 首版优先使用浏览器语音合成，避免服务端音频链路。
2. 支持播放、暂停、速度设置和字幕同步。
3. 不保存真实学生声音，不进行声纹识别。
4. 语音失败时，文本内容和学习流程不受影响。

## 7.5 退出闸门

- [ ] 对话、动画、绘本、练习至少三类真实可操作。
- [ ] 动画可以暂停和逐步查看。
- [ ] 绘本六页角色与风格一致。
- [ ] 图片均有替代文本，语音均有字幕。
- [ ] 断网或资源丢失时有占位和降级。
- [ ] 所有图片、音效和代码记录来源/许可证。

## 7.6 给 Codex 的任务卡

```text
当前处于阶段 7。请实现一个白名单 AnimationSpec 渲染器和六页 StorybookSpec 渲染器。
模型只能输出数据，不能输出并执行任意脚本。
加入暂停、步进、字幕、替代文本和资源丢失降级。
禁止接实时视频生成；图片使用已审查的本地资源。
```

## 7.7 参考资料

- [MDN Web Animations API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API)
- [MDN Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [WCAG 图片替代文本概览](https://www.w3.org/WAI/tutorials/images/)

---

# 阶段 8：掌握度与个性化路径

**建议时间：** 2026-08-10 至 2026-08-12  
**参与者：** 你  
**实现目的：** 用透明规则证明学习记录会改变后续推荐。

## 8.1 实践 Harness

- 两个固定虚拟学生和可重置历史。
- 固定事件序列和期望掌握度。
- 推荐解释测试：每条推荐必须有原因。
- 先修关系测试：未掌握先修时不能直接推荐高阶概念。
- 系数配置文件，不把设计参数写死在多个函数中。

## 8.2 首版算法

```text
单次表现分 = 正确性 × 0.60 + 少提示奖励 × 0.20 + 解释质量 × 0.20
新掌握度 = 旧掌握度 × 0.70 + 单次表现分 × 0.30
```

推荐优先级：先修未掌握 > 最近答错 > 到期复习 > 当前兴趣 > 进阶挑战。

## 8.3 具体实践步骤

1. 定义 `MasteryService.update(event)`，使用纯函数便于测试。
2. 定义 `RecommendationService.recommend(profile, mastery, graph)`。
3. 返回 `concept_id`、`reason_code`、`reason_text` 和建议模态。
4. 构造学生 A 连续答错训练数据、学生 B 已掌握分类的事件序列。
5. 重置后重复运行，结果必须一致。
6. 界面显示“为什么推荐”，不要展示虚假的精确学习能力诊断。

## 8.4 退出闸门

- [ ] 固定事件序列得到固定掌握度。
- [ ] 学生 A 和 B 得到不同推荐。
- [ ] 每条推荐有可读理由和机器理由码。
- [ ] 不会推荐缺失先修的概念。
- [ ] 系数被明确标为原型设计参数，不声称是教育学定论。

## 8.5 给 Codex 的任务卡

```text
当前处于阶段 8。请用纯函数实现 MasteryService 和 RecommendationService。
使用配置化系数和显式 reason_code；为两个固定虚拟学生建立事件序列测试。
不得引入机器学习训练；目标是透明、稳定、可解释。
```

---

# 阶段 9：四人交接与并行开发 Harness

**建议时间：** 2026-08-13 至 2026-08-16  
**参与者：** 全队 4 人  
**实现目的：** 让三名新成员在不依赖你口头操作的情况下跑通系统，并安全并行。

## 9.1 交接 Harness

- `README` 从零启动测试。
- `scripts/check.ps1` 一键检查。
- `reset_demo.ps1` 一键恢复。
- `docs/architecture.md`、`docs/content-workflow.md`、`docs/demo-script.md`。
- GitHub Issue 模板和 Pull Request 模板。
- P0 冻结标签；P1 每项独立 Issue。

## 9.2 第一天交接测试

1. 三名队友分别克隆仓库。
2. 不看你的电脑，只按 README 启动。
3. 每人记录卡住的步骤、错误和耗时。
4. README 的问题当天修复；不要用口头“你这样点一下”掩盖。
5. 全员运行 `scripts/check.ps1`，结果一致后再分工。

## 9.3 四人具体分工

| 人员 | 主责 | Harness 责任 |
|---|---|---|
| A（你） | 后端、模型、知识检索、学段策略、集成 | 保证主分支和 API 回归 |
| B | 前端、动画、绘本、字幕、移动端 | 组件测试、资源降级、截图证据 |
| C | U2/U3 内容、来源、题库、许可、盲审 | 卡片校验、来源台账、内容审查表 |
| D | 部署、测试、README、录屏、PPT | 一键检查、部署烟测、材料一致性 |

## 9.4 Git 并行 Harness

1. `main` 始终保持可演示。
2. 一项 Issue 对应一个短分支。
3. PR 必须包含目的、截图/接口样例、测试结果、风险和回滚方法。
4. 至少一名非作者审查。
5. 合并后立即运行完整 `check.ps1` 和五分钟演示烟测。

## 9.5 退出闸门

- [ ] 三名队友都能独立启动。
- [ ] 四人职责和目录所有权明确。
- [ ] P0 被标记并冻结。
- [ ] 第一个队友 PR 完整走过审查和回归。
- [ ] 工作区中没有互相覆盖的未提交文件。

---

# 阶段 10：在线编程环境（P1，可裁剪）

**建议时间：** 2026-08-17 至 2026-08-19  
**参与者：** A + B  
**实现目的：** 为高中学段提供受限 Python 实验；若影响 P0 稳定，应裁剪为代码阅读和补空题。

## 10.1 实践 Harness

- Monaco Editor 只负责编辑，不负责安全执行。
- Judge0 或独立沙箱负责执行。
- 固定三道安全实验，不允许任意软件包和网络访问。
- CPU、内存、时间、输出长度限制。
- 恶意代码测试：无限循环、内存膨胀、读文件、访问网络、进程创建。

## 10.2 具体实践步骤

1. 前端集成 Monaco，先做本地文本编辑和模板加载。
2. 后端定义 `CodeRunRequest`，只允许 Python 和规定模板 ID。
3. 在独立 Judge0 环境执行，不在 FastAPI 主进程中直接 `subprocess` 任意输入。
4. 返回 stdout、stderr、退出状态和超时标记。
5. 对五类恶意输入进行安全测试。
6. 若两天内无法满足隔离要求，降级为“预测输出—补全代码—查看固定结果”。

## 10.3 退出闸门

- [ ] 主应用服务器不直接执行任意代码。
- [ ] 无限循环能被终止。
- [ ] 网络和宿主文件访问被限制。
- [ ] 三道实验有固定模板和预期结果。
- [ ] 沙箱不可用时有安全降级。

## 10.4 参考资料

- [Judge0 GitHub](https://github.com/judge0/judge0)
- [Monaco Editor GitHub](https://github.com/microsoft/monaco-editor)

---

# 阶段 11：安全、评测与故障注入

**建议时间：** 2026-08-20 至 2026-08-23  
**参与者：** A + C + D  
**实现目的：** 把系统从“能演示”提升为“知道何时会失败，并能受控降级”。

## 11.1 总评测 Harness

`scripts/check.ps1` 至少执行：

```powershell
pytest backend/tests -q
npm --prefix frontend run test:unit
npm --prefix frontend run build
python scripts/validate_content.py
python scripts/run_golden_evals.py
python scripts/scan_secrets.py
```

如果某个命令未安装对应能力，应在当前阶段补齐，不能用空脚本假装通过。

## 11.2 评测集组成

- 5 条概念检索。
- 8 条四学段格式。
- 5 条固定题批改和补救。
- 4 条状态机。
- 4 条模型/数据库/资源失败降级。
- 4 条安全对抗：提示注入、个人信息、危险代码、敏感内容。

## 11.3 故障注入

1. 模型超时。
2. 模型返回非法结构。
3. 数据库暂时不可写。
4. 动画 JSON 缺字段。
5. 图片资源 404。
6. 网络变慢或断开。
7. 用户连续快速点击提交。
8. 页面刷新和重复请求。

每个故障都记录：触发方式、预期行为、实际行为、日志位置、是否阻断演示。

## 11.4 未成年人安全边界

- 只使用虚拟账号和合成历史。
- 不收集姓名、学校、电话、精确年龄和声纹。
- 不让模型索取个人联系方式。
- 对高风险内容提供适龄拒绝和可信成年人求助建议。
- 无教师/真实学生研究时，不声称教学效果已被验证。

## 11.5 退出闸门

- [ ] 一键检查全部通过。
- [ ] 30 条以上固定案例有可读报告。
- [ ] 关键故障都有降级。
- [ ] 日志可通过 `request_id` 追踪，但无密钥和真实隐私。
- [ ] P0 主路径连续运行 10 次无阻断。

## 11.6 参考资料

- [OpenAI Under-18 API Guidance](https://developers.openai.com/api/docs/guides/safety-checks/under-18-api-guidance)
- [OWASP API Security Top 10](https://owasp.org/API-Security/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

# 阶段 12：部署、演示与提交冻结

**建议时间：** 2026-08-24 至 2026-08-30  
**参与者：** 全队  
**实现目的：** 形成即使网络或 API 出现问题也能完成展示的可提交版本。

## 12.1 部署 Harness

- `docker-compose.yml` 或明确的平台部署配置。
- `/health`、版本号、构建提交 SHA。
- 线上主环境、本地备份、Fake 离线模式。
- 部署后烟测脚本。
- 演示账号和一键重置。

## 12.2 具体实践步骤

1. 用 Docker Compose 在新目录重建一次。
2. 部署后运行健康检查和五分钟主路径。
3. 在新电脑或队友电脑按 README 完整复现。
4. 准备线上、离线两套演示入口。
5. 录制完整视频和 30 秒备用片段。
6. 对照报告、PPT、视频和真实功能，删除任何夸大陈述。
7. 冻结功能；最后一周只修阻断性问题。

## 12.3 五分钟演示 Harness

固定脚本：

1. 小学低年级询问“AI 怎么认识小猫”。
2. 展示绘本/语音和来源。
3. 同题切换高中，展示数据集划分或代码入口。
4. 播放分类动画。
5. 故意答错，展示补救。
6. 展示掌握度变化和推荐理由。
7. 关闭真实模型，快速证明固定内容降级仍可用。

每次彩排记录总时长、卡顿点、错误和是否需要手动跳过。

## 12.4 退出闸门

- [ ] 新电脑可复现。
- [ ] 线上和离线模式都能演示。
- [ ] 五分钟脚本连续 10 次通过。
- [ ] 仓库无密钥、真实学生信息和无授权素材。
- [ ] 报告、PPT、视频、README 与系统一致。
- [ ] 官方命名、格式和截止日期已重新核验。

## 12.5 参考资料

- [Docker Compose Quickstart](https://docs.docker.com/compose/gettingstarted/)
- [FastAPI 容器部署](https://fastapi.tiangolo.com/deployment/docker/)

---

# 附录 A：一键检查脚本应达到的最终形态

`scripts/check.ps1` 的职责不是“打印检查完成”，而是任何一步失败就返回非零状态：

```powershell
$ErrorActionPreference = "Stop"

Write-Host "[1/6] Backend tests"
pytest backend/tests -q

Write-Host "[2/6] Frontend unit tests"
npm --prefix frontend run test:unit

Write-Host "[3/6] Frontend build"
npm --prefix frontend run build

Write-Host "[4/6] Content validation"
python scripts/validate_content.py

Write-Host "[5/6] Golden evaluations"
python scripts/run_golden_evals.py

Write-Host "[6/6] Secret scan"
python scripts/scan_secrets.py

Write-Host "All checks passed."
```

在项目早期，尚未建立的检查可以暂不写入；一旦写入，就必须真实执行，不能通过注释或吞掉错误制造“全绿”。

---

# 附录 B：每个阶段的证据目录

每个 `artifacts/stage-XX/` 至少保存：

```text
README.md             本阶段目标与结论
commands.txt          实际执行的命令
test-result.txt       测试输出
manual-checklist.md   人工验收结果
screenshots/          关键页面截图
known-issues.md       已知问题和是否阻断
```

不要保存真实密钥、完整模型敏感日志或真实学生信息。

---

# 附录 C：Codex 阶段任务的通用模板

```text
项目：JBGS-2026-02 K12 AI 教学助手
当前阶段：阶段 X（不要跨阶段）

本次唯一目标：
允许修改的文件：
禁止修改的文件/功能：

输入示例：
期望输出：

自动验收：
1.
2.
3.

人工验收：
1.
2.

完成后请汇报：
- 修改的文件及原因
- 执行的命令与结果
- 未解决风险
- 我下一步需要亲自验证什么
```

---

# 附录 D：阶段总览

| 阶段 | 核心结果 | Harness 关键点 | 未通过时禁止进入 |
|---|---|---|---|
| 0 | 安全仓库 | Git、密钥扫描、版本证据 | 阶段 1 |
| 1 | FastAPI 可运行 | `/health`、pytest、日志 | 阶段 2 |
| 2 | 前后端切片 | FakeProvider、契约、三态 UI | 阶段 3 |
| 3 | 真实模型可控 | Provider、超时、结构、降级 | 阶段 4 |
| 4 | 可追溯问答 | 五张卡、20 问、来源白名单 | 阶段 5 |
| 5 | 一核四教 | StagePolicy、状态机、快照 | 阶段 6 |
| 6 | 练习闭环 | 固定题、学习事件、重置 | 阶段 7 |
| 7 | 多模态 | 模板、字幕、替代文本、降级 | 阶段 8 |
| 8 | 个性化 | 固定事件、掌握度、推荐理由 | 阶段 9 |
| 9 | 四人并行 | README 复现、PR、P0 冻结 | 阶段 10/11 |
| 10 | 编程环境 | 独立沙箱和恶意代码测试 | 上线代码执行 |
| 11 | 质量冻结 | 30+ 回归、故障注入、安全 | 阶段 12 |
| 12 | 可提交版本 | 部署、备份、10 次彩排 | 正式提交 |

---

# 附录 E：调研资料使用边界

1. GitHub 项目用于借鉴工程结构和交互，不等于可以整库复制；采用前必须检查 LICENSE、NOTICE 和第三方依赖。
2. Hugging Face 的 GSM8K 可研究分步问题结构；OpenBookQA 在 Hugging Face 页面标注许可证不明，不复制题目；二者都不是中文 AI 通识教材。
3. 官方教程用于核对概念和 API，实际代码仍应固定依赖版本并通过本项目测试。
4. 网页可访问不等于素材可商用或可改编；图片、视频、音效和题库必须单独记录许可。
5. 调研和实现分离：先记录“它解决了什么问题”，再决定是否引入；不要看到一个仓库就立刻安装。

