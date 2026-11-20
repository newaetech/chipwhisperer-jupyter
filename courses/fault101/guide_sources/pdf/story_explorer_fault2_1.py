"""Builds 'Fault 2_1 Explorer - Student Guide.pdf'.   Usage: python story_explorer_fault2_1.py "<output pdf>" """
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
NBNAME = "Fault 2_1 - Introduction to Voltage Glitching Explorer.ipynb"
GUIDE_VERSION = "1.0 - November 2026"

doc = K.init(OUT,
             header_left="ChipWhisperer Fault101  -  Fault 2_1 Explorer Guide",
             header_right="Voltage Glitching Explorer",
             footer_left="Companion to: " + NBNAME,
             title="Fault101 Fault 2_1 Explorer - Step-by-Step Student Guide",
             subject="Step-by-step guide to the Fault 2_1 Voltage Glitching Explorer notebook: find a working glitch on real hardware by hand",
             roadmap=[("1  Fire", "a glitch by hand"), ("2 - 3  Scan", "width and timing"), ("4  Search", "automatically"),
                      ("5 - 6  Map", "and strengthen"), ("7  Measure", "reliability")])


def EDIT(rows):
    return table([["Variable", "Default", "What it does"]] + rows, [1.5 * inch, 1.0 * inch, W - 2.5 * inch])


S = []

# ================================================================ COVER
S += [*K.cover("FAULT101  -  FAULT 2_1  (EXPLORER)", ("Voltage Glitching", "Explorer"),
                  "Step-by-step student guide: find a working glitch on your own kit, by hand"),
      P("Fault 2_1 introduces **voltage glitching**: briefly pulling a chip's power rail down to make it misbehave. This guide goes "
        "with a **hands-on notebook** that walks you through finding a working glitch on your own ChipWhisperer-Husky, one "
        "experiment at a time - first by firing single glitches yourself and watching what happens, then by letting the computer "
        "search a range of settings for you. **This lab needs real hardware; there is no simulated mode.**"),
      Spacer(1, 10)]
S += callout("tip", [
    "This guide goes **with** the notebook - it does not replace it. Keep the notebook open next to this PDF. "
    "Every experiment tells you what to run, what to change, and what our own kit showed."], title="HOW TO USE THIS GUIDE")
S += [P("**Which files are which**", h3)]
S += table([
    ["File (folder: jupyter/courses/fault101/)", "What it is", "Open it?"],
    ["`%s`" % NBNAME, "The Explorer. Everything in this guide happens here.", "**Yes**"],
    ["`SOLN_Fault 2_1 - ...ipynb`", "Answer key for the original (non-Explorer) lab.", "If stuck"],
    ["`firmware/mcu/simpleserial-glitch/simpleserial-glitch.c`", "(a different folder: `chipwhisperer/firmware/...`) The target firmware. The function glitched in this lab is `glitch_loop()`: two nested loops that count from 0 to 2500.", "Background"],
], [3.0 * inch, 3.1 * inch, W - 6.1 * inch])
S += [P("**The four colored boxes you will see everywhere**", h3)] + legend()
S += [Spacer(1, 4),
      P("Guide version %s. Every number in this guide was measured on one real kit: ChipWhisperer-Husky, a CW313 board and a "
        "CW312T-SAM4S target (Windows 11, Python 3.12, ChipWhisperer 6.0.0, firmware 1.5.0). Your kit will very likely need "
        "**different** width/offset numbers - voltage glitching depends on the exact cabling and board, more than clock glitching "
        "does. The **method** in each experiment (scan, zoom in, compare) is what carries over; treat every specific number here "
        "as an example, not a target to match. **Settings can also drift within a single session on the same kit** - read the "
        "note after Experiment 2 before you assume a number here is permanent." % GUIDE_VERSION, small),
      PageBreak()]

# ================================================================ CONTENTS
S += K.contents()

