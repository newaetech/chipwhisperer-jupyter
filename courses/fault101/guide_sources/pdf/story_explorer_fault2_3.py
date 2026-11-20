"""Builds 'Fault 2_3 Explorer - Student Guide.pdf'.   Usage: python story_explorer_fault2_3.py "<output pdf>" """
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
NBNAME = "Fault 2_3 - Voltage Glitching to Memory Dump Explorer.ipynb"
GUIDE_VERSION = "1.0 - November 2026"

doc = K.init(OUT,
             header_left="ChipWhisperer Fault101  -  Fault 2_3 Explorer Guide",
             header_right="Memory Dump Explorer",
             footer_left="Companion to: " + NBNAME,
             title="Fault101 Fault 2_3 Explorer - Step-by-Step Student Guide",
             subject="Step-by-step guide to the Fault 2_3 Voltage Glitching Explorer: a response-length bug that is easy to glitch, in a direction the lab's name does not predict",
             roadmap=[("1  Baseline", "and reuse Fault 2_2"), ("2 - 3  Map", "the crash edge"), ("4  Check", "reliability + payload"),
                      ("5  Which way", "does it fail?")])


def EDIT(rows):
    return table([["Variable", "Default", "What it does"]] + rows, [1.5 * inch, 1.0 * inch, W - 2.5 * inch])


S = []

# ================================================================ COVER
S += [*K.cover("FAULT101  -  FAULT 2_3  (EXPLORER)", ("Memory Dump", "Explorer"),
                  "Step-by-step student guide: a bug that is easy to glitch - but maybe not the way you expect"),
      P("Fault 2_3 targets a bootloader's reply routine, whose length is controlled by a variable a fault can "
        "corrupt. The lab's name promises a **memory dump** - a fault that makes the device echo back more than "
        "it should. This guide's central finding is that on our kit, **the fault goes the other way**: it "
        "reliably shortens the reply instead of lengthening it. Both directions come from the exact same root "
        "cause, this one is just much easier to find than Fault 2_2's password bypass, and - like Fault 2_2 - "
        "the exact settings that work **drift** over the course of a session. **This lab needs real hardware; "
        "there is no simulated mode.**"),
      Spacer(1, 10)]
S += callout("tip", [
    "This guide goes **with** the notebook - it does not replace it. Keep the notebook open next to this PDF."], title="HOW TO USE THIS GUIDE")
S += [P("**Which files are which**", h3)]
S += table([
    ["File (folder: jupyter/courses/fault101/)", "What it is", "Open it?"],
    ["`%s`" % NBNAME, "The Explorer. Everything in this guide happens here.", "**Yes**"],
    ["`Fault 2_3 - Voltage Glitching to Memory Dump.ipynb`", "The original (non-Explorer) lab.", "Optional"],
    ["`SOLN_Fault 2_3 - ...ipynb`", "Answer key for the original lab.", "If stuck"],
    ["`firmware/mcu/bootloader-glitch/bootloader.c`", "(a different folder: `chipwhisperer/firmware/...`) The reply routine this lab targets.", "Background"],
], [3.0 * inch, 3.1 * inch, W - 6.1 * inch])
S += [P("**The four colored boxes you will see everywhere**", h3)] + legend()
S += [Spacer(1, 4),
      P("Guide version %s. Every number in this guide was measured on one real kit: ChipWhisperer-Husky, a CW313 "
        "board and a CW312T-SAM4S target (Windows 11, Python 3.12, ChipWhisperer 6.0.0, firmware 1.5.0) - the same "
        "kit as the Fault 2_1 and 2_2 guides. As with Fault 2_2, **the exact settings below drift within a single "
        "session** - treat specific numbers as 'this was possible', not as guarantees." % GUIDE_VERSION, small),
      PageBreak()]

# ================================================================ CONTENTS
S += K.contents()

