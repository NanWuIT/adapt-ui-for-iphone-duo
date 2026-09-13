[English](README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | 日本語

# iPhone Duo 向け UI の適応

`$adapt-ui-for-iphone-duo` は、Codex および互換性のあるコーディングエージェント向けのオープンソース [Agent Skill](https://agentskills.io/specification)（`SKILL.md`）です。iPhone Duo と折りたたみ式 iPhone ディスプレイに対応する SwiftUI／UIKit インターフェースを監査、設計、実装、検証します。

[スキルの手順](skills/adapt-ui-for-iphone-duo/SKILL.md)は、外側／カバーディスプレイと内側ディスプレイ、半開き状態、予約領域、縦型システムバー、サイズ変更可能なシーン、状態の継続、アクセシビリティ、および旧デバイス向けフォールバックに対応する、再現可能なネイティブ iOS ワークフローを提供します。これはスキルであり、UI フレームワーク、ランタイム依存関係、デバイス検出ライブラリ、独立したブランドではありません。

## 現在の状況

ハードウェアプロファイルとプラットフォームガイダンスは、Apple の一次情報を基に **2026-09-11** に確認されています。Apple の正式な製品名は **iPhone Duo** です。「iPhone 18 Duo」は、関連するユーザーリクエストでスキルを起動できるようにするため、プロジェクト独自の検索用エイリアスとしてのみ残されています。正式名称として提示するものではありません。

Apple は iPhone Duo Tech Talks で iOS 27.1 のサンプルを公開していますが、確認日時点では Xcode 27.1 beta は依然として 9 月後半に提供予定とされていました。そのため、このリポジトリでは、それらのシグネチャをコンパイル検証済み API ではなくプレビュー版のガイダンスとして扱っています。実装でコンパイル可能な内容は、常にインストール済み SDK によって決まります。

日付入りのツールチェーン状況と一次情報へのリンクについては、[Apple ガイダンス](skills/adapt-ui-for-iphone-duo/references/apple-guidance.md)を参照してください。

## 対象範囲

- 固定ジオメトリ、グローバルな画面前提、画面方向による分岐、広範なセーフエリア無視、手動配置、カスタムバーを対象とした SwiftUI／UIKit の監査。
- ナビゲーション分割ビューと、2 コンテンツ配置ビューの選択。
- 境界が定められたカスタムコンテンツに対する、折り目の有効な分割領域とカメラのオクルージョン領域。
- コンパクト、レギュラー、連続的なサイズ変更、ブック型、テーブルトップ型の構成。
- ナビゲーション、選択、下書き、再生、タスク、およびシーンごとの状態の継続。
- Dynamic Type、VoiceOver、Voice Control、右から左へのレイアウト、「視差効果を減らす」、「透明度を下げる」。
- iOS 27.1 API または Device Hub が利用できない場合の明示的なフォールバック。

このスキルは、モデル名、ピクセル寸法、物理寸法、ヒンジ角度をレイアウトのブレークポイントとして使用しません。Android の折りたたみ式デバイス、一般的なレスポンシブ Web サイト、または通常の iPad のみに対する適応は対象としていません。

## 公開ハードウェアプロファイル

| | 内側ディスプレイ | 外側ディスプレイ |
| --- | --- | --- |
| サイズ | 7.6 インチ折りたたみ式 OLED | 5.4 インチ OLED |
| 解像度 | 1878 × 2670 px | 1398 × 2034 px |
| 画素密度 | 430 ppi | 460 ppi |
| リフレッシュレート | 最大 120 Hz | 最大 120 Hz |
| 屋外ピーク輝度 | 3000 nits | 3000 nits |

Apple は、開いた状態の寸法を 164.6 × 117.8 × 5.2 mm、閉じた状態の寸法を 84.1 × 117.8 × 11.3 mm、重量を 254 g としています。これらの値は、ドキュメント、モックアップ、テスト計画のためだけに使用します。構造化され、情報源と対応付けられたデータは [device-profile.json](skills/adapt-ui-for-iphone-duo/references/device-profile.json) にあります。

## スキルが検出される仕組み

GitHub 上での検出とエージェントによる選択は別の段階です。プレビュー版の [`gh skill search`](https://cli.github.com/manual/gh_skill_search) は、公開 GitHub リポジトリから、クエリに一致する `name` または `description` を持つ `SKILL.md` を検索し、名前が一致するスキルを優先して表示します。インストール後に、[Codex](https://developers.openai.com/codex/skills) がスキル名と説明を参照し、タスクが一致するときに呼び出せるようになります。したがって、文書化されたフローは「検索またはインストール」の後に「エージェントによる選択」であり、未インストールの GitHub リポジトリは Codex のローカルスキル一覧には含まれません。

## インストール

[GitHub CLI の Agent Skills コマンド](https://cli.github.com/manual/gh_skill)は現在プレビュー版です。公開後は、GitHub の公開スキルインデックスを検索し、Codex 向けにスキルをインストールできます。

```bash
gh skill search "iphone duo"
gh skill install OWNER/adapt-ui-for-iphone-duo adapt-ui-for-iphone-duo --agent codex --scope user
```

リポジトリの公開後、`OWNER` を GitHub の所有者名に置き換えてください。このチェックアウトには Git リモートがないため、現時点では正式な所有者名を安全に特定できません。

既存のローカルチェックアウトからは、GitHub CLI で標準のスキルディレクトリを直接インストールできます。

```bash
gh skill install . adapt-ui-for-iphone-duo --from-local --agent codex --scope user
```

または、ユーザーレベルのシンボリックリンクを手動で作成し、Codex から利用できるようにします。

```bash
mkdir -p ~/.agents/skills
ln -s "$PWD/skills/adapt-ui-for-iphone-duo" ~/.agents/skills/adapt-ui-for-iphone-duo
```

スキルが参照資料を読み込み、スキャナーを実行できるよう、`skills/adapt-ui-for-iphone-duo` ディレクトリ全体を保持してください。安定した呼び出し識別子は、チェックアウト先のディレクトリ名に関係なく `$adapt-ui-for-iphone-duo` のままです。

## 使用方法

明示的に呼び出します。

```text
Use $adapt-ui-for-iphone-duo to audit this SwiftUI reader for iPhone Duo. Do not edit files.
```

```text
Use $adapt-ui-for-iphone-duo to adapt this player and queue screen while preserving our iOS 26 fallback.
```

```text
Use $adapt-ui-for-iphone-duo to verify this UIKit layout. Report which Duo poses cannot be tested with the installed Xcode.
```

トリガーメタデータは、折りたたみ式 iPhone、ブック型またはテーブルトップ型の姿勢、ヒンジや折り目の回避、予約領域、配置ビューに関するネイティブ iOS リクエストも認識します。無関係なレスポンシブレイアウトのタスクを除外するためのネガティブ境界も含まれています。

## オプションのソーススキャナー

スキャナーには Bash と [ripgrep](https://github.com/BurntSushi/ripgrep) が必要です。このリポジトリから次を実行します。

```bash
bash skills/adapt-ui-for-iphone-duo/scripts/audit-duo-layout.sh -- /path/to/ios-project
```

Swift および Objective-C のソースを再帰的に検査し、一般的な生成済み依存関係のツリーを無視しながら、確認候補となる `RISK` と適応型プリミティブを示す `INFO` を分けて出力します。検出結果は自動的に欠陥と判定されるものではありません。そのポリシーを意図的に適用する場合に限り `--fail-on-findings` を使用してください。終了コードの仕様とその他のオプションについては、`--help` を実行してください。

## コントリビューションの検証

リポジトリのルートから次を実行します。

```bash
bash scripts/validate.sh
```

検証では、スキルのメタデータ、JSON データと評価用フィクスチャ、Markdown リンク、シェルスクリプト、スキャナーの動作、およびインストール済みの場合は ShellCheck を確認します。インストール済みの GitHub CLI にプレビュー版 Agent Skills コマンドが含まれている場合は、`gh skill publish --dry-run` も実行します。完全なローカル検証には、Python 3、Bash、ripgrep が必要です。

## リポジトリ構成

```text
README.md / README.*.md                     英語版および各言語のプロジェクトドキュメント
skills/adapt-ui-for-iphone-duo/              インストール可能な Agent Skill 本体
  SKILL.md                                    トリガーメタデータとワークフロー
  agents/openai.yaml                          ユーザー向けスキルメタデータ
  references/                                 Apple のガイダンスとテストパターン
  scripts/audit-duo-layout.sh                 読み取り専用のネイティブソーススキャナー
evals/                                        トリガー境界とタスク契約のケース
scripts/validate.sh                           リポジトリ検証のエントリーポイント
tests/                                        スキャナーとバリデーターの回帰テスト
.github/workflows/validate.yml                継続的検証
```

## 一次情報

- [iPhone Duo の技術仕様](https://www.apple.com/iphone-duo/specs/)
- [iPhone Duo に備える](https://developer.apple.com/iphone-duo/)
- [iPhone Duo 向けの設計](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)
- [iPhone Duo の適応型レイアウトで姿勢を活用する](https://developer.apple.com/videos/play/tech-talks/111463/)

完全な情報源一覧は [Apple ガイダンス](skills/adapt-ui-for-iphone-duo/references/apple-guidance.md)で管理されています。

## コントリビューションとライセンス

[CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。このスキルは [MIT License](LICENSE) の下で提供されています。Apple の商標は互換性を説明する目的にのみ使用されています。詳しくは [NOTICE](NOTICE) を参照してください。このプロジェクトは独立したものであり、Apple との提携関係はなく、Apple による承認も受けていません。