# ================================================================ BIG PICTURE
S += [H1("The big picture")]
S += [P("**What is voltage glitching?** Digital logic needs its supply voltage to stay within a safe range to work correctly. "
        "If you briefly short the supply rail toward ground - for a few nanoseconds, at exactly the wrong moment - some "
        "transistors can fail to switch, which can flip a bit, skip an instruction, or corrupt a value in a register. The chip "
        "keeps running afterwards; it just computed something wrong for an instant. This is called a **fault**, and studying "
        "how a short voltage glitch creates one is called **fault injection**: a standard technique for evaluating whether a "
        "device's security logic (a password check, a signature check, a loop that is only supposed to run once) can be forced "
        "down the wrong path by a hardware fault it was never designed to tolerate.")]
S += [P("**What does the test firmware do?** `glitch_loop()` counts from 0 to 2500 in two nested loops and reports the final "
        "count. With no fault it is always exactly 2500. A fault that skips or corrupts an increment, or exits a loop early, "
        "changes that number. Because the correct answer is always the same, you know immediately whether a glitch did "
        "anything: if the reported count is not 2500, something was disturbed.")]
S += [P("**What is different about the Explorer?** The original lab goes straight to the automatic search. This Explorer has you "
        "fire single glitches by hand first, so you can see what `normal`, `reset` and `success` actually look like before you "
        "ask a loop to find thousands of them for you.")]
S += [P("Your path through the notebook:", h3), Roadmap(W), Spacer(1, 6)]
S += table([
    ["Experiment", "What you do", "What you learn"],
    ["1", "Fire single glitches by hand at one setting, then a few neighbours.", "The three outcomes (normal / reset / success) and the four glitch knobs."],
    ["2", "Scan the glitch width at a fixed offset.", "The target tolerates short glitches and crashes above a 'crash edge' - and a window of successes sits just below it."],
    ["3", "Scan `ext_offset` (which clock cycle is glitched).", "Only specific moments are vulnerable; the rest are harmless or just crash the target."],
    ["4", "Run the automatic search over a range you choose.", "Why a GlitchController beats hand-firing, and how the step size trades speed against luck."],
    ["5", "Draw a width x offset crash map.", "The whole picture at once: a slanted crash edge, with successes in a thin band along it."],
    ["6", "Compare `repeat` and the HP/LP transistors.", "Whether making the glitch 'stronger' actually helps on this kit."],
    ["7", "Measure how reliable your best setting is.", "A single success does not mean a setting works reliably; you need many shots to know its success rate."],
], [0.8 * inch, 2.6 * inch, W - 3.4 * inch], bold_first_col=True)
S += [PageBreak()]

# ================================================================ BEFORE YOU START
S += [H1("Before you start")]
S += [P("Tick every row. Almost every 'nothing happens' problem in this lab traces back to something on this list.")]
S += table([
    ["", "You need", "How to check"],
    ["[  ]", "**Lab 0 - SCA101 Setup** passed (same environment is used here).", "ChipWhisperer, numpy and matplotlib import without errors."],
    ["[  ]", "**ChipWhisperer-Husky** plugged straight into a USB port (not through a hub).", "Lab 0's hardware test ends with `hardware OK (disconnected again)`."],
    ["[  ]", "**CW312T-SAM4S** target seated on the **CW313** board, connected to the Husky with the 20-pin ribbon.", "See the SCA101 Linux guide, Part 4.2, for pictures of this assembly."],
    ["[  ]", "**The Husky `Crowbar` SMA cable** connected to the CW313's second SMA socket (the `Pos`/measurement cable alone is not enough).", "Without it, every glitch in this lab will show as `normal` - never `reset`, never `success`."],
    ["[  ]", "No other notebook holding the Husky open.", "**File > Shut Down Notebook** in any other open notebook before you start this one."],
], [0.45 * inch, 3.6 * inch, W - 4.05 * inch])
S += callout("warn", [
    "**The single most common reason this lab 'does nothing':** the Crowbar cable. The `Pos` SMA cable only lets the Husky "
    "*measure* power; a separate cable (`Crowbar`, to the CW313's other SMA socket) is what actually shorts the rail. If every "
    "shot in Experiment 1 comes back `normal`, check this cable before anything else."])
