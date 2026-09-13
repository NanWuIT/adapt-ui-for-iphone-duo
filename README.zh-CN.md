[English](README.md) | 简体中文 | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md)

# 为 iPhone Duo 适配 UI

`$adapt-ui-for-iphone-duo` 是一个面向 Codex 和兼容编程智能体的开源 [Agent Skill](https://agentskills.io/specification)（`SKILL.md`）。它用于审计、设计、实现和验证适配 iPhone Duo 与折叠式 iPhone 显示屏的 SwiftUI 和 UIKit 自适应界面。

[Skill 指令](skills/adapt-ui-for-iphone-duo/SKILL.md)提供了一套可重复执行的原生 iOS 工作流程，覆盖外屏／封面屏与内屏、部分折叠姿态、保留区域、竖向系统栏、可调整大小的场景、状态连续性、无障碍功能以及旧设备回退方案。它只是一个 skill，不是 UI 框架、运行时依赖项、设备检测库，也不是独立品牌。

## 当前状态

硬件规格和平台指南已于 **2026-09-11** 依据 Apple 一手资料完成核查。Apple 的官方产品名称是 **iPhone Duo**。“iPhone 18 Duo”仅作为项目自定义的检索别名保留，以便相关用户请求能够触发此 skill；本文不会将其表述为官方名称。

Apple 已在 iPhone Duo Tech Talks 中发布 iOS 27.1 示例，但截至核查日期，Xcode 27.1 beta 仍被列为将于 9 月稍晚推出。因此，本仓库将这些 API 签名标记为预览指南，而非经编译验证的 API。实际实现能否通过编译，始终以已安装的 SDK 为准。

有关工具链状态（含核查日期）和一手资料链接，请参阅 [Apple 指南](skills/adapt-ui-for-iphone-duo/references/apple-guidance.md)。

## 覆盖范围

- 审计 SwiftUI 和 UIKit 中的固定几何尺寸、全局屏幕假设、屏幕方向分支、范围过大的安全区域忽略设置、手动定位以及自定义栏。
- 在导航分栏视图与双内容排列视图之间进行选择。
- 处理会影响自定义有界内容的当前折叠分隔区域和摄像头遮挡区域。
- 支持紧凑、常规、连续调整大小、书本式和桌面式配置。
- 保持导航、选择、草稿、播放、任务以及每个场景的状态连续性。
- 支持动态字体、旁白、语音控制、从右到左布局、减弱动态效果以及降低透明度。
- 在 iOS 27.1 API 或 Device Hub 不可用时提供明确的回退方案。

此 skill 不会将型号名称、像素尺寸、物理尺寸或铰链角度用作布局断点。它不面向 Android 折叠设备、通用响应式网站或仅针对普通 iPad 的适配。

## 公开硬件规格

| | 内屏 | 外屏 |
| --- | --- | --- |
| 尺寸 | 7.6 英寸折叠式 OLED | 5.4 英寸 OLED |
| 分辨率 | 1878 × 2670 px | 1398 × 2034 px |
| 像素密度 | 430 ppi | 460 ppi |
| 刷新率 | 最高 120 Hz | 最高 120 Hz |
| 户外峰值亮度 | 3000 nits | 3000 nits |

Apple 列出的展开尺寸为 164.6 × 117.8 × 5.2 mm，闭合尺寸为 84.1 × 117.8 × 11.3 mm，重量为 254 g。这些数值仅用于文档、设计稿和测试规划。结构化数据及其来源映射详见 [device-profile.json](skills/adapt-ui-for-iphone-duo/references/device-profile.json)。

## Skill 如何被发现

GitHub 发现与智能体选择是两个独立步骤。预览版 [`gh skill search`](https://cli.github.com/manual/gh_skill_search) 会在 GitHub 公开仓库中搜索 `name` 或 `description` 与查询匹配的 `SKILL.md`，并优先排列名称匹配项。安装后，[Codex](https://developers.openai.com/codex/skills) 才会看到 skill 的名称和描述，并在任务匹配时选择调用它。因此，官方文档描述的流程是先搜索或安装，再由智能体选择；未安装的 GitHub 仓库不会进入 Codex 的本地 skill 列表。

## 安装

[GitHub CLI 的 Agent Skills 命令](https://cli.github.com/manual/gh_skill)目前仍处于预览阶段。仓库发布后，用户可以搜索 GitHub 的公开 skill 索引，并为 Codex 安装此 skill：

```bash
gh skill search "iphone duo"
gh skill install NanWuIT/adapt-ui-for-iphone-duo adapt-ui-for-iphone-duo --agent codex --scope user
```

GitHub 规范仓库为 `NanWuIT/adapt-ui-for-iphone-duo`。

如果已经在本地检出本仓库，GitHub CLI 可以直接安装符合标准的 skill 目录：

```bash
gh skill install . adapt-ui-for-iphone-duo --from-local --agent codex --scope user
```

也可以通过用户级符号链接手动向 Codex 暴露此 skill：

```bash
mkdir -p ~/.agents/skills
ln -s "$PWD/skills/adapt-ui-for-iphone-duo" ~/.agents/skills/adapt-ui-for-iphone-duo
```

请保留完整的 `skills/adapt-ui-for-iphone-duo` 目录，以便 skill 加载其参考资料并运行扫描器。无论检出目录名称为何，稳定的调用标识始终为 `$adapt-ui-for-iphone-duo`。

## 使用

显式调用：

```text
Use $adapt-ui-for-iphone-duo to audit this SwiftUI reader for iPhone Duo. Do not edit files.
```

```text
Use $adapt-ui-for-iphone-duo to adapt this player and queue screen while preserving our iOS 26 fallback.
```

```text
Use $adapt-ui-for-iphone-duo to verify this UIKit layout. Report which Duo poses cannot be tested with the installed Xcode.
```

触发元数据还会识别涉及折叠式 iPhone、书本式或桌面式姿态、铰链或折痕避让、保留区域以及排列视图的原生 iOS 请求。同时也设置了排除边界，避免被无关的响应式布局任务触发。

## 可选源代码扫描器

扫描器需要 Bash 和 [ripgrep](https://github.com/BurntSushi/ripgrep)。请从本仓库运行：

```bash
bash skills/adapt-ui-for-iphone-duo/scripts/audit-duo-layout.sh -- /path/to/ios-project
```

它会递归检查 Swift 和 Objective-C 源代码，忽略常见的自动生成依赖目录，并分别输出标记为 `RISK` 的待审查项和标记为 `INFO` 的自适应布局原语。扫描结果并不代表这些位置必然存在缺陷。仅在有意采用该策略时使用 `--fail-on-findings`；运行 `--help` 可查看退出码约定和其他选项。

## 验证贡献

请从仓库根目录运行：

```bash
bash scripts/validate.sh
```

验证过程会检查 skill 元数据、JSON 数据和评测样例、Markdown 链接、Shell 脚本、扫描器行为，并在安装了 ShellCheck 时运行它。如果已安装的 GitHub CLI 包含预览版 Agent Skills 命令，还会运行 `gh skill publish --dry-run`。完整的本地验证流程需要 Python 3、Bash 和 ripgrep。

## 仓库结构

```text
README.md / README.*.md                     英文及多语言项目文档
skills/adapt-ui-for-iphone-duo/              可安装的 Agent Skill 内容
  SKILL.md                                    触发元数据和执行流程
  agents/openai.yaml                          面向用户的 skill 元数据
  references/                                 Apple 指南和测试模式
  scripts/audit-duo-layout.sh                 只读原生源代码扫描器
evals/                                        触发边界和任务契约样例
scripts/validate.sh                           仓库验证入口
tests/                                        扫描器和验证器回归测试
.github/workflows/validate.yml                持续验证
```

## 一手资料

- [iPhone Duo 技术规格](https://www.apple.com/iphone-duo/specs/)
- [为 iPhone Duo 做好准备](https://developer.apple.com/iphone-duo/)
- [为 iPhone Duo 进行设计](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)
- [在 iPhone Duo 上使用自适应布局应对不同姿态](https://developer.apple.com/videos/play/tech-talks/111463/)

完整资料列表见 [Apple 指南](skills/adapt-ui-for-iphone-duo/references/apple-guidance.md)。

## 贡献和许可证

请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。本 skill 采用 [MIT License](LICENSE)。Apple 商标仅用于描述兼容性；详情请参阅 [NOTICE](NOTICE)。本项目为独立项目，与 Apple 没有关联，也未获得 Apple 的认可。
