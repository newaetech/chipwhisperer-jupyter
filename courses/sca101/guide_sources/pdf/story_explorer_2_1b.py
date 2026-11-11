"""Builds 'Lab 2_1B Explorer - Student Guide.pdf'.   Usage: python story_explorer_2_1b.py "<output pdf>" """
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
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "explorer_2_1b") + os.sep
NBNAME = "Lab 2_1B - Password Bypass Explorer.ipynb"
GUIDE_VERSION = "1.2 - November 2026"

doc = K.init(OUT,
             header_left="ChipWhisperer SCA101  -  Lab 2_1B Explorer Guide",
             header_right="Password Bypass Explorer",
             footer_left="Companion to: " + NBNAME,
             title="SCA101 Lab 2_1B Explorer - Step-by-Step Student Guide",
             subject="Step-by-step guide to the Lab 2_1B Password Bypass Explorer notebook: edit the numbers, watch the attack work",
             roadmap=[("1 - 2  Find", "the split"), ("3 - 4  Run", "the attack"), ("5 - 6  Break", "it and fix it"), ("7  Real chip", "hardware only"),
                      ("8  Your own", "password (hardware)")])


def FIG(name, width, cap):
    return figure(ASSETS + name, width, cap)


def EDIT(rows):
    return table([["Variable", "Default", "What it does"]] + rows, [1.65 * inch, 1.05 * inch, W - 2.7 * inch])


S = []

# ================================================================ COVER
S += [*K.cover("SCA101  -  LAB 2_1B  (EXPLORER)", ("Password Bypass", "Explorer"),
                  "Step-by-step student guide: edit the numbers, watch the attack work"),
      P("In Lab 2_1B you recover a password from a chip's power trace. This guide goes with a **second, hands-on notebook** "
        "where you change the numbers yourself - which guesses to compare, how to score them, how many captures to average, "
        "how much noise to add - and watch the results update, so you can see **why** the attack works and what would stop it. "
        "No hardware is needed: it runs on recorded traces. **With a ChipWhisperer-Husky you can also run every step on your own chip - "
        "and change the chip's password to one you invent yourself** (Step 8), then watch the attack find it."),
      Spacer(1, 10)]
S += callout("tip", [
    "This guide goes **with** the notebook - it does not replace it. Keep the notebook open next to this PDF. "
    "Every step says what to edit, what you should see, and what to try if you do not see it."], title="HOW TO USE THIS GUIDE")
S += [P("**Which files are which**", h3)]
S += table([
    ["File (folder: jupyter/courses/sca101/)", "What it is", "Open it?"],
    ["`%s`" % NBNAME, "The Explorer. Everything in this guide happens here.", "**Yes**"],
    ["`Lab 2_1B - Power Analysis for Password Bypass (MAIN).ipynb`", "The original lab. Do it before or after the Explorer.", "Optional"],
    ["`SOLN_Lab 2_1B - ...ipynb`", "Answer key for the original lab.", "If stuck"],
    ["`Lab 2_1B - Firmware Change and Flash Walkthrough.ipynb`", "How to change the password on your own chip (hardware). The Explorer's Step 8 does the same thing for you.", "Optional"],
    ["`firmware/mcu/basic-passwdcheck/basic-passwdcheck.c`", "(a different folder: `chipwhisperer/firmware/...`) The chip's firmware, where the password is stored. **Step 8 edits line 73 of it.**", "Step 8"],
    ["`... (HARDWARE).ipynb`, `... (SIMULATED).ipynb`", "Back-end helpers that the notebooks run for you.", "**No**"],
], [3.0 * inch, 2.9 * inch, W - 5.9 * inch])
S += [P("**The four colored boxes you will see everywhere**", h3)] + legend()
S += [Spacer(1, 4),
      P("Guide version %s. The numbers for Steps 1 to 6 come from running the notebook on **Ubuntu 22.04** with the recorded "
        "traces; the simulator picks a random recorded trace per guess, so your last digits will differ. **Steps 7 and 8 were run on "
        "a real ChipWhisperer-Husky with a CW313 and a SAM4S target** (Windows 11, Python 3.12, ChipWhisperer 6.0.0, firmware 1.5.0); "
        "every 'real chip' number in this guide was measured there. Your kit will give somewhat different absolute numbers - "
        "the **patterns** (a margin of about 5x, a split that moves about 40 samples per character) are what to look for." % GUIDE_VERSION, small),
      PageBreak()]

# ================================================================ CONTENTS
S += K.contents()

# ================================================================ BIG PICTURE
S += [H1("The big picture")]
S += [P("**What is the attack?** A simple password checker compares your guess with the real password one character at a time and "
        "**stops at the first wrong character**. A guess whose first character is right therefore gets one comparison further "
        "than a wrong one - it runs different code for longer - and that difference shows up in the chip's **power trace**. "
        "By finding which character makes the trace change, you recover the password **one character at a time** without ever "
        "being told it.")]
S += [P("**What is different about the Explorer?** The original lab walks you through the whole attack once. The Explorer lets you "
        "**poke at every part of it**: every code cell has a clearly marked block of numbers you can change. Change one, press "
        "**Shift+Enter**, and the plots and the printed numbers change straight away.")]
S += [P("Your path through the notebook:", h3), Roadmap(W), Spacer(1, 6)]
S += table([
    ["Step", "What you do", "What you learn", "Hardware?"],
    ["1", "Overlay a right and a wrong guess.", "A right character makes the trace take a different path.", "No"],
    ["2", "Find the sample where the traces split.", "The split moves **40 samples later** for every correct character.", "No"],
    ["3", "Score every possible character.", "The right one scores about 30x higher; how window and scoring method change that.", "No"],
    ["4", "Run the whole attack.", "185 captures instead of 60 million guesses.", "No"],
    ["5", "Add noise; average captures.", "How much noise the attack can take - and that averaging cuts noise by sqrt(R).", "No"],
    ["6", "Add random delays.", "A few samples of delay break a single capture; averaging restores it, up to a point.", "No"],
    ["7", "Run it on your own chip.", "The same code works on real traces - and what a real chip's numbers look like.", "**Yes**"],
    ["8", "Choose your own password.", "Which file and line hold the password, what rebuilding changes, and how the attack behaves on a password you invented.", "**Yes**"],
    ["9", "Answer nine questions.", "Put it all together.", "No"],
], [0.5 * inch, 2.1 * inch, 3.3 * inch, W - 5.9 * inch], bold_first_col=True)
S += [PageBreak()]

# ================================================================ BEFORE YOU START
S += [H1("Before you start")]
S += [P("Tick every row. Most problems later come from something on this list.")]
S += table([
    ["", "You need", "How to check"],
    ["[  ]", "**Lab 0 - SCA101 Setup** passed.", "ChipWhisperer, numpy and matplotlib import without errors."],
    ["[  ]", "**ChipWhisperer 6.0.0 and numpy 1.26.4** (the versions the labs were tested with).",
     "`python -c \"import chipwhisperer as cw, numpy; print(cw.__version__, numpy.__version__)\"` prints `6.0.0 1.26.4`. Anything else: see E-15."],
    ["[  ]", "The **`cwtraces`** package installed. It holds the recorded traces for the simulated labs.",
     "`python -c \"import cwtraces\"` prints nothing. If it says `ModuleNotFoundError`, see E-1."],
    ["[  ]", "Jupyter running from your ChipWhisperer environment.", "On Linux see the Linux guide Part 3."],
    ["[  ]", "The course notebooks, including the Explorer.", "`jupyter/courses/sca101/` contains `%s`." % NBNAME],
    ["[  ]", "**Only for Step 7:** the Husky kit assembled and plugged in.", "Lab 0's hardware test ends with `hardware OK (disconnected again)`."],
], [0.45 * inch, 3.3 * inch, W - 3.75 * inch])
S += callout("warn", [
    "**`cwtraces` is not installed by `jupyter/requirements.txt`**, so on a fresh install the simulated Lab 2_1B (and this Explorer) "
    "stops with `ModuleNotFoundError: No module named 'cwtraces'`. Install it **together with the numpy limit**, in one command "
    "(paste it as a single line):"])
