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
