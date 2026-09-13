[English](README.md) | [简体中文](README.zh-CN.md) | 繁體中文 | [日本語](README.ja.md)

# 讓 UI 適配 iPhone Duo

`$adapt-ui-for-iphone-duo` 是一項供 Codex 與相容程式開發代理使用的開源 [Agent Skill](https://agentskills.io/specification)（`SKILL.md`）。它能稽核、設計、實作及驗證適配 iPhone Duo 與折疊式 iPhone 顯示器的 SwiftUI 和 UIKit 介面。

[Skill 指令](skills/adapt-ui-for-iphone-duo/SKILL.md)提供一套可重複執行的原生 iOS 工作流程，涵蓋外螢幕／封面螢幕與內螢幕、部分摺疊、保留區域、垂直系統列、可調整大小的場景、狀態連續性、輔助使用功能，以及舊款裝置的相容替代方案。這是一項 skill，而不是 UI 框架、執行階段相依套件、裝置偵測程式庫或獨立品牌。

## 目前狀態

硬體設定檔與平台指南已於 **2026-09-11** 依據 Apple 官方第一手資料來源完成審查。Apple 的正式產品名稱是 **iPhone Duo**。

Apple 已在 iPhone Duo Tech Talks 中發布 iOS 27.1 範例，但截至審查日期，Xcode 27.1 beta 仍標示為將於九月稍晚推出。因此，本儲存庫將這些 API 定義列為預覽版指南，而不是已通過編譯驗證的 API。實作實際能否編譯，始終取決於已安裝的 SDK。

請參閱 [Apple 指南](skills/adapt-ui-for-iphone-duo/references/apple-guidance.md)，瞭解標註審查日期的工具鏈狀態及第一手資料來源連結。

## 涵蓋範圍

- 稽核 SwiftUI 和 UIKit 中的固定幾何尺寸、全域螢幕假設、裝置方向分支、大範圍安全區域覆寫、手動定位及自訂系統列。
- 依情境選用導覽分割檢視或雙內容排列檢視。
- 針對自訂且邊界固定的內容，處理目前生效的摺疊分隔區域與相機遮蔽區域。
- compact、regular、持續調整大小、書本式及桌上式配置。
- 維持導覽位置、選取內容、草稿、播放進度、執行中工作及各場景狀態的連續性。
- Dynamic Type、VoiceOver、Voice Control、由右至左的版面配置、減少動態效果及減少透明度。
- 無法使用 iOS 27.1 API 或 Device Hub 時，採用明確的相容替代方案。

這項 skill 不會以裝置型號、像素尺寸、實體尺寸或鉸鏈角度作為版面斷點。它不適用於 Android 折疊式裝置、一般響應式網站或普通的 iPad 專用版面調整。

## 公開硬體設定檔

| | 內螢幕 | 外螢幕 |
| --- | --- | --- |
| 尺寸 | 7.6 吋摺疊式 OLED | 5.4 吋 OLED |
| 解析度 | 1878 × 2670 px | 1398 × 2034 px |
| 像素密度 | 430 ppi | 460 ppi |
| 更新率 | 最高 120 Hz | 最高 120 Hz |
| 戶外峰值亮度 | 3000 nits | 3000 nits |

Apple 列出的展開尺寸為 164.6 × 117.8 × 5.2 mm，閉合尺寸為 84.1 × 117.8 × 11.3 mm，重量為 254 g。這些數值僅供撰寫文件、製作介面 mockup 及規劃測試之用。結構化且附來源對照的資料位於 [device-profile.json](skills/adapt-ui-for-iphone-duo/references/device-profile.json)。

## Skill 如何被找到

GitHub 探索與代理選擇是兩個獨立步驟。預覽版 [`gh skill search`](https://cli.github.com/manual/gh_skill_search) 會在 GitHub 公開儲存庫中搜尋 `name` 或 `description` 符合查詢的 `SKILL.md`，並優先排列名稱相符的項目。安裝後，[Codex](https://developers.openai.com/codex/skills) 才會看到 skill 的名稱與描述，並在工作內容相符時選擇呼叫。因此，官方文件描述的流程是先搜尋或安裝，再由代理選擇；尚未安裝的 GitHub 儲存庫不會進入 Codex 的本機 skill 清單。

## 安裝

[GitHub CLI 的 Agent Skills 指令](https://cli.github.com/manual/gh_skill)目前仍是預覽功能。儲存庫發布後，使用者可以在 GitHub 的公開 skill 索引中搜尋，並為 Codex 安裝這項 skill：

```bash
gh skill search "iphone duo"
gh skill install NanWuIT/adapt-ui-for-iphone-duo adapt-ui-for-iphone-duo --agent codex --scope user
```

GitHub 正式儲存庫為 `NanWuIT/adapt-ui-for-iphone-duo`。

若已有本機工作副本，GitHub CLI 可以直接安裝符合標準的 skill 目錄：

```bash
gh skill install . adapt-ui-for-iphone-duo --from-local --agent codex --scope user
```

也可以用手動建立的使用者層級符號連結，將它提供給 Codex：

```bash
mkdir -p ~/.agents/skills
ln -s "$PWD/skills/adapt-ui-for-iphone-duo" ~/.agents/skills/adapt-ui-for-iphone-duo
```

請保留完整的 `skills/adapt-ui-for-iphone-duo` 目錄，讓這項 skill 能載入參考資料並執行掃描器。無論工作副本的目錄名稱為何，固定的呼叫識別符皆維持為 `$adapt-ui-for-iphone-duo`。

## 使用方式

請明確呼叫：

```text
Use $adapt-ui-for-iphone-duo to audit this SwiftUI reader for iPhone Duo. Do not edit files.
```

```text
Use $adapt-ui-for-iphone-duo to adapt this player and queue screen while preserving our iOS 26 fallback.
```

```text
Use $adapt-ui-for-iphone-duo to verify this UIKit layout. Report which Duo poses cannot be tested with the installed Xcode.
```

觸發中繼資料也能辨識涉及下列情境的原生 iOS 要求：折疊式 iPhone、書本或桌上姿態、避開鉸鏈或摺痕、保留區域，以及排列檢視。此外也設有排除條件，以免因不相關的響應式版面工作而誤觸發。

## 選用的原始碼掃描器

掃描器需要 Bash 和 [ripgrep](https://github.com/BurntSushi/ripgrep)。請從本儲存庫執行：

```bash
bash skills/adapt-ui-for-iphone-duo/scripts/audit-duo-layout.sh -- /path/to/ios-project
```

它會遞迴掃描 Swift 和 Objective-C 原始碼，排除常見的自動產生目錄與相依套件目錄，並分別列出 `RISK` 審查候選項目和 `INFO` 自適應版面基礎元件。掃描結果不代表一定存在缺陷。只有在確定要採用這項檢查政策時，才使用 `--fail-on-findings`；執行 `--help` 可查看結束狀態碼規範及其他選項。

## 驗證貢獻內容

請從儲存庫根目錄執行：

```bash
bash scripts/validate.sh
```

驗證程序會檢查 skill 中繼資料、JSON 資料與評估案例檔案、Markdown 連結、shell 指令碼及掃描器行為；若已安裝 ShellCheck，也會一併執行。若已安裝的 GitHub CLI 包含預覽版 Agent Skills 命令，還會執行 `gh skill publish --dry-run`。完整的本機驗證流程需要 Python 3、Bash 和 ripgrep。

## 儲存庫結構

```text
README.md / README.*.md                     英文與多語言專案文件
skills/adapt-ui-for-iphone-duo/              可安裝的 Agent Skill 內容
  SKILL.md                                    觸發中繼資料與操作流程
  agents/openai.yaml                          面向使用者的 skill 中繼資料
  references/                                 Apple 指南與測試模式
  scripts/audit-duo-layout.sh                 唯讀的原生原始碼掃描器
evals/                                        觸發邊界與任務契約案例
scripts/validate.sh                           儲存庫驗證入口
tests/                                        掃描器與驗證器的迴歸測試
.github/workflows/validate.yml                持續驗證
```

## 第一手資料來源

- [iPhone Duo 技術規格](https://www.apple.com/iphone-duo/specs/)
- [準備迎接 iPhone Duo](https://developer.apple.com/iphone-duo/)
- [iPhone Duo 設計指南](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)
- [使用 iPhone Duo 自適應版面支援各種姿態](https://developer.apple.com/videos/play/tech-talks/111463/)

完整的資料來源清單請見 [Apple 指南](skills/adapt-ui-for-iphone-duo/references/apple-guidance.md)。

## 貢獻與授權條款

請參閱 [CONTRIBUTING.md](CONTRIBUTING.md)。這項 skill 採用 [MIT License](LICENSE) 授權。Apple 商標僅用於描述相容性；詳情請參閱 [NOTICE](NOTICE)。本專案為獨立開發，與 Apple 無隸屬關係，亦未獲 Apple 認可或背書。