S += code('python -m pip install cwtraces "numpy<=1.26.4"')
S += callout("tip", [
    "**Why the numpy limit?** ChipWhisperer 6.0.0 needs numpy 1.26.4 or older. On Python 3.12 (Ubuntu 24.04), a plain "
    "`pip install` of the notebook requirements can silently replace ChipWhisperer 6.0.0 with the old 5.6.1 and install numpy 2. "
    "This Explorer still runs on that mix, but **Lab 2_1B (MAIN)** and the solved notebook then fail with "
    "`TypeError: Chart.__init__() missing 1 required positional argument: 'data'`. If you followed the Linux guide's step 2.2 you "
    "already have the right versions; the check in the table above confirms it."], title="GOOD TO KNOW")
S += callout("tip", [
    "**You cannot break anything.** The simulator only ever __returns__ recorded traces. If a plot looks wrong or an error appears, "
    "use **Kernel > Restart & Run All** and you are back to the starting state."], title="GOOD TO KNOW")
S += [H2("How every edit-and-run cell works")]
S += table([
    ["Do this", "Keys"],
    ["Run the cell and move to the next one", "**Shift + Enter**"],
    ["Run the cell and stay on it (best for repeated experiments)", "**Ctrl + Enter**"],
    ["Start over from the top", "**Kernel > Restart & Run All**"],
], [4.6 * inch, W - 4.6 * inch])
S += [P("Every cell you are meant to change starts with the line **`# EDIT THESE`**. Change only what is in that block, then run "
        "the cell. Everything below it just does the drawing and the maths. Steps 5 and 6 need Step 5's cell to have been run first.")]
S += [CondPageBreak(4.2 * inch)]

# ================================================================ SETUP
S += [H1("Setup - open the notebook and run it")]
S += [STEP("S.1", "Open the Explorer")]
S += numbered([
    "Start Jupyter (for Linux: `source ~/.cwvenv/bin/activate`, then `cd ~/chipwhisperer/jupyter`, then `jupyter notebook`).",
    "Click **courses**, then **sca101**.",
    "Click **%s**." % NBNAME,
])
S += [Spacer(1, 4), STEP("S.2", "Choose the version")]
S += EDIT([["`VERSION`", "`'SIMULATED'`", "`'SIMULATED'` = recorded traces from the `cwtraces` package (no hardware). "
            "`'HARDWARE'` = your own Husky + SAM4S: the Setup cell builds and flashes the firmware for you."]])
S += [STEP("S.3", "Run the two Setup cells")]
S += callout("see", [
    "The second cell prints a green check mark and `Ready!  Mode: SIMULATED | trace length: 3000`. It defines the helper "
    "functions used by every later step, including `get_trace(guess)` - send a guess, get its 3000-sample power trace."])
S += callout("ifnot", [
    "`ImportError: The 'cwtraces' package is missing ...` - install it as described above, restart the kernel (E-1). "
    "`ValueError: VERSION must be ...` - mistyped; it must be exactly `'SIMULATED'` or `'HARDWARE'`."])
S += [Spacer(1, 4), STEP("S.4", "Optional: run everything once")]
S += [P("Choose **Kernel > Restart & Run All** to see the finished notebook. In simulated mode it takes about a minute "
        "(Step 4 makes 185 captures; Steps 5 and 6 run many attacks) and should finish with no red error boxes.")]
S += [PageBreak()]

# ================================================================ STEPS 1-2
S += [H1("Steps 1 and 2 - find the split")]
S += [STEP("1", "Look at a guess")]
S += [P("The checker compares your guess with the stored password with a loop that **stops at the first mismatch**:")]
S += code("""
for(uint8_t i = 0; i < sizeof(correct_passwd); i++){
    if (correct_passwd[i] != passwd[i]){
        passbad = 1;
        break;                       // stop at the first mismatch
    }
}
""")
S += [P("The ChipWhisperer records **3000 samples** while this runs. As in Lab 2_1A the trace is **upside down**: bigger negative "
        "swings mean more power. The notebook adds the `\\n` that the serial protocol needs, so you type guesses without it.")]
S += EDIT([["`GUESS_A`, `GUESS_B`", "`\"h\"`, `\"0\"`", "The two guesses to compare (without the newline)."],
           ["`START, END`", "`0, 1000`", "Zoom window in samples (the whole trace is 0 to 3000)."],
           ["`SMOOTH`", "`1`", "Smoothing width: 1 = raw samples, bigger = smoother."]])
S += [FIG("step1.png", 6.1 * inch, "A right first character (`h`) against a wrong one (`0`): identical at first, then different from about sample 430.")]
S += callout("see", [
    "The top plot shows two traces that sit on top of each other until about sample 430, then drift apart. The bottom plot - their "
    "difference - is **flat until about sample 430**, then bursts. The last line prints `total difference between the two traces: "
    "302.7` (yours will be close to 300)."])
S += callout("do", [
    "**Try:** (1) `GUESS_A = \"h\"`, `GUESS_B = \"x\"`: another wrong character - is the picture the same? (2) `\"h0\"` against `\"hx\"`: "
    "now the first character is right for both; where do they split? (3) `\"zzzzz\"` against `\"azzzz\"`. (4) Raise `SMOOTH` to 9."])
S += [CondPageBreak(3.5 * inch)]

S += [STEP("2", "Where do a right and a wrong guess split?")]
S += [P("To understand the leak, be the lab designer: we **know** the password (the simulator's is `h0px3`), so we can compare "
        "the **right** first `k+1` characters with the first `k` characters followed by `\\x01` (a byte that is never part of a "
        "password), for each position `k`, and find the exact sample where the traces stop matching.")]
S += EDIT([["`STUDY_PASSWORD`", "`\"h0px3\"`", "The password to study. On your own chip, use whatever you flashed."],
           ["`THRESHOLD`", "`0.05`", "A difference bigger than this counts as 'the traces have split'."],
           ["`AVERAGES`", "`10`", "Captures averaged for each trace (calms the noise)."],
           ["`SMOOTH_DIFF`", "`1`", "Smoothing applied to the difference before looking for the split."]])
S += [FIG("step2.png", 5.5 * inch, "Difference between a right and a wrong guess for each position; the dashed lines mark where they split.")]
S += callout("see", [
    "A table of five rows. The traces split at samples **433, 473, 513, 553 and 593**, and the last column shows **40** every time: "
    "**each extra correct character pushes the split 40 samples later.** That is the time the checker spends on one more comparison."])
S += callout("tip", [
    "**How long is 40 samples?** The time per character is fixed, but how many samples that covers depends on the capture settings. In "
    "Lab 2_1A the Husky took 4 samples per clock cycle, which would make 40 samples **10 clock cycles**. The recorded traces here "
    "come from a different capture setup (their autocorrelation shows no clear clock pattern), so the notebook counts in samples."],
    title="GOOD TO KNOW")
S += table([
    ["What we changed", "Result"],
    ["`THRESHOLD = 0.2`", "Splits at 445, 485, ... (still 40 apart, but the 'first big difference' comes a little later)"],
    ["`THRESHOLD = 0.01`", "Splits at 428, 468, ... (earlier: even tiny differences count)"],
    ["`AVERAGES = 1`", "433, 473, ... - the same. The recorded traces are very clean."],
], [2.2 * inch, W - 2.2 * inch], bold_first_col=True)
S += [PageBreak()]