S += callout("tip", [
    "**You cannot damage the kit by trying 'bad' settings.** A `reset` just means the target crashed; the notebook reboots it "
    "automatically. If a cell is stopped halfway (the square Stop button), run `recover()` in a new cell to put the glitch "
    "hardware and the target back to a known state."], title="GOOD TO KNOW")

# ================================================================ EXPERIMENT 1
S += [H1("Experiment 1 - fire a glitch by hand")]
S += [P("**Goal:** see the three things a single glitch can do, and learn what the four knobs mean.")]
S += table([
    ["Knob", "What it controls", "Husky range"],
    ["`WIDTH`", "how **long** the glitch is (how long the power is pulled down).", "0 to 2296"],
    ["`OFFSET`", "**where inside a clock cycle** the glitch starts.", "0 to 4592"],
    ["`EXT_OFFSET`", "**which clock cycle** after the trigger is glitched (0 = the first one).", "0, 1, 2, ..."],
    ["`REPEAT`", "how many glitch pulses fire in a row.", "1 to 8192"],
], [1.1 * inch, 3.6 * inch, W - 4.7 * inch])
S += [P("**Do this:** run the helper cell once (defines `fire_glitch`, `fire_many` and the others), then run the "
        "**Experiment 1** cell as it is. Change one number at a time and run it again.")]
S += table([
    ["Try", "WIDTH", "OFFSET", "EXT_OFFSET", "What to expect"],
    ["A (start)", "1770", "2670", "1", "right at the edge: expect some of everything"],
    ["B: a tiny glitch", "100", "2670", "1", "too short to do anything"],
    ["C: a huge glitch", "2200", "2670", "1", "too long to survive"],
    ["D: the wrong moment", "1770", "2670", "30", "right length, wrong clock cycle"],
    ["E: a different offset", "1770", "1000", "1", "right length, wrong part of the cycle"],
], [1.25 * inch] + [0.7 * inch] * 3 + [W - 1.25 * inch - 2.1 * inch])
S += callout("see", [
    "On our kit, **A** gave a mix of `success` and `reset`, with hardly any `normal` shots - between about 1 in 4 and 1 in 3 of "
    "30 shots was a success, and nearly all the rest were resets. **B, D and E** gave only `normal` (too weak, or the right "
    "length aimed at the wrong moment). **C** crashed the target every single time. Your exact counts will differ - the pattern "
    "(A is the interesting one; B/D/E do nothing; C always crashes) is what to look for."])

# ================================================================ EXPERIMENT 2
S += [H1("Experiment 2 - find the crash edge")]
S += [P("**Goal:** find how wide a glitch has to be before it starts to disturb the target, and see why a good setting hides "
        "right next to a bad one.")]
S += [P("The cell fires `SHOTS` glitches at every width from `WIDTH_START` to `WIDTH_STOP` and draws one stacked bar per width: "
        "grey = `normal`, red = `reset`, green = `success`.")]
S += numbered([
    "Run the cell as it is - a coarse pass over the whole width range. Where do the bars turn red? That is the **crash edge**.",
    "**Zoom in** on the edge (for example `WIDTH_START = 1700`, `WIDTH_STOP = 1850`, `WIDTH_STEP = 10`, `SHOTS = 20`) and run again. Do you see green now?",
    "Change `OFFSET` (try 2600, then 2750) and find the edge again. Does it move, and which way?",
    "Change `REPEAT` to 2 and find the edge again.",
])
S += callout("see", [
    "The coarse pass is grey at small widths, red at large widths, with a sharp edge in between (near width **1800** on our kit) "
    "and **usually no green at all** - the successes live in a band only a few steps wide, just *below* the edge. The zoomed "
    "pass is where green shows up."])
S += callout("warn", [
    "**These settings drift, even on the same kit, within a single session.** Working through Fault 2_2 and 2_3 on this exact "
    "board, a `(width, offset, ext_offset)` that gave a clean, repeatable result went completely quiet 20-30 minutes later with "
    "nothing physically changed - board temperature rising from continuous glitching is the suspected cause (we measured the "
    "Husky's internal temperature climb from about 44°C to 53°C over one long session). Expect the same here: if a width "
    "that worked a while ago stops crashing or stops succeeding, don't assume you did something wrong - rerun Experiment 2 to "
    "find the edge again before trusting an old number."], title="GOOD TO KNOW")

