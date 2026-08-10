---
name: project_hardware_plugin
description: hardware 插件——通用 EDA 伞形插件；use-kicad-cli(KiCad 9.0) + use-openscad
type: project
---

`hardware` 插件（active，commit scope `hw`）：通用硬件/EDA 伞形插件，所以取名 `hardware` 而非 `kicad`。当前两个 skill：

**use-kicad-cli（KiCad 9.0）：**
- 注册在 `commands` 下（同 swiftui-review 模式）→ 既是 `/hardware:use-kicad-cli` 斜杠命令，又能自动触发
- 精简 SKILL.md + 6 个 reference 按命令组拆（setup/pcb-export/sch-export/checks/sym-fp-jobset/workflows）
- 覆盖 KiCad 9.0 kicad-cli 全部 6 个命令组（sch/pcb/sym/fp/jobset/version）
- 4 条不可协商 CRITICAL：macOS 二进制不在 PATH（`/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`）；DRC/ERC 不加 `--exit-code-violations` 会静默通过；`--output` 对不同命令是目录 vs 文件；`pcb export gerbers`（复数，单数 `gerber` 在 9.0 弃用/10.0 移除）
- 全部命令/flag/退出码经独立 agent 对照 kicad.org 文档核验，零错误

**use-openscad：**
- 同模式：精简 SKILL.md + 5 个 reference（language/cli/design/workflows）
- CRITICAL：mesh 导出无需 `--render`（`canPreview()` 对 STL/3MF/AMF/DXF/SVG 返回 false，`do_export` 总走完整 CGAL 几何分支；`--render` 只影响 PNG 图像导出）
- macOS 二进制路径、退出码未官方文档化（用 `--hardwarnings` + 非零即失败）
- 借鉴 `iancanderson/openscad-agent` 仓库：二进制定位模式、版本化文件名、stderr grep 校验非流形

**How to apply:** 升级 KiCad/OpenSCAD 后重验命令/flag/退出码。改 CRITICAL 规则前用独立 agent 核验官方文档。

关联：[[feedback_skill_level_enforcement]]、[[feedback_claude_code_guide]]