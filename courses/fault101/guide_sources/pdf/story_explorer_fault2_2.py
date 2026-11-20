"""Builds 'Fault 2_2 Explorer - Student Guide.pdf'.   Usage: python story_explorer_fault2_2.py "<output pdf>" """
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if os.environ.get("GUIDE_BACKEND") == "latex":
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "latex"))
    import latexkit as K
    from latexkit import *
else:
    import pdfkit as K
    from pdfkit import *

OUT = sys.argv[1]
NBNAME = "Fault 2_2 - Voltage Glitching to Bypass Password Explorer.ipynb"
GUIDE_VERSION = "1.0 - November 2026"

doc = K.init(OUT,
             header_left="ChipWhisperer Fault101  -  Fault 2_2 Explorer Guide",
             header_right="Password Bypass Explorer",
             footer_left="Companion to: " + NBNAME,
             title="Fault101 Fault 2_2 Explorer - Step-by-Step Student Guide",
             subject="Step-by-step guide to the Fault 2_2 Voltage Glitching password-bypass Explorer: why Fault 2_1's settings do not carry over, and how to search for ones that do",
             roadmap=[("1  Reuse", "Fault 2_1's setting"), ("2 - 3  Map", "the nearby area"), ("4  Search", "a wider box"),
                      ("5 - 6  Zoom", "in and compare"), ("7  Check", "the guess itself")])


def EDIT(rows):
    return table([["Variable", "Default", "What it does"]] + rows, [1.5 * inch, 1.0 * inch, W - 2.5 * inch])


S = []

# ================================================================ COVER
S += [*K.cover("FAULT101  -  FAULT 2_2  (EXPLORER)", ("Password Bypass", "Explorer"),
                  "Step-by-step student guide: searching for the fault that makes a wrong password pass"),
      P("Fault 2_2 asks the same question as Fault 2_1, against different firmware: can a brief voltage glitch make "
        "a check come out wrong? Here the check is a password comparison instead of a counting loop. This guide's "
        "biggest lesson arrives early: **the settings that worked perfectly for Fault 2_1 do almost nothing useful "
        "here** - they just crash the target. Finding a setting that actually flips the password check's answer "
        "means widening the search, and even then, what you find will not sit still: these settings **drift** "
        "over the course of a session. **This lab needs real hardware; there is no simulated mode.**"),
      Spacer(1, 10)]
S += callout("tip", [
    "This guide goes **with** the notebook - it does not replace it. Keep the notebook open next to this PDF."], title="HOW TO USE THIS GUIDE")
S += [P("**Which files are which**", h3)]
S += table([
    ["File (folder: jupyter/courses/fault101/)", "What it is", "Open it?"],
    ["`%s`" % NBNAME, "The Explorer. Everything in this guide happens here.", "**Yes**"],
    ["`Fault 2_2 - Voltage Glitching to Bypass Password.ipynb`", "The original (non-Explorer) lab.", "Optional"],
    ["`SOLN_Fault 2_2 - ...ipynb`", "Answer key for the original lab.", "If stuck"],
    ["`firmware/mcu/simpleserial-glitch/simpleserial-glitch.c`", "(a different folder: `chipwhisperer/firmware/...`) The `password()` function this lab targets.", "Background"],
], [3.0 * inch, 3.1 * inch, W - 6.1 * inch])
S += [P("**The four colored boxes you will see everywhere**", h3)] + legend()
S += [Spacer(1, 4),
      P("Guide version %s. Every number in this guide was measured on one real kit: ChipWhisperer-Husky, a CW313 "
        "board and a CW312T-SAM4S target (Windows 11, Python 3.12, ChipWhisperer 6.0.0, firmware 1.5.0) - the same "
        "kit as the Fault 2_1 guide. **Read the drift warning after Experiment 5 before you trust any single "
        "number in this guide**: several of the exact figures below changed - in one case from 15%% success to "
        "0%% - when we re-measured them only minutes later in the same session." % GUIDE_VERSION, small),
      PageBreak()]

# ================================================================ CONTENTS
S += K.contents()

