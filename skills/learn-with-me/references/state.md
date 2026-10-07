# 学习档案

## 目录解析

默认根目录是 `$CODEX_HOME/learning/learn-with-me`；`CODEX_HOME` 未设置时使用用户主目录下 `.codex/learning/learn-with-me`。解析为绝对路径后才读取或写入。例如 Windows 的用户主目录为 `C:/Users/USERNAME` 时，档案位于该目录下的 `.codex/learning/learn-with-me`；以实际环境为准。

用户明确指定学习目录时使用其目录，并在默认根目录的 `INDEX.md` 保存该主题的绝对位置，便于恢复。不要把档案写进技能安装目录或自动放进当前业务仓库。

首次使用主题时显示其保存路径，按学习过程自动增量保存已发生的证据和当前问题，不每次请求保存确认。用户要求只聊、不记录时停止该会话的磁盘写入，不在结束时补存。

## 文件分工

只在实际需要时创建以下文件：

- 根目录 `PROFILE.md`：明确偏好和用户提供的基础信息。新档案默认中文、技术自学；用户修改时更新。
- 根目录 `INDEX.md`：主题中文名、短 slug、别名、实际目录、最近学习日期。读旧内容后增量更新，保留其他主题。
- 主题目录 `MISSION.md`：目标、基础、时间预算、资料范围、模块顺序、每个模块的独立验收任务。暂定目标要标为暂定；用户更改目标时保留简短变更说明。
- `SOURCES.md`：已读资料的标题、链接/文件位置、版本或适用范围、查阅日期，必要时记录访问限制。
- `PROGRESS.md`：模块与概念当前状态、支持证据、薄弱点、最近练习、尚未回答的问题、下一步。
- `sessions/YYYY-MM-DD-NNN.md`：本单元简短日志，含题目、用户回答摘要、提示程度、反馈与下一步。同日编号按已存在文件递增。
- `REVIEW.json`：`review.py` 维护的概念复习数据。没有检验过的概念不要预建卡片。
- `QUESTION-BANK.md`：启用提前备题时保存候选题及评价要点，格式与状态见 [并行备题](question-preparation.md)。题目缓存不计入学习进度。
- `practice/`：实际编程练习；`lessons/`：用户需要保留的课件或笔记。

slug 使用简短、明确的英文 kebab-case；先匹配索引别名，再决定新建。不同目标的主题可以分开，例如 `java-basics` 与 `java-interview`；主题不明确且有多个候选时询问。

## 证据与恢复

概念状态使用“未检验 / 提示后完成 / 当次独立完成 / 延迟检验通过”。对每次重要状态变化记录用户实际回答摘要或代码位置、日期、帮助程度及验证结果。“很清楚”“看懂了”和 AI 自己的解释不是掌握证据。

`PROGRESS.md` 是当前主题学习状态的入口，`REVIEW.json` 只负责复习日程。更新时先读旧文件，保留尚未解决的问题与其他概念，追加日志后同步进度与索引。需要升级复习状态时，以脚本输出为准，人工不要另写一套日程。

跨会话先读个人偏好、索引、任务与进度；日志只加载恢复当前问题所需的最近部分。用户改变方向时保留已学证据，调整后续路径。课程是否完成取决于各模块独立验收任务，而非累计选择题分数。

磁盘只保存真实发生的学习内容。文件工具不可用时说明本次记录仅在对话中，不声称已经保存。损坏的 JSON 先报错并保留原文件，修复需要根据可核对日志恢复，不重置为新档案。

## REVIEW.json 与脚本

脚本使用 Python 标准库；执行时以技能实际绝对路径定位 `scripts/review.py`，以主题绝对路径定位 `REVIEW.json`。以下命令中的路径需替换为实际解析结果；遵守环境的 shell/RTK 约束。

```text
python scripts/review.py due --file ABSOLUTE_REVIEW_PATH --date YYYY-MM-DD
python scripts/review.py record --file ABSOLUTE_REVIEW_PATH --date YYYY-MM-DD --concept hash-collision --label 哈希冲突 --quality 4 --event SESSION-QUESTION-ID
```

传入用户本地日期，不使用主机默认时区。一次真实回答分配一个稳定事件 ID，例如 `2026-10-07-001-q1`；重试同一写入复用 ID。

首次 `record` 自动创建文件和父目录。`due` 无文件时返回空列表，不建目录。文件顶层是 `concepts`，每个概念含 `label`、`ease_factor`、`repetitions`、`interval_days`、`last_review`、`next_review`、`history`。历史事件含 `event_id`、`date`、`quality`。

脚本在写入前校验记录，以临时文件替换原文件。重复事件不重复计分；同一概念同日的连续正确回答不延长间隔；错误仍重置到次日。只允许按时间顺序追加，避免旧回答覆盖新状态。单个主题避免同时执行多个写入。
