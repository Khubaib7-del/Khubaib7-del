#!/usr/bin/env python3
"""Build every generated asset for the profile README and the dashboard page.

Writes static SVGs to assets/cards/ (light, no third-party services, one-shot
entrance animations that settle within ~2s so scrolling stays smooth) and
docs/data.json, which docs/index.html turns into the interactive dashboard
(hover a week to see the repos and pull requests behind it).

Data comes from the public GitHub REST API (a token, when present, only lifts
rate limits) and the contribution calendar (GraphQL with a token, otherwise the
public contributions page).
"""
from __future__ import annotations

import base64
import datetime as dt
import html
import json
import math
import os
import re
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

USER = os.environ.get("PROFILE_USER", "Khubaib7-del")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "assets" / "cards"
ICONS = ROOT / "assets" / "icons"
DOCS = ROOT / "docs"

# Palette: cool graphite with bright, high-contrast accents.
BG, PANEL, LINE = "#0d0f17", "#141724", "#2a2f47"
INK, MUTED, FAINT = "#f5f6fb", "#a9aecb", "#6b7194"
SKY, VIOLET, MINT, PINK = "#38bdf8", "#a78bfa", "#34d399", "#f472b6"
FONT = "'Inter','Segoe UI',Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono','SFMono-Regular',Consolas,'Liberation Mono',monospace"

SKIP_LANGS = {"Jupyter Notebook", "Makefile", "CMake", "Batchfile", "PowerShell", "Dockerfile",
              "Shell", "Procfile", "HTML", "CSS", "SCSS", "TeX", "Roff", "Smarty", "Nix"}
LANG_COLORS = {"Rust": SKY, "TypeScript": VIOLET, "JavaScript": "#facc15", "Python": MINT,
               "Kotlin": PINK, "Assembly": "#e2e8f0", "C++": "#fb7185", "C": "#94a3b8",
               "PLpgSQL": "#5eead4", "Other": "#475069"}

STYLE = ("<style>"
         "@keyframes up{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}"
         "@keyframes fade{from{opacity:0}to{opacity:1}}"
         "@keyframes draw{to{stroke-dashoffset:0}}"
         "@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
         ".a{animation:up .7s cubic-bezier(.2,.8,.2,1) both}"
         ".f{animation:fade .9s ease both}"
         ".d{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.8s cubic-bezier(.4,0,.2,1) .2s forwards}"
         "@media (prefers-reduced-motion:reduce){*{animation:none!important;stroke-dashoffset:0!important}}"
         "</style>")