# ================================================================ BIG PICTURE
S += [H1("The big picture")]
S += [P("**What is different from Fault 2_1?** The target firmware now runs `password()`: it compares a 5-byte "
        "guess against a built-in constant (`\"touch\"` - a fixed string baked into this open-source demo "
        "firmware, not a secret worth hiding) and reports pass or fail. Unlike the SCA101 password lab, this "
        "check never stops early: it always runs all five comparisons, so there is no timing information to "
        "measure - the **only** way to make a wrong guess pass is to disturb the chip while it runs, corrupting "
        "the comparison's result directly.")]
S += [P("**Why doesn't Fault 2_1's setting just work again?** A glitch setting disturbs *whatever instruction is "
        "executing at that instant*. The counting loop and the password check are different code, running at "
        "different times, so the instant that mattered for one means nothing for the other. This Explorer makes "
        "you discover that the hard way before showing you how to search past it.")]
S += [P("Your path through the notebook:", h3), Roadmap(W), Spacer(1, 6)]
S += table([
    ["Experiment", "What you do", "What you learn"],
    ["1", "Fire Fault 2_1's exact winning setting at this firmware.", "It does not bypass anything - it just crashes the target."],
    ["2", "Scan width to map this firmware's own crash edge.", "A real crash boundary exists here too, at a similar width - but no success hides next to it."],
    ["3", "Scan `ext_offset` widely at that edge.", "A periodic crash pattern, but still no success anywhere nearby."],
    ["4", "Run a randomized search across a much bigger box.", "Success lives in a completely different corner of the search space - and how often you find one varies a lot between runs."],
    ["5", "Zoom in on a success and map its neighbourhood.", "A usable plateau in width/offset - and a hard lesson: these settings drift over time."],
    ["6", "Compare `hp` alone against `hp + lp` together.", "Stronger is not always better - and even that comparison needs re-checking, because of the drift."],
    ["7", "Check whether the guess itself matters.", "It does not: this is a control-flow fault, not a side channel."],
], [0.8 * inch, 2.7 * inch, W - 3.5 * inch], bold_first_col=True)
S += [PageBreak()]

# ================================================================ BEFORE YOU START
S += [H1("Before you start")]
S += [P("Same kit and checklist as Fault 2_1.")]
S += table([
    ["", "You need", "How to check"],
    ["[  ]", "Fault 2_1 completed (same setup, same hardware checklist).", "You can fire a glitch and see `normal`/`reset`/`success` outcomes."],
    ["[  ]", "**ChipWhisperer-Husky** plugged straight into a USB port (not through a hub).", "Lab 0's hardware test ends with `hardware OK (disconnected again)`."],
    ["[  ]", "**CW312T-SAM4S** target seated on the **CW313** board, ribbon connected.", "See the SCA101 Linux guide, Part 4.2."],
    ["[  ]", "The Husky **`Crowbar`** SMA cable connected to the CW313's second SMA socket.", "Without it, every glitch here will show as `normal` too."],
    ["[  ]", "No other notebook holding the Husky open.", "**File > Shut Down Notebook** in any other open notebook."],
], [0.45 * inch, 3.6 * inch, W - 4.05 * inch])
S += callout("warn", [
    "**This lab can take longer than Fault 2_1.** Experiment 4's randomized search ran for up to 4 minutes on our "
    "kit before finding a working setting, and sometimes found nothing at all in that time. That is expected - "
    "plan for it, and do not assume something is broken just because a search does not finish quickly."])

# ================================================================ EXPERIMENT 1
S += [H1("Experiment 1 - try Fault 2_1's winning setting here")]
S += [P("**Goal:** find out whether the setting that reliably glitched Fault 2_1's counting loop "
        "(`WIDTH=1770, OFFSET=2670, EXT_OFFSET=1`) does anything useful against this firmware's password check.")]
S += [P("**Do this:** run the sanity-check cell first (it confirms the correct password `touch` passes and wrong "
        "guesses fail, with no glitching). Then run the Experiment 1 cell with a **wrong** guess at Fault 2_1's "
        "setting.")]
S += callout("see", [
    "**Almost every shot is `reset`.** The setting that calmly disturbed a 2500-count loop is far too strong for "
    "whatever the chip is doing at that same instant while checking a password - it simply crashes the target, "
    "every time, regardless of which wrong guess you send. A glitch setting belongs to *one piece of code at one "
    "moment*, not to the chip in general."])