# ================================================================ STEPS 3-4
S += [H1("Steps 3 and 4 - score the characters, run the attack")]
S += [STEP("3", "Score every possible character")]
S += [P("Now the real attack: we **don't** know the password. Try every possible character after what we know so far, compare each "
        "trace with a wrong-guess reference (`\\x01`), and give each a **score** - how different it is from the reference. The right "
        "character takes the other path, so it scores far higher than the 35 wrong ones.")]
S += EDIT([["`KNOWN_PREFIX`", "`\"\"`", "The characters already found (start with nothing)."],
           ["`WINDOW_START, WINDOW_END`", "`0, 3000`", "Which samples to compare; the rest are ignored."],
           ["`METRIC`", "`\"sum_abs\"`", "How to turn the difference into one number: `sum_abs` (add up sizes), `sum_sq` (add up squares) or `max_abs` (the single biggest)."],
           ["`REPEATS`", "`1`", "Captures averaged per guess."]])
S += [FIG("step3.png", W, "Score of every first character: `h` towers over the other 35.")]
S += callout("see", [
    "One red bar far taller than the rest, and a line such as `best character: 'h' (score 301.5) | runner-up: 'q' (8.8) | margin: 34.1x`."])
S += [P("What we got when we changed the settings:", h3)]
S += table([
    ["Setting", "Best character (score)", "Runner-up", "Margin", "Right answer?"],
    ["defaults: window 0-3000, `sum_abs`", "`h` (301.5)", "`q` (8.8)", "34x", "yes"],
    ["window 440-600", "`h` (21.2)", "`7` (0.6)", "36x", "yes"],
    ["window 400-500", "`h` (5.5)", "`3` (0.4)", "15x", "yes"],
    ["window 0-300", "`x` (1.5)", "`a` (1.5)", "1.0x", "**no** - a tie"],
    ["`METRIC = \"sum_sq\"`", "`h` (76.4)", "`l` (0.1)", "1364x", "yes"],
    ["`METRIC = \"max_abs\"`", "`h` (0.5)", "`d` (0.0)", "16x", "yes"],
    ["`KNOWN_PREFIX = \"h0p\"`", "`x` (287.2)", "`o` (8.9)", "32x", "yes (the 4th character)"],
], [2.35 * inch, 1.35 * inch, 1.0 * inch, 0.75 * inch, W - 5.45 * inch])
S += callout("do", [
    "**Try:** (1) Walk the prefix: `\"h\"`, `\"h0\"`, `\"h0p\"` - you are finding characters 2, 3, 4. (2) Window `0, 300`: why does it fail? "
    "__(The first split is at sample 433 - the window ends before the traces differ.)__ (3) Compare the margins for the three metrics - "
    "which separates the right character most clearly? (4) `REPEATS = 4`: does the margin change?"])
S += [CondPageBreak(3.5 * inch)]

S += [STEP("4", "Run the whole attack")]
S += [P("Repeat Step 3 for position 1, then 2, then 3... each time adding the best-scoring character to the password found so far. "
        "That is **five rounds of 36 guesses** instead of trying every possible 5-character password.")]
S += EDIT([["`PASSWORD_LENGTH`", "`5`", "How many characters the password has."],
           ["`ATTACK_START, ATTACK_END`", "`0, 3000`", "Which samples to compare."],
           ["`ATTACK_METRIC`", "`\"sum_abs\"`", "`sum_abs`, `sum_sq` or `max_abs`."],
           ["`ATTACK_REPEATS`", "`1`", "Captures averaged per guess."]])
S += [FIG("step4.png", W, "One bar chart per round: in every round exactly one character towers over the other 35.")]
S += callout("see", [
    "`round 1: 'h'`, `round 2: 'h0'`, ... `round 5: 'h0px3'`, then `recovered password: 'h0px3'`, `captures used: 185 (in 16 s)`, and "
    "`brute force would need up to 60,466,176 guesses; the power attack used 185 - about 326,844 times fewer.` In simulated mode the last line "
    "also says `MATCH` against the simulator's hidden password."])
S += table([
    ["What we changed", "Recovered", "Captures"],
    ["`ATTACK_END = 600`", "`h0px7` - four right", "185"],
    ["`ATTACK_END = 500`", "`h0lbl` - first two right", "185"],
    ["`ATTACK_END = 480`", "`h0gud` - first two right", "185"],
    ["`ATTACK_METRIC = \"sum_sq\"` or `\"max_abs\"`", "`h0px3`", "185"],
    ["`ATTACK_REPEATS = 2`", "`h0px3`", "370 (about 28 s)"],
], [3.0 * inch, 2.4 * inch, W - 5.4 * inch], bold_first_col=True)
S += callout("do", [
    "**Try:** set `ATTACK_END` to 500, 480 and 600 as in the table. The window must reach **past the split point**, which moves "
    "40 samples later for every correct character (433, 473, 513, 553, 593): with the window ending at 500 the third character's "
    "split (513) is outside it, so every candidate scores about the same and the attack picks one at random. Which characters does "
    "each setting get right?"])
S += [CondPageBreak(4.8 * inch)]

# ================================================================ STEPS 5-6
S += [H1("Steps 5 and 6 - break it, then fix it")]
S += [STEP("5", "What breaks the attack? Noise - and what fixes it")]
S += [P("The recorded traces are extremely clean. A real chip next to a noisy supply is not. To **turn the noise up** and run the attack "
        "many times quickly, the notebook builds a **model from real traces**: for each position it captures one clean 'right' and "
        "one clean 'wrong' trace (averaged), then adds random noise to every simulated capture. Averaging `R` captures reduces "
        "the noise by a factor of the square root of `R`, so the model uses a smaller noise for repeats. Each cell of the grid runs the "
        "whole attack `TRIALS` times and counts how often it finds the full password.")]
S += callout("warn", [
    "**This is a model built from real data, not a new measurement.** It answers 'how much noise can the attack take?', not "
    "'what are my chip's exact numbers?'."])
S += EDIT([["`NOISE_LEVELS`", "`[0.2, 0.4, 0.8, 1.6, 3.2]`", "Noise (standard deviation) added to every sample. The real recordings have about 0.003."],
           ["`REPEAT_LEVELS`", "`[1, 4, 16, 64]`", "Captures averaged per guess."],
           ["`TRIALS`", "`10`", "Full attacks per cell."],
           ["`MODEL_WINDOW`, `MODEL_METRIC`", "`(0, 3000)`, `\"sum_abs\"`", "Samples compared and scoring method."]])
S += [FIG("step5.png", W, "Attacks that recovered the whole password (out of 10): green = always, red = never.")]
S += [P("What we got (one run of the defaults - yours will differ a little because the noise is random):", h3)]
S += table([
    ["noise \\ captures averaged", "1", "4", "16", "64"],
    ["0.2", "10/10", "10/10", "10/10", "10/10"],
    ["0.4", "2/10", "10/10", "10/10", "10/10"],
    ["0.8", "0/10", "3/10", "10/10", "10/10"],
    ["1.6", "0/10", "0/10", "2/10", "10/10"],
    ["3.2", "0/10", "0/10", "0/10", "4/10"],
], [2.0 * inch] + [(W - 2.0 * inch) / 4] * 4, bold_first_col=True)
S += callout("do", [
    "**Try:** (1) Read along the first column: where does a single capture stop working? (2) Read down a column: each time you "
    "quadruple the averaging, how much more noise can the attack take? (About double.) (3) `MODEL_WINDOW = (0, 1000)`: the attack "
    "tolerates **less** noise (at noise 0.8 with 4 captures it drops to 0/10, and at 3.2 with 64 captures from 4/10 to 0/10) - "
    "a bigger window collects more signal."])
