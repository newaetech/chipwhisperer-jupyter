"""Shared reportlab helpers for the SCA101 student guides (house style: navy/teal, coloured call-out boxes).

Usage in a story script:
    import pdfkit as K
    from pdfkit import *
    doc = K.init(out_path, header_left=..., header_right=..., footer_left=..., title=..., subject=..., roadmap=[...])
    S = [] ... build the story with the helpers ...
    K.build(doc, S)
"""
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                PageBreak, Table, TableStyle, Image, KeepTogether,
                                Preformatted, CondPageBreak, Flowable)
from reportlab.platypus.tableofcontents import TableOfContents

NAVY = colors.HexColor("#1F3A5F")
TEAL = colors.HexColor("#1B7F8C")
GREY = colors.HexColor("#5B6770")
LIGHT = colors.HexColor("#F3F4F6")

PAGE_W, PAGE_H = letter
LM = RM = 0.8 * inch
TM = 0.85 * inch
BM = 0.8 * inch
W = PAGE_W - LM - RM  # usable width

# ---------------------------------------------------------------- styles
body = ParagraphStyle("body", fontName="Helvetica", fontSize=10.5, leading=15, spaceAfter=6)
small = ParagraphStyle("small", parent=body, fontSize=8.5, leading=11.5, textColor=GREY, spaceAfter=3)
cell = ParagraphStyle("cell", parent=body, fontSize=9.2, leading=12, spaceAfter=0)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")
cellh = ParagraphStyle("cellh", parent=cell, fontName="Helvetica-Bold", textColor=colors.white)
caption = ParagraphStyle("caption", parent=body, fontSize=8.5, leading=11, textColor=GREY,
                         alignment=TA_CENTER, spaceAfter=10)
h1 = ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=NAVY, spaceBefore=4, spaceAfter=10)
h2 = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=NAVY,
                    spaceBefore=12, spaceAfter=5, keepWithNext=1)
h3 = ParagraphStyle("H3", fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=TEAL,
                    spaceBefore=8, spaceAfter=3, keepWithNext=1)
bul = ParagraphStyle("bul", parent=body, leftIndent=16, bulletIndent=4, spaceAfter=3)
codestyle = ParagraphStyle("code", fontName="Courier", fontSize=8.6, leading=11.2)
toc1 = ParagraphStyle("toc1", fontName="Helvetica-Bold", fontSize=9.8, leading=11.4, leftIndent=0)
toc2 = ParagraphStyle("toc2", fontName="Helvetica", fontSize=8.8, leading=9.4, leftIndent=18)

CODE_SZ = 9.3  # inline-code size; tables use a smaller one so long messages wrap less


