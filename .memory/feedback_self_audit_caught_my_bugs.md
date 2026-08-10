---
name: feedback_self_audit_caught_my_bugs
description: 自审抓 bug 的 12 个具体模式；测试必须写 should-fail 和 should-pass 两条路径；多文件核心变更后跑独立审计
  agent
type: feedback
---

多次自审验证：不要轻信自己刚写的代码——fresh-agent 独立审计能抓到 inline review 发现不了的 bug。

**Why:** 对自己刚写的代码有不当信任，手测只验"正常情况绿"不验"注入违规应红"。自审 agent 无实现上下文，能发现账面声明错误、死链、措辞歧义等。

**How to apply:**
1. 守卫/校验脚本后，必须注入一个应失败样例验证它真的 fail，不能只验它对干净输入 pass
2. bash case glob 里绝不写裸 `*|*` 分支（`*|*` 是「* OR *」通配一切）；模式里的 `|` 是 alternation
3. bash 里改父 shell 变量（计数器）绝不能在 `cmd | while` 管道子 shell 里；用进程替换 `< <(...)` 或临时文件
4. bash 双引号里 `\n` 是字面 backslash-n 不是换行——用 `printf '<tag>\n%s\n</tag>' "$var"` 或 `$'...\n...'`
5. 断链扫描用 `[a-z_-]+` 替代 `\w+`（`\w` 不匹配连字符，会截断 `codebase-design` 等 skill 名）
6. 写文档交叉引用后，grep 反向验证目标真的存在
7. 写 grep 提取 markdown 表数据行时，用「只匹配数据行独有的特征」，别用 `^\|` 会带表头
8. 文档里给脚本两种调用方式时，实测两种都能工作——别把死路径写成同等合法
9. 措辞「then read X it references」在 diff 上下文有歧义——明确「X 是概览，不替代全文读取」
10. 设计文档里的数字账面声明（"共 N 处"），写完必须用设计自己的验证命令对设计文本实数一遍
11. frontmatter description 草稿写完后，逐短语对照它所实现的 REQ 的短语列表 diff 一遍
12. 跨 skill 引用共享文件时，用 `ln -s ../../references/xxx.md` 符号链接，不走跨 skill 私有 references 路径