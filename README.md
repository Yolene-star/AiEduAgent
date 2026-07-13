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
- 待你在 GitHub 网页确认远程仓库为 Private。
- 待你决定是否在阶段 1 前安装 Python 3.12；当前机器 `python3` 是 3.10.19。

阶段 0 完成后，再进入阶段 1：FastAPI `/health` 最小后端。

## Git 使用

当前运行环境使用分离 Git 目录 `.repo/`。常用命令如下：

```bash
git --git-dir=.repo --work-tree=. status --short --branch
git --git-dir=.repo --work-tree=. add .
git --git-dir=.repo --work-tree=. diff --cached
git --git-dir=.repo --work-tree=. commit -m "chore: complete stage 0 safety baseline"
```

提交前必须检查暂存内容，确认没有 `.env`、密钥、数据库、依赖目录或构建产物。