# ================================================================ EXPERIMENT 2
S += [H1("Experiment 2 - map this firmware's own crash edge")]
S += [P("**Goal:** Experiment 1 sat deep inside a crash region. Find where that region's edge actually is for "
        "**this** firmware, the same way Fault 2_1 Experiment 2 did for the counting loop.")]
S += numbered([
    "Run the cell as it is: it scans width at a fixed offset and ext_offset, with a wrong guess.",
    "Change `EXT_OFFSET` to 2, then to 0. Does the crash region change?",
    "Zoom in with `WIDTH_STEP = 2` around the edge you find.",
])
S += callout("see", [
    "At `ext_offset=1` (offset 2670): width 1750 and below is `normal`; 1758-1764 is a mix of `normal` and "
    "`reset`; 1766 and above is `reset` every time. `ext_offset=2` gives a very similar edge a couple of steps "
    "earlier. `ext_offset=0`, and every value from 3 up to about 5, never disturbs the target at all across this "
    "whole width range - only cycles 1 and 2 are sensitive here, exactly like Fault 2_1's counting loop. **No "
    "width in this scan ever produced a `success`.** Crashing this check is easy; making it lie from here is not."])

# ================================================================ EXPERIMENT 3
S += [H1("Experiment 3 - scan a wide range of moments")]
S += [P("**Goal:** this password check's trigger window stays high much longer than one or two clock cycles - it "
        "covers five comparisons plus a serial write-back. Scan `ext_offset` widely to see the rest of that "
        "window.")]
S += [P("**Do this:** run the cell as it is - a width just below Experiment 2's edge, scanned across "
        "`ext_offset` 0 to 60.")]
S += callout("see", [
    "`reset` appears in short bursts roughly every 20 cycles (around 1-2, 20-25, 33, 40-42, 53 and 59-60), with "
    "`normal` everywhere else - probably the serial/UART handling inside the trigger window, not the comparison "
    "itself. **Still no `success` anywhere in this range.** We have now swept 60 different moments at a width "
    "right on an edge, and found nothing: whatever works here, it is not a small tweak away from where Fault 2_1's "
    "pattern would suggest looking."])

# ================================================================ EXPERIMENT 4
S += [H1("Experiment 4 - widen the net: a randomized search")]
S += [P("**Goal:** three experiments in the 'obvious' area found nothing but crashes. Rather than inching the "
        "ranges wider by hand, let the computer try **random** combinations across a much bigger box and watch "
        "for the first success.")]
S += [P("**Do this:** run the cell as it is. **This can take a few minutes** and may find nothing within the "
        "time budget - both are normal outcomes here.")]
S += callout("see", [
    "This is the one experiment where how much luck you need varies a lot between runs. In one run, a search "
    "like this tried **7248 settings over about 230 seconds and found only 2 successes** - roughly 1 in 3600 "
    "attempts. Run again later in the same session, it found one in **1149 attempts, about 46 seconds** - a very "
    "different hit rate (see the drift warning after Experiment 5: the *size* of the good region itself seems to "
    "change over time, not just its exact location). What stayed consistent across every run: successes shared a "
    "**much bigger width (close to 1970-1990) and a much bigger offset (close to 3000-3100)** than anywhere in "
    "Experiments 1 to 3 - a completely different corner of the search space from the one that merely crashes the "
    "target."])
S += callout("tip", [
    "**If your run finds nothing in the time budget, that is a real result, not a failure.** It means this "
    "particular fault, from this glitch circuit, did not defeat this check within the search you tried - not "
    "every fault-and-target combination gives in, and recording that honestly is part of a real security "
    "evaluation."])

# ================================================================ EXPERIMENT 5
S += [H1("Experiment 5 - zoom in on what you found")]
S += [P("**Goal:** turn one lucky random hit into a setting you understand, and see how wide the 'good' "
        "neighbourhood actually is.")]
