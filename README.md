# learn-with-ai-skill

一个中文 AI 学习教练 Skill，把学习路线、费曼复述、实践测验和间隔复习结合起来。默认面向编程与技术自学，适用于项目实践、源码阅读和技术面试，也可以用于通用知识和课程复习。

技能名称：**我的技术学习教练**。调用名：**`learn-with-me`**。

## 如何学习

1. **先了解基础**：询问相关前置知识和实际做过的任务，确认适合从哪里开始。
2. **确定目标与路线**：明确希望独立完成什么，再安排资料、实践任务和验收方式。
3. **小步教学与费曼复述**：每轮聚焦一个概念，让学习者解释、预测或动手实现，根据回答修补缺口。
4. **提前备题与针对性追问**：独立题提前准备，有并行能力时并行；依赖回答的追问、补弱题和难度调整在真实回答后生成。默认仍逐题展示。
5. **记录与复习**：保存真实学习证据，区分提示后完成、当次独立完成和延迟检验通过；根据表现安排间隔复习。

用户可以要求直接解释、看完整解法、跳过问题或停止保存记录。

## 安装

可以用 [skills CLI](https://github.com/vercel-labs/skills) 选择目标 Agent 并安装：

```bash
npx skills@latest add chuanmu1314/learn-with-ai-skill
```

也可以下载仓库，把 `skills/learn-with-me` 整个目录放入 Codex 的 `$CODEX_HOME/skills/`。未设置 `CODEX_HOME` 时，目录为 `~/.codex/skills/learn-with-me/`。

该目录包含 `SKILL.md`、教学参考文件和复习脚本，安装时保留完整结构。

## 使用示例

```text
用 $learn-with-me 带我学习 Java 并发，先了解我的基础，再通过小项目检验理解。

用 $learn-with-me 带我读这个仓库的请求处理源码。

用 $learn-with-me 模拟一次后端技术面试，根据我的回答追问。

用 $learn-with-me 继续上次的学习，复习今天到期的概念。
```

## 文件结构

```text
skills/learn-with-me/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── teaching.md
│   ├── assessment.md
│   ├── question-preparation.md
│   └── state.md
└── scripts/review.py
```

`review.py` 只依赖 Python 标准库。持久化复习需要 Python 3.10 或更新版本。Agent 按用户当地日期传入 `--date`，按概念保存复习计划。重复保存同一事件不会重复计分，同一天连续答对不会延长间隔。

并行备题需要运行环境提供子 Agent 或其他并行能力；没有时使用当前回合批量备题与缓存。技能本身不会在会话结束后启动后台服务。

## 学习数据与密钥

学习档案默认保存在 `$CODEX_HOME/learning/learn-with-me/`，未设置时为 `~/.codex/learning/learn-with-me/`，与技能安装目录分开。用户也可以指定其他学习目录或要求仅在对话中记录。

本仓库只分发技能指令与脚本，不包含个人学习档案、回答记录、API 密钥或模型配置。技能无需自己的 API 密钥；所用 Agent、模型或练习项目的凭据由使用者在本地配置。不要把 `.env`、私钥、凭据文件和个人学习记录提交到公开仓库。

复习日期在再次学习时检查；定时提醒需要用户另行要求，并由运行环境的自动化能力处理。生成的教学内容与评分应通过原始资料、实际代码或测试核对。

## 设计来源

本项目重新编写了一套独立的技能指令与复习脚本，借鉴以下项目的教学思路：

- [mattpocock/skills — teach](https://github.com/mattpocock/skills/blob/main/docs/productivity/teach.md)：目标驱动、可信资料和跨会话学习。
- [kirilxd/claude-tutor](https://github.com/kirilxd/claude-tutor)：测验、薄弱项追踪与间隔复习。
- [koukekoukej-glitch/feynman-tutor](https://github.com/koukekoukej-glitch/feynman-tutor)：对话、复述与理解缺口定位。

使用本项目无需安装这些项目，不依赖它们的服务器、hooks 或产品专用命令。

## 许可证

[MIT](LICENSE)。