S += [CondPageBreak(4.2 * inch)]

S += [STEP("6", "A defence: random delays")]
S += [P("A well-known defence is to make the chip wait a **random** time before it does the check. The same guess then gives a trace "
        "**shifted** by a different amount every time. Our scoring compares samples at the __same position__, so even two identical guesses "
        "look different. The cell shifts every simulated capture by a random number of samples between `-JITTER` and `+JITTER` and, like "
        "Step 5, runs the whole attack several times for each combination of delay size and captures averaged.")]
S += EDIT([["`JITTER_LEVELS`", "`[0, 2, 3, 4, 8, 16, 32]`", "Random delay sizes (+/- samples) in the grid."],
           ["`JITTER_REPEATS`", "`[1, 4, 16]`", "Captures averaged per guess."],
           ["`JITTER_NOISE`, `JITTER_TRIALS`", "`0.01`, `5`", "A little ordinary noise; full attacks per cell."],
           ["`SHOW_JITTER`", "`8`", "The delay used for the two example charts."]])
S += [FIG("step6a.png", W, "Left: with a delay of up to +/-8 samples the wrong characters score almost as high as the right one. Right: five copies of the same guess no longer line up."),
      FIG("step6b.png", 5.4 * inch, "Attacks that recovered the whole password: delay size (rows) against captures averaged (columns).")]
S += [P("What we got (6 attacks per cell):", h3)]
S += table([
    ["delay (+/- samples) \\ captures averaged", "1", "4", "16"],
    ["0", "6/6", "6/6", "6/6"],
    ["2", "6/6", "6/6", "6/6"],
    ["3", "1/6", "6/6", "6/6"],
    ["4", "2/6", "6/6", "6/6"],
    ["8", "0/6", "3/6", "6/6"],
    ["16", "0/6", "0/6", "0/6"],
    ["32", "0/6", "0/6", "0/6"],
], [2.8 * inch] + [(W - 2.8 * inch) / 3] * 3, bold_first_col=True)
S += callout("see", [
    "A single capture survives a delay of 2 samples but breaks at **3**. Averaging **4 to 16** captures restores the attack up to about "
    "**8** samples. At **16 samples or more** (bigger than the features in the trace) even 16 averages barely help."])
S += callout("do", [
    "**Try:** (1) Explore the edge: `JITTER_LEVELS = [3, 4, 5, 6, 7, 8]`. (2) Why does averaging help at all, when every capture is "
    "shifted differently? __(The shifts are random and independent, so the average is a smooth blur in which the right guess still stands "
    "out - like noise.)__ (3) What would an attacker do about a 32-sample delay? __(Re-align each trace before comparing - the subject of "
    "later labs.)__"])
S += [CondPageBreak(4.5 * inch)]

# ================================================================ STEP 7
S += [H1("Step 7 - run it on your own chip (hardware)")]
S += [P("Everything except the models in Steps 5 and 6 works unchanged on the real chip, because both back-ends give you the same "
        "`cap_pass_trace()` function. (Steps 5 and 6 build their model from your **live** traces, so they work too, just with a slower start.)")]
S += callout("do", [
    "**Before you start:** (1) Assemble the Husky kit as in Lab 0 and plug it in; check the **SAM4S** target board is the one mounted. "
    "(2) In the first cell set `VERSION = 'HARDWARE'`. (3) Choose **Kernel > Restart & Run All** - the Setup cell builds and flashes "
    "`basic-passwdcheck`. (4) Close any other notebook connected to the Husky: only one program can hold it."])
S += callout("see", [
    "The Setup cell prints a block of `scope.gain ... changed from ... to ...` lines (that is the scope being configured: gain 22 = 25 dB, "
    "target clock 7.36 MHz, ADC 29.45 MHz = 4 samples per clock cycle), then the firmware build output and the flashing messages, and "
    "finishes with `Ready!  Mode: HARDWARE | trace length: 3000`. A harmless `SAM3U Serial buffers OVERRUN` warning can appear once. "
    "The Step 7 cell then times one capture and estimates how long Step 4 will take."])
S += [H2("What you should see - the recorded traces next to a real chip")]
S += [P("The table compares the simulator with a real **Husky + CW313 + SAM4S** (one kit, 25 dB gain). **Your numbers will not be identical** - "
        "look for the same __pattern__.")]
S += table([
    ["Where", "Recorded (SIMULATED)", "Real chip (HARDWARE)"],
    ["Time for one capture", "about 0.1 s", "about **0.5 s** (the target is reset before every capture)"],
    ["Step 2: where right and wrong first split", "sample 433, then +40 per character", "about sample **437**, then about **+40** per character (the first gap can read 40 to 51 because of noise)"],
    ["Step 3: score of the right character", "about 300", "about **340**"],
    ["Step 3: scores of the wrong characters", "about 8", "**about 10 to 65** (median about 45)"],
    ["Step 3: margin (right / best wrong)", "about 34x", "about **5x**"],
    ["Step 4: result", "`h0px3` from 185 captures in about 20 s", "`h0px3` from 185 captures in about **100 s**"],
], [2.2 * inch, 1.9 * inch, W - 4.1 * inch], bold_first_col=True)
S += callout("tip", [
    "**Why is the margin smaller?** A real chip is much noisier than the recordings, so the winning character stands 5 times above the "
    "runner-up instead of 34 times. That is still plenty for one capture per guess. The __absolute__ scores depend on the scope gain and on "
    "how well the measurement SMA cable is seated (they moved by a factor of 2 on the kit used here); the **ratio** is what matters."],
    title="GOOD TO KNOW")
S += [FIG("hw_step2.png", 6.3 * inch, "Step 2 on a real chip: the traces of a right and a wrong guess split near sample 437, and each further correct character moves the split about 40 samples later."),
      FIG("hw_step3.png", 6.0 * inch, "Step 3 on a real chip: one character (here `h`, score about 345) towers over the other 35 (the best of them scores about 60)."),
      FIG("hw_step4.png", W, "Step 4 on a real chip: five rounds, five clear winners (red) - the whole password from 185 captures in about 100 s.")]
S += [P("**Experiments - predict first, then run:**", h3)]
S += table([
    ["Change", "What do you predict?", "How you will know"],
    ["Step 2 on your chip", "Is the split-to-split gap still about 40 samples?", "The `later than the previous by` column."],
    ["Step 3 with `REPEATS = 1`, then `4`", "Is your chip noisier than the recorded traces? Does averaging help?", "The margin printed under the bar chart (real chip: about 5x)."],
    ["Change the password in the firmware (**Step 8** does it for you); run the attack on it",
     "Does the attack find your new password? Does it take longer?", "Step 8's recovered password and its time."],
], [2.6 * inch, 2.1 * inch, W - 4.7 * inch])
S += callout("warn", [
    "**On hardware the firmware's real password is the answer.** The line that says `MATCH` against `h0px3` only appears in simulated mode; "
    "if you changed the firmware password, compare the recovered one with your own."])
S += [CondPageBreak(2.4 * inch)]

# ================================================================ STEP 8
S += [PageBreak(), H1("Step 8 - choose your own password (hardware)")]
S += [P("So far the chip has been guarding `h0px3`. That password is **not** in the notebook and **not** in any Python code: it is a text "
        "string inside the **firmware** - the program that runs on the target chip. To change it you change one line of the firmware's C "
        "source file, **rebuild** the firmware and **write it onto the chip**. This step shows exactly which file, which line, what else "
        "changes, and what the attack does with a password you invented.")]
S += callout("warn", [
    "**Hardware only.** In `'SIMULATED'` mode the traces are fixed recordings of `h0px3`; they cannot react to a new password. The Step 8 "
    "cells then only show information and refuse to change anything."], title="WATCH OUT")