# ================================================================ BIG PICTURE
S += [H1("The big picture")]
S += [P("**What is the bug?** The test bootloader receives a hex-encoded upload, 'decrypts' it (a ROT-13 "
        "substitution - nothing secret), and replies with a fixed acknowledgement. A loop sends back "
        "`ascii_idx` bytes from a buffer, and nothing re-checks `ascii_idx` between being set and being used in "
        "that loop:")]
S += code(
"ascii_buffer[ascii_idx++] = 'r'; ascii_buffer[ascii_idx++] = '0';   /* + 6x '\\n' */\n"
"...\n"
"for(i = 0; i < ascii_idx; i++)\n"
"    putch(ascii_buffer[i]);")
S += [P("If a fault corrupts `ascii_idx` (or the loop's comparison against it) in between, the reply is the "
        "wrong length. Corrupt it **upward** past what was written and you leak extra bytes sitting after it in "
        "memory - the over-read this lab is named for. Corrupt it **downward** and the reply is silently "
        "**truncated** instead - still a real bug (a caller expecting a fixed-length reply gets less and may "
        "misread what is missing), just a quieter one. Which direction you get depends on exactly how the "
        "compiler laid things out - which is exactly the point of this Explorer: it has you find out which "
        "direction happens on your own build, rather than assuming the dramatic one.")]
S += [P("Your path through the notebook:", h3), Roadmap(W), Spacer(1, 6)]
S += table([
    ["Experiment", "What you do", "What you learn"],
    ["1", "Try Fault 2_1/2_2's settings here too.", "Still nothing - the interesting part of this routine's window is elsewhere."],
    ["2", "Scan width at a later moment to find the crash/success edge.", "A clean, easy-to-find edge: past it, almost every shot truncates the reply - at that instant."],
    ["3", "Scan a wide range of moments at a reliable width.", "Several good moments scattered through the window - far denser than Fault 2_2's."],
    ["4", "Check reliability and whether the payload matters.", "The same length truncates every time at a given setting, regardless of what you uploaded."],
    ["5", "Search specifically for a longer-than-baseline reply.", "On our kit, never found - only ever truncation, across thousands of attempts."],
], [0.8 * inch, 3.0 * inch, W - 3.8 * inch], bold_first_col=True)
S += [PageBreak()]

# ================================================================ BEFORE YOU START
S += [H1("Before you start")]
S += [P("Same kit and checklist as Fault 2_1 and 2_2.")]
S += table([
    ["", "You need", "How to check"],
    ["[  ]", "Fault 2_1 and 2_2 completed (same setup and hardware).", "You can fire a glitch and read the outcomes."],
    ["[  ]", "**ChipWhisperer-Husky** plugged straight into a USB port.", "Lab 0's hardware test ends with `hardware OK (disconnected again)`."],
    ["[  ]", "**CW312T-SAM4S** on **CW313**, ribbon connected.", "See the SCA101 Linux guide, Part 4.2."],
    ["[  ]", "The Husky **`Crowbar`** SMA cable connected.", "Without it, every glitch here shows as `normal` too."],
    ["[  ]", "No other notebook holding the Husky open.", "**File > Shut Down Notebook** elsewhere first."],
], [0.45 * inch, 3.3 * inch, W - 3.75 * inch])
S += callout("tip", [
    "**This one is easier than Fault 2_2.** A plain width-then-moment scan found working settings in well under "
    "a minute on our kit - no blind random search over a huge box was needed. Do not let Fault 2_2's difficulty "
    "set your expectations for every lab."])

# ================================================================ EXPERIMENT 1
S += [H1("Experiment 1 - try Fault 2_1/2_2's settings here too")]
S += [P("**Goal:** check, rather than assume, whether a setting that worked for the counting loop or the "
        "password check does anything to this response routine.")]
S += callout("see", [
    "All `normal`. `ext_offset=1` is early in this firmware's own (much longer) trigger window - which starts "
    "when the upload begins, not when the reply is sent - and this width is too gentle for this firmware's own "
    "crash threshold anyway. The interesting part of the window is much later."])

