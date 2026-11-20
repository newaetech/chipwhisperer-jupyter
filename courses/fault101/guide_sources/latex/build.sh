#!/bin/sh
# Build every .tex file in this folder to PDF (run twice per file so the contents page fills in).
# Usage:  ./build.sh                 build all guides and the template
#         ./build.sh Lab_2_1B_Explorer_Guide.tex     build one file
# Needs a LaTeX distribution (TeX Live, MiKTeX or TinyTeX) on the PATH. If a package is missing on TeX Live / TinyTeX:
#   tlmgr install colortbl needspace enumitem fancyhdr tocloft listings tcolorbox pgf caption float
cd "$(dirname "$0")" || exit 1
extra=""
pdflatex --version | grep -qi miktex && extra="--enable-installer"
files="$*"
[ -z "$files" ] && files=$(ls *.tex)
for f in $files; do
    echo "== $f"
    for pass in 1 2; do
        pdflatex -interaction=nonstopmode -halt-on-error $extra "$f" >/dev/null || { echo "   FAILED in pass $pass - see ${f%.tex}.log"; break; }
    done
done