# ───────────────────────── data ─────────────────────────
def _get(url: str, data: bytes | None = None):
    req = urllib.request.Request(url, data=data, headers={
        "User-Agent": "profile-builder", "Accept": "application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=40) as r:
        body = r.read()
    return json.loads(body) if body[:1] in (b"{", b"[") else body.decode()


def _search(q: str, pages: int = 1) -> tuple[int, list]:
    items, total = [], 0
    for p in range(1, pages + 1):
        d = _get(f"https://api.github.com/search/issues?q={urllib.parse.quote(q)}&per_page=100&page={p}")
        total = d.get("total_count", 0)
        items += d.get("items", [])
        if len(items) >= total:
            break
    return total, items


def calendar() -> list[tuple[str, int]]:
    if TOKEN:
        q = {"query": "query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{"
                      "weeks{contributionDays{date contributionCount}}}}}}", "variables": {"u": USER}}
        try:
            d = _get("https://api.github.com/graphql", json.dumps(q).encode())
            weeks = d["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
            return [(x["date"], x["contributionCount"]) for w in weeks for x in w["contributionDays"]]
        except Exception as e:
            print("graphql calendar failed, scraping:", e)
    page = _get(f"https://github.com/users/{USER}/contributions")
    ids = {cid: date for date, cid in re.findall(r'data-date="([\d-]+)" id="([^"]+)"', page)}
    days = []
    for cid, text in re.findall(r'for="([^"]+)"[^>]*>([^<]*)</tool-tip>', page):
        if cid in ids:
            m = re.match(r"(\d[\d,]*) contribution", text)
            days.append((ids[cid], int(m.group(1).replace(",", "")) if m else 0))
    return sorted(days)


def gather() -> dict:
    days = calendar()
    since = days[0][0]
    repos = [r for r in _get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
             if not r["fork"] and not r["archived"]]
    lang_bytes: Counter = Counter()
    commits: list[dict] = []
    for r in repos:
        if r["name"].lower() != USER.lower():
            for k, v in _get(r["languages_url"]).items():
                if k not in SKIP_LANGS:
                    lang_bytes[k] += v
        for p in range(1, 11):
            try:
                batch = _get(f"https://api.github.com/repos/{USER}/{r['name']}/commits"
                             f"?author={USER}&since={since}T00:00:00Z&per_page=100&page={p}")
            except Exception:
                break
            if not isinstance(batch, list) or not batch:
                break
            commits += [{"repo": r["name"], "date": c["commit"]["author"]["date"][:10]} for c in batch]
            if len(batch) < 100:
                break
    pr_total, prs = _search(f"author:{USER} type:pr created:>={since}", pages=3)
    issues, _ = _search(f"author:{USER} type:issue")
    reviewed, _ = _search(f"reviewed-by:{USER} type:pr -author:{USER}")
    pr_list = [{"title": i["title"], "repo": i["repository_url"].rsplit("/", 1)[-1], "url": i["html_url"],
                "date": i["created_at"][:10], "merged": bool((i.get("pull_request") or {}).get("merged_at"))}
               for i in prs]
    return {"user": USER, "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes"),
            "days": days, "repos": [{"name": r["name"], "stars": r["stargazers_count"], "lang": r["language"],
                                    "url": r["html_url"]} for r in repos],
            "languages": dict(lang_bytes.most_common()), "commits": commits, "prs": pr_list,
            "pr_total": pr_total, "issues": issues, "reviewed": reviewed}


def derive(d: dict) -> dict:
    days = [(dt.date.fromisoformat(a), c) for a, c in d["days"]]
    longest = run = 0
    for _, c in days:
        run = run + 1 if c else 0
        longest = max(longest, run)
    seq = days[:-1] if days and days[-1][1] == 0 else days
    cur = 0
    for _, c in reversed(seq):
        if not c:
            break
        cur += 1
    weeks = []
    index = {day: i // 7 for i, (day, _) in enumerate(days)}
    for i in range(0, len(days), 7):
        chunk = days[i:i + 7]
        weeks.append({"start": chunk[0][0].isoformat(), "total": sum(c for _, c in chunk),
                      "commits": Counter(), "prs": []})
    for c in d["commits"]:
        w = index.get(dt.date.fromisoformat(c["date"]))
        if w is not None:
            weeks[w]["commits"][c["repo"]] += 1
    for p in d["prs"]:
        w = index.get(dt.date.fromisoformat(p["date"]))
        if w is not None:
            weeks[w]["prs"].append(p)
    for w in weeks:
        w["commits"] = dict(w["commits"].most_common())
    best = max(days, key=lambda x: x[1]) if days else (dt.date.today(), 0)
    weekday = [0] * 7
    for day, c in days:
        weekday[(day.weekday() + 1) % 7] += c  # Sun..Sat
    merged = sum(1 for p in d["prs"] if p["merged"])
    return {"total": sum(c for _, c in days), "active": sum(1 for _, c in days if c), "span": len(days),
            "current": cur, "longest": longest, "best_day": [best[0].isoformat(), best[1]],
            "weeks": weeks, "weekday": weekday, "commit_total": len(d["commits"]),
            "repos_committed": len({c["repo"] for c in d["commits"]}), "merged": merged,
            "pr_count": len(d["prs"])}


# ───────────────────────── svg helpers ─────────────────────────
def esc(s) -> str:
    return html.escape(str(s))


def frame(w: int, h: int, body: str, title: str, panel: bool = True) -> str:
    bg = (f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="16" fill="{BG}" stroke="{LINE}"/>'
          if panel else "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(title)}"><title>{esc(title)}</title>{STYLE}{bg}{body}</svg>\n')


def text(x, y, s, size=13, fill=INK, weight=500, anchor="start", font=FONT, ls=0, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-family="{font}" font-size="{size}" '
            f'font-weight="{weight}" letter-spacing="{ls}" text-anchor="{anchor}" {extra}>{esc(s)}</text>')


def eyebrow(x, y, s, fill=MUTED):
    return text(x, y, s.upper(), 11, fill, 700, font=MONO, ls=1.6)


def delay(sec: float) -> str:
    return f'style="animation-delay:{sec:.2f}s"'


def icon_uri(name: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode((ICONS / f"{name}.svg").read_bytes()).decode()


def short(n: int) -> str:
    return f"{n/1000:.1f}k" if n >= 10000 else f"{n:,}"


def human_bytes(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


# ───────────────────────── cards ─────────────────────────
def header() -> str:
    w, h = 840, 150
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="1" fill="{FAINT}" opacity=".35"/>'
                   for x in range(560, 830, 18) for y in range(18, 140, 18))
    tag = "Software developer · learning AI engineering"
    body = (dots
            + f'<g class="a">{text(44, 78, "Khubaib Nazeer", 52, INK, 800, ls=-1.5)}</g>'
            + f'<clipPath id="t"><rect x="44" y="94" width="560" height="30" '
              f'style="transform-origin:44px 0;animation:grow 1.4s steps({len(tag)}) .5s both"/></clipPath>'
            + f'<g clip-path="url(#t)">{text(46, 116, tag, 20, MUTED, 500, font=MONO)}</g>'
            + f'<rect x="{46 + len(tag) * 12.05:.0f}" y="99" width="10" height="21" fill="{SKY}" class="f" {delay(1.9)}/>')
    return frame(w, h, body, "Khubaib Nazeer — software developer, learning AI engineering")


SOCIAL = {
    "portfolio": '<circle cx="26" cy="26" r="9" fill="none" stroke="#f5f6fb" stroke-width="1.8"/><path d="M17 26h18M26 17c3 3 3 15 0 18M26 17c-3 3-3 15 0 18" fill="none" stroke="#f5f6fb" stroke-width="1.8"/>',
    "linkedin": '<path fill="#f5f6fb" d="M18.5 22h3.4v11h-3.4zM20.2 16.6a2 2 0 1 1 0 4 2 2 0 0 1 0-4zM24.2 22h3.3v1.5h.05c.46-.87 1.58-1.8 3.26-1.8 3.49 0 4.13 2.3 4.13 5.28V33h-3.4v-5.4c0-1.29-.03-2.95-1.8-2.95-1.8 0-2.07 1.4-2.07 2.86V33h-3.4z"/>',
    "email": '<rect x="16" y="19" width="20" height="14" rx="2.5" fill="none" stroke="#f5f6fb" stroke-width="1.8"/><path d="M17 20.5l9 6.5 9-6.5" fill="none" stroke="#f5f6fb" stroke-width="1.8" stroke-linejoin="round"/>',
    "x": '<path fill="#f5f6fb" d="M29.6 17h3.1l-6.8 7.8 8 10.2h-6.3l-4.9-6.4-5.6 6.4H14l7.3-8.3L13.7 17h6.4l4.4 5.9zm-1.1 16.2h1.7L19.2 18.7h-1.8z"/>',
}


def social(name: str) -> str:
    body = (f'<circle cx="26" cy="26" r="25" fill="{PANEL}" stroke="{LINE}" stroke-width="1.2"/>' + SOCIAL[name])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="52" height="52" viewBox="0 0 52 52" role="img" '
            f'aria-label="{name}"><title>{name}</title>{body}</svg>\n')


TOOLKIT = [
    ("Languages", ["c", "cpp", "py", "js", "ts", "rust", "assembly"]),
    ("Frontend", ["html", "css", "tailwind", "bootstrap", "react"]),
    ("Backend & data", ["nodejs", "express", "postgres", "mongodb", "mongoose", "mongodb-atlas"]),
    ("Tools", ["git", "github", "vscode", "pycharm", "postman"]),
    ("AI agents", ["claude-code", "codex", "hark-pro"]),
]


def toolkit() -> str:
    w, size, gap, row_h = 840, 46, 12, 70
    h = 40 + row_h * len(TOOLKIT) + 10
    body, k = "", 0
    for r, (label, icons) in enumerate(TOOLKIT):
        y = 34 + r * row_h
        hl = label == "AI agents"
        if r:
            body += f'<line x1="32" y1="{y - 12}" x2="{w - 32}" y2="{y - 12}" stroke="{LINE}" stroke-dasharray="2 6"/>'
        body += f'<g class="f" {delay(r * .12)}>{eyebrow(36, y + 28, label, SKY if hl else MUTED)}</g>'
        for i, name in enumerate(icons):
            x = 230 + i * (size + gap)
            body += (f'<g class="a" {delay(.15 + k * .045)}><image x="{x}" y="{y}" width="{size}" height="{size}" '
                     f'href="{icon_uri(name)}"/></g>')
            k += 1
        if hl:
            body += f'<g class="f" {delay(1.2)}>{text(230 + len(icons) * (size + gap) + 10, y + 28, "Claude Code · Codex · Hark Pro", 13, MUTED, 500)}</g>'
    return frame(w, h, body, "Toolkit")


PROJECTS = [
    ("GitAtlas", "Any GitHub repo as a walkable 3D world: city mode, dependency graphs, commit constellations.",
     ["React", "Three.js", "TypeScript"], SKY, "gitatlas"),
    ("Thruline", "Shared memory, decision log and review queue for AI coding agents, in one Rust binary.",
     ["Rust", "TypeScript", "MCP"], VIOLET, "thruline"),
    ("Selvard", "Privacy-first Android security shield. Link, permission and DNS checks run on the device.",
     ["Kotlin", "Android", "Local-first"], MINT, "selvard"),
    ("CogniVision", "Live classroom attention and cheating-behaviour detection. 90.1% validation accuracy.",
     ["PyTorch", "YOLOv8", "FastAPI"], PINK, "cognivision"),
    ("Bite Balance", "Full-stack meal planner with nutrition tracking, JWT auth and a PostgreSQL API.",
     ["React", "Node", "PostgreSQL"], "#facc15", "bite-balance"),
    ("POP Rush", "Balloon-popping arcade game written entirely in x86 Assembly, with three game modes.",
     ["x86 Assembly", "DOS", "Game"], "#e2e8f0", "pop-rush"),
]


def wrap(s: str, n: int) -> list[str]:
    out, line = [], ""
    for word in s.split():
        if len(line) + len(word) + 1 > n:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return out + [line]


def project(i: int) -> str:
    name, desc, stack, color, _ = PROJECTS[i]
    w, h = 410, 176
    body = (f'<rect x="14" y="22" width="3" height="{h - 44}" rx="1.5" fill="{color}"/>'
            + f'<g class="a" {delay(i * .08)}>'
            + text(26, 42, name, 22, INK, 750, ls=-.4)
            + text(w - 26, 40, "↗", 18, color, 600, "end")
            + "".join(text(26, 72 + j * 20, ln, 13.5, MUTED, 450) for j, ln in enumerate(wrap(desc, 50)[:3])))
    x = 26
    for s in stack:
        cw = 16 + len(s) * 7.2
        body += (f'<rect x="{x}" y="{h - 44}" width="{cw:.0f}" height="24" rx="12" fill="{PANEL}" stroke="{LINE}"/>'
                 + text(x + cw / 2, h - 28, s, 11.5, INK, 600, "middle", MONO))
        x += cw + 8
    body += "</g>"
    return frame(w, h, body, name)


def ring(cx, cy, r, frac, color, label, value, sub, k):
    c = 2 * math.pi * r
    frac = max(0.0, min(1.0, frac))
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LINE}" stroke-width="9"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="9" stroke-linecap="round" '
            f'pathLength="1" stroke-dasharray="{frac:.4f} 1" stroke-dashoffset="{frac:.4f}" '
            f'transform="rotate(-90 {cx} {cy})" style="animation:draw 1.4s cubic-bezier(.4,0,.2,1) {0.2 + k * .15:.2f}s forwards"/>'
            + text(cx, cy + 7, value, 22, INK, 800, "middle")
            + text(cx, cy + r + 30, label, 11, MUTED, 700, "middle", MONO, 1.2)
            + text(cx, cy + r + 47, sub, 11.5, FAINT, 500, "middle"))


def overview(d: dict, x: dict) -> str:
    w, h = 840, 250
    body = eyebrow(32, 38, "Last 12 months")
    merge = x["merged"] / x["pr_count"] if x["pr_count"] else 0
    body += ring(92, 118, 44, x["active"] / max(1, x["span"]), SKY, "ACTIVE DAYS", f"{x['active']}", f"of {x['span']}", 0)
    body += ring(222, 118, 44, x["current"] / max(1, x["longest"]), VIOLET, "STREAK", f"{x['current']}d", f"best {x['longest']}d", 1)
    body += ring(352, 118, 44, merge, MINT, "PRS MERGED", f"{round(merge * 100)}%", f"{x['merged']} of {x['pr_count']}", 2)
    tiles = [("Contributions", short(x["total"]), SKY), ("Commits", short(x["commit_total"]), INK),
             ("Pull requests", short(d["pr_total"]), INK), ("Repos committed to", str(x["repos_committed"]), INK),
             ("Issues opened", str(d["issues"]), INK), ("Best day", f"{x['best_day'][1]}", INK)]
    for i, (k, v, col) in enumerate(tiles):
        tx, ty = 448 + (i % 2) * 190, 58 + (i // 2) * 62
        body += (f'<g class="a" {delay(.1 + i * .07)}><rect x="{tx}" y="{ty}" width="176" height="52" rx="10" '
                 f'fill="{PANEL}" stroke="{LINE}"/>' + text(tx + 14, ty + 21, k, 11.5, MUTED, 600)
                 + text(tx + 14, ty + 42, v, 19, col, 800) + "</g>")
    body += f'<line x1="424" y1="56" x2="424" y2="{h - 26}" stroke="{LINE}"/>'
    return frame(w, h, body, "GitHub overview")


def iso_calendar(d: dict, x: dict) -> str:
    w, h = 840, 380
    days = d["days"]
    peak = max([c for _, c in days] + [1])
    ramp = ["#1f2438", "#1e3a8a", "#2563eb", "#38bdf8", "#a5f3fc"]

    def level(c):
        if c == 0:
            return 0
        f = c / peak
        return 1 if f < .1 else 2 if f < .3 else 3 if f < .6 else 4

    def shade(hexc, k):
        r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
        return f"#{int(r * k):02x}{int(g * k):02x}{int(b * k):02x}"

    s, cos, sin = 8.4, math.cos(math.pi / 6), math.sin(math.pi / 6)
    ox, oy = 40, 96
    cells = []
    for i, (_, c) in enumerate(days):
        col, row = i // 7, i % 7
        cells.append((col + row, col, row, c))
    body = eyebrow(32, 38, "Contribution calendar · 3D")
    groups = defaultdict(str)
    for _, col, row, c in sorted(cells):
        # weeks run down-right, weekdays run down-left
        bx = ox + col * s * cos - row * s * cos + 7 * s * cos
        by = oy + col * s * sin + row * s * sin
        hgt = 2 + (math.sqrt(c / peak) * 58 if c else 0)
        top = ramp[level(c)]
        pts_top = [(bx, by - hgt), (bx + s * cos, by - hgt + s * sin), (bx, by - hgt + 2 * s * sin), (bx - s * cos, by - hgt + s * sin)]
        left = [(bx - s * cos, by - hgt + s * sin), (bx, by - hgt + 2 * s * sin), (bx, by + 2 * s * sin), (bx - s * cos, by + s * sin)]
        right = [(bx + s * cos, by - hgt + s * sin), (bx, by - hgt + 2 * s * sin), (bx, by + 2 * s * sin), (bx + s * cos, by + s * sin)]
        poly = lambda p, f: f'<polygon points="{" ".join(f"{a:.0f},{b:.0f}" for a, b in p)}" fill="{f}"/>'
        groups[col] += poly(left, shade(top, .55)) + poly(right, shade(top, .75)) + poly(pts_top, top)
    for col in sorted(groups):
        body += f'<g class="a" {delay(.1 + col * .018)}>{groups[col]}</g>'
    stats = [("Current streak", f"{x['current']} days"), ("Longest streak", f"{x['longest']} days"),
             ("Best day", f"{x['best_day'][1]} on {dt.date.fromisoformat(x['best_day'][0]).strftime('%b %-d')}"),
             ("Average per active day", f"{x['total'] / max(1, x['active']):.1f}")]
    for i, (k, v) in enumerate(stats):
        y = 92 + i * 56
        body += (f'<g class="a" {delay(.6 + i * .08)}>' + text(620, y, k, 12, MUTED, 600)
                 + text(620, y + 24, v, 20, INK, 800) + "</g>")
    lx = 620
    body += text(lx, 336, "less", 10.5, FAINT, 500, font=MONO)
    for i, c in enumerate(ramp):
        body += f'<rect x="{lx + 36 + i * 16}" y="326" width="12" height="12" rx="2" fill="{c}"/>'
    body += text(lx + 36 + 5 * 16 + 6, 336, "more", 10.5, FAINT, 500, font=MONO)
    return frame(w, h, body, "3D contribution calendar")


def languages(d: dict) -> str:
    w, h = 840, 290
    items = list(d["languages"].items())
    total = sum(v for _, v in items) or 1
    top = items[:7]
    rest = sum(v for _, v in items[7:])
    if rest:
        top.append(("Other", rest))
    cx, cy, r = 150, 152, 80
    body = eyebrow(32, 38, "Languages · by code size")
    start = 0.0
    for i, (name, v) in enumerate(top):
        frac = v / total
        gapf = 0.006 if len(top) > 1 else 0
        seg = max(0.001, frac - gapf)
        body += (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LANG_COLORS.get(name, "#64748b")}" '
                 f'stroke-width="26" pathLength="1" stroke-dasharray="{seg:.4f} 1" stroke-dashoffset="{-start:.4f}" '
                 f'transform="rotate(-90 {cx} {cy})" class="f" {delay(.1 + i * .12)}/>')
        start += frac
    lead = top[0]
    body += text(cx, cy - 4, f"{lead[1] / total * 100:.0f}%", 30, INK, 800, "middle")
    body += text(cx, cy + 20, lead[0], 13, MUTED, 600, "middle")
    for i, (name, v) in enumerate(top):
        col, rowi = i // 4, i % 4
        lx, ly = 300 + col * 270, 84 + rowi * 44
        frac = v / total
        color = LANG_COLORS.get(name, "#64748b")
        body += (f'<g class="a" {delay(.2 + i * .07)}>'
                 f'<rect x="{lx}" y="{ly - 11}" width="12" height="12" rx="3" fill="{color}"/>'
                 + text(lx + 22, ly, name, 14.5, INK, 700)
                 + text(lx + 238, ly, f"{frac * 100:.1f}%", 13.5, INK, 700, "end", MONO)
                 + f'<rect x="{lx + 22}" y="{ly + 9}" width="216" height="4" rx="2" fill="{LINE}"/>'
                 + f'<rect x="{lx + 22}" y="{ly + 9}" width="{max(3, 216 * frac / (top[0][1] / total)):.1f}" height="4" rx="2" fill="{color}"/>'
                 + "</g>")
    body += text(300, h - 30, f"{human_bytes(total)} of code across {len(d['repos']) - 1} repositories", 12, FAINT, 500)
    return frame(w, h, body, "Languages")


def activity(d: dict, x: dict) -> str:
    w, h = 840, 320
    weeks = x["weeks"][-53:]
    left, right, top, bottom = 52, 34, 70, 74
    pw, ph = w - left - right, h - top - bottom
    peak = max([wk["total"] for wk in weeks] + [1])
    step = 10 ** max(0, len(str(peak)) - 1)
    nice = math.ceil(peak / step) * step
    pts = [(left + pw * i / max(1, len(weeks) - 1), top + ph * (1 - wk["total"] / nice)) for i, wk in enumerate(weeks)]
    dpath = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(0, i - 1)], pts[i], pts[i + 1], pts[min(len(pts) - 1, i + 2)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, min(top + ph, p1[1] + (p2[1] - p0[1]) / 6))
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, min(top + ph, p2[1] - (p3[1] - p1[1]) / 6))
        dpath += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    area = dpath + f" L{pts[-1][0]:.1f},{top + ph} L{pts[0][0]:.1f},{top + ph} Z"
    body = eyebrow(32, 38, "Weekly activity")
    body += text(w - 32, 38, "● contributions   ◆ pull requests", 11.5, MUTED, 600, "end", MONO)
    body += (f'<defs><linearGradient id="ga" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SKY}" stop-opacity=".35"/>'
             f'<stop offset="1" stop-color="{SKY}" stop-opacity="0"/></linearGradient></defs>')
    for k in range(5):
        y = top + ph * k / 4
        body += f'<line x1="{left}" y1="{y:.1f}" x2="{w - right}" y2="{y:.1f}" stroke="{LINE}" stroke-dasharray="2 6"/>'
        body += text(left - 12, y + 4, short(int(nice * (1 - k / 4))), 11, MUTED, 500, "end", MONO)
    body += f'<path d="{area}" fill="url(#ga)" class="f" {delay(.9)}/>'
    body += f'<path d="{dpath}" fill="none" stroke="{SKY}" stroke-width="2.6" stroke-linejoin="round" pathLength="1" class="d"/>'
    body += text(left - 12, top + ph + 26, "PRs", 10.5, VIOLET, 700, "end", MONO)
    body += f'<line x1="{left}" y1="{top + ph + 22}" x2="{w - right}" y2="{top + ph + 22}" stroke="{LINE}"/>'
    pr_peak = max([len(wk["prs"]) for wk in weeks] + [1])
    for i, wk in enumerate(weeks):
        n = len(wk["prs"])
        if n:
            r = 3 + 5 * math.sqrt(n / pr_peak)
            px, py = pts[i][0], top + ph + 36
            body += (f'<rect x="{px - r:.1f}" y="{py - r - 14:.1f}" width="{2 * r:.1f}" height="{2 * r:.1f}" '
                     f'transform="rotate(45 {px:.1f} {py - 14:.1f})" fill="{VIOLET}" opacity=".9" class="f" {delay(1.4 + i * .01)}/>')
    bi = max(range(len(weeks)), key=lambda i: weeks[i]["total"])
    edge = pts[bi][0] > w - 160
    body += f'<circle cx="{pts[bi][0]:.1f}" cy="{pts[bi][1]:.1f}" r="5" fill="{BG}" stroke="{INK}" stroke-width="2.4" class="f" {delay(1.8)}/>'
    top_repo = next(iter(weeks[bi]["commits"]), "")
    note = f"peak {weeks[bi]['total']} · mostly {top_repo}" if top_repo else f"peak {weeks[bi]['total']}"
    body += f'<g class="f" {delay(1.9)}>' + text(pts[bi][0] + (-12 if edge else 12), pts[bi][1] + 4, note, 12, INK, 700, "end" if edge else "start") + "</g>"
    last = None
    for i, wk in enumerate(weeks):
        m = wk["start"][5:7]
        if m != last and 1 < i < len(weeks) - 2:
            body += text(pts[i][0], h - 12, dt.date.fromisoformat(wk["start"]).strftime("%b").upper(), 10.5, MUTED, 600, "middle", MONO, 1)
        last = m
    return frame(w, h, body, "Weekly activity")


