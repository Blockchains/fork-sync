#!/usr/bin/env python3
"""Sync every curated Blockchains fork with its upstream.
  python3 scripts/sync.py [--dry-run] [--only slug1,slug2] [--pace SECONDS]
Uses the `gh` CLI (GH_TOKEN env in Actions, or a logged-in gh on a workstation).
modes: merge    -> POST /repos/{fork}/merge-upstream (fork's parent == upstream)
       tracking -> force-move refs/heads/<tracking_branch> to upstream HEAD (fork inside the same network but parented elsewhere)
--dry-run only reads (works with the default Actions GITHUB_TOKEN): reports which forks are behind."""
import json, subprocess, sys, time, os, datetime
def gh(path, method="GET", fields=None):
    cmd = ["gh", "api", "-X", method, path]
    for k, v in (fields or {}).items():
        cmd += (["-F", f"{k}={'true' if v else 'false'}"] if isinstance(v, bool) else ["-f", f"{k}={v}"])
    p = subprocess.run(cmd, capture_output=True, text=True)
    try: data = json.loads(p.stdout) if p.stdout.strip() else {}
    except Exception: data = {"raw": p.stdout[:200]}
    return p.returncode, data, p.stderr.strip()[:200]
def head(repo, branch):
    rc, d, _ = gh(f"repos/{repo}/commits/{branch}")
    return d.get("sha") if rc == 0 else None
def main():
    dry = "--dry-run" in sys.argv
    only = set(sys.argv[sys.argv.index("--only") + 1].split(",")) if "--only" in sys.argv else None
    pace = float(sys.argv[sys.argv.index("--pace") + 1]) if "--pace" in sys.argv else 1.0
    forks = json.load(open(os.path.join(os.path.dirname(__file__), "..", "forks.json")))
    res = []
    for f in forks:
        if only and f["slug"] not in only: continue
        up_sha = head(f["upstream"], f["upstream_branch"])
        fb = f.get("tracking_branch") or f["branch"]
        fork_sha = head(f["fork"], fb)
        r = {"slug": f["slug"], "fork": f["fork"], "branch": fb, "upstream": f["upstream"], "upstream_sha": up_sha, "fork_sha_before": fork_sha}
        if not up_sha or not fork_sha:
            r["result"] = "error-reading-heads"
        elif up_sha == fork_sha:
            r["result"] = "up-to-date"
        elif dry:
            r["result"] = "behind (dry-run)"
        elif f["mode"] == "merge":
            rc, d, err = gh(f"repos/{f['fork']}/merge-upstream", "POST", {"branch": fb})
            r["result"] = f"merged:{d.get('merge_type')}" if rc == 0 else f"merge-failed:{d.get('message') or err}"
        else:
            rc, d, err = gh(f"repos/{f['fork']}/git/refs/heads/{fb}", "PATCH", {"sha": up_sha, "force": True})
            if rc != 0:
                rc, d, err = gh(f"repos/{f['fork']}/git/refs", "POST", {"ref": f"refs/heads/{fb}", "sha": up_sha})
            r["result"] = "tracking-updated" if rc == 0 else f"tracking-failed:{d.get('message') or err}"
        res.append(r); print(f"{r['slug']:40s} {r['result']}", flush=True)
        if not dry and r["result"] not in ("up-to-date",): time.sleep(pace)
    summary = {"at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "dry_run": dry, "total": len(res),
               "counts": {k: sum(1 for x in res if x["result"].split(":")[0] == k) for k in sorted(set(x["result"].split(":")[0] for x in res))}, "results": res}
    os.makedirs("reports", exist_ok=True)
    json.dump(summary, open("reports/last-sync.json", "w"), indent=1)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as s:
            s.write(f"## Fork sync ({'dry-run' if dry else 'write'})\n\n" + "\n".join(f"- **{k}**: {v}" for k, v in summary["counts"].items()) + "\n\n| fork | branch | result |\n|---|---|---|\n")
            s.write("\n".join(f"| [{x['fork']}](https://github.com/{x['fork']}) | {x['branch']} | {x['result']} |" for x in res) + "\n")
    print(json.dumps(summary["counts"]))
    failed = [x for x in res if "failed" in x["result"] or x["result"].startswith("error")]
    sys.exit(1 if failed and len(failed) > len(res) // 2 else 0)
if __name__ == "__main__": main()
