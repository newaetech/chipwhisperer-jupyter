"""LaTeX back-end for the SCA101 student-guide story scripts.

It offers the same helper names as pdfkit.py (H1, H2, P, table, code, callout, figure, numbered, ...), but instead of drawing a PDF with
reportlab it writes a LaTeX document that uses scaguide.sty. Run a story script with the environment variable GUIDE_BACKEND=latex:

    set GUIDE_BACKEND=latex
    python story_explorer_2_1b.py "Lab_2_1B_Explorer_Guide.tex"

The output folder then contains the .tex, scaguide.sty and a figures/ folder with every picture the guide uses; build it with
    pdflatex Lab_2_1B_Explorer_Guide.tex     (twice, so the contents page fills in)
The text, tables and call-outs of the .tex are plain LaTeX: edit them directly, or edit the story script and regenerate.
"""
import os, re, shutil, textwrap

# ---------------------------------------------------------------- constants kept for source compatibility with pdfkit
inch = 72.0
PAGE_W = 8.5 * inch
W = PAGE_W - 2 * 0.8 * inch              # usable text width, in points
NAVY, TEAL, GREY, LIGHT = "guidenavy", "guideteal", "guidegrey", "guidelight"

KINDS = {
    "do": ("DO THIS", None, None), "see": ("YOU SHOULD SEE", None, None), "ifnot": ("IF IT DOESN'T", None, None),
    "warn": ("WATCH OUT", None, None), "tip": ("GOOD TO KNOW", None, None),
}
NOTICE_TEXT = [
    ("This guide accompanies ChipWhisperer course material that references (commercial) training material on "
     "ChipWhisperer.io. You can freely execute and use the lab per the open-source license (including in your "
     "own courses if you distribute similarly), but you must maintain notice about the source: "
     "https://www.ChipWhisperer.io."),
    ("Copyright (C) NewAE Technology Inc., 2015-2020. ChipWhisperer is a trademark of NewAE Technology Inc., "
     "claimed in all jurisdictions, and registered in at least the United States of America, European Union, "
     "and Peoples Republic of China. Tutorials derived from our open-source work must be released under the "
     "associated open-source license, and notice of the source must be clearly displayed."),
    ("THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT "
     "LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO "
     "EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER "
     "IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR "
     "THE USE OR OTHER DEALINGS IN THE SOFTWARE."),
]


class Style:
    def __init__(self, name, parent=None, **kw):
        self.name = name
        self.__dict__.update(kw)


def ParagraphStyle(name, parent=None, **kw):
    return Style(name, parent, **kw)


body, small, cell, cellb, cellh, caption, h1, h2, h3, bul, codestyle, toc1, toc2 = (
    Style(n) for n in ("body", "small", "cell", "cellb", "cellh", "caption", "H1", "H2", "H3", "bul", "code", "toc1", "toc2"))


class Node:
    def __init__(self, tex, kind="block"):
        self.tex, self.kind = tex, kind


class Spacer(Node):
    def __init__(self, w, h):
        super().__init__(r"\vspace{%gpt}" % h, "spacer")


class PageBreak(Node):
    def __init__(self):
        super().__init__(r"\clearpage", "pagebreak")


class CondPageBreak(Node):
    def __init__(self, h):
        super().__init__(r"\Needspace{%dpt}" % round(h), "cond")


def KeepTogether(items):
    items = list(items)
    return Node("\n\n".join(i.tex for i in items))


# ---------------------------------------------------------------- text conversion
_SPECIAL = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$", "&": r"\&", "#": r"\#", "_": r"\_", "%": r"\%",
            "~": r"\textasciitilde{}", "^": r"\textasciicircum{}", "<": r"\textless{}", ">": r"\textgreater{}", '"': r"\textquotedbl{}",
            "|": r"\textbar{}"}
_BREAK_AFTER = set("/\\_.-,=:")


def esc(s):
    return "".join(_SPECIAL.get(c, c) for c in s)


def esc_code(s):
    # long identifiers and paths may break after / _ . so they never run out of a narrow table column; short code stays unbroken
    long_ = len(s) > 20
    out = []
    for c in s:
        out.append(_SPECIAL.get(c, c))
        if long_ and c in "/_.\\":
            out.append(r"\bk{}")
    return "".join(out)


def quote(t):
    """Straight quotes in prose -> TeX quotes (paired "..." and an opening ' before a word)."""
    if t.count('"') % 2 == 0:
        t = re.sub(r'"([^"]*)"', lambda m: "``" + m.group(1) + "''", t)
    return re.sub(r"(?<![\w])'(?=[\w])", "`", t)