# ================================================================ EXPERIMENT 2
S += [H1("Experiment 2 - find this firmware's own crash edge")]
S += [P("**Goal:** scan width at a fixed offset, somewhere later in the trigger window than Experiment 1 "
        "(`ext_offset` around two-thirds of the way through `trig_count`), the way Fault 2_1 and 2_2 did for "
        "their own crash edges.")]
S += callout("see", [
    "At one particular `(offset, ext_offset)`: width 1775 and below was `normal`; 1800-1825 a transition; and "
    "**1850 and above gave `success` every single time**, up to 2125, every reply shortened to the same 6 bytes. "
    "That is how clean this edge can look at one instant."])
S += callout("warn", [
    "**This moves too, like Fault 2_2's settings.** Re-running the exact same cell roughly twenty minutes later "
    "in the same session, that same `ext_offset` had gone completely quiet - `normal` at every width from 1600 "
    "to 2125. Experiment 3 found a different `ext_offset` nearby that had picked up the effect instead, and the "
    "same kind of edge reappeared there, just less sharp (a mix of outcomes above about 1825, not a clean 100%). "
    "**Don't treat any single `(width, offset, ext_offset)` as permanent** - if a setting that worked goes quiet, "
    "check its neighbours (especially in `ext_offset`) before assuming the effect disappeared."], title="GOOD TO KNOW")

# ================================================================ EXPERIMENT 3
S += [H1("Experiment 3 - how much of the window is like this?")]
S += [P("**Goal:** Experiment 2 picked one moment almost at random. Scan a reliably-strong width across the "
        "*whole* trigger window to see how much of it behaves the same way.")]
S += callout("see", [
    "Mostly `normal`, with `success` at a handful of specific moments scattered through the window - in one run, "
    "around 750, 1350, 1800 and 2100 out of roughly 2150 total; in another, 1500, 1800 and 2100. Roughly one good "
    "moment every few hundred cycles - far denser than Fault 2_2 ever found for its password bypass. Here, a "
    "plain scan over width and a handful of moments, with no blind random search, turns up several working "
    "settings in well under a minute."])

# ================================================================ EXPERIMENT 4
S += [H1("Experiment 4 - reliability and payload-independence")]
S += [P("**Goal:** confirm a currently-working setting is reproducible, and check whether the uploaded message "
        "itself makes any difference - this fault corrupts a loop bound, not the message's content, so it "
        "should not.")]
S += callout("see", [
    "Two very different payloads (the original hex sentence, and a message of all `0x41` bytes) behaved almost "
    "identically at a setting that was working at the time: 14 of 20 and 12 of 20 shots succeeded - close enough "
    "to call 'the same rate', given how much these settings drift on their own (Experiment 2). **Every success "
    "truncated to the same length** (6 bytes) regardless of which payload was sent. That confirms the fault "
    "corrupts a loop bound or counter, not the content you uploaded. Different settings truncated to different "
    "lengths across our testing (we also saw replies of 1, 2, 3, 4, 5 and 7 bytes), but a *given* setting kept "
    "giving the *same* length for as long as it kept working at all."])

# ================================================================ EXPERIMENT 5
S += [H1("Experiment 5 - which direction does it fail in, and why does that matter?")]
S += [P("**Goal:** this lab is named 'memory dump' because the intended bug is an **over-read** - a fault "
        "making `ascii_idx` too big, so the reply leaks bytes that were never meant to go out. Search "
        "specifically for a reply longer than the 8-byte baseline, across a wide box of settings.")]
S += callout("see", [
    "Across every search we ran on this kit - several thousand attempts in total, spread over a wide box of "
    "widths, offsets and moments - **the reply was never longer than the 8-byte baseline.** The fault only ever "
    "truncated it. That is the real finding here: the same root cause produced an under-read, not the over-read "
    "the lab's name promises."])
S += callout("tip", [
    "**Neither direction is 'better' or 'worse' to report.** A silent truncation can be just as damaging in a "
    "protocol where a caller trusts a length field and a short reply means something was quietly dropped. "
    "Recording which direction actually happened, honestly, is more useful than assuming the dramatic one did. "
    "If your own kit or a different compiler build ever produces a longer-than-baseline reply, that is the "
    "over-read this lab was named for - write down the exact setting and what extra bytes came back."], title="GOOD TO KNOW")