S += [H2("8.1  Where the password lives")]
S += table([
    ["**Folder**", "`firmware/mcu/basic-passwdcheck/` inside the `chipwhisperer` folder. From the notebook (which lives in `chipwhisperer/jupyter/courses/sca101/`) "
                   "that is `../../../firmware/mcu/basic-passwdcheck/`. On Linux: `~/chipwhisperer/firmware/mcu/basic-passwdcheck/`. "
                   "On Windows: wherever you cloned `chipwhisperer`, for example `C:\\Users\\you\\ChipWhisperer\\chipwhisperer\\firmware\\mcu\\basic-passwdcheck\\`."],
    ["**File**", "`basic-passwdcheck.c` - the **only** file you edit."],
    ["**Line**", "**73** in the course version of the file: `char correct_passwd[] = \"h0px3\";`  If your copy has a different line number "
                 "(someone edited above it), search the file for `correct_passwd`."],
], [0.9 * inch, W - 0.9 * inch], header=False)
S += code("""
chipwhisperer/
  jupyter/courses/sca101/                 <- the notebooks live here
  firmware/mcu/basic-passwdcheck/
      basic-passwdcheck.c                 <- EDIT line 73 (the only file you edit)
      makefile                            <- how to build it (leave alone)
      basic-passwdcheck-CWHUSKY.hex       <- the build that is written to the chip
      basic-passwdcheck-CWHUSKY.elf/.bin/.lss/.map/.sym/.eep   <- other build outputs
      objdir-CWHUSKY/                     <- compiled pieces
""")
S += [P("The lines around it, with what each one does:")]
S += code("""
char passwd[32];                    // line 72: your GUESS goes here (at most 31 characters)
char correct_passwd[] = "h0px3";    // line 73: THE PASSWORD - the one thing you change
...
for(uint8_t i = 0; i < sizeof(correct_passwd); i++){   // line 103: once per password character
    if (correct_passwd[i] != passwd[i]){               // line 104: compare guess and password
        passbad = 1;                                   // line 105: remember it was wrong
        break;                                         // line 106: STOP at the first wrong one
    }                                                  //           = the leak you attack
}
""")
S += callout("do", [
    "Open the notebook's Step 8 and run the **first code cell** (`show_password_line()`). It prints the line from __your__ copy of the file and the "
    "full path of the file."])
S += callout("see", [
    "`  73:     char correct_passwd[] = \"h0px3\";`  followed by `file: ...\\firmware\\mcu\\basic-passwdcheck\\basic-passwdcheck.c`. If your copy was edited "
    "before, it shows the edited password (and perhaps a second, commented-out line that starts with `//`)."])

S += [H2("8.2  What makes a good password")]
S += table([
    ["Rule", "Why"],
    ["**1 to 31 characters**", "The chip's input buffer holds 31 characters plus an end marker. A password of 32 or more can **never** be typed in full, so it can never "
                                "unlock. (Measured: 5, 8, 12 and 31 characters unlock; 32 and 40 do not.)"],
    ["**Lowercase letters `a-z` and digits `0-9`**", "These are the 36 characters the attack tries. The chip itself accepts any character, but the attack cannot find one "
                                                     "outside this set - you will see it fail on purpose below."],
    ["**No `\"` and no `\\`**", "They would break the C string on that line. The notebook refuses them."],
    ["**Short is faster**", "The attack makes about 37 captures per character, about 0.5 s each on a real chip: roughly 20 s per character."],
], [2.2 * inch, W - 2.2 * inch])

S += [H2("8.3  What changes when you change it")]
S += [FIG("pw_flow.png", W, "Everything that happens when you change the password. You touch one file; the notebook does the rest.")]
S += table([
    ["Thing", "What happens"],
    ["`basic-passwdcheck.c`", "**You change it** - one line. The notebook first saves a copy of the original as `basic-passwdcheck.c.orig` (once)."],
    ["`basic-passwdcheck-CWHUSKY.hex`, `.elf`, `.bin`, `.lss`, `.map`, `.sym`, `.eep` and the `objdir-CWHUSKY/` folder",
     "**Rebuilt** every time `make` runs (about 4 s). The `.hex` is what gets written to the chip. Git ignores these files, so `git status` shows only the `.c` file as changed."],
    ["Where the password text appears", "As readable text in the `.elf`, `.bin`, `.lss` and `objdir-CWHUSKY/basic-passwdcheck.o`. The `.hex` file writes every byte as two hex "
                                         "digits, so `lfbc1` appears there as `6c66626331`. (Try: `grep -a lfbc1 basic-passwdcheck-CWHUSKY.bin`.)"],
    ["The chip's flash memory", "**Reprogrammed** with the new build (about 5 s). The old password is gone from the chip. Re-running the Setup cell later builds and flashes "
                                 "**from the edited `.c` file**, so the new password stays until you restore the original."],
    ["The power traces", "Still a split per character, now at __your__ characters. The positions barely move: about sample 437 for the first character, then about 40 more per character."],
    ["`STUDY_PASSWORD`, `PASSWORD_LENGTH` in the notebook", "**You** keep these equal to the firmware's password (Steps 2, 4, 5 and 6 each have them in their EDIT block). The Step 8 cell sets them only for Step 8's own attack."],
    ["Lab 2_1B (MAIN) and the solved notebook", "Their attack loop is fixed at 5 characters and the last check says `assert guessed_pw == 'h0px3'`. For a new password change the loop count "
                                                "(`for _ in range(5):`), the `assert`, and `EXPECTED_PW`."],
], [2.2 * inch, W - 2.2 * inch])

S += [H2("8.4  Do it in the notebook")]
S += numbered([
    "Run the **helper-functions** cell. It prints `helpers ready. mode: HARDWARE`. (It defines `use_password()`, `ask_chip()`, `attack_my_password()` and `restore_original_password()`.)",
    "In **Put your password on the chip** edit `MY_NEW_PASSWORD = \"lfbc1\"` to your own 1 to 31 characters (a-z, 0-9) and run the cell.",
    "Run **Attack your password**. Leave `ATTACK_LENGTH = None` the first time.",
    "Go back to Steps 2 and 4 and set `STUDY_PASSWORD` and `PASSWORD_LENGTH` to your password and its length, then re-run them - the split positions and the whole attack now work on your password.",
    "When you are finished run **Put the original back** with `RESTORE_ORIGINAL = True`.",
])
S += callout("see", [
    "`use_password()` prints, in order: `backup of the original saved as basic-passwdcheck.c.orig`, `edited basic-passwdcheck.c`, "
    "`rebuilt basic-passwdcheck-CWHUSKY.hex`, `flashed basic-passwdcheck-CWHUSKY.hex to the target` (a harmless `SAM3U Serial buffers OVERRUN` warning may appear here), then **two questions to the chip**: "
    "`chip says to the RIGHT password 'lfbc1': Access granted, Welcome!` and `chip says to a WRONG one 'lfbcx': PASSWORD FAIL`. "
    "If you see both, the chip now holds your password. The whole cell takes about 15 seconds."])
S += callout("see", [
    "The attack prints one line per character: `round | winner | score | runner-up | score | margin`. With a correct prefix the margin is about **5x** "
    "(`l`, then `f`, `b`, `c`, `1`) and the last line reads `recovered 'lfbc1' in 98 s`, followed by `the chip says to the recovered password 'lfbc1': Access granted, Welcome!`."])

