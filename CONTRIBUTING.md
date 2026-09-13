# Contributing

Contributions that improve the accuracy, triggering, implementation workflow, scanner, or verification quality of `$adapt-ui-for-iphone-duo` are welcome.

## Principles

- Base hardware facts and platform API claims on primary Apple sources.
- Record a review date and exact source URL for facts that can change.
- Keep pixels and physical dimensions informational; never promote them to runtime layout breakpoints.
- Preserve older supported iOS behavior and distinguish runtime availability from compile-SDK availability.
- Treat scanner matches as review candidates and actively control false positives.
- Keep `skills/adapt-ui-for-iphone-duo/SKILL.md` procedural and concise; put detailed platform material in its `references/` directory.
- Keep the invocation identifier `adapt-ui-for-iphone-duo` stable.
- Treat `README.md` as the English source and keep `README.zh-CN.md`, `README.zh-TW.md`, and `README.ja.md` structurally and factually synchronized.
- Keep the repository-only evals, tests, and validation tooling outside the installable `skills/adapt-ui-for-iphone-duo` payload.
- Keep the bundled `LICENSE.txt` and `NOTICE` byte-for-byte synchronized with the repository-level `LICENSE` and `NOTICE`.

## Publishing and discoverability

Publish the repository as `adapt-ui-for-iphone-duo`. The repository name, skill directory, `SKILL.md` name, and stable invocation then use the same verb-led identifier without introducing a separate brand.

Use this GitHub repository description:

```text
Agent Skill for Codex and compatible coding agents that adapts SwiftUI and UIKit interfaces for iPhone Duo and foldable iPhone displays.
```

Add these GitHub topics:

```text
agent-skills, codex, codex-skill, swiftui, uikit, ios, iphone,
iphone-duo, foldable-iphone, foldable, adaptive-ui, accessibility, skill-md
```

The `agent-skills` topic follows GitHub CLI's Skill publishing guidance. The other topics describe the purpose, platforms, frameworks, and format without keyword stuffing. GitHub's normal repository search considers the name, description, and topics by default; its dedicated `gh skill search` command matches only the `SKILL.md` name and description, with name matches ranked first.

GitHub CLI's current preview implementation also applies a scaled repository-star bonus after textual relevance. Treat stars as an organic adoption signal: improve usefulness, releases, and examples rather than attempting to manipulate it. The preview ranking can change.

Before the first public release:

1. Make the repository public with `main` as its default branch, then set the exact description and topics above.
2. Run `bash scripts/validate.sh`.
3. With a GitHub CLI version that includes the preview Agent Skills commands, run `gh skill publish --dry-run`.
4. Publish a semantic-version release, for example `gh skill publish --tag v0.1.0`. Unversioned `gh skill install` resolves the latest tagged release before the default branch.
5. After GitHub has indexed the default branch, check `gh skill search "iphone duo"`, `gh skill search swiftui`, and `gh skill search foldable`.
6. Check normal repository search with `iphone duo in:name,description,topics`, `topic:agent-skills swiftui`, and `"foldable iPhone" in:readme`.

Do not add an `llms.txt`, duplicate keyword file, package manifest, or unrelated topics solely for ranking. Neither Codex nor GitHub documents those as Skill selection signals.

## Make a change

1. Scope the change to the skill, references, scanner, tests, or contributor infrastructure.
2. Update or add regression coverage. Trigger changes belong in `evals/trigger-cases.json`; workflow changes belong in `evals/task-cases.json`; scanner changes require shell fixtures and assertions. The JSON evals are golden contracts for external or manual evaluation; repository validation checks their structure but does not claim to execute model selection.
3. If user-facing behavior, hardware data, commands, or toolchain status changes, update every localized README. For hardware or toolchain facts, update the review date, source map, and preview/compile-verification status together.
4. Run the complete local validation from the repository root:

   ```bash
   bash scripts/validate.sh
   ```

5. If framework advice includes a new SDK symbol, compile it with the stated Xcode build. When that SDK is unavailable, mark the signature preview-only instead of presenting it as verified.

The validator requires Bash, Python 3, and [ripgrep](https://github.com/BurntSushi/ripgrep). It also runs [ShellCheck](https://www.shellcheck.net/) when available; CI installs it and treats its findings as failures.

## Pull-request checklist

- [ ] `bash scripts/validate.sh` passes.
- [ ] New local Markdown links resolve.
- [ ] Localized READMEs retain their language navigation, commands, call identifier, dates, and hardware data.
- [ ] JSON remains valid and source-mapped where applicable.
- [ ] Positive and negative trigger boundaries remain intentional.
- [ ] `skills/adapt-ui-for-iphone-duo/SKILL.md` passes the current Agent Skills naming and directory rules.
- [ ] Scanner output does not claim that a candidate is a defect.
- [ ] Exact tests and toolchain limitations are documented.
- [ ] No Apple affiliation, endorsement, or official status is implied.

By contributing, you agree that your contribution is licensed under the repository's [MIT License](LICENSE).