# ---------------------------------------------------------------- markup helpers
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def md(s):
    """`code`, **bold**, __italic__, [text](url) mini-markup -> reportlab markup."""
    codes, links = [], []

    def grab_code(m):
        codes.append(m.group(1))
        return "@@C%d@@" % (len(codes) - 1)

    def grab_link(m):
        links.append((m.group(1), m.group(2)))
        return "@@L%d@@" % (len(links) - 1)

    s = re.sub(r"`([^`]*)`", grab_code, s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", grab_link, s)
    e = esc(s)
    e = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", e)
    e = re.sub(r"__(.+?)__", r"<i>\1</i>", e)

    def put_link(m):
        text, url = links[int(m.group(1))]
        return '<a href="%s" color="#1B7F8C"><u>%s</u></a>' % (url, esc(text))

    e = re.sub(r"@@L(\d+)@@", put_link, e)

    def put_code(m):
        return '<font face="Courier" size="%s" color="#8B1A1A">%s</font>' % (CODE_SZ, esc(codes[int(m.group(1))]))

    return re.sub(r"@@C(\d+)@@", put_code, e)


def P(s, style=body):
    return Paragraph(md(s), style)


def bullets(items, style=bul):
    return [Paragraph(md(t), style, bulletText="•") for t in items]


def numbered(items, style=bul, start=1):
    return [Paragraph(md(t), style, bulletText="%d." % (i + start)) for i, t in enumerate(items)]


def code(text, width=None):
    """Monospaced command box. Lines up to 100 characters are kept on ONE line (the font shrinks a little to fit) so a
    command never needs a backslash continuation - those break when copied out of a PDF."""
    text = text.strip("\n")
    longest = max(len(ln) for ln in text.split("\n"))
    assert longest <= 100, "code line too long (%d)" % longest
    avail = (width or W) - 22
    size = min(codestyle.fontSize, avail / (0.6 * longest))
    style = codestyle if size >= codestyle.fontSize else ParagraphStyle("codefit", parent=codestyle, fontSize=size, leading=size * 1.3)
    t = Table([[Preformatted(text, style)]], colWidths=[width or W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("LINEBEFORE", (0, 0), (0, -1), 3, TEAL),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return [t, Spacer(1, 7)]


def icode(text):
    """Code block narrow enough to sit inside a callout box."""
    return code(text, width=W - 28)[0]


KINDS = {
    "do":    ("DO THIS",          colors.HexColor("#EAF1FD"), colors.HexColor("#2F6FDE")),
    "see":   ("YOU SHOULD SEE",   colors.HexColor("#E8F5EC"), colors.HexColor("#2E8B57")),
    "ifnot": ("IF IT DOESN'T",    colors.HexColor("#FFF3DE"), colors.HexColor("#D98200")),
    "warn":  ("WATCH OUT",        colors.HexColor("#FCE9E7"), colors.HexColor("#C0392B")),
    "tip":   ("GOOD TO KNOW",     colors.HexColor("#EFEAF8"), colors.HexColor("#6B4FBB")),
}


def callout(kind, items, title=None):
    label, bg, bar = KINDS[kind]
    head = ParagraphStyle("ch", parent=cell, fontName="Helvetica-Bold", textColor=bar, fontSize=8.5, spaceAfter=2)
    inner = [Paragraph(title or label, head)]
    for it in items:
        if isinstance(it, str):
            inner.append(Paragraph(md(it), cell))
            inner.append(Spacer(1, 2))
        else:
            inner.append(it)
    t = Table([["", inner]], colWidths=[5, W - 5])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), bar), ("BACKGROUND", (1, 0), (1, 0), bg),
        ("LEFTPADDING", (1, 0), (1, 0), 9), ("RIGHTPADDING", (1, 0), (1, 0), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (0, 0), (0, 0), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return [t, Spacer(1, 8)]


def table(rows, widths, header=True, zebra=True, bold_first_col=False):
    global CODE_SZ
    CODE_SZ = 8.4
    try:
        data = []
        for r, row in enumerate(rows):
            out = []
            for c, v in enumerate(row):
                if isinstance(v, str):
                    st = cellh if (header and r == 0) else (cellb if (bold_first_col and c == 0) else cell)
                    out.append(Paragraph(md(v), st))
                else:
                    out.append(v)
            data.append(out)
    finally:
        CODE_SZ = 9.3
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C9CED3")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    if zebra:
        for r in range(1 if header else 0, len(rows)):
            if (r % 2) == 0:
                style.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#F6F8FA")))
    t.setStyle(TableStyle(style))
    return [t, Spacer(1, 9)]


def TC(text, tag):
    """Table cell with a small grey 'Source:' tag underneath."""
    global CODE_SZ
    CODE_SZ = 8.4
    try:
        return Paragraph(md(text) + '<br/><font size="7.3" color="#5B6770">Source: %s</font>' % esc(tag), cell)
    finally:
        CODE_SZ = 9.3


def figure(path, width, cap):
    ir = ImageReader(path)
    iw, ih = ir.getSize()
    img = Image(path, width=width, height=width * ih / iw)
    return KeepTogether([img, Paragraph(md(cap), caption)])


def STEP(num, title):
    return Paragraph('<font backColor="#1F3A5F" color="white">&nbsp;%s&nbsp;</font>&nbsp;&nbsp;%s' % (num, esc(title)), h2)


def H1(text):
    return Paragraph(esc(text), h1)


def H2(text):
    return Paragraph(esc(text), h2)


def H2T(text):
    """Section heading that may sit directly above a long (splittable) table."""
    return Paragraph(esc(text), ParagraphStyle("H2", parent=h2, keepWithNext=0))


def legend():
    cells = []
    for k, desc in (("do", "An action to take."), ("see", "What the screen should show."),
                    ("ifnot", "What to try if it didn't."), ("warn", "A mistake that costs time.")):
        label, bg, bar = KINDS[k]
        st = ParagraphStyle("lg", parent=cell, fontSize=8.2, leading=10.5)
        lab = ParagraphStyle("lgl", parent=st, fontName="Helvetica-Bold", textColor=bar)
        cells.append([Paragraph(label, lab), Paragraph(desc, st)])
    t = Table([cells], colWidths=[W / 4] * 4)
    ts = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 5),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LEFTPADDING", (0, 0), (-1, -1), 7)]
    for i, k in enumerate(("do", "see", "ifnot", "warn")):
        _, bg, bar = KINDS[k]
        ts += [("BACKGROUND", (i, 0), (i, 0), bg), ("LINEBEFORE", (i, 0), (i, 0), 3, bar),
               ("LINEAFTER", (i, 0), (i, 0), 6, colors.white)]
    t.setStyle(TableStyle(ts))
    return [t, Spacer(1, 6)]


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


def notice():
    return [KeepTogether([P("**Notice**", h3)] + [P(t, small) for t in NOTICE_TEXT])]


def cover(kicker, title_lines, subtitle):
    """Cover-page heading block: small teal kicker, big navy title (one string per line) and a grey subtitle."""
    return [Spacer(1, 0.7 * inch),
            Paragraph(esc(kicker), ParagraphStyle("k", fontName="Helvetica-Bold", fontSize=12, textColor=TEAL, leading=16)),
            Paragraph("<br/>".join(esc(t) for t in title_lines),
                      ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=34, leading=40, textColor=NAVY, spaceAfter=10)),
            Paragraph(esc(subtitle), ParagraphStyle("s", fontName="Helvetica", fontSize=15, leading=20, textColor=GREY, spaceAfter=16))]