S += [H2("8.5  Do the same by hand (no helper)")]
S += [P("The helper does three things you can do yourself. This is also what the **Firmware Change and Flash Walkthrough** notebook shows.")]
S += numbered([
    "**Edit** line 73 of `firmware/mcu/basic-passwdcheck/basic-passwdcheck.c` in any text editor. Keep the quotes and the semicolon: `char correct_passwd[] = \"lfbc1\";`",
    "**Build** - open a terminal in that folder and run (one line):",
])
S += code('make PLATFORM=CWHUSKY CRYPTO_TARGET=NONE SS_VER=SS_VER_2_1 -j')
S += numbered(start=3, items=[
    "**Flash** the new `basic-passwdcheck-CWHUSKY.hex` to the SAM4S: re-run the Setup cell (it builds and flashes), or run the flashing cell of the Firmware Change "
    "and Flash Walkthrough notebook, which calls `cw.program_target(scope, prog, hex_path)`.",
    "**Check** with the chip's own answer: `ask_chip(\"lfbc1\")` should say `Access granted, Welcome!`, anything else `PASSWORD FAIL`.",
])
S += callout("tip", [
    "On **Windows** `make` needs Unix tools such as `rm`. The notebook finds them in Git's `usr\\bin` folder (installed with Git for Windows) and adds them for the build; "
    "from a plain terminal use **Git Bash** or add that folder to `PATH`. On **Linux** `make` just works once the compiler packages from the Linux guide are installed."],
    title="GOOD TO KNOW")

S += [H2("8.6  What we measured - four passwords on a real chip")]
S += [P("Every row was run on the real Husky + SAM4S with **one capture per guess** and the attack window 0 to 3000. Predict the result before you read it, then try it.")]
S += table([
    ["Password on the chip", "Attack length", "Result", "Time", "What to notice"],
    ["`h0px3` (original)", "5", "`h0px3`", "98 s", "Margin about 5x in every round; the splits are at samples 437, 488, 528, 568, 608."],
    ["`lfbc1`", "5", "`lfbc1`", "98 s", "Same picture with different letters."],
    ["`glitch42` (8 characters)", "8", "`glitch42`", "157 s", "8 rounds instead of 5, and the **last** split is later in the trace (about sample 757 instead of 608)."],
    ["`abC12` (capital `C`)", "5", "`abhiv` - **wrong**", "98 s", "Rounds 1 and 2 are right (margin about 5x). At round 3 the margin falls to **1.0x** and the rest is guessing: the attack never tries a capital `C`."],
    ["`lfbc1`", "3", "`lfb`", "58 s", "The attack simply stops early; the 3 characters it found are right."],
    ["`lfbc1`", "8", "`lfbc1` + 3 wrong characters", "about 160 s", "Rounds 6 and 7 have a margin of **1.0x**: past the end of the password every candidate is wrong in exactly the same way."],
], [1.45 * inch, 0.7 * inch, 1.2 * inch, 0.7 * inch, W - 4.05 * inch])
S += [FIG("pw_margins.png", 6.1 * inch, "Margin in every round, for all the experiments. A password the attack can find stays near 5x; the moment the guess is on a wrong "
          "track - an unlisted character, or past the end of the password - the margin drops to 1x."),
      FIG("pw_abc12.png", 6.5 * inch, "Why `abC12` fails at the third character. Left: round 2, one bar is far above the rest. Right: round 3, the right answer is a capital C, "
          "which the attack never tries, so all 36 bars are equally 'wrong' and the tallest is just noise."),
      FIG("pw_splits.png", 5.6 * inch, "Where the traces split, for three passwords. Each correct character moves the split about 40 to 45 samples later, whatever the letters are - "
          "so a longer password only costs more time, it does not hide anything.")]
S += callout("tip", [
    "**The lesson:** the attack gives a clear answer (margin about 5x) while it is on a correct prefix, and goes quiet (about 1x) the moment it is not. "
    "A margin that collapses to 1.0x tells you __this position is not an a-z / 0-9 character, or the password has ended__ - and `ask_chip()` tells you which: "
    "a correct, complete password gives `Access granted`. A different password changes **which letters win**, never **how well** the attack works - "
    "that is why a longer or cleverer password would not have saved this chip. Only changing the __code__ (comparing in constant time) does."],
    title="WHAT THIS SHOWS")

S += [H2("8.7  Put the original back")]
S += [P("Set `RESTORE_ORIGINAL = True` in the last Step 8 cell and run it. It copies `basic-passwdcheck.c.orig` back over `basic-passwdcheck.c`, rebuilds, reflashes, and prints "
        "the original line again - so the next person starts from `h0px3`. If you forgot: copy `basic-passwdcheck.c.orig` over `basic-passwdcheck.c` yourself, or in a terminal "
        "in the `chipwhisperer` folder run (one line):")]
S += code('git checkout -- firmware/mcu/basic-passwdcheck/basic-passwdcheck.c')
S += [P("then run the Setup cell once to rebuild and reflash.")]
S += callout("warn", [
    "**Things that trip people up:** (1) After **Restart & Run All** the EDIT blocks of Steps 2, 4, 5 and 6 are back to `\"h0px3\"` and `5` - the chip still has __your__ password "
    "(it lives in the file), so set them again. (2) Running Lab 2_1A or another lab **flashes a different firmware** onto the target; run this notebook's Setup cell again before "
    "attacking (it reflashes `basic-passwdcheck`). (3) Only one program can hold the Husky at a time: close other notebooks first."],
    title="WATCH OUT")
S += [CondPageBreak(2.4 * inch)]

# ================================================================ STEP 9
S += [H1("Step 9 - check your understanding")]
S += [P("Try each question first. The answers are underneath - cover them up!")]
S += table([
    ["#", "Question", "Answer"],
    ["1", "Why does a right first character look different from a wrong one in the power trace?",
     "The checker stops at the first wrong character. With a right character it carries on to compare the next one, so it runs **different code for longer** - which draws a different amount of power over time."],
    ["2", "How much later does the split happen for each extra correct character?",
     "**40 samples** (samples 433, 473, 513, 553, 593). That is the time of one more comparison; if your capture takes 4 samples per clock cycle (as the Husky's default setup does in Lab 2_1A) it is 10 clock cycles."],
    ["3", "Why did the attack with `ATTACK_END = 500` get the first two characters but fail after that?",
     "The window stops at sample 500, but the third character's split is at about 513 and later ones even further. Outside the window the traces look identical, so every wrong character scores about the same and the attack picks one at random. **The window must reach past the split point, which moves later with each correct character.**"],
    ["4", "How many guesses does brute force need for a 5-character password from 36 characters? How many captures did the power attack use?",
     "**36^5 = 60,466,176** in the worst case. The power attack used **185** (5 rounds of 36 guesses plus 5 references) - hundreds of thousands of times fewer."],
    ["5", "Why does averaging more captures rescue the attack when the noise goes up? What does it cost?",
     "Noise adds random values to every sample; averaging `R` captures cancels most of it - the noise shrinks by the square root of `R`. The price is `R` times as many captures. In the grid, each 4x increase in averaging let the attack survive about 2x more noise."],
    ["6", "Why does a small random delay break the single-capture attack? What does averaging do about it, and when does that stop working?",
     "A random shift means identical guesses no longer line up sample by sample, so their difference is large even for wrong guesses - a delay of about 3 samples already breaks a single capture. Because every shift is random and independent, **averaging 4 to 16 captures** blurs them into an average where the right guess still stands out (up to about 8 samples of delay). At 16 samples or more even 16 averages barely help and the attacker must **re-align** the traces first."],
    ["7", "Name two ways a designer could stop this attack.",
     "Compare the whole password in **constant time** (never stop early); add **random delays** (the attacker then needs re-alignment); **limit wrong attempts** or lock out; hide or mask the check in hardware."],
    ["8", "You change the password to `abC12`. Which characters does the attack still recover, and why does it stop working at the third?",
     "The first two, `a` and `b` (margin about 5x each). The third is a capital `C`, which is **not one of the 36 characters the attack tries**, so no candidate is right: every score "
     "is about the same, the margin is **1.0x**, and the winner is just noise (the attack printed `abhiv`). The chip itself still unlocks for `abC12` - the limit is in the attack's list of characters, not in the chip."],
    ["9", "The password is `lfbc1` but you run the attack with `ATTACK_LENGTH = 8`. What do rounds 6 to 8 look like, and what do they tell you?",
     "The first five rounds find `lfbc1` (margin about 5x). Rounds 6 and 7 have a margin of **1.0x**: past the end of the password every candidate is wrong in exactly the same way, so nothing stands out. "
     "A margin that collapses to 1.0x right after a run of clear ones means __the password has ended__ (or the next character is outside the list); `ask_chip()` confirms it, because the 5-character answer already gives `Access granted`."],
], [0.4 * inch, 2.4 * inch, W - 2.8 * inch])
S += [H2T("You are done when...")]
S += table([
    ["", "Check"],
    ["[  ]", "You found the split sample for each position and saw it move **40 samples** per correct character (Step 2)."],
    ["[  ]", "You scored every character and can say why `h` wins (Step 3)."],
    ["[  ]", "You recovered the whole password and counted the captures: **185** (Step 4)."],
    ["[  ]", "You found how much noise the attack tolerates and how averaging helps (Step 5)."],
    ["[  ]", "You found how big a random delay breaks it, and when averaging stops helping (Step 6)."],
    ["[  ]", "**With a Husky:** you ran Steps 1 to 4 against your own chip and compared your numbers with the table in Step 7."],
    ["[  ]", "**With a Husky:** you can say which **file and line** hold the password (`basic-passwdcheck.c`, line 73), which files are rebuilt, and what the notebook variables "
             "`STUDY_PASSWORD` and `PASSWORD_LENGTH` must be set to - and you recovered a password of your own creation (Step 8)."],
], [0.45 * inch, W - 0.45 * inch])
S += [P("**Next:** the following SCA101 labs go from __how long__ to __how much power__: the **value** of the data being processed changes "
        "the power, and that is how AES keys are recovered.")]
