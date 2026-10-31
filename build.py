"""Genera dark_mode.svg y light_mode.svg: ASCII de la foto + panel tipo neofetch con datos de GitHub.

Uso: GH_TOKEN=... python build.py   (en local vale con `gh auth token`; en la Action, GITHUB_TOKEN)
"""
import datetime as dt
import json
import os
import subprocess
import urllib.request
from html import escape

USER = "ianfloresfdez"
CREATED = dt.date(2021, 5, 30)  # alta de la cuenta de GitHub
WIDTH = 60  # caracteres de cada línea del panel
X_PANEL, Y0, LINE = 415, 30, 20

# (clave, valor); None = línea en blanco; str = cabecera de sección
INFO = [
    "ian@floresfdez",
    (("OS",), "Windows 11"),
    (("Uptime",), "{uptime}"),
    (("Host",), "i5-13600K · RX 6800 16 GB · 32 GB RAM"),
    (("Kernel",), "Desarrollador · IA local y agentes LLM"),
    (("IDE",), "VS Code, Claude Code"),
    None,
    (("Languages", "Programming"), "Python, TypeScript, Rust, PHP"),
    (("Languages", "Computer"), "HTML, CSS, SQL, YAML, Dockerfile"),
    (("Languages", "Real"), "Español, English"),
    None,
    (("LLM", "Local"), "Ollama (Vulkan), gemma4, gpt-oss"),
    (("Projects",), "llm-gateway, jack, codegraph, jobscout-mcp"),
    (("Stack", "Infra"), "Docker, Helm, kind, GitHub Actions"),
    None,
    "- Contact",
    (("GitHub",), "ianfloresfdez"),
    None,
    "- GitHub Stats",
    "{stats1}",
    "{stats2}",
]

THEMES = {
    "dark": dict(bg="#161b22", fg="#c9d1d9", key="#ffa657", value="#a5d6ff", cc="#616e7f", add="#3fb950"),
    "light": dict(bg="#f6f8fa", fg="#24292f", key="#953800", value="#0a3069", cc="#c2cfde", add="#1a7f37"),
}


def token():
    t = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if t:
        return t
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def gql(query, **variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token()}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]


def stats():
    u = gql(
        """query($login: String!) { user(login: $login) {
             followers { totalCount }
             repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100) {
               totalCount nodes { stargazerCount } }
             repositoriesContributedTo(contributionTypes: [COMMIT, PULL_REQUEST]) { totalCount } } }""",
        login=USER,
    )["user"]
    commits = 0
    for year in range(CREATED.year, dt.date.today().year + 1):
        c = gql(
            """query($login: String!, $from: DateTime!, $to: DateTime!) { user(login: $login) {
                 contributionsCollection(from: $from, to: $to) {
                   totalCommitContributions restrictedContributionsCount } } }""",
            login=USER, **{"from": f"{year}-01-01T00:00:00Z", "to": f"{year}-12-31T23:59:59Z"},
        )["user"]["contributionsCollection"]
        commits += c["totalCommitContributions"] + c["restrictedContributionsCount"]
    return dict(
        repos=u["repositories"]["totalCount"],
        stars=sum(n["stargazerCount"] for n in u["repositories"]["nodes"]),
        contrib=u["repositoriesContributedTo"]["totalCount"],
        followers=u["followers"]["totalCount"],
        commits=commits,
    )


def uptime(today):
    y, m, d = today.year - CREATED.year, today.month - CREATED.month, today.day - CREATED.day
    if d < 0:
        m -= 1
        d += (today.replace(day=1) - dt.timedelta(days=1)).day
    if m < 0:
        y -= 1
        m += 12
    plural = lambda n, s, p: f"{n} {s if n == 1 else p}"
    return f"{plural(y, 'año', 'años')}, {plural(m, 'mes', 'meses')}, {plural(d, 'día', 'días')}"


def dots(n):
    return " " + "." * max(n - 2, 1) + " "