# ================================================================ EXPERIMENT 3
S += [H1("Experiment 3 - find the right moment")]
S += [P("**Goal:** a glitch only matters if it lands on the right instruction. `EXT_OFFSET` slides the glitch later in time, one "
        "clock cycle per step, after the trigger.")]
S += numbered([
    "Run the cell as it is: it fires at `EXT_START` to `EXT_STOP`, with a fixed width and offset.",
    "Which `EXT_OFFSET` values give green? Which give red? Which give only grey?",
    "Widen the range (`EXT_STOP = 60`, `SHOTS = 10`) and run again. Does any later cycle give a success?",
    "Change `WIDTH` by about 10 either way and repeat. Is the vulnerable cycle still the same one?",
])
S += callout("see", [
    "On our kit, cycle 0 and cycles 4 and up were grey (harmless). Cycles 1 to 3 were the interesting ones - mostly red, with "
    "**only cycle 1** turning green. Moving off that one cycle made the glitch fail, so timing matters as much as width. A wider "
    "scan found a few more red cycles further out (around 59 to 60) but no second green one."])

# ================================================================ EXPERIMENT 4
S += [H1("Experiment 4 - let the computer search")]
S += [P("You have now found by hand that a working setting is rare and sits at a precise width, offset and clock cycle. "
        "Trying every combination by hand would take forever, so the lab uses a `GlitchController` to walk through a range "
        "and keep score automatically.")]
S += table([
    ["Variable", "What it does"],
    ["`MAX_SUCCESSES`", "stop the search once this many successes have been found."],
    ["`NUM_TRIES`", "how many times each (width, offset, ext_offset) combination is tried."],
    ["`WIDTH_RANGE`, `OFFSET_RANGE`, `EXT_OFFSET_RANGE`", "the box of settings to search."],
    ["`STEP`", "the distance between neighbouring width / offset values tried."],
], [2.6 * inch, W - 2.6 * inch])
S += numbered([
    "Run the search with the ranges as they are. Note the run time and how many attempts it needed.",
    "Make `STEP` bigger (25), then smaller (1). What happens to the run time and the number of successes found?",
    "Raise `MAX_SUCCESSES` to 5.",
    "Move a range **away** from the good area (for example `WIDTH_RANGE = (1000, 1040)`). What does the result look like?",
])
S += callout("see", [
    "**As it is:** the search stopped at the first success - a hundred to a few hundred attempts, 4 to 15 seconds on our kit. "
    "**`STEP = 25`:** far fewer settings are tried, so whether it lands on a working one is luck - sometimes a success in about "
    "a second, sometimes none in the whole range. **`STEP = 1`:** nothing is skipped, so it still finds the first success "
    "quickly, but asking for more takes much longer. **A range far from the good area:** no successes at all, wasted time."])

# ================================================================ EXPERIMENT 5
S += [H1("Experiment 5 - draw a crash map")]
S += [P("**Goal:** see the whole picture at once. This cell fires glitches over a grid of widths and offsets and plots one mark "
        "per shot.")]
S += numbered([
    "Run the cell as it is (about a minute). Look at the **shape** of the red region: where does it start? Does the edge run straight, or lean?",
    "Is there any offset where a very wide glitch is still harmless? What does that say about where inside a clock cycle the glitch has to land?",
    "Zoom in on the edge with a small window and a small step (this run takes a few minutes).",
    "Pick three green marks and add WIDTH + OFFSET for each. What do you notice?",
])
S += callout("see", [
    "The first pass was grey almost everywhere, with a red patch for wide glitches at higher offsets. The zoomed pass showed a "
    "**slanted** crash-region edge, with green marks lying in a thin line right along it, just outside the red. On our kit "
    "WIDTH + OFFSET was close to the same total (around 4430-4480) for every green mark: a working glitch needs to be long "
    "enough **and** early enough in the cycle, in just the right combination."])