S += [PageBreak()]

# ================================================================ TROUBLESHOOTING
S += [H1("Troubleshooting")]
S += [P("Find the message you see, read what it means, try the fix. The **Source** line says how each entry was established.")]


def T(rows):
    return table([["#", "What you see", "What it means", "Fix"]] + rows, [0.45 * inch, 2.15 * inch, 1.75 * inch, W - 4.35 * inch])


S += [H2T("Setup and the recorded traces")]
S += T([
    ["E-1", "`ModuleNotFoundError: No module named 'cwtraces'`, or the notebook's `ImportError: The 'cwtraces' package is missing ...`",
     TC("The recorded-trace package is not installed. The standard install steps do not install it.", "Reproduced"),
     "In your ChipWhisperer environment: `python -m pip install cwtraces \"numpy<=1.26.4\"` (one line). Then **Kernel > Restart** "
     "and run the Setup cells again."],
    ["E-15", "The version check prints `5.6.1` (not `6.0.0`) or a numpy starting with `2`; or Lab 2_1B (MAIN) fails with "
     "`TypeError: Chart.__init__() missing 1 required positional argument: 'data'`",
     TC("pip replaced ChipWhisperer 6.0.0 with the old 5.6.1 and installed numpy 2 while installing the notebook requirements "
        "(newest scipy needs numpy 2; ChipWhisperer 6.0.0 needs numpy 1.26.4 or older). Seen on a fresh Python 3.12 install.",
        "Reproduced"),
     "Follow **L-49** in the Linux guide: delete the environment and repeat steps 1.3, 1.5 and 2.2, using the 2.2 command **with** "
     "`\"numpy<=1.26.4\"`. The check must print `6.0.0 1.26.4`."],
    ["E-2", "`ValueError: Only guesses up to 5 chars recorded, sorry about that.`",
     TC("The simulator only knows guesses of up to 5 characters. In Step 3, `KNOWN_PREFIX` plus one more character was too long.", "Source code"),
     "Use a `KNOWN_PREFIX` of at most 4 characters in Step 3 (the simulated password has 5)."],
    ["E-3", "`ValueError: Part of guess (...) not in recorded enumeration list`",
     TC("The simulator only records the characters a-z, 0-9, space and `\\x01`.", "Source code"),
     "Use only those characters in a guess."],
    ["E-4", "`NameError: name 'get_trace' is not defined` (or `cap_pass_trace`, `score`, ...)",
     TC("The Setup cells have not been run in this session (for example after a kernel restart).", "Notebook source code"),
     "**Kernel > Restart & Run All**, or run the two Setup cells again."],
    ["E-5", "`NameError: name 'MODEL_WINDOW'` (or `LIBRARY`, `model_attack`) in Step 6",
     TC("Step 6 uses the model built in Step 5.", "Notebook source code"),
     "Run the Step 5 cell first (or use **Restart & Run All**)."],
    ["E-6", "The plot or numbers did not change after you edited a cell",
     TC("Edits only take effect when you run the cell.", "General Jupyter"),
     "Press **Shift+Enter** (or **Ctrl+Enter**) on the cell you edited."],
])
S += [Spacer(1, 4), H2T("Results that look wrong")]
S += T([
    ["E-7", "Step 4 recovers the wrong password, or only the first few characters",
     TC("The comparison window ends before the traces split, or there is too much noise for the settings.", "Reproduced"),
     "Use `ATTACK_START, ATTACK_END = 0, 3000`. A window that ends at 500 gets only the first two characters; at 600, four."],
    ["E-8", "A bar chart with several equally tall bars and a margin near 1.0x",
     TC("The window you chose does not contain the split (Step 3), so every character looks the same.", "Reproduced"),
     "Move the window so it covers sample 433 (and later), for example `440, 600` or the whole trace."],
    ["E-9", "Step 4 or Step 5 takes a long time",
     TC("Simulated mode: each capture takes about 0.1 s, so 185 captures take about 16 s and doubling `ATTACK_REPEATS` doubles it. Step 5 builds its model first (about 10 s).", "Reproduced"),
     "Wait; or lower `ATTACK_REPEATS`, `TRIALS` or the length of `NOISE_LEVELS`. On hardware, time one capture with the Step 7 cell."],
    ["E-10", "Results differ slightly every time you run Steps 3 to 6",
     TC("The simulator returns a random one of 100 recorded traces per guess, and the models add random noise.", "Source code"),
     "Expected. Margins and counts move a little; the pattern should not."],
])
S += [Spacer(1, 4), H2T("Hardware (Steps 7 and 8)")]
S += T([
    ["E-11", "`OSError: Could not find ChipWhisperer` or `Unable to communicate with found ChipWhisperer ...`",
     TC("The Husky is not visible, or another program already holds it.", "Source code"),
     "**Kernel > Shut Down All Kernels**, close other lab tabs, unplug and replug the Husky. On Linux see the Linux guide section on USB devices."],
    ["E-12", "`RuntimeError: firmware build failed`",
     TC("The firmware could not be built (missing compiler, or the notebooks are not inside the `chipwhisperer` folder).", "Notebook source code"),
     "Run Lab 0 check 3. On Linux see the Linux guide section on compilers and firmware builds."],
    ["E-13", "`OSError: timeout` or `Verify FAILED` while flashing",
     TC("The wrong target board is on the CW313 (the look-alike iCE40 board), it is not seated, or the Husky is stuck.", "Husky kit bring-up"),
     "Check the board's printed text says SAM4S, reseat it, then **physically unplug and replug the Husky** and run the Setup cell again."],
    ["E-14", "`Timeout happened during acquisition`, or traces that are flat",
     TC("The scope never saw the trigger, or the Measure SMA cable is not connected.", "Notebook source code / Husky kit bring-up"),
     "Check the CW313 jumper `JP2` is on T-GPIO4 and the Husky's `Pos` SMA is connected to the CW313 (see the hardware pictures in the Linux guide). "
     "If you just ran another lab, the chip holds __that__ lab's firmware: run this notebook's Setup cell again to reflash `basic-passwdcheck`."],
    ["E-16", "`RuntimeError: could not find the active correct_passwd line in ...`",
     TC("The notebook looks for one **uncommented** line of the form `char correct_passwd[] = \"...\";`. It is missing, commented out with `//`, or written differently.", "Notebook source code"),
     "Open `basic-passwdcheck.c`, search for `correct_passwd`, and make sure exactly one uncommented line looks like `char correct_passwd[] = \"yourpassword\";`. "
     "Or put the original back: copy `basic-passwdcheck.c.orig` over it."],
    ["E-17", "`ValueError: length must be 1 to 31 characters (it is ...)` or `only plain printable characters, and no \" or \\`",
     TC("The password breaks one of the rules in section 8.2. The notebook stops before it touches the file.", "Notebook source code"),
     "Choose 1 to 31 characters, best only a-z and 0-9, with no quote mark and no backslash."],
    ["E-18", "`RuntimeError: firmware build failed - see the text above` right after you edited the file by hand",
     TC("The C file no longer compiles (a missing quote or semicolon), or `make` cannot find its tools.", "Notebook source code"),
     "Read the first line that contains `error:` in the printed output and fix that line. Restore with the `.orig` copy if unsure. On Windows see the tip in section 8.5."],
    ["E-19", "The chip answers `PASSWORD FAIL` even to the password you just set",
     TC("The password is **32 or more characters** (it can never be typed in full), or the flash did not happen so the chip still holds an older build.", "Measured on hardware"),
     "Use at most 31 characters. Check that `flashed ... to the target` was printed; if not, run the Setup cell again (see E-13 if it says `Verify FAILED`)."],
    ["E-20", "The attack recovers the wrong password, or the margins drop to 1.0x",
     TC("A character outside a-z / 0-9, a wrong `ATTACK_LENGTH`, or the chip holds a different password than `STUDY_PASSWORD`.", "Measured on hardware"),
     "Compare with the table in section 8.6. Ask the chip directly: `ask_chip(\"yourpassword\")` must say `Access granted`. Keep `STUDY_PASSWORD` and `PASSWORD_LENGTH` equal to the firmware's."],
])
S += [CondPageBreak(4.0 * inch)]

