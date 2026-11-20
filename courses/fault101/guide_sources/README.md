# Fault101 student guides: generator sources

Mirrors `courses/sca101/guide_sources/`: the PDF student guides for the Fault101 Explorer notebooks are
generated from the Python story scripts in `pdf/` (reportlab backend; `pdfkit.py` here is the same shared
house-style helper copied from the SCA101 one - see that folder's README for the full helper reference,
markup syntax and the LaTeX backend, all of which work identically here).

## The guides

| Story script | PDF in `courses/fault101/` | Companion notebook |
|---|---|---|
| `pdf/story_explorer_fault2_1.py` | `Fault 2_1 Explorer - Student Guide.pdf` | `Fault 2_1 - Introduction to Voltage Glitching.ipynb` (hands-on edition) |
| `pdf/story_explorer_fault2_2.py` | `Fault 2_2 Explorer - Student Guide.pdf` | `Fault 2_2 - Voltage Glitching to Bypass Password Explorer.ipynb` |
| `pdf/story_explorer_fault2_3.py` | `Fault 2_3 Explorer - Student Guide.pdf` | `Fault 2_3 - Voltage Glitching to Memory Dump Explorer.ipynb` |

Build a PDF (needs `reportlab`; the SCA101 `guide_tools/.venv` has it):

```powershell
python story_explorer_fault2_1.py "..\..\Fault 2_1 Explorer - Student Guide.pdf"
python story_explorer_fault2_2.py "..\..\Fault 2_2 Explorer - Student Guide.pdf"
python story_explorer_fault2_3.py "..\..\Fault 2_3 Explorer - Student Guide.pdf"
```

Run from `pdf/`. `GUIDE_BACKEND=latex` writes a `.tex` file instead (see the SCA101 README) - no `.tex`
sources exist for these three yet, only the reportlab PDFs.

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

If you re-run the hardware exploration on a different kit and get different numbers (a different crash
edge, an actual over-read for 2_3, a less/more drifty 2_2), update the story script and regenerate - don't
hand-edit the PDF.