# ================================================================ EXPERIMENT 6
S += [H1("Experiment 6 - stronger or weaker?")]
S += [P("The glitch is produced by switching a transistor that shorts the target's power rail toward ground. You can try to "
        "make it stronger by repeating the pulse (`REPEAT`) or by using both the high-power and low-power transistors "
        "together. A stronger glitch should crash the target at a smaller width - does the crash edge actually move?")]
S += table([
    ["Setting", "What it means"],
    ["`hp`", "the high-power crowbar transistor."],
    ["`lp`", "the low-power crowbar transistor."],
    ["both off", "no crowbar at all - a control: nothing should happen."],
], [1.3 * inch, W - 1.3 * inch])
S += numbered([
    "Run the cell as it is. For every setting in `SETTINGS` it scans the width and reports the crash edge.",
    "Compare the edges. Does `REPEAT` 2 or 4 move it? Does `hp + lp`? What does the control do?",
    "Add a setting of your own to `SETTINGS`.",
])
S += callout("see", [
    "On our kit, `hp` alone at repeat 1, 2 and 4 gave about the **same** crash edge - repeating the pulse did not make it "
    "stronger here. `hp + lp` together moved the edge to a **smaller** width: two transistors really were stronger. `lp` alone "
    "never crashed the target in this range, and the control (both off) never did either. A surprise like 'repeat did "
    "nothing' is a result worth writing down, not a mistake."])

# ================================================================ EXPERIMENT 7
S += [H1("Experiment 7 - how reliable is your best glitch?")]
S += [P("**Goal:** a setting that worked once may not work again. A real evaluation needs to know **how often** a given "
        "setting succeeds, because that decides how many attempts (and how many crashes) using it actually costs.")]
S += numbered([
    "Run the cell as it is. Which of the listed candidates has the best success rate?",
    "Replace the candidates with your own best settings from Experiments 2 to 5.",
    "Raise `SHOTS` to 200 for the winner and run it twice. How much does the measured rate change by chance alone?",
])
S += callout("see", [
    "Success rates between 0% and about 40% on our kit. Neighbouring settings differed a lot - moving the width or offset by "
    "only 10 steps could take a setting from 'works a third of the time' to 'never works, always crashes'. The same setting "
    "also gave a slightly different rate each time it was measured, so a single run of 20 shots tells you very little on its own."])

# ================================================================ CHALLENGES
S += [H1("Challenges (optional)")]
S += [P("Use the helper functions (`fire_glitch`, `fire_many`, `scan`, `plot_tallies`, `crash_edge`, `glitch_on`, `recover`) and "
        "the EDIT ME cells to try these on your own kit:")]
S += numbered([
    "**The cheapest success.** Find ranges and a `STEP` for the automatic search that collect 10 successes in the fewest attempts and the least time.",
    "**Why always the same number?** Look at the counter value after a success. Is it always the same one? What does that tell you about *what* the glitch changed, if the answer is always identical?",
    "**A different vulnerable moment.** Experiment 3 found one vulnerable clock cycle. With a wider scan and different widths, can you find a second one - or one that only ever crashes the target, never succeeds?",
    "**Fewer crashes per success.** Every `reset` is a crashed target, which in a real evaluation is easy to notice. Find a setting with a success rate of at least 5% and fewer than one reset per success.",
])