# ================================================================ APPENDIX
S += [H1("Appendix A - every variable you can edit")]
S += table([
    ["Step", "Variable", "Default", "What it does"],
    ["Setup", "`VERSION`", "`'SIMULATED'`", "`'SIMULATED'` = recorded traces; `'HARDWARE'` = your own chip."],
    ["1", "`GUESS_A`, `GUESS_B`", "`\"h\"`, `\"0\"`", "The two guesses to overlay."],
    ["1", "`START, END`, `SMOOTH`", "`0, 1000`, `1`", "Zoom window and smoothing."],
    ["2", "`STUDY_PASSWORD`", "`\"h0px3\"`", "The password to study."],
    ["2", "`THRESHOLD`", "`0.05`", "How big a difference counts as 'split'."],
    ["2", "`AVERAGES`, `SMOOTH_DIFF`", "`10`, `1`", "Captures averaged; smoothing of the difference."],
    ["3", "`KNOWN_PREFIX`", "`\"\"`", "Characters already found."],
    ["3", "`WINDOW_START, WINDOW_END`", "`0, 3000`", "Samples compared."],
    ["3", "`METRIC`, `REPEATS`", "`\"sum_abs\"`, `1`", "Scoring method; captures averaged."],
    ["4", "`PASSWORD_LENGTH`", "`5`", "Characters to recover."],
    ["4", "`ATTACK_START, ATTACK_END`", "`0, 3000`", "Samples compared."],
    ["4", "`ATTACK_METRIC`, `ATTACK_REPEATS`", "`\"sum_abs\"`, `1`", "Scoring method; captures averaged."],
    ["5", "`NOISE_LEVELS`, `REPEAT_LEVELS`", "see Step 5", "Rows and columns of the noise grid."],
    ["5", "`TRIALS`", "`10`", "Attacks per cell."],
    ["5", "`MODEL_WINDOW`, `MODEL_METRIC`", "`(0, 3000)`, `\"sum_abs\"`", "Samples compared and scoring in the model."],
    ["6", "`JITTER_LEVELS`, `JITTER_REPEATS`", "see Step 6", "Rows and columns of the delay grid."],
    ["6", "`JITTER_NOISE`, `JITTER_TRIALS`", "`0.01`, `5`", "Ordinary noise; attacks per cell."],
    ["6", "`SHOW_JITTER`", "`8`", "Delay for the example charts."],
    ["8", "`MY_NEW_PASSWORD`", "`\"lfbc1\"`", "The password written into the firmware (1 to 31 characters, best a-z and 0-9)."],
    ["8", "`ATTACK_LENGTH`", "`None`", "Characters the attack tries to recover. `None` = the password's own length; try 3 and 8 for a 5-character password."],
    ["8", "`RESTORE_ORIGINAL`", "`False`", "`True` puts the original `h0px3` firmware back on the chip."],
    ["2, 4, 5, 6", "`STUDY_PASSWORD`, `PASSWORD_LENGTH`", "`\"h0px3\"`, `5`", "**Set these to your new password and its length** after Step 8 - each of those cells has its own copy."],
], [0.6 * inch, 2.2 * inch, 1.7 * inch, W - 4.5 * inch])

S += [PageBreak(), H1("Appendix B - Glossary")]
S += table([
    ["Term", "Meaning"],
    ["**password checker**", "Firmware that compares a guess with the stored password one character at a time and stops at the first difference."],
    ["**power trace**", "The recorded power draw of the chip while it runs; here 3000 samples."],
    ["**split (divergence)**", "The sample where the traces of a right and a wrong guess stop being the same."],
    ["**reference**", "A trace of a guess known to be wrong (here a guess ending in `\\x01`), used to compare the others against."],
    ["**score / metric**", "One number saying how different two traces are: `sum_abs`, `sum_sq` or `max_abs`."],
    ["**window**", "The range of samples used in the comparison."],
    ["**averaging**", "Taking several captures of the same guess and averaging them; random noise shrinks by the square root of the number of captures."],
    ["**noise**", "Random variation added to every sample."],
    ["**random delay (jitter)**", "A defence: the chip waits a random time before the check, so traces are shifted by a different amount each time."],
    ["**re-alignment**", "Lining traces up again (for example on a feature) before comparing them."],
    ["**brute force**", "Trying every possible password. For 5 characters from 36 that is 36^5 = 60,466,176 guesses."],
    ["**model**", "A simplified stand-in built from real recorded traces; good for asking 'what if', not a new measurement."],
    ["**`cwtraces`**", "The Python package that holds the recorded traces for the simulated labs."],
    ["**firmware**", "The program that runs on the target chip. Here: `basic-passwdcheck`, written in C, which holds the password and compares guesses against it."],
    ["**build (make)**", "Turning the C source file into a file the chip can run (`.hex`, plus `.elf`, `.bin` and others). Run again after every edit."],
    ["**flash / reprogram**", "Writing the built `.hex` file into the chip's memory. The old firmware, and its password, is overwritten."],
    ["**margin**", "The winning character's score divided by the runner-up's. About 5x on a real chip means a clear winner; about 1x means no signal."],
], [2.2 * inch, W - 2.2 * inch])
S += [Spacer(1, 10)] + K.notice()

K.build(doc, S)
