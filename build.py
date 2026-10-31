"""Genera dark_mode.svg y light_mode.svg: ASCII de la foto + panel tipo neofetch con el CV.

Uso: python build.py   (la Action lo ejecuta a diario para que "Uptime" vaya al día)
"""
import datetime as dt
from html import escape

CAREER_START = dt.date(2020, 11, 1)  # primer empleo (COVERCAR)
WIDTH = 60  # caracteres de cada línea del panel
X_PANEL, Y0, LINE = 430, 30, 20
ART_FONT, ART_LINE = 8, 9  # el ASCII va más pequeño para que se vean ojos y boca
ART_WIDTH = 390  # px que ocupa cada fila del ASCII; deja 25 px de margen hasta el panel

# ((clave, subclave...), valor); None = línea en blanco; str = cabecera de sección
INFO = [
    "ian@flores",
    (("Role",), "Software Engineer — AI & Backend"),
    (("Location",), "Barcelona, Spain"),
    (("Uptime",), "{uptime}"),
    None,
    "- Experience",
    (("Work", "Current"), "Software Engineer @ NEORIS (EPAM), 2023–"),
    (("Work", "Previous"), "Full-stack Developer @ COVERCAR, 2020–23"),
    None,
    "- Skills",
    (("AI", "ML"), "LLMs, RAG, embeddings, agentic systems, MCP"),
    (("Languages", "Code"), "Python, PHP, JavaScript, Java, SQL"),
    (("Frameworks",), "Laravel, Symfony, Django, Angular, Next.js"),
    (("Infra",), "AWS, Docker, MySQL, MongoDB, Git, ETL"),
    (("Languages", "Real"), "Spanish, Catalan, English, German"),
    None,
    "- Awards",
    (("HackDays4Learning", "2025"), "1st place · Quizzards"),
    (("HackDays4Learning", "2026"), "2nd place · Paper2Quizz"),
    None,
    "- Education",
    (("Education", "AI"), "AI & Big Data specialization · IOC"),
    (("Education", "Web"), "Web App Development · 9.18/10"),
    None,
    "- Contact",
    (("Email",), "ianfloresf71@gmail.com"),
    (("LinkedIn",), "ian-flores-fdez"),
    (("Web",), "ratemydecks.com"),
]

THEMES = {
    "dark": dict(bg="#161b22", fg="#c9d1d9", key="#ffa657", value="#a5d6ff", cc="#616e7f"),
    "light": dict(bg="#f6f8fa", fg="#24292f", key="#953800", value="#0a3069", cc="#c2cfde"),
}


def uptime(today):
    y, m = today.year - CAREER_START.year, today.month - CAREER_START.month
    if m < 0:
        y -= 1
        m += 12
    plural = lambda n, s, p: f"{n} {s if n == 1 else p}"
    return f"{plural(y, 'year', 'years')}, {plural(m, 'month', 'months')} in production"


def kv_line(keys, value):
    """'. Key.Sub: ...... value' ajustado a WIDTH caracteres."""
    label_len = len(".".join(keys)) + 1
    fill = WIDTH - 2 - label_len - len(value)
    keys_svg = ".".join(f'<tspan class="key">{escape(k)}</tspan>' for k in keys)
    return (f'<tspan class="cc">. </tspan>{keys_svg}:<tspan class="cc"> {"." * max(fill - 2, 1)} </tspan>'
            f'<tspan class="value">{escape(value)}</tspan>')


def header(title):
    return f'{escape(title)} <tspan class="cc">-{"—" * (WIDTH - len(title) - 3)}-</tspan>'


def render(theme, ascii_art, today):
    c = THEMES[theme]
    lines = []
    for item in INFO:
        if item is None:
            lines.append('<tspan class="cc">. </tspan>')
        elif isinstance(item, str):
            lines.append(header(item))
        else:
            lines.append(kv_line(item[0], item[1].format(uptime=uptime(today))))

    art = ascii_art.rstrip("\n").split("\n")
    height = max(Y0 - 6 + (len(art) - 1) * ART_LINE, Y0 + (len(lines) - 1) * LINE) + 20
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
    ]
    # cada fila con ancho fijo (textLength): sin Consolas la letra de reserva es más ancha y pisaba el panel
    cols = max(len(row) for row in art)
    for i, row in enumerate(art):
        if row.strip():
            out.append(f'<text x="15" y="{Y0 - 6 + i * ART_LINE}" fill="{c["fg"]}" font-size="{ART_FONT}px" '
                       f'textLength="{ART_WIDTH}" lengthAdjust="spacingAndGlyphs">{escape(row.ljust(cols))}</text>')
    out.append(f'<text x="{X_PANEL}" y="{Y0}" fill="{c["fg"]}">')
    for i, line in enumerate(lines):
        out.append(f'<tspan x="{X_PANEL}" y="{Y0 + i * LINE}">{line}</tspan>')
    out.append("</text>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    today = dt.date.today()
    for theme in THEMES:
        with open(f"ascii_{theme}.txt", encoding="utf-8") as f:
            art = f.read()
        with open(f"{theme}_mode.svg", "w", encoding="utf-8", newline="\n") as f:
            f.write(render(theme, art, today))


if __name__ == "__main__":
    main()
