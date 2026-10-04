# AGENTS.md: fork-sync

Instructions for AI coding agents (Grok, Cursor, Claude Code, Codex, Copilot and others) working **in** this repo or **using it as a building block**. Humans: see [README.md](README.md).

## What this is

Keeps the curated Blockchains forks in line with their upstreams: forks.json lists each fork, upstream, branch and mode (merge via the merge-upstream API, or tracking for forks whose GitHub parent differs from the real upstream); nightly workflow + box-side script.

- Kind: automation, dataset, cli · stability: `stable` · licence: NOASSERTION
- Machine-readable manifest: [`blocks.json`](blocks.json) (schema: [BLOCKS-SCHEMA](https://github.com/Blockchains/.github/blob/main/docs/BLOCKS-SCHEMA.md))
- How it fits with the other Blockchains repos: [Build with Blocks](https://github.com/Blockchains/.github/blob/main/docs/BUILD-WITH-BLOCKS.md)

## Setup

```bash
gh auth status
```

## Build and test

```bash
python3 scripts/sync.py --dry-run
```

Tests hit **live** public networks/APIs (the org rule is no mocks). A failure can be an upstream outage: re-run before changing code.

## Environment

| Variable | Required | Purpose |
|---|---|---|
| `FORK_SYNC_TOKEN` | no | repo secret; PAT with repo + workflow on Blockchains |

## Structure

| Path | What |
|---|---|
| `forks.json` | fork list |
| `scripts/sync.py` | sync logic (merge-upstream / tracking force-move) |
| `.github/workflows/sync.yml` | nightly workflow |

## Conventions

- `mode: tracking` only for forks whose GitHub parent is not the real upstream (e.g. go-ethereum, chainlink, buidler→hardhat).
- No licence file yet: default copyright applies.

## Extension points

- Add a fork: append an entry with slug/fork/upstream/branches/mode/category/license.

## Do

- Run with `--dry-run` first.

## Don't

- List archived repos.
- Invent data, mock network responses in shipped code, or hard-code values that should come from the live source; every repo here is 'no mocks, real data'.
- Commit secrets, keys or `.env` files. Run `gitleaks` before pushing; CI and the org policy reject leaks.

## Using it from another project

- **forks.json** (file): `slug, fork, upstream, upstream_branch, branch, mode, tracking_branch, category, license, wave`
- **scripts/sync.py** (cli): `python3 scripts/sync.py [--dry-run] [--only a,b] [--pace SECONDS]`
- **Nightly fork sync** (github-action): `02:17 UTC + workflow_dispatch (input: only)`

See the README section [Use as a building block](README.md#use-as-a-building-block) for a copy-paste example.

## Related blocks

- [Blockchains/blockchainlab-index](https://github.com/Blockchains/blockchainlab-index): indexes the synced forks nightly, after this runs
- [Blockchains/awesome-blockchainlab](https://github.com/Blockchains/awesome-blockchainlab): list of the same forks
- [Blockchains/grokhack-index](https://github.com/Blockchains/grokhack-index): syncs its own fork list best-effort