def now_terminal() -> str:
    w, h = 840, 230
    lines = [("$ ", "cat now.txt", INK),
             ("building ", "Tern, an AI research and study desktop app (Rust)", INK),
             ("shipping ", "Selvard, privacy-first Android security", INK),
             ("learning ", "AI engineering: RAG, agents, evals", INK),
             ("open to   ", "internships, freelance websites and apps", INK)]
    body = (f'<rect x="1" y="1" width="{w - 2}" height="36" rx="15" fill="{PANEL}"/>'
            f'<rect x="1" y="22" width="{w - 2}" height="16" fill="{PANEL}"/>'
            + "".join(f'<circle cx="{24 + i * 18}" cy="19" r="5.5" fill="{c}"/>' for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]))
            + text(w / 2, 24, "khubaib@dev: ~", 12, MUTED, 600, "middle", MONO))
    for i, (k, v, _) in enumerate(lines):
        y = 76 + i * 34
        col = SKY if i == 0 else VIOLET
        n = len(k) + len(v)
        body += (f'<clipPath id="l{i}"><rect x="30" y="{y - 20}" width="{n * 8.6 + 20:.0f}" height="28" '
                 f'style="transform-origin:30px 0;animation:grow {0.35 + n * .012:.2f}s steps({n}) {0.3 + i * .55:.2f}s both"/></clipPath>'
                 f'<g clip-path="url(#l{i})"><text x="32" y="{y}" font-family="{MONO}" font-size="14.5" font-weight="600">'
                 f'<tspan fill="{col}">{esc(k)}</tspan><tspan fill="{INK if i else MUTED}">{esc(v)}</tspan></text></g>')
    body += f'<rect x="32" y="{76 + len(lines) * 34 - 16}" width="9" height="19" fill="{SKY}" class="f" {delay(.3 + len(lines) * .55)}/>'
    return frame(w, h, body, "Now")