# ================================================================ TROUBLESHOOTING
S += [H1("If something goes wrong")]
S += table([
    ["What you see", "Most likely cause", "What to do"],
    ["Every shot is `normal`, never `reset` or `success`, even at a large width.", "The Crowbar SMA cable is not connected.", "Connect it to the CW313's second SMA socket (see Before You Start), then run the setup cells again."],
    ["Every shot is `reset`.", "The width is too large for this offset, or the target is stuck from an earlier crash.", "Lower `WIDTH` (try 1700), run `recover()`, try again."],
    ["Plenty of `reset`, but no `success`.", "The settings are slightly off - successes live in a band only a few steps wide, at the edge of the crash region.", "Go back to Experiment 2 and zoom in with a step of 5 or 10; use more `SHOTS`."],
    ["A `success` appears once and not the next time at the same setting.", "Normal: the success rate is a probability, not a guarantee (see Experiment 7).", "Fire more shots and compare *rates*, not single results."],
    ["You pressed Stop, or a cell was interrupted.", "The target may be mid-crash and the glitch hardware left enabled.", "Run `recover()` in a new cell."],
    ["`OSError: Could not find ChipWhisperer` / `Unable to communicate with device`.", "The Husky is unplugged, or another notebook still holds it.", "Plug it in; close every other open notebook (File > Shut Down Notebook); restart this kernel."],
    ["`USBErrorPipe`, `Unknown hwInfoVer`, or `ValueError: Unknown ChipWhisperer`.", "The Husky's USB link or FPGA stopped answering.", "Unplug the Husky's USB cable and plug it back in directly (not through a hub); restart the kernel and run the setup cells again."],
    ["A scan or search takes a very long time.", "Every `reset` costs about half a second while the target reboots.", "Use fewer widths (bigger step), fewer `SHOTS`, or a narrower range."],
], [1.9 * inch, 2.1 * inch, W - 4.0 * inch])
S += callout("warn", [
    "Stay inside the ranges quoted in each experiment, and do not unplug any cable while a cell is running. A crashed target is "
    "a normal outcome here - the notebook reboots it for you automatically."])

# ================================================================ APPENDIX
S += [H1("Appendix - every variable you can edit")]
S += EDIT([
    ["`WIDTH`", "1770", "Glitch length, in Husky phase-shift steps (0 to 2296)."],
    ["`OFFSET`", "2670", "Where inside the clock cycle the glitch starts (0 to 4592)."],
    ["`EXT_OFFSET`", "1", "Which clock cycle after the trigger is glitched (0, 1, 2, ...)."],
    ["`REPEAT`", "1", "Number of glitch pulses fired per shot."],
    ["`SHOTS`", "varies", "How many glitches to fire for one measurement; more shots = a better estimate of the success rate, but slower."],
    ["`WIDTH_START/STOP/STEP`", "varies", "The width range scanned in Experiments 2, 5 and 6."],
    ["`OFFSET_START/STOP/STEP`", "varies", "The offset range scanned in Experiment 5."],
    ["`EXT_START/STOP`", "0 / 8", "The ext_offset range scanned in Experiment 3."],
    ["`MAX_SUCCESSES`", "1", "How many successes the automatic search (Experiment 4) collects before stopping."],
    ["`NUM_TRIES`", "5", "How many times each setting is retried in the automatic search."],
    ["`SETTINGS`", "list", "(name, repeat, hp, lp) tuples compared in Experiment 6."],
    ["`CANDIDATES`", "list", "(width, offset, ext_offset, repeat) tuples compared in Experiment 7."],
])

# ================================================================ GLOSSARY
S += [H1("Appendix - Glossary")]
S += table([
    ["Term", "Meaning"],
    ["Voltage glitch", "A brief, deliberate dip in a chip's supply voltage, used to see whether it disturbs normal execution."],
    ["Fault injection", "Deliberately causing a hardware fault (here, with a voltage glitch) to test how a device's logic responds."],
    ["`normal`", "Outcome: the glitch had no visible effect; the firmware's counter still reached 2500."],
    ["`reset`", "Outcome: the glitch crashed the target; the notebook reboots it and continues."],
    ["`success`", "Outcome: the glitch changed the result (the counter is not 2500)."],
    ["Crash edge", "The boundary (in width, or in width+offset) past which the target reliably crashes instead of running normally."],
    ["`ext_offset`", "Which clock cycle, counted from the trigger, the glitch is placed on."],
    ["Crowbar", "The transistor (and its SMA cable on the Husky) that shorts the target's power rail to produce the glitch."],
    ["HP / LP", "The high-power and low-power crowbar transistors; using both together makes a stronger glitch than either alone."],
    ["`GlitchController`", "The ChipWhisperer class that walks through a grid of glitch settings and tallies the outcomes."],
], [1.5 * inch, W - 1.5 * inch])

S += K.notice()

K.build(doc, S)
