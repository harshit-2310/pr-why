"""Command line interface for pr-why."""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def load_diff(args):
    if args.diff:
        return Path(args.diff).read_text(encoding="utf-8")
    if args.pr:
        repo, number = args.pr.split("#", 1)
        if not repo or not number.isdigit():
            raise ValueError("PR must use owner/repo#number format")
        req = Request(f"https://api.github.com/repos/{repo}/pulls/{number}", headers={"Accept": "application/vnd.github+json", "User-Agent": "pr-why"})
        with urlopen(req, timeout=30) as response:
            data = json.load(response)
        diff_url = data["diff_url"]
        with urlopen(Request(diff_url, headers={"User-Agent": "pr-why"}), timeout=30) as response:
            return response.read().decode("utf-8", errors="replace")
    return sys.stdin.read()


def explain(diff, args):
    if not diff.strip():
        raise ValueError("No diff provided. Use --diff FILE, --pr owner/repo#number, or stdin.")
    if args.api_key:
        endpoint = args.base_url.rstrip("/") + "/chat/completions"
        payload = {"model": args.model, "messages": [{"role": "system", "content": "Explain a pull request diff clearly and accurately. Separate what changed, why it matters, and risks. Do not claim intent not evidenced by the diff."}, {"role": "user", "content": diff[:args.max_chars]}], "temperature": 0.2}
        request = Request(endpoint, data=json.dumps(payload).encode(), headers={"Authorization": f"Bearer {args.api_key}", "Content-Type": "application/json", "User-Agent": "pr-why"})
        with urlopen(request, timeout=90) as response:
            result = json.load(response)
        return result["choices"][0]["message"]["content"].strip()
    files = []
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            files.append(line[6:])
    additions = sum(1 for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++"))
    deletions = sum(1 for line in diff.splitlines() if line.startswith("-") and not line.startswith("---"))
    summary = ["## Pull request change summary", "", f"This change touches {len(set(files))} file(s), with {additions} addition(s) and {deletions} deletion(s).", "", "### Files changed"]
    summary.extend(f"- `{name}`" for name in dict.fromkeys(files))
    summary += ["", "### Review note", "This is a structural summary only. Set an OpenAI-compatible API key with `--api-key` (or `OPENAI_API_KEY`) for a model-generated explanation."]
    return "\n".join(summary)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pr-why", description="Explain a pull request diff using any OpenAI-compatible model API.")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--diff", metavar="FILE", help="read a unified diff from a local file")
    source.add_argument("--pr", metavar="OWNER/REPO#NUMBER", help="fetch a public GitHub pull request diff")
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY"), help="model API key (or set OPENAI_API_KEY)")
    parser.add_argument("--base-url", default=os.getenv("PR_WHY_BASE_URL", "https://api.openai.com/v1"), help="OpenAI-compatible API base URL")
    parser.add_argument("--model", default=os.getenv("PR_WHY_MODEL", "gpt-4o-mini"), help="model identifier")
    parser.add_argument("--max-chars", type=int, default=60000, help="maximum diff characters sent to the model")
    parser.add_argument("--output", metavar="FILE", help="write report to a file")
    args = parser.parse_args(argv)
    try:
        result = explain(load_diff(args), args)
        if args.output:
            Path(args.output).write_text(result + "\n", encoding="utf-8")
            print(f"Report written to {args.output}")
        else:
            print(result)
        return 0
    except (ValueError, OSError, HTTPError, URLError, KeyError, json.JSONDecodeError) as exc:
        print(f"pr-why: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
