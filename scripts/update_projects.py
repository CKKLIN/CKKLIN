#!/usr/bin/env python3
"""Automatically refresh the Projects showcase section of README.md
from the list of CKKLIN's public, non-fork repositories.
"""
import json
import os
import re
import urllib.request

USER = "CKKLIN"
TOKEN = os.environ.get("GITHUB_TOKEN", "")


def api(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "codex-project-updater",
        "Accept": "application/vnd.github+json",
    })
    if TOKEN:
        req.add_header("Authorization", "token " + TOKEN)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def public_repos():
    repos = []
    page = 1
    while True:
        data = api(
            "https://api.github.com/users/%s/repos?per_page=100&page=%d&sort=updated"
            % (USER, page)
        )
        if not data:
            break
        for repo in data:
            if not repo.get("fork") and not repo.get("private"):
                repos.append(repo["name"])
        if len(data) < 100:
            break
        page += 1
    # newest first (API is already sorted by updated desc; keep that order)
    return repos[:8]


def build_section(names):
    cards = []
    for name in names:
        cards.append(
            '<a href="https://github.com/%s/%s" target="_blank">\n'
            '    <img src="https://github-readme-stats.vercel.app/api/pin/?username=%s&theme=dark&repo=%s" width="49%%" alt=""/>\n'
            "  </a>" % (USER, name, USER, name)
        )
    return (
        "<div align=\"center\">\n"
        "   <h2 align=\"center\"><strong> \U0001F636\u200d\U0001F32B\uFE0F 项目展示 | Projects \U0001F636\u200d\U0001F32B\uFE0F </strong></h2><br>\n"
        "   " + "\n   ".join(cards) + "\n"
        "</div>"
    )


def main():
    start = "<!-- PROJECTS:START -->"
    end = "<!-- PROJECTS:END -->"
    with open("README.md", encoding="utf-8") as f:
        content = f.read()
    if start not in content or end not in content:
        print("Markers not found in README.md; nothing to do.")
        return
    names = public_repos()
    section = start + "\n" + build_section(names) + "\n" + end
    pattern = re.escape(start) + r".*?" + re.escape(end)
    new_content = re.sub(pattern, section, content, flags=re.S)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Updated project showcase with %d repo(s): %s" % (len(names), ", ".join(names)))


if __name__ == "__main__":
    main()