def kv_line(keys, value):
    """'. Key.Sub: ...... value' ajustado a WIDTH caracteres."""
    label_len = len(".".join(keys)) + 1
    fill = WIDTH - 2 - label_len - len(value)
    keys_svg = ".".join(f'<tspan class="key">{escape(k)}</tspan>' for k in keys)
    return (f'<tspan class="cc">. </tspan>{keys_svg}:<tspan class="cc">{dots(fill)}</tspan>'
            f'<tspan class="value">{escape(value)}</tspan>')


def stat_pair(k1, v1, k2, v2, extra=""):
    """Dos estadísticas en una línea: '. A: ... 1 | B: ... 2'."""
    half = (WIDTH - 2 - 3) // 2
    a = half - len(k1) - 1 - len(v1) - len(extra)
    b = (WIDTH - 2 - 3 - half) - len(k2) - 1 - len(v2)
    extra_svg = ""
    if extra:
        n = extra.strip(" {}").split(": ")
        extra_svg = f' {{<tspan class="key">{n[0]}</tspan>: <tspan class="value">{n[1]}</tspan>}}'
    return (f'<tspan class="cc">. </tspan><tspan class="key">{k1}</tspan>:<tspan class="cc">{dots(a)}</tspan>'
            f'<tspan class="value">{v1}</tspan>{extra_svg} | <tspan class="key">{k2}</tspan>:'
            f'<tspan class="cc">{dots(b)}</tspan><tspan class="value">{v2}</tspan>')


def header(title):
    return f'{escape(title)} <tspan class="cc">-{"—" * (WIDTH - len(title) - 3)}-</tspan>'


def render(theme, ascii_art, s, today):
    c = THEMES[theme]
    lines = []
    for item in INFO:
        if item is None:
            lines.append('<tspan class="cc">. </tspan>')
        elif item == "{stats1}":
            lines.append(stat_pair("Repos", f"{s['repos']:,}", "Stars", f"{s['stars']:,}",
                                   extra=f" {{Contributed: {s['contrib']:,}}}"))
        elif item == "{stats2}":
            lines.append(stat_pair("Commits", f"{s['commits']:,}", "Followers", f"{s['followers']:,}"))
        elif isinstance(item, str):
            lines.append(header(item))
        else:
            lines.append(kv_line(item[0], item[1].format(uptime=uptime(today))))

    art = ascii_art.rstrip("\n").split("\n")
    rows = max(len(art), len(lines))
    height = Y0 + (rows - 1) * LINE + 20
    width = X_PANEL + int(WIDTH * 9.6) + 20

    out = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        f'<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" '
        f'width="{width}px" height="{height}px" font-size="16px">',
        "<style>",
        "@font-face { src: local('Consolas'), local('Consolas Bold'); font-family: 'ConsolasFallback';"
        " font-display: swap; -webkit-size-adjust: 109%; size-adjust: 109%; }",
        f".key {{fill: {c['key']};}} .value {{fill: {c['value']};}} .cc {{fill: {c['cc']};}}",
        "text, tspan {white-space: pre;}",
        "</style>",
        f'<rect width="{width}px" height="{height}px" fill="{c["bg"]}" rx="15"/>',
        f'<text x="15" y="{Y0}" fill="{c["fg"]}">',
    ]
    for i, row in enumerate(art):
        out.append(f'<tspan x="15" y="{Y0 + i * LINE}">{escape(row)}</tspan>')
    out.append("</text>")
    out.append(f'<text x="{X_PANEL}" y="{Y0}" fill="{c["fg"]}">')
    for i, line in enumerate(lines):
        out.append(f'<tspan x="{X_PANEL}" y="{Y0 + i * LINE}">{line}</tspan>')
    out.append("</text>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    today = dt.date.today()
    s = stats()
    for theme in THEMES:
        with open(f"ascii_{theme}.txt", encoding="utf-8") as f:
            art = f.read()
        with open(f"{theme}_mode.svg", "w", encoding="utf-8", newline="\n") as f:
            f.write(render(theme, art, s, today))
    print(s)


if __name__ == "__main__":
    main()
