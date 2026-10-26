#!/usr/bin/env python3
"""Build the static SVG cards for the profile README.

Everything is drawn here and committed as plain, non-animated SVG, so the
profile never depends on third-party stat services (which rate-limit, break,
or go paid) and stays light to scroll.

Outputs (assets/cards/):
  header.svg     name banner in the portfolio's style
  stats.svg      contributions, streaks, active days, repos, stars
  languages.svg  segmented language bar with a legend
  activity.svg   weekly contributions over the last year as a path graph

Data: GitHub REST for repos and languages, and GraphQL for the contribution
calendar when GITHUB_TOKEN is set (falls back to the public contributions page).
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import urllib.request
from collections import defaultdict
from pathlib import Path

USER = os.environ.get("PROFILE_USER", "Khubaib7-del")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = Path(__file__).resolve().parent.parent / "assets" / "cards"

# Portfolio palette (khubaib-nazeer-protfolio.vercel.app)
BG = "#0c0a09"
PANEL = "#151210"
LINE = "#2a2420"
INK = "#f3f0e9"
DIM = "#9d9890"
EMBER = "#ff5a1f"
EMBER_SOFT = "#ff8a4d"
FONT = "'Space Grotesk','Segoe UI',Inter,Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono','SFMono-Regular',Consolas,'Courier New',monospace"

SKIP_REPOS = {USER.lower()}
SKIP_LANGS = {"Jupyter Notebook", "Makefile", "CMake", "Batchfile", "PowerShell",
              "Dockerfile", "Shell", "Procfile", "Smarty", "Roff", "TeX", "HTML", "CSS", "SCSS"}
LANG_COLORS = {
    "Rust": "#ff5a1f", "TypeScript": "#ff8a4d", "Python": "#f3c26b", "JavaScript": "#e9d98a",
    "C++": "#93bf9f", "C": "#6b9a7c", "Kotlin": "#e5aac3", "Assembly": "#a59afa",
    "Java": "#d9a17a", "Go": "#9dd9ef", "PLpgSQL": "#9dd9ef", "Other": "#5c5650",
}


def _get(url: str, data: bytes | None = None) -> bytes:
    req = urllib.request.Request(url, data=data, headers={
        "User-Agent": "profile-cards", "Accept": "application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def repos() -> list[dict]:
    items = json.loads(_get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner"))
    return [r for r in items if not r["fork"] and not r["archived"] and r["name"].lower() not in SKIP_REPOS]


def languages(rs: list[dict]) -> list[tuple[str, float]]:
    # Each repo counts equally: one huge repo (vendored code, generated files)
    # should not drown out everything else.
    share: dict[str, float] = defaultdict(float)
    for r in rs:
        langs = json.loads(_get(r["languages_url"]))
        langs = {k: v for k, v in langs.items() if k not in SKIP_LANGS}
        total = sum(langs.values())
        for k, v in langs.items():
            share[k] += v / total if total else 0
    total = sum(share.values()) or 1
    ranked = sorted(((k, v / total) for k, v in share.items()), key=lambda x: -x[1])
    top, rest = ranked[:6], sum(v for _, v in ranked[6:])
    if rest > 0.004:
        top.append(("Other", rest))
    return top


def calendar() -> list[tuple[dt.date, int]]:
    if TOKEN:
        q = {"query": "query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{"
                      "weeks{contributionDays{date contributionCount}}}}}}", "variables": {"u": USER}}
        try:
            d = json.loads(_get("https://api.github.com/graphql", json.dumps(q).encode()))
            weeks = d["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
            return [(dt.date.fromisoformat(x["date"]), x["contributionCount"])
                    for w in weeks for x in w["contributionDays"]]
        except Exception as e:  # fall back to the public page
            print("graphql failed, scraping:", e)
    page = _get(f"https://github.com/users/{USER}/contributions").decode()
    dates = dict(re.findall(r'data-date="([\d-]+)" id="([^"]+)"', page))
    dates = {v: k for k, v in dates.items()}
    days = []
    for cid, text in re.findall(r'for="([^"]+)"[^>]*>([^<]*)</tool-tip>', page):
        if cid in dates:
            m = re.match(r"(\d[\d,]*) contribution", text)
            days.append((dt.date.fromisoformat(dates[cid]), int(m.group(1).replace(",", "")) if m else 0))
    return sorted(days)


def streaks(days: list[tuple[dt.date, int]]) -> tuple[int, int]:
    longest = run = 0
    for _, c in days:
        run = run + 1 if c else 0
        longest = max(longest, run)
    cur = 0
    seq = list(days)
    if seq and seq[-1][1] == 0:  # today not counted yet: streak can still be alive
        seq = seq[:-1]
    for _, c in reversed(seq):
        if not c:
            break
        cur += 1
    return cur, longest


def svg(w: int, h: int, body: str, title: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{html.escape(title)}"><title>{html.escape(title)}</title>'
            f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="14" fill="{BG}" stroke="{LINE}"/>'
            f"{body}</svg>\n")


def label(x, y, text, size=12, fill=DIM, weight=500, anchor="start", font=MONO, spacing=1.5):
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-family="{font}" font-size="{size}" '
            f'font-weight="{weight}" letter-spacing="{spacing}" text-anchor="{anchor}">{html.escape(text)}</text>')


def header() -> str:
    w, h = 840, 210
    grid = "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="{h}" stroke="{INK}" stroke-width="1" opacity=".035"/>'
                   for x in range(60, w, 60))
    body = (
        f'<defs><radialGradient id="g" cx="82%" cy="20%" r="70%"><stop offset="0" stop-color="{EMBER}" stop-opacity=".38"/>'
        f'<stop offset="1" stop-color="{EMBER}" stop-opacity="0"/></radialGradient></defs>'
        f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="url(#g)"/>{grid}'
        + label(44, 52, "SOFTWARE ENGINEER · FULL-STACK · AI / ML", 12, EMBER_SOFT, 600)
        + label(44, 112, "KHUBAIB NAZEER", 54, INK, 700, font=FONT, spacing=-1)
        + f'<text x="44" y="150" font-family="{FONT}" font-size="22" font-weight="500" fill="{DIM}">'
          f'Built from curiosity<tspan fill="{EMBER}">.</tspan> Building thoughtful websites and software.</text>'
        + label(44, 184, "BS COMPUTER SCIENCE · FAST NUCES LAHORE", 11, DIM, 500)
    )
    return svg(w, h, body, "Khubaib Nazeer — Built from curiosity")


def stats(days, rs) -> str:
    w, h = 840, 132
    year = sum(c for _, c in days)
    active = sum(1 for _, c in days if c)
    cur, longest = streaks(days)
    stars = sum(r["stargazers_count"] for r in rs)
    items = [("CONTRIBUTIONS", f"{year:,}", "last 12 months"), ("CURRENT STREAK", f"{cur}", "days"),
             ("LONGEST STREAK", f"{longest}", "days"), ("ACTIVE DAYS", f"{active}", "last 12 months"),
             ("REPOSITORIES", f"{len(rs)}", f"{stars} stars")]
    col = (w - 48) / len(items)
    body = ""
    for i, (k, v, sub) in enumerate(items):
        x = 24 + i * col
        if i:
            body += f'<line x1="{x}" y1="30" x2="{x}" y2="{h-30}" stroke="{LINE}"/>'
        body += label(x + 20, 44, k, 10.5, DIM, 600)
        body += label(x + 20, 84, v, 34, EMBER if i == 0 else INK, 700, font=FONT, spacing=-0.5)
        body += label(x + 20, 104, sub, 11, DIM, 400, spacing=0.5)
    return svg(w, h, body, "GitHub stats")


def langs_card(langs) -> str:
    w, h = 840, 150
    x0, bw, y = 32, w - 64, 58
    body = label(32, 38, "LANGUAGES · SHARE ACROSS REPOSITORIES", 11, DIM, 600)
    body += f'<clipPath id="bar"><rect x="{x0}" y="{y}" width="{bw}" height="14" rx="7"/></clipPath><g clip-path="url(#bar)">'
    x = x0
    for name, v in langs:
        seg = bw * v
        body += f'<rect x="{x:.1f}" y="{y}" width="{seg + 0.6:.1f}" height="14" fill="{LANG_COLORS.get(name, "#7a726a")}"/>'
        x += seg
    body += "</g>"
    per_row = 4
    for i, (name, v) in enumerate(langs):
        cx = 32 + (i % per_row) * ((w - 64) / per_row)
        cy = 104 + (i // per_row) * 24
        body += f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{LANG_COLORS.get(name, "#7a726a")}"/>'
        body += label(cx + 18, cy, name, 13, INK, 600, font=FONT, spacing=0)
        body += label(cx + (w - 64) / per_row - 28, cy, f"{v * 100:.1f}%", 12, DIM, 400, "end", spacing=0)
    return svg(w, h, body, "Languages")


def activity(days) -> str:
    w, h = 840, 250
    weeks: list[tuple[dt.date, int]] = []
    for i in range(0, len(days), 7):
        chunk = days[i:i + 7]
        weeks.append((chunk[0][0], sum(c for _, c in chunk)))
    weeks = weeks[-52:]
    left, right, top, bottom = 48, 24, 58, 44
    pw, ph = w - left - right, h - top - bottom
    peak = max([c for _, c in weeks] + [1])
    nice = max(4, ((peak + 3) // 4) * 4)
    pts = [(left + pw * i / max(1, len(weeks) - 1), top + ph * (1 - c / nice)) for i, (_, c) in enumerate(weeks)]
    # smooth path (Catmull-Rom to Bezier)
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[max(0, i - 1)], pts[i], pts[i + 1]
        p3 = pts[min(len(pts) - 1, i + 2)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, min(top + ph, p1[1] + (p2[1] - p0[1]) / 6))
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, min(top + ph, p2[1] - (p3[1] - p1[1]) / 6))
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    area = d + f" L{pts[-1][0]:.1f},{top + ph} L{pts[0][0]:.1f},{top + ph} Z"
    body = label(32, 38, "CONTRIBUTION ACTIVITY · WEEKLY, LAST 12 MONTHS", 11, DIM, 600)
    body += (f'<defs><linearGradient id="a" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{EMBER}" stop-opacity=".45"/>'
             f'<stop offset="1" stop-color="{EMBER}" stop-opacity="0"/></linearGradient></defs>')
    for k in range(5):
        y = top + ph * k / 4
        body += f'<line x1="{left}" y1="{y:.1f}" x2="{w - right}" y2="{y:.1f}" stroke="{LINE}" stroke-dasharray="3 5"/>'
        body += label(left - 10, y + 4, str(int(nice * (1 - k / 4))), 10, DIM, 400, "end", spacing=0)
    body += f'<path d="{area}" fill="url(#a)"/><path d="{d}" fill="none" stroke="{EMBER}" stroke-width="2.4" stroke-linejoin="round"/>'
    bi = max(range(len(weeks)), key=lambda i: weeks[i][1])
    body += f'<circle cx="{pts[bi][0]:.1f}" cy="{pts[bi][1]:.1f}" r="4.5" fill="{BG}" stroke="{EMBER_SOFT}" stroke-width="2.4"/>'
    near_edge = pts[bi][0] > w - right - 60
    body += label(pts[bi][0] - (10 if near_edge else 0), pts[bi][1] + (4 if near_edge else -12),
                  f"peak {weeks[bi][1]} / week", 10.5, EMBER_SOFT, 600, "end" if near_edge else "middle", spacing=0)
    last_month = None
    for i, (start, _) in enumerate(weeks):
        if start.month != last_month and i < len(weeks) - 2:
            if last_month is not None or start.day <= 7:
                body += label(pts[i][0], h - 20, start.strftime("%b").upper(), 10, DIM, 500, "middle", spacing=1)
            last_month = start.month
    return svg(w, h, body, "Weekly contribution activity")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rs = repos()
    days = calendar()
    cards = {"header.svg": header(), "stats.svg": stats(days, rs),
             "languages.svg": langs_card(languages(rs)), "activity.svg": activity(days)}
    for name, body in cards.items():
        (OUT / name).write_text(body, encoding="utf-8")
        print(f"wrote {name} ({len(body.encode()) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