S += numbered([
    "Put the `(width, offset, ext_offset)` Experiment 4 found into `CENTER` (or start from ours: `(1979, 3071, 121)`).",
    "Run the cell: it tries a small grid of neighbours around `CENTER`, all at the same `ext_offset`.",
    "Change `EXT_OFFSET_TRY` to a few cycles either side of `CENTER`'s. Is the neighbourhood just as wide there?",
])
S += callout("see", [
    "When we first mapped it, most of a 20-by-40-step block around `(1979, 3071)` gave at least one success out "
    "of 8 shots, with individual points ranging from about 10% to 40% - a genuinely usable plateau, much wider "
    "than the thin diagonal line Fault 2_1 found. `ext_offset` was pickier: only a few specific values (121 and "
    "130 among the ones we tried, and 89 at a different width/offset) gave any success at all there."])
S += callout("warn", [
    "**These settings drift.** When we came back to the *exact same* `(1979, 3071, 121)` later in the same "
    "session, it gave **zero** successes in 60 shots - not one. A nearby point our random search found "
    "independently, `(1973, 3083, 141)`, was still giving occasional successes at that point. Nothing about the "
    "wiring or the code had changed; the glitch circuit's precise sweet spot moves over time, likely with the "
    "board's temperature and small clock drift, by more than you might expect. **Treat every specific number in "
    "this guide as 'this was possible,' not as a guarantee you can reproduce on demand.** Always re-measure with "
    "fresh shots before trusting a setting, and if one stops working, try its near neighbours before assuming it "
    "never worked at all."], title="WATCH OUT")

# ================================================================ EXPERIMENT 6
S += [H1("Experiment 6 - does a stronger glitch work better here too?")]
S += [P("**Goal:** Fault 2_1 found that `hp + lp` together crashed the target at a smaller width than `hp` alone "
        "- a stronger glitch. Does using both transistors also help bypass **this** check?")]
S += [P("**Do this:** run the cell at your best setting from Experiment 5, once with `hp` only and once with "
        "`hp + lp`.")]
S += callout("see", [
    "In one back-to-back comparison at a setting that was working at the time: `hp` alone gave about 15% success "
    "(6 of 40), `hp + lp` together gave **0%** - every shot was a `reset`. The stronger glitch did not help; it "
    "pushed the disturbance past the useful instant straight into a crash - the opposite of Fault 2_1's counting "
    "loop. **The caveat:** because these settings drift, treat a single comparison like this as one data point, "
    "not a law - re-run both with fresh shots at your own current best setting before you trust which one wins. "
    "What should not change is the general lesson: which transistor combination helps depends on the code being "
    "glitched, not just on the physical circuit, so it is always worth comparing both instead of assuming "
    "'stronger is always better'."])

# ================================================================ EXPERIMENT 7
S += [H1("Experiment 7 - does the guess itself matter?")]
S += [P("**Goal:** measure your best setting's reliability, and check something important: does the *content* of "
        "the wrong guess change anything? In the SCA101 power-analysis lab, the guess mattered enormously - that "
        "attack is a side channel. If this fault works (or doesn't) regardless of what you send, that tells you "
        "it is a pure control-flow corruption, not a leak of any kind.")]
S += [P("**Do this:** run the cell as it is - it fires the same number of glitches at several different wrong "
        "guesses, back-to-back at the same setting, and add a guess of your own.")]
S += callout("see", [
    "Run all the guesses back-to-back (so drift has the least chance to matter between them) and compare their "
    "success counts **to each other**, not to a fixed target percentage. On our kit they came out close to each "
    "other, whatever the absolute level happened to be at that moment - no guess stood out as easier or harder, "
    "including a guess that was only one character away from the real password. That confirms the lesson from "
    "the firmware listing: the fault corrupts the comparison's *outcome*, not a part of it that depends on which "
    "byte was wrong, so there is nothing to gain from a 'smarter' wrong guess - unlike a real side-channel attack, "
    "where the guess is everything."])

# ================================================================ CHALLENGES
S += [H1("Challenges (optional)")]
S += numbered([
    "**Characterize the second spot.** Map the neighbourhood around `(1985, 2999, 89)` the way Experiment 5 mapped `(1979, 3071, 121)`. Is it as wide?",
    "**A tighter automatic search.** Now that you know roughly where the good region is, write a `GlitchController` search (like Fault 2_1 Experiment 4) with `width` and `offset` ranges centred on it. How much faster is it than Experiment 4's blind random search?",
    "**Does `repeat` help or hurt?** Try `REPEAT = 2` at your best setting. Does the success rate go up or down?",
    "**A fourth spot.** Run Experiment 4 again (a new random seed) for several minutes. Does it always find settings with a large width and a large offset, or can a bypass exist somewhere else too?",
])

