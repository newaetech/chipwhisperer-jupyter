# Fault101 student guides: generator sources

Mirrors `courses/sca101/guide_sources/`: the PDF student guides for the Fault101 Explorer notebooks are
generated from the Python story scripts in `pdf/` (reportlab backend; `pdfkit.py` here is the same shared
house-style helper copied from the SCA101 one - see that folder's README for the full helper reference,
markup syntax and the LaTeX backend, all of which work identically here).

## The guides

| Story script | PDF in `courses/fault101/` | LaTeX in `latex/` | Companion notebook |
|---|---|---|---|
| `pdf/story_explorer_fault2_1.py` | `Fault 2_1 Explorer - Student Guide.pdf` | `Fault_2_1_Explorer_Guide.tex` | `Fault 2_1 - Introduction to Voltage Glitching Explorer.ipynb` (hands-on edition; this file also serves as the lab's only notebook - there is no separate stock worksheet version, unlike 2_2 and 2_3) |
| `pdf/story_explorer_fault2_2.py` | `Fault 2_2 Explorer - Student Guide.pdf` | `Fault_2_2_Explorer_Guide.tex` | `Fault 2_2 - Voltage Glitching to Bypass Password Explorer.ipynb` |
| `pdf/story_explorer_fault2_3.py` | `Fault 2_3 Explorer - Student Guide.pdf` | `Fault_2_3_Explorer_Guide.tex` | `Fault 2_3 - Voltage Glitching to Memory Dump Explorer.ipynb` |

Build a PDF (needs `reportlab`; the SCA101 `guide_tools/.venv` has it):

```powershell
python story_explorer_fault2_1.py "..\..\Fault 2_1 Explorer - Student Guide.pdf"
python story_explorer_fault2_2.py "..\..\Fault 2_2 Explorer - Student Guide.pdf"
python story_explorer_fault2_3.py "..\..\Fault 2_3 Explorer - Student Guide.pdf"
```

Run from `pdf/`. The `latex/` folder mirrors `courses/sca101/guide_sources/latex/` exactly (same
`latexkit.py`, `scaguide.sty`, `build.ps1`/`build.sh` - copied, not forked) and is built the same way:

```powershell
cd ..\latex
.\build.ps1                               # all three fault101 guides
.\build.ps1 Fault_2_2_Explorer_Guide.tex  # one file
```

All three compiled cleanly with MiKTeX (`--enable-installer`) on the first try, no missing packages beyond
what the SCA101 README already lists. To regenerate a `.tex` from its story script instead of hand-editing
it (the two can drift apart otherwise):

```powershell
cd ..\pdf
$env:GUIDE_BACKEND = "latex"
python story_explorer_fault2_2.py "..\latex\Fault_2_2_Explorer_Guide.tex"
Remove-Item Env:GUIDE_BACKEND
```

## Why these three guides read the way they do

Every "what you should see" number in all three was measured on one real kit (Husky + CW313 +
CW312T-SAM4S, Windows 11, ChipWhisperer 6.0.0, firmware 1.5.0) - not invented, and not carried over from
the stock lab's own suggested ranges, which did **not** reproduce on this kit (same lesson as the SCA101
guides' "the SOLN ranges do not work on this kit"). Two findings worth knowing before editing these:

- **Settings drift within a session.** A `(width, offset, ext_offset)` that gave a clean, repeatable result
  could go completely quiet twenty minutes later with nothing else changed (board temperature rising from
  continuous glitching is the suspected cause). Both the 2_2 and 2_3 guides call this out explicitly and
  hedge their numbers accordingly - don't tighten that language without re-measuring.
- **Fault 2_3's firmware truncates rather than extends.** The lab is named "memory dump" (an over-read), but
  on this kit the fault only ever shortened the bootloader's reply, across several thousand search attempts.
  The guide reports this honestly instead of assuming the dramatic direction.
- **Fault 2_1's crash region is not one simple edge.** A full-range width scan (0-2296) shows two separate
  red bands with a gap of normal behaviour between them, not "grey then red and staying red" - re-verified
  on 2026-11-20 and both the notebook and guide were corrected to describe this accurately. If you ever find
  the notebook's own markdown and a guide's "what you should see" disagree, re-run the experiment and fix
  whichever one is wrong rather than assuming the guide is the source of truth.
- **Fault 2_2's Experiment 8 ("choose your own password") edits real firmware on disk.** Its helper
  functions (`use_password`, `restore_original_password`) open `simpleserial-glitch.c` with `newline=""` on
  both read and write specifically to avoid Python's default text-mode behaviour, which silently converts
  the file's line endings to the OS default on write and turns a one-line edit into a whole-file diff (hit
  this for real while building the chapter). Keep that pattern in any similar firmware-editing helper added
  to another guide.

If you re-run the hardware exploration on a different kit and get different numbers (a different crash
edge, an actual over-read for 2_3, a less/more drifty 2_2), update the story script **and** the notebook's
own markdown together and regenerate the PDF - don't hand-edit the PDF, and don't let the two fall out of
sync with each other.
