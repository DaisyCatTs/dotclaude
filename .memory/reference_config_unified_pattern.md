---
name: reference_config_unified_pattern
description: 插件配置统一格式：扁平 JSON（baseUrl/model/apiKey），.env 引用，CLI flag > 进程 env > .local.json
  > .json 优先级
type: reference
---

## 统一配置格式

dotclaude 插件配置管理的最佳实践，经过 pi 和 vision 两个插件的统一验证：

### 文件命名与位置

- `.claude/<plugin>.json` — 项目共享，git tracked
- `.claude/<plugin>.local.json` — 项目本地，gitignored（`**/.claude/*.local.*`）
- `~/.claude/<plugin>.local.json` — 全局个人

### 优先级链（高→低）

1. CLI flag（`$ARGUMENTS`）
2. 进程 env（`PI_PROVIDER`、`VB_HOOK_ENABLED` 等）
3. `.claude/<plugin>.local.json`（项目本地）
4. `~/.claude/<plugin>.local.json`（全局个人）
5. `.claude/<plugin>.json`（项目共享）

### 扁平键名约定

所有插件使用统一的扁平命名，每个插件独立（不需要前缀）：

```json
{
  "baseUrl": "http://gateway:port/v1",
  "model": "model-id",
  "apiKey": "$ENV_VAR_REF"
}
```

- `baseUrl` — 端点 URL（若插件有两个端点，加前缀区分：`visionBaseUrl`）
- `model` — 模型 ID
- `apiKey` — API 密钥，支持 `$VAR`/`${VAR}` 环境变量引用
- 插件独有字段直接用简洁名：`blockedModels`、`port` 等

### 环境变量引用

- 配置值中用 `$VAR` 或 `${VAR}` 语法引用环境变量
- 运行时由脚本的 `resolve_env()` 函数解析
- 密钥永远不出现在磁盘文件中

### 配置验证

- `doctor` 子命令检查：安装、配置文件、端点连通性、循环依赖检测
- `--list-models` 显示生效配置

### 适用场景

任何需要 provider/model/API key/base URL 配置的插件。不依赖插件内置 `settings.json`（官方只支持 `agent` 和 `subagentStatusLine`）。

关联：[[project_mattpocock_fork]]