def md(s, table=False):
    """`code`, **bold**, __italic__, [text](url)  ->  LaTeX."""
    s = s.replace("\n", " ")
    codes, links = [], []

    def grab_code(m):
        codes.append(m.group(1)); return "\ue000C%d\ue001" % (len(codes) - 1)

    def grab_link(m):
        links.append((m.group(1), m.group(2))); return "\ue000L%d\ue001" % (len(links) - 1)

    s = re.sub(r"`([^`]*)`", grab_code, s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", grab_link, s)

    def inline(t):
        out, pos = [], 0
        for m in re.finditer(r"\*\*(.+?)\*\*|__(.+?)__", t):
            out.append(esc(quote(t[pos:m.start()])))
            out.append((r"\textbf{%s}" % inline(m.group(1))) if m.group(1) is not None else (r"\emph{%s}" % inline(m.group(2))))
            pos = m.end()
        out.append(esc(quote(t[pos:])))
        return "".join(out)

    e = inline(s)
    macro = "codesmall" if table else "code"
    e = re.sub("\ue000C(\\d+)\ue001", lambda m: "\\%s{%s}" % (macro, esc_code(codes[int(m.group(1))])), e)
    e = re.sub("\ue000L(\\d+)\ue001", lambda m: "\\href{%s}{%s}" % (links[int(m.group(1))][1].replace("%", r"\%").replace("#", r"\#"), esc(links[int(m.group(1))][0])), e)
    return e


def _wrap(t, width=118):
    if "\\begin" in t or "\\end" in t or "\n" in t:
        return t
    return textwrap.fill(t, width=width, break_long_words=False, break_on_hyphens=False)


# ---------------------------------------------------------------- building blocks (same names as pdfkit)
def P(s, style=body):
    if style is small:
        return Node(_wrap(r"\guidesmall{%s}" % md(s)), "para")
    if style is h3:
        return Node(r"\guidehthree{%s}" % md(s), "heading")
    return Node(_wrap(md(s)), "para")


def Paragraph(text, style=body):
    return Node(_wrap(md(re.sub(r"<[^>]+>", " ", text))), "para")


def bullets(items, style=bul):
    return [Node("\\begin{itemize}[leftmargin=1.6em,itemsep=2pt,topsep=2pt,parsep=0pt]\n" + "\n".join("\\item " + md(i) for i in items) + "\n\\end{itemize}")]


def numbered(items, style=bul, start=1):
    return [Node("\\begin{enumerate}[label=\\arabic*.,leftmargin=1.8em,itemsep=2pt,topsep=2pt,parsep=0pt,start=%d]\n" % start
                 + "\n".join("\\item " + md(i) for i in items) + "\n\\end{enumerate}")]


def code(text, width=None):
    text = text.strip("\n")
    longest = max(len(ln) for ln in text.split("\n"))
    assert longest <= 100, "code line too long (%d)" % longest
    assert "\\end{guidecode}" not in text
    return [Node("\\begin{guidecode}\n" + text + "\n\\end{guidecode}"), Spacer(1, 0)]


def icode(text):
    return code(text)[0]


def callout(kind, items, title=None):
    label = KINDS[kind][0]
    body_tex = "\n\n".join(it.tex if isinstance(it, Node) else _wrap(md(it)) for it in items)
    return [Node("\\begin{guidecallout}{%s}{%s}\n%s\n\\end{guidecallout}" % (kind, esc(title or label), body_tex)), Spacer(1, 0)]


def TC(text, tag):
    return Node(md(text, table=True) + r"\srctag{%s}" % esc(tag), "cell")


def table(rows, widths, header=True, zebra=True, bold_first_col=False):
    total = float(sum(widths))
    spec = "|" + "|".join("R{%.4f}" % (w / total) for w in widths) + "|"
    lines = ["{\\small\\arrayrulecolor{guidegrid}"]
    if zebra:
        lines.append("\\rowcolors{2}{white}{guidezebra}" if header else "\\rowcolors{1}{guidezebra}{white}")
    lines += ["\\begin{longtable}{%s}" % spec, "\\hline"]
    for r, row in enumerate(rows):
        cells = []
        for c, v in enumerate(row):
            t = v.tex if isinstance(v, Node) else md(v, table=True)
            if header and r == 0:
                t = r"\hdrcell{%s}" % t
            elif bold_first_col and c == 0:
                t = r"\textbf{%s}" % t
            cells.append(t)
        if header and r == 0:
            lines.append("\\rowcolor{guidenavy}" + " & ".join(cells) + " \\\\ \\hline\n\\endhead")
        else:
            lines.append(" & ".join(cells) + " \\\\ \\hline")
    lines += ["\\end{longtable}}"]
    return [Node("\n".join(lines), "table"), Spacer(1, 4)]


_FIGS = {}


def figure(path, width, cap):
    base = os.path.basename(path)
    if base in _FIGS and _FIGS[base] != path:
        base = os.path.basename(os.path.dirname(path)) + "_" + base
    _FIGS[base] = path
    frac = min(1.0, width / W)
    return Node("\\guidefigure{figures/%s}{%.3f}{%s}" % (base, frac, md(cap)), "figure")


def STEP(num, title):
    return Node(r"\guidestep{%s}{%s}" % (esc(num), esc(quote(title))), "heading")


def H1(text):
    return Node(r"\guidehone{%s}" % esc(quote(text)), "heading")


def H2(text):
    return Node(r"\guidehtwo{%s}" % esc(quote(text)), "heading")


H2T = H2


def legend():
    return [Node(r"\guidelegend")]


def notice():
    return [Node("\\guidehthree{Notice}\n\n" + "\n\n".join(_wrap(r"\guidesmall{%s}" % md(t)) for t in NOTICE_TEXT))]


_CFG = {}


class Roadmap(Node):
    def __init__(self, width):
        labels = _CFG.get("roadmap", [])
        n, total, gap = len(labels), 17.5, 0.55
        bw = (total - gap * (n - 1)) / max(n, 1)
        t = ["\\begin{center}", "\\begin{tikzpicture}"]
        for i, (a, b) in enumerate(labels):
            x = i * (bw + gap) + bw / 2
            fill = "guidenavy" if i < n - 1 else "guideteal"
            t.append("\\node[rounded corners=4pt,fill=%s,text=white,align=center,minimum height=1.15cm,minimum width=%.2fcm,inner sep=3pt]"
                     " (n%d) at (%.2f,0) {\\textbf{%s}\\\\{\\footnotesize %s}};" % (fill, bw, i, x, esc(a), esc(b)))
        for i in range(n - 1):
            t.append("\\draw[-{Stealth},guidegrey,thick] (n%d.east) -- (n%d.west);" % (i, i + 1))
        t += ["\\end{tikzpicture}", "\\end{center}"]
        super().__init__("\n".join(t), "block")


def make_toc():
    return Node(r"\tableofcontents")


def cover(kicker, title_lines, subtitle):
    return [Node(r"\guidecover{%s}{%s}{%s}" % (esc(kicker), r"\\ ".join(esc(t) for t in title_lines), esc(quote(subtitle))))]


def contents():
    return [make_toc(), PageBreak()]


def init(out, header_left, header_right, footer_left, title, subject, roadmap=None):
    _CFG.update(header_left=header_left, header_right=header_right, footer_left=footer_left, title=title, subject=subject,
                roadmap=roadmap or [])
    out = re.sub(r"\.pdf$", ".tex", out)
    return {"out": out}


def build(doc, story, heading_gap=1.9):
    out_path = doc["out"]
    out_dir = os.path.dirname(os.path.abspath(out_path))
    os.makedirs(os.path.join(out_dir, "figures"), exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    if os.path.abspath(here) != os.path.abspath(out_dir):          # building next to scaguide.sty: nothing to copy
        shutil.copyfile(os.path.join(here, "scaguide.sty"), os.path.join(out_dir, "scaguide.sty"))
    for base, src in _FIGS.items():
        dst = os.path.join(out_dir, "figures", base)
        if os.path.abspath(src) != os.path.abspath(dst):
            shutil.copyfile(src, dst)
    nodes = []
    for n in story:
        if isinstance(n, Node):
            if n.kind == "pagebreak":
                while nodes and nodes[-1].kind == "spacer":
                    nodes.pop()
            nodes.append(n)
    parts = [n.tex for n in nodes if n.tex and n.tex != r"\vspace{0pt}"]
    comment = ("% " + _CFG["title"].replace("%", "") + "\n"
               "% Generated by guide_tools/latex/latexkit.py from the story script; this file is plain LaTeX - edit it directly.\n"
               "% Build: pdflatex <this file>   (run it twice so the contents page fills in).  Needs scaguide.sty and figures/ next to it.\n")
    setup = ("\\documentclass[11pt,letterpaper]{article}\n\\usepackage{scaguide}\n"
             "\\guidesetup{\n  headerleft={" + esc(_CFG["header_left"]) + "},\n  headerright={" + esc(_CFG["header_right"]) +
             "},\n  footerleft={" + esc(_CFG["footer_left"]) + "},\n  title={" + esc(_CFG["title"]) +
             "},\n  subject={" + esc(_CFG["subject"]) + "}}\n\n\\begin{document}\n\n")
    head = comment + setup
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(head + "\n\n".join(parts) + "\n\n\\end{document}\n")
    print("wrote", out_path, "(%d figures)" % len(_FIGS))
