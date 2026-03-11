# Repository Guidelines

## Project Structure & Module Organization
`qfc-design` is a documentation repository for QFC architecture, roadmap, and product design. Top-level numbered Markdown files such as `00-PROJECT-OVERVIEW.md`, `01-BLOCKCHAIN-DESIGN.md`, and `07-WALLET-DESIGN.md` hold the main design specs. `START-HERE.md` is the onboarding entry point, `README.md` indexes the document set, `CLAUDE.md` contains agent-facing notes, and `logo/` stores brand assets. Keep new design docs at the repository root unless they are clearly asset files.

## Build, Test, and Development Commands
This repo does not have an application build. The main workflow is editing and reviewing Markdown.

- `cd qfc-design && git status` checks pending doc changes.
- `cd qfc-design && rg '^#' *.md` quickly audits heading structure.
- `cd qfc-design && markdownlint *.md` is recommended if you have `markdownlint` installed locally.

When changing a document set, update both `README.md` and `START-HERE.md` if navigation or reading order changes.

## Writing Style & Naming Conventions
Prefer concise, implementation-oriented Markdown with clear section hierarchies. Use ATX headings (`#`, `##`, `###`), fenced code blocks with language tags, and short bullet lists for requirements or phases. Keep filenames numbered when they are part of the canonical reading sequence: `NN-TOPIC-NAME.md`. Use uppercase hyphenated filenames to match the existing set. Preserve existing bilingual content where present instead of rewriting languages for consistency alone.

## Review Guidelines
Treat document changes like specification changes. Verify terminology matches related docs, especially when editing consensus, wallet, explorer, or roadmap material. Cross-check references before renaming sections or files, and keep examples aligned with the current repo names such as `qfc-core`, `qfc-wallet`, and `qfc-explorer`.

## Commit & Pull Request Guidelines
Recent history uses Conventional Commit prefixes, mostly `docs:` for documentation updates. Keep commit subjects short and scoped, for example `docs: update wallet roadmap milestones`. PRs should explain which design areas changed, call out downstream implementation impact, and note any files that must be updated together. Include screenshots only when changing visual assets under `logo/`.