# ================================================================ TROUBLESHOOTING
S += [H1("If something goes wrong")]
S += table([
    ["What you see", "Most likely cause", "What to do"],
    ["The sanity check does not print `passok=1` for `touch`.", "Firmware did not flash, or a stale serial buffer.", "Re-run the build/flash cells; re-run `reboot_flush()`."],
    ["Every shot is `normal`, never `reset` or `success`, even at a huge width.", "The Crowbar SMA cable is not connected.", "Fit the cable (Fault 2_1's guide), run the setup cells again."],
    ["Every shot is `reset`.", "You are inside a crash region for this width/offset.", "Try a smaller width, or a different part of the search space (Experiment 4)."],
    ["Experiment 4 finds nothing in the time budget.", "A real result - see Experiment 4's 'what you should see'.", "Run it again (new random settings), or raise `TIME_BUDGET_S`."],
    ["A setting that worked earlier stops working.", "Drift (see the warning after Experiment 5).", "Re-measure with fresh shots; try nearby settings too."],
    ["`OSError: Could not find ChipWhisperer`.", "Husky unplugged, or another notebook still holds it.", "Plug it in; shut down every other notebook; restart this kernel."],
    ["`USBErrorPipe` / `Unknown hwInfoVer`.", "The Husky's USB link or FPGA stopped answering.", "Unplug and replug the Husky directly into the computer; restart the kernel."],
    ["A cell was interrupted (Stop button).", "Target or glitch hardware may be left in an odd state.", "Run `recover()` in a new cell."],
], [2.0 * inch, 2.1 * inch, W - 4.1 * inch])

# ================================================================ APPENDIX
S += [H1("Appendix - every variable you can edit")]
S += EDIT([
    ["`GUESS`", '`b"xxxxx"`', "A 5-byte wrong guess sent to the password check."],
    ["`WIDTH`, `OFFSET`, `EXT_OFFSET`", "varies", "The glitch settings fired, in Husky phase-shift steps / clock cycles."],
    ["`REPEAT`", "1", "Number of glitch pulses fired per shot."],
    ["`SHOTS`", "varies", "How many glitches to fire for one measurement."],
    ["`WIDTH_START/STOP/STEP`", "varies", "The width range scanned in Experiment 2."],
    ["`EXT_START/STOP/STEP`", "0 / 60 / 1", "The ext_offset range scanned in Experiment 3."],
    ["`WIDTH_RANGE`, `OFFSET_RANGE`, `EXT_OFFSET_RANGE`", "wide", "The box searched randomly in Experiment 4."],
    ["`TIME_BUDGET_S`", "240", "How long Experiment 4 keeps trying before giving up."],
    ["`CENTER`", "a found success", "The `(width, offset, ext_offset)` Experiment 5 zooms in around."],
    ["`WIDTH_STEPS`, `OFFSET_STEPS`", "lists", "Offsets from `CENTER` tried in Experiment 5's grid."],
    ["`GUESSES`", "list", "The guesses compared in Experiment 7."],
])

# ================================================================ GLOSSARY
S += [H1("Appendix - Glossary")]
S += table([
    ["Term", "Meaning"],
    ["Voltage glitch / fault injection", "See the Fault 2_1 guide's glossary - the same concepts apply here."],
    ["Control-flow corruption", "A fault that changes *what the program does* (skips a step, flips a result) rather than leaking information through timing or power, as a side-channel attack would."],
    ["Drift", "The tendency of a glitch setting's success rate to change over time on the same kit, likely with temperature and small clock variations - not a measurement mistake."],
    ["Plateau", "A region of settings (not just one point) that all give some success rate - as opposed to a single pinpoint setting."],
    ["`passok`", "The one-byte result the password check sends back: 1 for pass, 0 for fail."],
], [1.7 * inch, W - 1.7 * inch])

S += K.notice()

K.build(doc, S)
