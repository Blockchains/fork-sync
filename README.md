# fork-sync

[![Nightly fork sync](https://github.com/Blockchains/fork-sync/actions/workflows/sync.yml/badge.svg)](https://github.com/Blockchains/fork-sync/actions/workflows/sync.yml)

Keeps the curated **Blockchains** forks in line with their upstreams. These forks feed [blockchainlab-index](https://github.com/Blockchains/blockchainlab-index), [awesome-blockchainlab](https://github.com/Blockchains/awesome-blockchainlab) and the Blockchain Lab `/forge` composer.

- [`forks.json`](forks.json) lists every fork. Each entry has the upstream, the branch and a sync mode:
  - `merge`: the fork's parent is the upstream. Sync uses `POST /repos/{fork}/merge-upstream`, the same as the "Sync fork" button.
  - `tracking`: the fork sits in the upstream's network but was forked from a different parent, for example `Blockchains/go-ethereum`, whose parent is `2key/go-ethereum`. Sync force-moves the tracking branch (e.g. `upstream-master`) to the upstream head and leaves the fork's own default branch alone.
- [`scripts/sync.py`](scripts/sync.py) does the work. It needs only Python 3 and the `gh` CLI.

```bash
python3 scripts/sync.py --dry-run          # read-only: which forks are behind
python3 scripts/sync.py                    # sync all (needs a token with repo + workflow scope on Blockchains)
python3 scripts/sync.py --only viem,wagmi  # subset
```

## Schedule
`.github/workflows/sync.yml` runs nightly at 02:17 UTC and on demand (**Actions → Nightly fork sync → Run workflow**).

- If the repository secret **`FORK_SYNC_TOKEN`** is set, the workflow syncs for real. Use a fine-grained PAT, or a classic one with `repo` + `workflow`, for an account that can push to the Blockchains forks. `workflow` scope is needed because upstream commits often touch `.github/workflows`.
- Without the secret, it runs a **read-only drift check** using the default `GITHUB_TOKEN`, which can't write to other repositories. Real syncs then come from the box-side routine (`python3 scripts/sync.py` with a logged-in `gh`).

Each run writes `reports/last-sync.json`, which is uploaded as the `sync-report` artifact, plus a table in the job summary.

<!-- blocks:start -->
## Use as a building block

> **For AI agents and builders:** read [`AGENTS.md`](AGENTS.md) (setup, commands, structure, rules), [`llms.txt`](llms.txt) (doc map) and the machine-readable [`blocks.json`](blocks.json) ([schema](https://github.com/Blockchains/.github/blob/main/docs/BLOCKS-SCHEMA.md)). How all Blockchains blocks fit together: **[Build with Blocks](https://github.com/Blockchains/.github/blob/main/docs/BUILD-WITH-BLOCKS.md)** · org catalogue: [https://blockchains.github.io/blocks.json](https://blockchains.github.io/blocks.json).

**What it exports**

| Export | Type | Install / access |
|---|---|---|
| `forks.json` | file | `slug, fork, upstream, upstream_branch, branch, mode, tracking_branch, category, license, wave` |
| `scripts/sync.py` | cli | `python3 scripts/sync.py [--dry-run] [--only a,b] [--pace SECONDS]` |
| `Nightly fork sync` | github-action | `02:17 UTC + workflow_dispatch (input: only)` |

**Minimal example**

```bash
git clone https://github.com/Blockchains/fork-sync && cd fork-sync
python3 scripts/sync.py --dry-run                    # read-only: which forks are behind
jq -r '.[] | select(.category=="oracles") | .fork' forks.json
```

**Inputs → outputs**

- In: `forks.json` (JSON); `FORK_SYNC_TOKEN` (secret) enables real syncs in Actions; otherwise read-only drift check
- Out: `reports/last-sync.json` (JSON artifact) per-fork result; `synced forks` (GitHub)

**Composes with**

- [Blockchains/blockchainlab-index](https://github.com/Blockchains/blockchainlab-index): indexes the synced forks nightly, after this runs
- [Blockchains/awesome-blockchainlab](https://github.com/Blockchains/awesome-blockchainlab): list of the same forks
- [Blockchains/grokhack-index](https://github.com/Blockchains/grokhack-index): syncs its own fork list best-effort

**Versioning & stability:** `stable`. forks.json entries are additive; archived forks must be removed (merge-upstream fails on archived repos).
<!-- blocks:end -->

## Licence

No licence file has been added yet, so default copyright applies (all rights reserved). Each fork keeps its upstream licence.

## Contributing

Issues and pull requests are welcome. Please read the [contributing guide](https://github.com/Blockchains/.github/blob/main/CONTRIBUTING.md), [code of conduct](https://github.com/Blockchains/.github/blob/main/CODE_OF_CONDUCT.md) and [security policy](https://github.com/Blockchains/.github/blob/main/SECURITY.md) first.

---
Built by Blockchain Lab — [blockchainlab.com](https://blockchainlab.com/?utm_source=github&utm_medium=readme&utm_campaign=fork-sync)