def main() -> None:
    CARDS.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    cache = os.environ.get("PROFILE_CACHE")
    d = json.loads(Path(cache).read_text()) if cache and Path(cache).exists() else gather()
    if cache and not Path(cache).exists():
        Path(cache).write_text(json.dumps(d))
    x = derive(d)
    out = {"header.svg": header(), "toolkit.svg": toolkit(), "overview.svg": overview(d, x),
           "calendar.svg": iso_calendar(d, x), "languages.svg": languages(d),
           "activity.svg": activity(d, x), "now.svg": now_terminal()}
    out.update({f"social-{n}.svg": social(n) for n in SOCIAL})
    out.update({f"project-{p[4]}.svg": project(i) for i, p in enumerate(PROJECTS)})
    for name, body in out.items():
        (CARDS / name).write_text(body, encoding="utf-8")
    for old in ("stats.svg",):
        (CARDS / old).unlink(missing_ok=True)
    dash = {"user": d["user"], "generated": d["generated"], "derived": {k: v for k, v in x.items() if k != "weeks"},
            "weeks": x["weeks"], "days": d["days"], "languages": d["languages"], "pr_total": d["pr_total"],
            "issues": d["issues"], "reviewed": d["reviewed"], "repos": d["repos"]}
    (DOCS / "data.json").write_text(json.dumps(dash, separators=(",", ":")), encoding="utf-8")
    kb = sum(len(b.encode()) for b in out.values()) / 1024
    print(f"wrote {len(out)} cards ({kb:.0f} KB) and docs/data.json")


if __name__ == "__main__":
    main()
