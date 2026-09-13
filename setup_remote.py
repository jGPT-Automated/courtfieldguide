#!/usr/bin/env python3
"""
setup_remote.py — ensure the GitHub repo and the Vercel project exist and are linked.

Safe to re-run: creation is attempted, and "already exists" is treated as success.
Prints a single JSON object describing the resulting state.

Auth: JGPT_GITHUB_TOKEN / JGPT_VERCEL_TOKEN / JGPT_VERCEL_TEAM_ID injected by the skill.
"""
from __future__ import annotations

import json
import os
import sys
from urllib import request, error

GH = "https://api.github.com"
VC = "https://api.vercel.com"

OWNER = os.environ.get("JGPT_GITHUB_OWNER") or "jGPT-Automated"
REPO = "courtfieldguide"
PROJECT = "courtfieldguide"
TEAM = os.environ.get("JGPT_VERCEL_TEAM_ID") or "team_pQChcm1syvxKXL4W5MzYDVvy"


def call(method, url, token, body=None, extra_headers=None):
    data = json.dumps(body).encode() if body is not None else None
    hdrs = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "field-guide-setup/1.0",
    }
    if extra_headers:
        hdrs.update(extra_headers)
    req = request.Request(url, data=data, method=method, headers=hdrs)
    try:
        with request.urlopen(req, timeout=45) as r:
            raw = r.read().decode() or "{}"
            return r.status, json.loads(raw)
    except error.HTTPError as e:
        raw = e.read().decode(errors="replace") or "{}"
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"raw": raw}


def gh_token():
    t = os.environ.get("JGPT_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not t:
        raise RuntimeError("JGPT_GITHUB_TOKEN not set")
    return t


def vc_token():
    t = os.environ.get("JGPT_VERCEL_TOKEN") or os.environ.get("VERCEL_TOKEN")
    if not t:
        raise RuntimeError("JGPT_VERCEL_TOKEN not set")
    return t


def ensure_repo():
    t = gh_token()
    st, body = call("GET", f"{GH}/repos/{OWNER}/{REPO}", t)
    if st == 200:
        return {"created": False, "default_branch": body.get("default_branch"), "url": body.get("html_url"),
                "full_name": body.get("full_name")}

    payload = {
        "name": REPO,
        "description": "A sourced field guide to notable public outdoor basketball courts in the United States.",
        "homepage": "",
        "private": False,
        "has_issues": True,
        "has_wiki": False,
        "auto_init": True,
        "license_template": "mit",
    }
    st, body = call("POST", f"{GH}/orgs/{OWNER}/repos", t, payload)
    if st not in (200, 201):
        # fall back to the authenticated user's namespace only if the org path is not permitted
        st2, body2 = call("POST", f"{GH}/user/repos", t, payload)
        if st2 not in (200, 201):
            return {"created": False, "error": f"org:{st} {body} | user:{st2} {body2}"}
        body = body2
    return {"created": True, "default_branch": body.get("default_branch"), "url": body.get("html_url"),
            "full_name": body.get("full_name")}


def ensure_project():
    t = vc_token()
    st, body = call("GET", f"{VC}/v9/projects/{PROJECT}?teamId={TEAM}", t)
    if st == 200:
        return {"created": False, "id": body.get("id"), "name": body.get("name"),
                "linked_repo": (((body.get("link") or {}).get("repo")) or None)}

    payload = {
        "name": PROJECT,
        "framework": None,
        "gitRepository": {"type": "github", "repo": f"{OWNER}/{REPO}"},
        "outputDirectory": "dist",
        "buildCommand": None,
        "installCommand": None,
        "publicSource": True,
    }
    st, body = call("POST", f"{VC}/v10/projects?teamId={TEAM}", t, payload)
    if st not in (200, 201):
        return {"created": False, "error": f"{st} {body}"}
    return {"created": True, "id": body.get("id"), "name": body.get("name"),
            "linked_repo": (((body.get("link") or {}).get("repo")) or None)}


def main():
    out = {"owner": OWNER, "repo": REPO, "project": PROJECT, "team": TEAM}
    try:
        out["github"] = ensure_repo()
    except Exception as e:
        out["github"] = {"error": str(e)}
    try:
        out["vercel"] = ensure_project()
    except Exception as e:
        out["vercel"] = {"error": str(e)}
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