# ---------------------------------------------------------------- document
_CFG = {}


class Roadmap(Flowable):
    def __init__(self, width):
        super().__init__()
        self.width, self.height = width, 62

    def draw(self):
        c = self.canv
        labels = _CFG["roadmap"]
        n = len(labels)
        gap = 16
        bw = (self.width - gap * (n - 1)) / n
        for i, (a, b) in enumerate(labels):
            x = i * (bw + gap)
            c.setFillColor(NAVY if i < n - 1 else TEAL)
            c.roundRect(x, 6, bw, 48, 7, stroke=0, fill=1)
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(x + bw / 2, 34, a)
            c.setFont("Helvetica", 8.5)
            c.drawCentredString(x + bw / 2, 20, b)
            if i < n - 1:
                c.setStrokeColor(GREY); c.setFillColor(GREY)
                x0 = x + bw + 2
                c.line(x0, 30, x0 + gap - 6, 30)
                p = c.beginPath(); p.moveTo(x0 + gap - 4, 30); p.lineTo(x0 + gap - 9, 33.5)
                p.lineTo(x0 + gap - 9, 26.5); p.close(); c.drawPath(p, stroke=0, fill=1)


class Doc(BaseDocTemplate):
    def afterFlowable(self, fl):
        if isinstance(fl, Paragraph):
            name = fl.style.name
            if name in ("H1", "H2"):
                txt = re.sub(r"<[^>]+>", "", fl.text).replace("&nbsp;", " ").replace("&amp;", "&")
                txt = re.sub(r"\s+", " ", txt).strip()
                key = "h-%s" % self.seq.nextf("hh")
                self.canv.bookmarkPage(key)
                lvl = 0 if name == "H1" else 1
                self.canv.addOutlineEntry(txt, key, level=lvl, closed=False)
                self.notify("TOCEntry", (lvl, txt, self.page, key))


def _on_page(canv, doc):
    canv.saveState()
    canv.setStrokeColor(colors.HexColor("#C9CED3"))
    canv.line(LM, PAGE_H - 0.55 * inch, PAGE_W - RM, PAGE_H - 0.55 * inch)
    canv.setFont("Helvetica", 8.5); canv.setFillColor(GREY)
    canv.drawString(LM, PAGE_H - 0.48 * inch, _CFG["header_left"])
    canv.drawRightString(PAGE_W - RM, PAGE_H - 0.48 * inch, _CFG["header_right"])
    canv.line(LM, 0.6 * inch, PAGE_W - RM, 0.6 * inch)
    canv.drawString(LM, 0.42 * inch, _CFG["footer_left"])
    canv.drawRightString(PAGE_W - RM, 0.42 * inch, "Page %d" % doc.page)
    canv.restoreState()


def init(out, header_left, header_right, footer_left, title, subject, roadmap=None):
    _CFG.update(header_left=header_left, header_right=header_right, footer_left=footer_left, roadmap=roadmap or [])
    doc = Doc(out, pagesize=letter, leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
              title=title, author="ChipWhisperer SCA101 course materials", subject=subject)
    frame = Frame(LM, BM, W, PAGE_H - TM - BM, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="first", frames=[frame], onPage=lambda c, d: None, autoNextPageTemplate="rest"),
                          PageTemplate(id="rest", frames=[frame], onPage=_on_page)])
    return doc


def make_toc():
    toc = TableOfContents()
    toc.levelStyles = [toc1, toc2]
    toc.dotsMinLevel = 0
    return toc


def contents():
    """'Contents' heading + the table of contents + a page break."""
    return [Paragraph("Contents", ParagraphStyle("H1x", parent=h1)), make_toc(), PageBreak()]


def build(doc, story, heading_gap=1.9):
    """Post-process the story (no blank pages from trailing spacers; keep table headings with their first rows) and build."""
    out = []
    for f in story:
        if isinstance(f, PageBreak):
            while out and isinstance(out[-1], Spacer):
                out.pop()
        if isinstance(f, Paragraph) and f.style.name == "H2" and f.style.keepWithNext == 0:
            out.append(CondPageBreak(heading_gap * inch))
        out.append(f)
    doc.multiBuild(out)
    print("wrote", doc.filename)