# ================================================================ CHALLENGES
S += [H1("Challenges (optional)")]
S += numbered([
    "**Map the full truncation spectrum.** Collect every distinct reply length you can find across several settings. Is there a pattern to which settings give which length?",
    "**Compare search difficulty properly.** Time a plain width-then-moment scan here against Fault 2_2's blind random search. Which bug was easier to glitch, and by roughly how much?",
    "**Does `repeat` change the truncation length?** Try `REPEAT = 2` or `3` at a working setting.",
    "**A longer payload.** Upload a message close to the buffer's limit (80 hex characters) and repeat Experiment 2. Does the crash edge or the truncated length change?",
])

# ================================================================ TROUBLESHOOTING
S += [H1("If something goes wrong")]
S += table([
    ["What you see", "Most likely cause", "What to do"],
    ["The baseline assert fails.", "Firmware did not flash, or a stale serial buffer.", "Re-run the build/flash cells; re-run `reboot_flush()`."],
    ["Every shot is `normal`, even at a huge width.", "The Crowbar SMA cable is not connected.", "Fit the cable, run the setup cells again."],
    ["Every shot is `reset`.", "You are above the crash threshold for this width.", "Lower `WIDTH` a little."],
    ["`target.read()` returns nothing at all.", "The target may be stuck mid-reply.", "Run `recover()`, then `reboot_flush()`."],
    ["A setting that worked earlier stops working.", "Drift (see the note after Experiment 2).", "Re-measure with fresh shots; try nearby `ext_offset` values."],
    ["`OSError: Could not find ChipWhisperer`.", "Husky unplugged, or another notebook still holds it.", "Plug it in; shut down every other notebook; restart this kernel."],
    ["`USBErrorPipe` / `Unknown hwInfoVer`.", "The Husky's USB link or FPGA stopped answering.", "Unplug and replug the Husky directly; restart the kernel."],
    ["A cell was interrupted (Stop button).", "Target or glitch hardware may be left in an odd state.", "Run `recover()` in a new cell."],
], [2.0 * inch, 2.1 * inch, W - 4.1 * inch])

# ================================================================ APPENDIX
S += [H1("Appendix - every variable you can edit")]
S += EDIT([
    ["`WIDTH`, `OFFSET`, `EXT_OFFSET`", "varies", "The glitch settings fired, in Husky phase-shift steps / clock cycles."],
    ["`REPEAT`", "1", "Number of glitch pulses fired per shot."],
    ["`SHOTS`", "varies", "How many glitches to fire for one measurement."],
    ["`WIDTH_START/STOP/STEP`", "varies", "The width range scanned in Experiment 2."],
    ["`EXT_STEP`", "150", "The step used when scanning the whole trigger window in Experiment 3."],
    ["`PAYLOAD_A`, `PAYLOAD_B`", "two messages", "The two uploads compared in Experiment 4."],
    ["`WIDTH_RANGE`, `OFFSET_RANGE`, `TIME_BUDGET_S`", "wide / 120", "The box and time budget searched in Experiment 5."],
])

# ================================================================ GLOSSARY
S += [H1("Appendix - Glossary")]
S += table([
    ["Term", "Meaning"],
    ["Voltage glitch / fault injection / drift", "See the Fault 2_1 and 2_2 guides' glossaries - the same concepts apply here."],
    ["Over-read", "A fault (or bug) that makes code send back more data than intended, potentially leaking memory it should not."],
    ["Truncation / under-read", "A fault (or bug) that makes code send back less data than intended - the direction this lab's firmware actually took on our kit."],
    ["`ascii_idx`", "The variable controlling how many bytes the bootloader's reply loop sends back."],
    ["`trig_count`", "How many ADC samples the trigger stayed high for during one capture - used to size the `ext_offset` search range."],
], [1.7 * inch, W - 1.7 * inch])

S += K.notice()

K.build(doc, S)
