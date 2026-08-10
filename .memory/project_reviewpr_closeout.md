---
name: project_reviewpr_closeout
description: review-pr skill 加 Phase 3 收尾(hide+resolve)与 Phase 5 收尾(总结评论+重写 PR title/body)
type: project
---

review-pr skill 扩展为五阶段：Phase 3 收尾（hide + resolve）+ Phase 5 收尾（总结评论 + 重写 PR）。

**Phase 3 收尾（hide + resolve）**：每条已彻底解决的评论（fix 已 push，或 reject 已回复）→ `minimizeComment`(GraphQL, classifier=OUTDATED) 隐藏 + `resolveReviewThread` 解析线程。关键事实（经 GraphQL introspection 核验，非文档二手）：
- enum 名是 `ReportedContentClassifiers`（非文档写的 `ReportContentClassifier`），值含 OUTDATED/RESOLVED 等
- `resolveReviewThread` 入参是 `threadId`（线程 node ID），**不等于**评论 node_id；需先查 `pullRequest.reviewThreads` 取线程 id + 首评论的 GraphQL `id`（= REST node_id）做匹配
- GraphQL 评论类型字段是 `fullDatabaseId` 不是 `databaseId`
- issue 级评论无线程，只能 hide 不能 resolve；escalate 评论保持开放

**Phase 5 收尾（总结评论 + 重写 PR）**：Phase 4 停止条件满足后、TaskStop 前，以用户第一人称发 `gh pr comment --body-file -` 总结（改了什么 + review 发现及处置），并用 `gh pr edit -t/--body-file -` 重写 title/body。title 仅在不再匹配实际改动时才改（不 churn）。body 讲 What/Why/Changes/Review-cycle 指针/Verification；评论记录 review cycle，body 描述 change，二者不重复。

**Stop hook 强制 Phase 5 merge ask**。用户反馈：AI 幻觉会直接结束回合、跳过「询问是否合并」。机制（不再是纯提示词）：
- `github/hooks/closeout-stop.sh`（Stop hook，plugin.json `hooks.Stop` 无 matcher）：review-pr 在 Phase 4 停止条件满足时先 arm 状态文件（`arm-closeout.sh $PR [--auto-merge]` 写 `.git/review-pr-closeout.json`，gitdir 解析），用户回答任何选项（含 Don't merge）/auto-merge 完成或中止后 `clear-closeout.sh $PR` 清除（PR 匹配才删）。**每用户回合只阻塞一次**：`stop_hook_active=true`（同回合第二次结束尝试）时提前 `exit 0` 放行（官方反循环模式，claude-code-guide 核验），所以提醒注入一次后回合能正常结束，不撞 8 连块上限。阻塞 = `hookSpecificOutput.additionalContext`（exit 0 + JSON，消息回喂模型，非 hook error），消息带 clear 脚本绝对路径作逃生口
- Stop hook 事实（claude-code-guide 核验）：无 matcher/`if`（永远每次触发）；输入**无 prompt 字段**；`stop_hook_active` 是回合级（任何 stop hook 阻塞后所有 hook 都见 true，跨用户回合重置）；`exit 0` 无 JSON = 放行回合正常结束；阻塞 = exit 0 + additionalContext 或 exit 2 stderr 都回喂模型继续回合；插件 hook 在 subagent stop 也会触发 → 必须 `agent_id` 存在即放行；8 连块上限 `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` 仍存在但本 hook 已不再触发；hook cwd = session cwd，`CLAUDE_PLUGIN_ROOT` 导出可用
- 守卫必测 should-fail：armed/auto 阻塞、subagent/非 git/无 jq/空 stdin/corrupt state 放行、错 PR clear 不清、非数字 PR 拒绝。arm 脚本 JSON 需转义（PR 强制 `[0-9]+` + jq 构造）；auto 模式 suspend 路径（escalate 开 → 回退显式 ask）需重 arm 为 ask 模式；hook 消息要求阻塞后**先验证 closeout 是否真实 pending**（stale 状态假警报：ask 已答/总结已发/PR 已合并但 clear 没跑）——简单检查（`gh pr view --json state,mergedAt`、summary marker）自行判断，复杂/模糊起独立 subagent（同 Phase 3 triage 模式），stale → clear 后结束回合不重问

**「指针」做成真链接**。用户明确称赞 campbase PR #4 的体验：总结评论 + body 里引用该评论的 URL。经核验的 gh 事实：
- `gh pr comment` **无条件把新建/更新后的评论 URL 打到 stdout**（cli/cli `pkg/cmd/pr/shared/commentable.go`，仅 `--quiet` 抑制，该 flag 未对外暴露）→ `SUMMARY_URL=$(gh pr comment ... --body-file - <<'EOF' ...)` 可捕获
- 顺序是**因果不是并列**：body 需要评论 URL，所以必须先发评论再重写 body
- body heredoc 是引号 `<<'EOF'`，`$SUMMARY_URL` 不展开 → 必须粘贴字面 URL；**不能**改成不引号 heredoc（body 里的反引号/`$` 会被当命令替换执行）
- `--edit-last` 是坑：它改的是「当前用户最近一条评论」，而 Phase 3 的 issue 级 reject 回复也是同一用户发的，可能把回复覆盖掉。改用首行标记 `<!-- review-pr:summary -->` + `gh api --paginate .../issues/$PR/comments --jq '.[] | select(.body|startswith(...)) | .id'` 定位，再 `gh api --method PATCH repos/$REPO/issues/comments/<id> -F body=@- --jq .html_url`
- `-F body=@-` 逐字传 stdin：`magicFieldValue`（`pkg/cmd/api/fields.go`）见到 `@` 前缀就直接 return 原始字符串，**跳过**类型转换与 `{owner}`/`{repo}`/`{branch}` 占位符替换；`--method PATCH` 能覆盖「有 field 就自动 POST」的默认
- `gh api --paginate` 的 `--jq` 是**逐页**执行的（跨页聚合要 `--slurp`），所以 `.[] | select(...)` 是对的写法，与 review-loop.sh 现有用法一致

脚本 review-loop.sh 的 `[comment]` 行加了 `node=<id>` token 供 hide/resolve/closeout 键控。新增 references/closeout.md。

Why: 用户要求 PR merge-ready 时以自己名义写总结发言并重写 PR title/body。
How to apply: 改 GraphQL 字段名前必跑 introspection 核验；评论 node_id 与线程 node_id 是两个不同的 ID，别混。关联 [[feedback_verification]]、[[feedback_null_alternative_first]]。

**残留拦截陷阱（2026-08-09 PR #29 实测）：** 旧版 stop hook（无 `stop_hook_active` 守卫）在 closeout 仍 armed 时触发的拦截消息，会作为 **additionalContext 残留注入**到后续回合——即使 hook 已升级为每回合只拦一次、closeout 状态也已清除，那些陈旧的 "Stop hook feedback" 仍会多次出现在上下文里，造成"问题仍被拦"的假象。遇到连续 stop-hook 拦截时，先验证是否真实：`find . -name review-pr-closeout.json`（状态文件）+ `bash hooks/closeout-stop.sh` 实测当前输入是否放行 + `gh pr view --json state,mergedAt`。状态文件不存在且 hook 实测放行 → 拦截是残留，直接结束回合不重复动作。见 [[feedback_verify_problem_real]]。
