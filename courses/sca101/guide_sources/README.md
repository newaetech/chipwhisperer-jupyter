# SCA101 student guides: LaTeX and generator sources

The student guides for the Explorer notebooks are PDFs. This folder holds everything needed to **edit them, rebuild them, or write a new one**:

| Folder | What it is |
|---|---|
| `latex/` | **LaTeX sources.** `scaguide.sty` (the house style), one `.tex` per guide, a `template_explorer_guide.tex` for new guides, the `figures/` they use, and build scripts. |
| `pdf/` | The **Python generator**: one `story_*.py` script per guide (the content), `pdfkit.py` (draws the PDFs with reportlab) and the figures. The same scripts can also write the LaTeX files (see below). |

The notebooks themselves (`*.ipynb`) are not LaTeX: edit those in Jupyter. These sources are for the **PDF guides that go with them**.

## The guides

| LaTeX file | Builds | PDF in `courses/sca101/` |
|---|---|---|
| `latex/Lab_2_1A_Explorer_Guide.tex` | Lab 2_1A Explorer, step by step (v1.1) | `Lab 2_1A Explorer - Student Guide.pdf` |
| `latex/Lab_2_1B_Explorer_Guide.tex` | Lab 2_1B Explorer, including "choose your own password" (v1.2) | `Lab 2_1B Explorer - Student Guide.pdf` |
| `latex/Lab_2_1A_Real_Husky_Guide.tex` | What a real Husky shows for Lab 2_1A (v1.0) | `Lab 2_1A - What You Should See on a Real Husky.pdf` |
| `latex/template_explorer_guide.tex` | A short skeleton that uses every macro once | - |

The Linux install guide is built by the same Python generator (`story_linux.py`) but is not part of this folder.

## Build a PDF from the LaTeX (the easy way to edit)

1. Install LaTeX: **MiKTeX** (Windows; it installs missing packages by itself), **TeX Live** or **TinyTeX**. Or use **Overleaf**: upload the whole `latex/` folder and choose `pdfLaTeX` as the compiler.
2. From the `latex/` folder:

```powershell
.\build.ps1                                  # all guides and the template
.\build.ps1 Lab_2_1B_Explorer_Guide.tex      # one file
```

```bash
./build.sh                                   # Linux / macOS
./build.sh Lab_2_1B_Explorer_Guide.tex
```

Or by hand: `pdflatex Lab_2_1B_Explorer_Guide.tex`, **twice** (the second run fills in the contents page).

Packages used (all standard): `geometry xcolor array longtable needspace float enumitem fancyhdr tocloft caption graphicx tikz tcolorbox listings hyperref`, and `colortbl` (loaded by xcolor's `table` option). On TeX Live / TinyTeX install any that are missing with
`tlmgr install colortbl needspace enumitem fancyhdr tocloft listings tcolorbox pgf caption float`.

**Edit the `.tex` directly.** The text, tables and call-out boxes are ordinary LaTeX: change a sentence, a table cell or a number and rebuild. The LaTeX version looks like the reportlab PDF but is not identical: Helvetica is used when the `psnfss` fonts are installed (otherwise Latin Modern Sans), and a page break can land one page earlier or later.

## Write a new guide

Copy `latex/template_explorer_guide.tex`, rename it, and replace the text. It uses every piece of the style once, with comments:

| You write | You get |
|---|---|
| `\guidecover{KICKER}{Title\\Line 2}{Subtitle}` | the cover heading |
| `\guidehone{...}`, `\guidehtwo{...}`, `\guidehthree{...}` | chapter heading, section heading (both in the contents), small teal heading |
| `\guidestep{1.1}{Heading}` | a numbered step with a navy badge (in the contents) |
| `\begin{guidecallout}{do\|see\|ifnot\|warn\|tip}{TITLE} ... \end{guidecallout}` | the coloured DO THIS / YOU SHOULD SEE / IF IT DOESN'T / WATCH OUT / GOOD TO KNOW boxes |
| `\begin{guidecode} ... \end{guidecode}` | a code box (verbatim) |
| `\code{...}`, `\codesmall{...}` | inline code (normal text / inside tables) |
| `longtable` with `R{0.3}` columns, `\hdrcell{...}` | the navy-header tables (see the template) |
| `\guidefigure{figures/x.png}{0.8}{Caption}` | a centred picture, width as a fraction of the page |
| `\guidelegend`, `\tableofcontents` | the four-box legend, the contents page |

Put pictures in `latex/figures/`. Special characters in normal text need a backslash: `\_ \& \% \# \$`.

## Regenerate from the Python (when you change the content a lot)

The `.tex` files in `latex/` were **generated** from the story scripts in `pdf/`. If you prefer to edit the content in Python (one place for the PDF and the LaTeX), change the story and regenerate - note that this **overwrites** hand edits made to the `.tex`.

```powershell
cd pdf
$env:GUIDE_BACKEND = "latex"                  # write LaTeX instead of a PDF
python story_explorer_2_1b.py ..\latex\Lab_2_1B_Explorer_Guide.tex
Remove-Item Env:GUIDE_BACKEND                 # back to PDF output
```

```bash
cd pdf
GUIDE_BACKEND=latex python story_explorer_2_1b.py ../latex/Lab_2_1B_Explorer_Guide.tex
```

The LaTeX back-end (`latex/latexkit.py`) needs only the Python standard library. To build the **reportlab PDFs** instead, install reportlab (`python -m pip install reportlab`) and run `python story_explorer_2_1b.py "Lab 2_1B Explorer - Student Guide.pdf"` (no `GUIDE_BACKEND`).

In a story script, content is written with a small set of helpers (`H1`, `H2`, `STEP`, `P`, `table`, `callout`, `code`, `numbered`, `FIG`, ...): see `story_explorer_2_1b.py` for a long example. Inline markup in the text: `` `code` ``, `**bold**`, `__italic__`, `[text](url)`.

## Notes

* Every "real chip" number in these guides was measured on a Husky + CW313 + SAM4S (Windows 11, ChipWhisperer 6.0.0, firmware 1.5.0). The captures behind them are in `courses/sca101/traces/hardware_reference/`.
* The figures are static PNGs. Pictures that come from running a notebook (for example `hw_step2.png`) are screenshots of that notebook's output; if you change the notebook, regenerate them from it.
