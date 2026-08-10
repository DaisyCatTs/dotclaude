---
name: reference_git_coauthor_allowlist
description: git-agent co-author email 域名 allowlist 机制 + 多 provider 支持（GLM/Qwen/DeepSeek/Moonshot）的配置方法
type: reference
---

git-agent 二进制在 `require_model_co_author: true` 时，会校验 `--co-author` 的 email 域名是否在 allowlist 内，否则 exit 1 且不调 LLM。错误信息示例：
`error: require_model_co_author is enabled — pass --co-author with an email from one of: anthropic.com, openai.com, google.com, ...`

**allowlist 不是硬编码**，是两部分的并集：
1. 内置 `DefaultModelCoAuthorDomains` = `anthropic.com, openai.com, google.com`（源码 `domain/project/config.go`，git-agent 仓库在 `~/Developer/FradSer/git-agent/git-agent-cli`）。
2. 配置键 `model_co_author_domains`（stringslice，user/project/local 三级均合法），**追加**到内置列表（非覆盖）。

**要让 skill 在非 Anthropic 模型上跑通，两层都要对**：
- skill 层：`/git:commit` 和 `/git:commit-and-push` 各有一张 model-prefix→域名映射表（见 `git/skills/*/SKILL.md` + `git/references/cli.md` 的 allowlist 小节）。
- git-agent 配置层：对应域名必须在 allowlist 内。

本机已配置（user scope，全局跨仓库，不进版本控制）：
```
git-agent config set --user model_co_author_domains "zhipuai.cn,qwen.ai,deepseek.com,moonshot.ai"
```
实际写入值：`zhipuai.cn,qwen.ai,deepseek.com,moonshot.ai`（4 家国内厂商，对应 GLM/Qwen/DeepSeek/Moonshot）。

各 provider 域名来源已用 GitHub org 核实：anthropics→anthropic.com、openai→openai.com、google-gemini→google.com、zhipuai→zhipuai.cn、QwenLM→qwen.ai、deepseek-ai→deepseek.com、MoonshotAI→moonshot.ai。

**坑**：`config set` 对 stringslice 是该 scope 的**整行覆盖**（逗号分隔），不是向已有值 append。修改时要重写完整列表。

与 [[project_gitagent_scopes]]（scope 生成）不同主题，但都属 git-agent 配置层。与 [[feedback_git_commit_hook_needed]]（PreToolUse hook 拦 git add/commit）相关但不同层：hook 管"别用裸 git"，本条管"co-author 域名校验"。
