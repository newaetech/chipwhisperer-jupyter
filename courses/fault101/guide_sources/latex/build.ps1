# Build every .tex file in this folder to PDF (run it twice per file so the contents page fills in).
# Usage:  .\build.ps1                 build all guides and the template
#         .\build.ps1 Lab_2_1B_Explorer_Guide.tex     build one file
# Needs a LaTeX distribution (MiKTeX or TeX Live / TinyTeX) on the PATH. MiKTeX installs missing packages by itself;
# on TinyTeX / TeX Live install them once with:
#   tlmgr install colortbl needspace enumitem fancyhdr tocloft listings tcolorbox pgf caption float
param([string[]]$Files)
Set-Location -LiteralPath $PSScriptRoot
if (-not $Files) { $Files = Get-ChildItem -Filter *.tex | ForEach-Object { $_.Name } }
$extra = @()
if ((& pdflatex --version) -match "MiKTeX") { $extra = @("--enable-installer") }
foreach ($f in $Files) {
    Write-Host "== $f"
    for ($pass = 1; $pass -le 2; $pass++) {
        & pdflatex -interaction=nonstopmode -halt-on-error @extra $f | Out-Null
        if ($LASTEXITCODE -ne 0) { Write-Host "   FAILED in pass $pass - see $([IO.Path]::ChangeExtension($f, 'log'))"; break }
    }
}
