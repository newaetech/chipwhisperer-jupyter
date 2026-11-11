"""Builds 'Lab 2_1A Explorer - Student Guide.pdf' (v1.1).   Usage: python story_explorer_2_1a.py "<output pdf>"
This is a re-creation of the v1.0 guide (its generator was lost): Steps 1 to 6 keep their text and numbers, Step 7 now matches the
notebook (live-trace loop measurement) and shows what a real Husky gives.  GUIDE_BACKEND=latex writes a .tex file instead of a PDF."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if os.environ.get("GUIDE_BACKEND") == "latex":          # GUIDE_BACKEND=latex writes a .tex file instead of a PDF
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "latex"))
    import latexkit as K
    from latexkit import *
else:
    import pdfkit as K
    from pdfkit import *

OUT = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets", "explorer_2_1a") + os.sep
ASSETS_HW = os.path.join(HERE, "assets", "hw_2a") + os.sep
NBNAME = "Lab 2_1A - Instruction Power Explorer.ipynb"
GUIDE_VERSION = "1.1 - November 2026"

doc = K.init(OUT,
             header_left="ChipWhisperer SCA101  -  Lab 2_1A Explorer Guide",
             header_right="Instruction Power Explorer",
             footer_left="Companion to: " + NBNAME,
             title="SCA101 Lab 2_1A Explorer - Step-by-Step Student Guide",
             subject="Step-by-step guide to the Lab 2_1A Instruction Power Explorer notebook: edit the numbers, watch the trace change",
             roadmap=[("1 - 3  Read", "a power trace"), ("4 - 5  Find", "the loop"), ("6  Model", "other loop counts"), ("7  Real chip", "hardware only")])


def FIG(name, width, cap, hw=False):
    return figure((ASSETS_HW if hw else ASSETS) + name, width, cap)


def EDIT(rows):
    return table([["Variable", "Default", "What it does"]] + rows, [1.65 * inch, 1.05 * inch, W - 2.7 * inch])


S = []

# ================================================================ COVER
S += [*K.cover("SCA101  -  LAB 2_1A  (EXPLORER)", ("Instruction Power", "Explorer"),
               "Step-by-step student guide: edit the numbers, watch the trace change"),
      P("In Lab 2_1A you capture four power traces and compare them by eye. This guide goes with a **second, hands-on notebook** "
        "where you change the numbers yourself - zoom, smooth, count, measure and predict - and watch the plots update, so you can see "
        "exactly **why** a power trace looks the way it does. No hardware is needed for the first six steps; with a ChipWhisperer-Husky, "
        "Step 7 lets you write your own loop and measure it on the real chip."),
      Spacer(1, 10)]
S += callout("tip", [
    "This guide goes **with** the notebook - it does not replace it. Keep the notebook open next to this PDF. "
    "Every step says what to edit, what you should see, and what to try if you do not see it."], title="HOW TO USE THIS GUIDE")
S += [P("**Which files are which**", h3)]
S += table([
    ["File (folder: jupyter/courses/sca101/)", "What it is", "Open it?"],
    ["`%s`" % NBNAME, "The Explorer. Everything in this guide happens here.", "**Yes**"],
    ["`Lab 2_1A - Instruction Power Differences (MAIN).ipynb`", "The original lab. Do it before or after the Explorer.", "Optional"],
    ["`... (HARDWARE).ipynb`, `... (SIMULATED).ipynb`", "Back-end helpers. The notebooks run them for you.", "**No**"],
    ["`traces/lab2_1A_trace0.npy` to `trace3.npy`", "The four recorded power traces the Explorer uses.", "No (just keep them)"],
    ["`traces/hardware_reference/*.npy`", "Captures from a real Husky: the notebook's Step 7 plots them, and you can compare your own capture with them.", "No (just keep them)"],
    ["`Lab 2_1A - What You Should See on a Real Husky.pdf`", "What a healthy real-chip run looks like (more detail than Step 7 below).", "With a Husky"],
], [3.0 * inch, 2.9 * inch, W - 5.9 * inch])
S += [P("**The four colored boxes you will see everywhere**", h3)] + legend()
S += [Spacer(1, 4),
      P("Guide version %s. The numbers for Steps 1 to 6 were produced by running the notebook, headless and in a real Jupyter session, on "
        "**Ubuntu 22.04** (Python 3.10) with the recorded traces. **Step 7 and every 'real chip' number were measured on a real "
        "ChipWhisperer-Husky with a CW313 and a SAM4S target** (Windows 11, Python 3.12, ChipWhisperer 6.0.0, firmware 1.5.0). Version 1.1 replaces the "
        "Step 7 of version 1.0, which counted pulses on the live trace - that does not work reliably on real traces." % GUIDE_VERSION, small),
      PageBreak()]

# ================================================================ CONTENTS
S += K.contents()

# ================================================================ BIG PICTURE
S += [H1("The big picture")]
S += [P("**What is this about?** A microcontroller does its work one clock cycle at a time, and the electricity it draws changes a little with what it is "
        "doing. The ChipWhisperer records that as a **power trace**. If you know how to read the trace you can tell __what the chip is doing and how long it "
        "takes__ - without ever seeing its code. That is the idea behind every side-channel attack in this course.")]
S += [P("**What is different about the Explorer?** The original lab shows you four traces. The Explorer lets you poke at them: every code cell has a clearly "
        "marked block of numbers you can change. Change one, press **Shift+Enter**, and the plot and the printed numbers change straight away.")]
S += [P("Your path through the notebook:", h3), Roadmap(W), Spacer(1, 6)]
S += table([
    ["Step", "What you do", "What you learn", "Hardware?"],
    ["1", "Zoom, smooth and flip a real trace.", "What the x and y axes mean (and that the trace is upside down).", "No"],
    ["2", "Measure the clock with autocorrelation.", "There are 4 samples per clock cycle.", "No"],
    ["3", "Overlay two traces and slide one.", "Single instructions are hard to see; changes shift later activity.", "No"],
    ["4", "Find the loop's pulses automatically.", "20 pulses; how smoothing changes the count; the divide loop's pulses move closer.", "No"],
    ["5", "Compare the size of A with the time per trip.", "Data changes timing: the divide gets faster as the number shrinks.", "No"],
    ["6", "Stack real loop trips for any loop count.", "How loop count changes the trace; when noise hides pulses.", "No"],
    ["7", "Edit the C code on the real chip and measure the loop.", "Check your predictions on real silicon - and what a real chip's numbers look like.", "**Yes**"],
    ["8", "Answer seven questions.", "Put it all together.", "No"],
], [0.5 * inch, 2.4 * inch, 3.0 * inch, W - 5.9 * inch], bold_first_col=True)
S += [PageBreak()]

# ================================================================ BEFORE YOU START
S += [H1("Before you start")]
S += [P("Tick every row. Most problems later come from something on this list.")]
S += table([
    ["", "You need", "How to check"],
    ["[  ]", "**Lab 0 - SCA101 Setup** passed (at least the software checks).", "ChipWhisperer, numpy, matplotlib and holoviews import without errors."],
    ["[  ]", "Jupyter running from your ChipWhisperer environment.", "On Linux see the Linux guide Part 3; the first cell shows no `ModuleNotFoundError`."],
    ["[  ]", "The course notebooks, with the `traces` folder next to the lab files.", "`jupyter/courses/sca101/` contains the Explorer notebook and a `traces` folder with four `.npy` files."],
    ["[  ]", "**Only for Step 7:** the Husky kit (CW313 + CW312T-SAM4S) assembled and plugged in.", "Lab 0's hardware test ends with `hardware OK (disconnected again)`."],
], [0.45 * inch, 3.3 * inch, W - 3.75 * inch])
S += callout("warn", [
    "Open the **Explorer** notebook, not the `(HARDWARE)` or `(SIMULATED)` files. Those two are helpers that other notebooks run for you; "
    "opened on their own they do nothing useful."])
S += callout("tip", [
    "**You cannot break anything.** The recorded traces are only ever __read__. If a plot looks wrong or an error appears, "
    "use **Kernel > Restart & Run All** and you are back to the starting state."], title="GOOD TO KNOW")
S += [H2("How every edit-and-run cell works")]
S += table([
    ["Do this", "Keys"],
    ["Run the cell and move to the next one", "**Shift + Enter**"],
    ["Run the cell and stay on it (best for repeated experiments)", "**Ctrl + Enter**"],
    ["Start over from the top", "**Kernel > Restart & Run All**"],
    ["Insert a cell above / below (command mode)", "**Esc**, then **A** / **B**"],
], [4.6 * inch, W - 4.6 * inch])
S += [P("Every cell you are meant to change starts with the line **`# EDIT THESE`** (marked with a pencil in the notebook). Change only what is in that block, "
        "then run the cell. Everything below it just does the drawing and the maths.")]
S += [CondPageBreak(4.0 * inch)]

# ================================================================ SETUP
S += [H1("Setup - open the notebook and run it")]
S += [STEP("S.1", "Open the Explorer")]
S += numbered([
    "Start Jupyter (for Linux: `source ~/.cwvenv/bin/activate`, then `cd ~/chipwhisperer/jupyter`, then `jupyter notebook`).",
    "Click **courses**, then **sca101**.",
    "Click **%s**." % NBNAME,
])
S += [Spacer(1, 4), STEP("S.2", "Choose the version")]
S += [P("The first code cell has one setting you may change:")]
S += EDIT([["`VERSION`", "`'SIMULATED'`", "`'SIMULATED'` = use the recorded traces only (Steps 1 to 6, no hardware). `'HARDWARE'` = also connect to the Husky so Step 7 works."]])
S += [STEP("S.3", "Run the two Setup cells")]
S += [P("Press **Shift+Enter** on the `VERSION` cell, then on the cell below it (the one that starts `%matplotlib inline`).")]
S += callout("see", [
    "The second cell prints a green check mark and `Ready!  Loaded 4 recorded traces of 2000 samples each.` That cell loads the traces and defines the helper "
    "functions used by every later step. __In HARDWARE mode__ it also connects to the Husky first: you see a block of `scope.gain ... changed from ... to ...` lines, "
    "the firmware build and `Hardware ready`, and the traces for Steps 1 to 6 are still the recorded ones."])
S += callout("ifnot", [
    "`FileNotFoundError: ... traces/lab2_1A_trace0.npy` - the traces folder is missing or the notebook is not in `courses/sca101` (E-1). "
    "`ModuleNotFoundError` - you are not using your ChipWhisperer environment (Lab 0)."])
S += [STEP("S.4", "Optional: run everything once")]
S += [P("To see the finished notebook before you start experimenting, choose **Kernel > Restart & Run All**. It should finish in a few seconds with no red error "
        "boxes. (Step 7 prints a polite message instead of running - that is expected without hardware.)")]
S += [PageBreak()]

# ================================================================ STEPS 1-3
S += [H1("Steps 1 to 3 - read a trace")]
S += [STEP("1", "Look at a power trace")]
S += [P("A trace is a list of 2000 numbers - one measurement per **sample**. The x-axis is the sample number (time, in tiny steps). The y-axis is the measured value. "
        "Careful: ChipWhisperer measures a __voltage drop__ across a resistor, so the trace is **upside down** - larger negative swings mean more power. `FLIP` turns it the right way up.")]
S += table([
    ["Trace", "What the target was doing between the trigger signals"],
    ["0", "Nothing (the baseline)"],
    ["1", "20 multiplies, one after another"],
    ["2", "A loop that does the multiply 20 times"],
    ["3", "A loop that does a divide 20 times"],
], [0.9 * inch, W - 0.9 * inch])
S += [P("**Edit these:**", h3)]
S += EDIT([
    ["`TRACE`", "`2`", "Which recorded trace to show: 0, 1, 2 or 3."],
    ["`START, END`", "`0, 600`", "The zoom window, in samples (the whole trace is 0 to 2000)."],
    ["`SMOOTH`", "`1`", "Smoothing width. 1 = raw samples; bigger = smoother."],
    ["`FLIP`", "`False`", "`True` turns the plot upside down so that UP means MORE power."],
])
S += [FIG("cell09_1.png", 6.2 * inch, "Before: the cell as shipped (`TRACE = 2`, window 0 to 600, raw samples, not flipped)."),
      FIG("step1_after.png", 5.0 * inch, "After: a screenshot of the real notebook running on Linux - I changed `TRACE` to 3, `END` to 200, `SMOOTH` to 5 and `FLIP` to True, then pressed Ctrl+Enter.")]
S += callout("see", [
    "The plot redraws and the line under it says `showing samples 0 to 200 - 200 samples out of 2000`. In the second picture the divide loop's humps now point up (`FLIP`) "
    "and the little spikes are mostly gone (`SMOOTH`)."])
S += callout("do", [
    "**Try:** (1) Set `START, END = 0, 100` and count the individual samples. (2) Raise `SMOOTH` to 9 - what disappears? (3) Look at all four traces. Which two look most alike? "
    "Which one has a clearly repeating shape?"])

S += [STEP("2", "How fast is the clock? (measure it yourself)")]
S += [P("The ChipWhisperer takes several samples per **clock cycle**. How many? You will measure it with **autocorrelation**: compare the trace with a copy of itself slid sideways by "
        "`L` samples. If something repeats every `L` samples, the copies line up well at that `L` and the score is high.")]
S += EDIT([
    ["`TRACE_FOR_CLOCK`", "`0`", "Which trace to analyse (0 to 3)."],
    ["`LAG_MIN, LAG_MAX`", "`2, 8`", "Search for the repeat period between these two numbers of samples."],
])
S += [FIG("cell11_2.png", 6.0 * inch, "The tallest bar between lag 2 and lag 8 (red) is at 4: the trace repeats every 4 samples.")]
S += callout("see", [
    "`best repeat period: 4 samples -> one clock cycle = 4 samples`. So there are **4 samples per clock cycle**. The next cell draws a red line at every cycle - the shape repeats from line to line."])
S += callout("warn", [
    "Try `LAG_MIN, LAG_MAX = 5, 12` and the winner becomes 8 - a __multiple__ of the real answer (a pattern that repeats every 4 samples also repeats every 8). Then put it back to `2, 8` "
    "and run the cell again. Every later step uses this number; if you leave 8 there, all the cycle counts come out double."])
S += [FIG("cell13_3.png", 6.2 * inch, "Zoom on trace 0 with red lines at every clock cycle (60 samples = 15 cycles).")]

S += [STEP("3", "Compare two traces")]
S += [P("Plot any two traces on top of each other and slide one sideways. Does the baseline change when you add 20 multiplies?")]
S += EDIT([
    ["`A_TRACE, B_TRACE`", "`0, 1`", "Which two traces to compare."],
    ["`SHIFT_B`", "`0`", "Slide trace B right (+) or left (-) by this many samples."],
    ["`START, END`", "`0, 500`", "Zoom window."],
])
S += [FIG("cell15_4.png", 6.0 * inch, "Trace 0 (blue) against trace 1 (orange) with `SHIFT_B = 0`.")]
S += callout("see", [
    "`average difference between the two in this window: 0.0943`, then `for scale: the wiggles in trace A are typically 0.0942 in size`. The difference is as big as the wiggles "
    "themselves, so the two traces do not line up. Adding 20 instructions delays everything that follows them, which is one reason a straight comparison is hard."])
S += callout("do", [
    "**Try:** (1) `0, 2` - the loop is much easier to spot than 20 loose multiplies. (2) Use `SHIFT_B` to slide the orange trace; does it ever line up with the blue one? "
    "(3) Why might 20 single instructions be hard to see? __(Each takes only a cycle or two - a handful of samples.)__"])
S += [PageBreak()]

# ================================================================ STEPS 4-5
S += [H1("Steps 4 and 5 - find the loop")]
S += [STEP("4", "Find the loop")]
S += [P("A loop runs the same few instructions again and again, so its trace is the same shape repeated - one **pulse** per trip round the loop. `find_pulses()` smooths the trace, "
        "finds the repeating highs, and stops when the pattern stops repeating.")]
S += EDIT([
    ["`SMOOTH_WIDTH`", "`21`", "How hard to smooth before looking for highs."],
    ["`MIN_GAP`", "`30`", "Highs closer together than this many samples count as one pulse."],
    ["`TOLERANCE`", "`0.4`", "How much the spacing may change from pulse to pulse (0.4 = 40%)."],
    ["`LOOP_TRACES`", "`[2, 3]`", "Which traces to analyse."],
])
S += [FIG("cell17_5.png", 6.2 * inch, "Both loops with the finder's markers (red triangles): 20 pulses each.")]
S += callout("see", [
    "`trace 2: 20 pulses, spacing in samples: 60 every time (= 15 cycles)`. `trace 3: 20 pulses, spacing in samples: [88, 84, 84, 84, 80, 80, 80, 80, 80, 76, 76, 76, 72, 68, 64, 64, 64, 64, 64]` "
    "(= 22 down to 16 cycles). The multiply loop takes the same time every trip; the divide loop gets faster as it goes."])
S += [P("**What we got when we changed `SMOOTH_WIDTH`** (everything else at its default):", h3)]
S += table([
    ["SMOOTH_WIDTH", "3", "11", "21", "41", "101"],
    ["Pulses found in trace 2 (multiply loop)", "2", "20", "20", "20", "19"],
    ["Pulses found in trace 3 (divide loop)", "9", "20", "20", "20", "2"],
], [2.8 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch, W - 6.0 * inch])
S += callout("do", [
    "**Try:** (1) `SMOOTH_WIDTH = 3`: too little smoothing - noise makes fake highs. (2) `101`: too much - the pulses blur together. (3) Find the range that is right for both traces "
    "(11 to 41 here). (4) Set `LOOP_TRACES = [0, 1, 2, 3]`. Traces 0 and 1 have no loop, yet the finder reports a couple of 'pulses' (2 and 7 at the default setting). Look at their "
    "__spacing__ lists - they are not regular. **Never trust a count without looking at the spacing.**"])
S += callout("tip", [
    "**What is actually in the loop?** The compiler turned `A *= 2` into a shift (`lsls`), not a multiply - a free optimisation - and one trip round the loop is roughly ten instructions, "
    "most of them loading and storing the two `volatile` variables (`A` and the counter `i`). The divide loop uses the real `sdiv` divide instruction instead. "
    "(Listing from arm-none-eabi-gcc 10.3.1; other compiler versions arrange things slightly differently.)"], title="GOOD TO KNOW")
S += [CondPageBreak(4.5 * inch)]

S += [STEP("5", "Why does the divide loop speed up?")]
S += [P("Division is hard for a processor. The ARM documentation says the divide instruction takes between 2 and 12 cycles depending on the numbers it is dividing. The firmware did "
        "`A /= 3` twenty times starting from `A = 0x7FFFFFFF`, so after every trip `A` is a third of what it was. The notebook prints the size of `A` (in bits) next to the measured time of each trip.")]
S += EDIT([
    ["`A_START`", "`0x7FFFFFFF`", "The value the recorded firmware started with."],
    ["`DIVISOR`", "`3`", "The number it divided by."],
])
S += table([
    ["trip", "A before the divide", "bits in A", "measured cycles"],
    ["0", "`0x7fffffff`", "31", "22"],
    ["1", "`0x2aaaaaaa`", "30", "21"],
    ["4", "`0x1948b0f`", "25", "20"],
    ["9", "`0x1aa2f`", "17", "19"],
    ["12", "`0xfc8`", "12", "18"],
    ["14", "`0x1c0`", "9", "16"],
    ["18", "`0x5`", "3", "16"],
], [0.8 * inch, 2.4 * inch, 1.2 * inch, W - 4.4 * inch])
S += [FIG("cell20_6.png", 5.8 * inch, "Cycles per trip (blue) and bits in `A` (green) fall together.")]
S += callout("see", [
    "The last line prints `correlation between 'bits in A' and 'cycles per trip': r = +0.97`. Near +1 means the two move together: the smaller the number, the faster the divide. "
    "The __data__ changes the __timing__."])
S += callout("do", [
    "**Try:** change `A_START` and `DIVISOR` and watch the `A` and `bits` columns change. The __measured__ column does not - the recording used `0x7FFFFFFF` and 3. "
    "You can test a different start value for real in Step 7."])
S += [PageBreak()]

# ================================================================ STEP 6
S += [H1("Step 6 - what if the loop ran 5 times? Or 50?")]
S += [P("On hardware you would edit the C code, rebuild and reflash to find out. Here is a shortcut: take the real multiply loop, average its middle trips into one clean "
        "**template trip** (60 samples = 15 cycles, averaged from 18 real trips), stack copies to make a trace for any loop count, and add noise.")]
S += callout("warn", [
    "This is a **model** built from real data, not a new measurement. Real hardware has details it does not capture. Step 7 lets you check a prediction for real."])
S += EDIT([
    ["`LOOP_COUNT`", "`20`", "How many trips round the loop to build."],
    ["`NOISE`", "`0.01`", "Noise added to the model: 0 = perfectly clean, 0.1 = quite noisy, 0.3 = awful."],
    ["`SEED`", "`1`", "Change for a different random noise pattern."],
])
S += [FIG("cell23_7.png", 6.2 * inch, "Top: the model with 20 stacked trips (finder counts 20). Bottom: the real recording.")]
S += callout("see", [
    "`prediction: 20 trips x 60 samples = 1200 samples = 300 clock cycles`, and the model's pulses sit at the same places as the real recording's. The notebook also prints that the real "
    "recording's own noise is only about 0.0045 - it is a very clean recording."])
S += [P("**The pulse finder's count against noise** (smoothing fixed at 21) - what we got:", h3)]
S += table([
    ["NOISE", "0", "0.02", "0.05", "0.1", "0.2", "0.3"],
    ["`LOOP_COUNT = 5`: pulses found", "5", "5", "5", "5", "3", "3"],
    ["`LOOP_COUNT = 20`: pulses found", "20", "20", "20", "20", "3", "3"],
    ["`LOOP_COUNT = 40`: pulses found", "40", "40", "40", "26", "3", "3"],
], [2.6 * inch, 0.7 * inch, 0.7 * inch, 0.7 * inch, 0.7 * inch, 0.7 * inch, W - 6.1 * inch])
S += [P("**Slider version.** The next cell shows the same model with two sliders (trips and noise). Drag them and the plot redraws. If the sliders do not appear, use the cell above - it does the same thing.")]
S += [FIG("step6_sliders.png", 4.6 * inch, "Sliders at 10 trips and noise 0.19: the model is so noisy the pulse finder says 3, not 10.")]
S += callout("do", [
    "**Try:** (1) `LOOP_COUNT = 5`, then 50; check the printed prediction (__trips x 60 samples__). (2) Raise `NOISE` until the count goes wrong - where does it fail? "
    "(3) Go back to Step 4 and raise `SMOOTH_WIDTH`: can you rescue the count? (4) Why can we stack copies of the multiply loop's trip but not the divide loop's? __(Step 5: its trips are all different.)__"])
S += [PageBreak()]

# ================================================================ STEP 7
S += [H1("Step 7 - your turn on the real chip (hardware only)")]
S += [P("Now test your predictions on the real target. The cell **edits the C code that runs between the trigger signals**, rebuilds the firmware, flashes the chip, captures a fresh trace and "
        "**measures the loop** in it. Each run takes about 10 seconds because it rebuilds and reflashes.")]
S += callout("do", [
    "**Before you start:** (1) Assemble the Husky kit as in Lab 0 and plug it in. (2) In the first cell set `VERSION = 'HARDWARE'`. (3) Choose **Kernel > Restart & Run All** - the Setup cells "
    "now also connect to the Husky and flash a baseline firmware. (4) Close any other notebook that is connected to the Husky: only one program can hold it."])
S += [H2("A live trace looks different from the recorded ones")]
S += table([
    ["", "Recorded traces (Steps 1 - 6)", "Live trace from the Husky"],
    ["Length", "2000 samples", "**5000 samples**"],
    ["Samples per clock cycle", "4", "**4** (target clock 7.36 MHz, ADC 29.45 MHz) - the same"],
    ["Multiply loop (`A *= 2;`)", "15 cycles (60 samples) per trip", "**20 cycles (80 samples)** per trip - a different firmware build"],
    ["Divide loop (`A /= 3;`)", "22 cycles falling to 16", "**30 cycles falling to 23**"],
    ["Where your code starts", "from about sample 0", "near **sample 410** (start-up code runs first)"],
    ["How a loop is found", "`find_pulses()` (Step 4)", "**`measure_loop()`**: it compares each block of `P` samples with the next block; inside a loop they repeat, so the match is above 0.9 at the loop's trip length"],
], [2.0 * inch, 2.1 * inch, W - 4.1 * inch], bold_first_col=True)
S += callout("warn", [
    "**Do not use `find_pulses()` on a live trace.** It was tuned on the smooth recorded traces and finds only a couple of pulses on a real capture. Step 7 uses the correlation measurement instead."])
S += [P("**Before you capture your own**, run the notebook's __reference captures__ cell. It plots the four live traces next to the recorded ones and measures the experiments below on bundled captures "
        "(`traces/hardware_reference/`), so you can see what to expect first.")]
S += EDIT([
    ["`MY_OPERATION`", "`\"A *= 2;\"`", "The C statement inside the loop. Try `\"A += 2;\"`, `\"A ^= 0x55;\"`, `\"A *= 3;\"`, `\"A /= 3;\"`."],
    ["`MY_COUNT`", "`20`", "How many trips round the loop."],
    ["`MY_A_START`", "`\"0x2BAA\"`", "Starting value of `A`. For a divide try `\"0x7FFFFFFF\"` or `\"0x100\"`."],
])
S += [P("With the defaults the notebook builds this C code between the triggers:")]
S += code("""
volatile long int A = 0x2BAA;
volatile int i;
for (i = 0; i < 20; i++) {
    A *= 2;
}
""")
S += [FIG("loop_found.png", 6.0 * inch, "Step 7 with `A *= 2;` x 20 on a real chip. The green band is the loop the measurement found (sample 410 to 2036); the lower plot shows the trip length "
          "in each 300-sample window: a steady **20 cycles** while the loop runs (red).", hw=True)]
S += callout("see", [
    "The cell prints the C code, rebuilds, flashes, shows a plot titled `YOUR capture: A *= 2; x 20`, and prints `every trip takes 80 samples = 20 clock cycles` and "
    "`the loop runs from sample 410 to 2036 (1626 samples) = about 20.3 trips (you asked for 20)`. The largest swing printed above it is about 0.4; the ADC limit is 0.5."])
S += [P("**Experiments - predict first, then run:**", h3)]
S += table([
    ["Change", "What do you predict?", "Measured on a real Husky + SAM4S"],
    ["`MY_COUNT` = 10, then 40", "How long is the whole loop? How many trips does the measurement find?",
     "**20 cycles (80 samples) per trip** every time; the loop starts near sample 410 and spans **10.3, 20.4 and 40.3 trips** - the count scales with `MY_COUNT`"],
    ["`\"A += 2;\"`, `\"A ^= 0x55;\"`, `\"A *= 3;\"`", "Is the trip still about 20 cycles? Can you tell an add from an XOR by timing?",
     "**All 20 cycles per trip** (20.4, 20.3, 20.3 trips): an add, an xor and a multiply take the same time here, so you **cannot tell them apart by timing**"],
    ["`\"A /= 3;\"` with `\"0x7FFFFFFF\"`", "Do the trips get shorter, as in Step 4?", "**30, 29, 28, 27, 26, 25, 24, 23 cycles** in successive windows"],
    ["The same divide with `\"0x100\"`", "`A` is small from the start. Do the trips still change length?",
     "Starts at about **23 cycles** and settles at **20** after a few trips: once `A` reaches 0 the divide is as fast as any other instruction"],
], [1.7 * inch, 1.9 * inch, W - 3.6 * inch])
S += [FIG("scaling.png", 5.2 * inch, "The loop's length scales with `MY_COUNT`: 826, 1628 and 3226 samples for 10, 20 and 40 trips - 80 samples (20 cycles) per trip.", hw=True),
      FIG("divide.png", 5.6 * inch, "A constant loop stays at 20 cycles per trip. The divide of a big number starts at 30 and shrinks to 23; the divide of a small number settles at 20.", hw=True)]
S += callout("tip", [
    "**For the divide loops the trip length is not constant**, so a single period does not describe them. The Step 7 cell notices this and prints the trip length of every window instead "
    "(`trip length per window (cycles): [30, 29, 29, ...]`)."], title="GOOD TO KNOW")
S += callout("warn", [
    "**Safe to experiment:** the notebook edits a private copy of the firmware (`firmware/mcu/simpleserial-base-lab2`) and restores a clean copy every time the Setup cell runs. "
    "Your own change never touches the original `simpleserial-base`."])
S += [P("More about the live trace - the Setup lines to expect, the four live traces next to the recorded ones, a flat or clipped trace - is in the separate PDF "
        "**Lab 2_1A - What You Should See on a Real Husky**.")]
S += [CondPageBreak(2.4 * inch)]

# ================================================================ STEP 8
S += [H1("Step 8 - check your understanding")]
S += [P("Try each question first. The answers are underneath - cover them up!")]
S += table([
    ["#", "Question", "Answer"],
    ["1", "How many samples make one clock cycle? How did you find out?",
     "**4.** The autocorrelation has its tallest bar at 4 samples (Step 2): the shape repeats every 4 samples, and that is the clock."],
    ["2", "How many pulses did the multiply loop make, and how many cycles was each trip? And the divide loop?",
     "**20 pulses** in each. The multiply loop: 60 samples = **15 cycles** every trip. The divide loop: from about 88 samples (**22 cycles**) down to about 64 samples (**16 cycles**)."],
    ["3", "The divide loop's pulses move closer together. Why?",
     "The divide finishes sooner when its numbers are smaller. `A` is divided by 3 every trip, so it needs fewer bits and each trip takes fewer cycles. "
     "**The data changes the timing** - the key idea behind many side-channel attacks."],
    ["4", "Why is a loop of 20 easier to spot than 20 instructions written out one after another?",
     "A loop repeats the same shape many times, so the repetition stands out. 20 separate one-cycle instructions are a short burst of near-identical activity that blends into what is "
     "around it (and the loop adds about ten instructions of overhead per trip)."],
    ["5", "If the multiply loop ran 10 times instead of 20, what would you expect? What about 40?",
     "**10 pulses** and a loop about half as long (about 600 samples). **40 pulses** and about 2400 samples - if your capture window is shorter than that you only see the first part."],
    ["6", "We wrote `A *= 2;` - is the chip actually using a multiplier? How would you find out?",
     "No. The compiler replaced `* 2` with a __shift__ (`lsls`), which is cheaper. You find out by reading the compiled code (the `.lss` file after a hardware build). "
     "**Never assume the machine does what the C source looks like it does.**"],
    ["7", "On a real chip your multiply loop takes 20 cycles per trip, but the recorded one took 15. Is something wrong? What stays the same?",
     "No. The recorded traces came from a different firmware build, so the compiler laid the same C loop out differently. What stays the same: a loop repeats its pattern, "
     "the loop's length scales with the count, an add, an xor and a multiply cost the same, and a divide gets faster as `A` shrinks."],
], [0.4 * inch, 2.4 * inch, W - 2.8 * inch])
S += [H2T("You are done when...")]
S += table([
    ["", "Check"],
    ["[  ]", "You measured 4 samples per clock cycle yourself (Step 2)."],
    ["[  ]", "You found 20 pulses in both loops and can say how long a trip takes in cycles (Step 4)."],
    ["[  ]", "You can explain why the divide loop speeds up (Step 5)."],
    ["[  ]", "You predicted what a different loop count would look like (Step 6)."],
    ["[  ]", "**With a Husky:** you changed the C code, measured the loop on the real chip and compared your numbers with the table in Step 7."],
], [0.45 * inch, W - 0.45 * inch])
S += [P("**Next:** Lab 2_1B uses the same idea to break a password check - the chip works a little longer for each correct character, and that shows up in the trace. "
        "Its own Explorer notebook and guide (**Lab 2_1B Explorer - Student Guide**) go with it.")]
S += [PageBreak()]

# ================================================================ TROUBLESHOOTING
S += [H1("Troubleshooting")]
S += [P("Find the message you see, read what it means, try the fix. The **Source** line says how each entry was established.")]


def T(rows):
    return table([["#", "What you see", "What it means", "Fix"]] + rows, [0.45 * inch, 2.15 * inch, 1.75 * inch, W - 4.35 * inch])


S += [H2T("The first six steps (no hardware)")]
S += T([
    ["E-1", "`FileNotFoundError: ... traces/lab2_1A_trace0.npy`",
     TC("The traces folder is missing, or the notebook is not in `courses/sca101`.", "Notebook source code"),
     "Check `jupyter/courses/sca101/traces/` holds four `.npy` files and that the Explorer notebook sits beside it. An old copy of the notebooks may lack them - use the course version."],
    ["E-2", "`NameError: name 'traces' is not defined` (or `find_pulses`, `plot_trace`, ...)",
     TC("The Setup cells have not been run in this session (for example after a kernel restart).", "Notebook source code"),
     "**Kernel > Restart & Run All**, or run the two Setup cells again."],
    ["E-3", "`RuntimeError: Run the Step 2 cell first - it measures how many samples make one clock cycle.`",
     TC("A later step needs the number Step 2 measures.", "Notebook source code"),
     "Run the Step 2 cell (the autocorrelation one), then the step you were on."],
    ["E-4", "Later cycle counts are twice what the guide says",
     TC("You left `LAG_MIN, LAG_MAX = 5, 12` in Step 2, so the clock measured 8 samples per cycle.", "Reproduced"),
     "Set `LAG_MIN, LAG_MAX = 2, 8`, run the Step 2 cell again, then re-run the later cells."],
    ["E-5", "The plot or numbers did not change after you edited a cell",
     TC("Edits only take effect when you run the cell.", "General Jupyter"),
     "Press **Shift+Enter** (or **Ctrl+Enter**) on the cell you edited."],
    ["E-6", "No plot appears, only text such as `<Figure size 1100x340 ...>`",
     TC("The Setup cell's `%matplotlib inline` did not run, or matplotlib is missing.", "General Jupyter"),
     "Re-run the Setup cell. If it still fails: `python -m pip install matplotlib` in your ChipWhisperer environment, then restart the kernel."],
    ["E-7", "The pulse count is wrong (too many, too few, or 2 pulses from a trace with no loop)",
     TC("The smoothing is too light or too heavy, or the trace has no real loop.", "Reproduced"),
     "Look at the printed spacing list, not just the count. Try `SMOOTH_WIDTH` between 11 and 41 (see the table in Step 4)."],
    ["E-8", "The sliders do not appear, or `Error displaying widget: model not found`",
     TC("`ipywidgets` is missing, or the notebook was reopened without re-running the cell.", "General Jupyter"),
     "Re-run the slider cell. If it prints `ipywidgets is not installed`: `python -m pip install ipywidgets`. The cell above the sliders does the same job."],
])
S += [Spacer(1, 4), H2T("Step 7 (hardware)")]
S += T([
    ["E-9", "`Step 7 needs a ChipWhisperer. Set VERSION = 'HARDWARE' ...`",
     TC("`VERSION` is still `'SIMULATED'`.", "Notebook source code"),
     "Set `VERSION = 'HARDWARE'` in the first cell, then **Kernel > Restart & Run All**."],
    ["E-10", "`RuntimeError: firmware build failed` with compiler text above it",
     TC("The firmware could not be built: missing compiler, missing C library, or the notebooks are not inside the `chipwhisperer` folder.", "Notebook source code"),
     "Run Lab 0 check 3 (`make` and `arm-none-eabi-gcc`). On Linux see the Linux guide entries L-24 to L-26."],
    ["E-11", "`OSError: Could not find ChipWhisperer` or `Unable to communicate with found ChipWhisperer ...`",
     TC("The Husky is not visible, or another program already holds it.", "Source code"),
     "**Kernel > Shut Down All Kernels** (and close other lab tabs), then unplug and replug the Husky. On Linux see Linux guide 6.3."],
    ["E-12", "`OSError: timeout` (SAM-BA) or `Verify FAILED` while flashing",
     TC("The SAM4S target board is not the one on the CW313 (the look-alike iCE40 FPGA board), is not seated, or the Husky is stuck.", "Husky kit bring-up"),
     "Check the board label says SAM4S, reseat it, check the 20-pin ribbon, then physically unplug and replug the Husky (a stuck Husky can also fail at its first FPGA upload with "
     "`usb1.USBErrorTimeout`) and run the Setup cells again."],
    ["E-13", "`IOError: capture_trace timed out 3x - check trigger (CW313 JP2 = T-GPIO4) and target`, or `Timeout in OpenADC capture(), no trigger seen`",
     TC("The scope never saw the trigger: wrong jumper, target not running, no power - or the board still holds **another lab's firmware** (for example Lab 2_1B's), which does not raise the trigger.", "Measured on hardware"),
     "Check CW313 jumper `JP2` is on **T-GPIO4**, the target is powered over the ribbon, then run the **Setup cells again** (they reflash the right firmware)."],
    ["E-14", "The captured trace is almost flat",
     TC("The Measure SMA cable (Husky `Pos`) is not connected properly.", "Husky kit bring-up"),
     "Reseat both ends of the `Pos` cable (finger-tight) as in the Lab 0 assembly list."],
    ["E-15", "The cell shows `[*]` for a long time",
     TC("Step 7 is rebuilding and reflashing (about 10 s).", "Notebook source code"),
     "Wait. If it is still busy after a minute, use **Kernel > Interrupt**, then check E-11 and E-12."],
    ["E-16", "A solid band stuck at +/-0.5 (the printed largest swing is 0.5)",
     TC("The signal is bigger than the ADC can measure (**clipping**). Seen once on a real kit after the `Pos` cable was moved.", "Husky kit bring-up"),
     "Reseat both ends of the `Pos` cable. If it persists lower the gain, for example `scope.gain.db = 15`, and capture again."],
    ["E-17", "`no repeating loop found near the start of your code`, or a number of trips far from `MY_COUNT`",
     TC("The live trace is flat or clipped, or the loop is too short or too weak to match.", "Measured on hardware"),
     "Check E-14 and E-16, run Step 7 again, and look at the green band in the plot - it must cover the whole loop. Details: section 5 of __What You Should See on a Real Husky__."],
    ["E-18", "`WARNING:root:SAM3U Serial buffers OVERRUN` once after flashing",
     TC("A harmless USB buffer warning; it appeared once in most real runs and the run carried on.", "Husky kit bring-up"),
     "Ignore it. If it is followed by failed captures, use a short data-capable USB-C cable straight into the computer (no hub)."],
])
S += [CondPageBreak(4.0 * inch)]

# ================================================================ APPENDIX
S += [H1("Appendix A - every variable you can edit")]
S += table([
    ["Step", "Variable", "Default", "What it does"],
    ["Setup", "`VERSION`", "`'SIMULATED'`", "`'SIMULATED'` = recorded traces; `'HARDWARE'` = also connect to the Husky."],
    ["1", "`TRACE`", "`2`", "Which trace to show (0 to 3)."],
    ["1", "`START, END`", "`0, 600`", "Zoom window in samples."],
    ["1", "`SMOOTH`", "`1`", "Smoothing width (1 = raw)."],
    ["1", "`FLIP`", "`False`", "Turn the plot upside down so up = more power."],
    ["2", "`TRACE_FOR_CLOCK`", "`0`", "Trace used to measure the clock."],
    ["2", "`LAG_MIN, LAG_MAX`", "`2, 8`", "Range of repeat periods to search. Put back to 2, 8 after experimenting."],
    ["2", "`ZOOM, WIDTH`", "`100, 60`", "Where to look, and how many samples to show, with cycle lines."],
    ["3", "`A_TRACE, B_TRACE`", "`0, 1`", "Which two traces to overlay."],
    ["3", "`SHIFT_B`", "`0`", "Slide trace B sideways by this many samples."],
    ["3", "`START, END`", "`0, 500`", "Zoom window."],
    ["4", "`SMOOTH_WIDTH`", "`21`", "Smoothing used by the pulse finder."],
    ["4", "`MIN_GAP`", "`30`", "Smallest allowed spacing between pulses."],
    ["4", "`TOLERANCE`", "`0.4`", "Allowed change in spacing from pulse to pulse."],
    ["4", "`LOOP_TRACES`", "`[2, 3]`", "Traces to analyse."],
    ["5", "`A_START, DIVISOR`", "`0x7FFFFFFF, 3`", "Starting value and divisor used for the table of `A`."],
    ["6", "`LOOP_COUNT`", "`20`", "Trips in the model."],
    ["6", "`NOISE`", "`0.01`", "Noise added to the model."],
    ["6", "`SEED`", "`1`", "Random seed for the noise."],
    ["7", "`MY_OPERATION`", "`\"A *= 2;\"`", "C statement inside the loop."],
    ["7", "`MY_COUNT`", "`20`", "Trips round the loop on the real chip."],
    ["7", "`MY_A_START`", "`\"0x2BAA\"`", "Starting value of `A` on the real chip."],
], [0.7 * inch, 1.9 * inch, 1.5 * inch, W - 4.1 * inch])

S += [PageBreak(), H1("Appendix B - Glossary")]
S += table([
    ["Term", "Meaning"],
    ["**sample**", "One measurement of the power signal. A trace is a list of samples (2000 in the recorded traces, 5000 on a live capture)."],
    ["**clock cycle**", "One tick of the target's clock. The chip does its work in these steps. Here, 4 samples = 1 cycle."],
    ["**trace**", "The recorded power signal for one run of the code between the trigger signals."],
    ["**trigger**", "A signal from the target that tells the ChipWhisperer when to start and stop recording."],
    ["**trip (iteration)**", "One pass round a loop. A loop of 20 makes 20 trips."],
    ["**pulse**", "The repeating hump a loop leaves in the trace - one per trip."],
    ["**autocorrelation**", "Comparing a signal with a slid copy of itself to find how often it repeats."],
    ["**smoothing (moving average)**", "Replacing each sample with the average of its neighbours to reduce noise."],
    ["**`volatile`**", "A C keyword that stops the compiler removing or merging accesses to a variable, so the work really happens."],
    ["**`.lss` file**", "The compiler's listing of the machine code it produced. Read it to see what the chip really runs."],
    ["**`sdiv`**", "The ARM instruction for signed divide; its time depends on the numbers."],
    ["**model**", "A simplified stand-in for the real thing, here built by stacking real recorded trips. Useful for predicting, not a measurement."],
    ["**live trace**", "A trace captured from your own Husky, as opposed to a recorded one. Longer (5000 samples) and starts with start-up code."],
    ["**`measure_loop()`**", "Step 7's loop measurement: it compares each block of `P` samples with the next one; a loop shows up as a long run of good matches at its trip length."],
], [2.2 * inch, W - 2.2 * inch])
S += [Spacer(1, 10)] + K.notice()

K.build(doc, S)
