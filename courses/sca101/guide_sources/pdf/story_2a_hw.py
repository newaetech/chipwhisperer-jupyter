"""Builds 'Lab 2_1A - What You Should See on a Real Husky.pdf'.   Usage: python story_2a_hw.py "<output pdf>" """
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
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "hw_2a") + os.sep
GUIDE_VERSION = "1.0 - November 2026"


def FIG(name, width, cap):
    return figure(ASSETS + name, width, cap)


doc = K.init(OUT,
             header_left="ChipWhisperer SCA101  -  Lab 2_1A on a real Husky",
             header_right="What you should see",
             footer_left="Companion to: Lab 2_1A (MAIN / HARDWARE) and the Lab 2_1A Explorer",
             title="SCA101 Lab 2_1A - What You Should See on a Real Husky",
             subject="Expected results for Lab 2_1A and its Explorer notebook when VERSION is switched from SIMULATED to HARDWARE")
S = []

# ================================================================ COVER
S += [*K.cover("SCA101  -  LAB 2_1A  (HARDWARE)", ("What You Should See", "on a Real Husky"),
                  "Expected results when you switch Lab 2_1A and its Explorer from SIMULATED to HARDWARE"),
      P("Lab 2_1A (**instruction power differences**) and its Explorer notebook run on **recorded traces** by default. Setting "
        "`VERSION = 'HARDWARE'` in the Setup cell runs the same code on your own **ChipWhisperer-Husky + CW313 + SAM4S** - and the traces look "
        "**different** from the recorded ones: longer, a different loop speed, a different starting point. None of that is a fault. This guide shows "
        "what a healthy kit produces, so you can tell \"it is working\" from \"something is wrong\", and how to measure a loop on a live trace."),
      Spacer(1, 10)]
S += callout("tip", [
    "All numbers here were **measured on one real kit** (Husky firmware 1.5.0, ChipWhisperer 6.0.0, SAM4S target, Windows 11, Python 3.12, 25 dB gain). "
    "Yours will be close, not identical: look for the same **pattern**. The captures behind every figure are bundled in "
    "`jupyter/courses/sca101/traces/hardware_reference/` so you can compare your own against them."], title="HOW TO USE THIS GUIDE")
S += callout("warn", [
    "**Step 7 of the Explorer changed.** Version 1.0 of `Lab 2_1A Explorer - Student Guide.pdf` described an earlier Step 7 that counted pulses on the live trace with "
    "`find_pulses()`; that does not work reliably on real traces. **Version 1.1 of that guide and this guide match the notebook** (check the version on the guide's "
    "cover). Steps 1 to 6 are unchanged."], title="WHICH STEP 7?")
S += [P("**What is in this guide**", h3)]
S += table([
    ["Section", "What", "Use it when"],
    ["1", "What changes when VERSION = 'HARDWARE'", "You switch for the first time."],
    ["2", "The Setup cell: what it should print", "You want to know it connected and configured correctly."],
    ["3", "The four traces: recorded next to a real chip", "You open the first plots of the lab."],
    ["4", "Explorer Step 7: measure a loop you wrote yourself", "You run Step 7 or want to know what numbers to expect."],
    ["5", "When it does not look like this", "A plot is flat, saturated, or the capture times out."],
    ["6", "The bundled reference traces", "You want to compare without hardware."],
], [0.8 * inch, 3.2 * inch, W - 4.0 * inch])
S += [PageBreak()]
S += K.contents()

# ================================================================ 1. WHAT CHANGES
S += [H1("1  What changes when VERSION = 'HARDWARE'")]
S += [P("Open the notebook's first code cell and change one word, then choose **Kernel > Restart & Run All**:")]
S += code("VERSION = 'HARDWARE'")
S += [P("Before you run it: the Husky kit assembled as in Lab 0 (CW313 with the **SAM4S** board, jumper `JP2` on T-GPIO4, the **Pos** SMA cable from the Husky "
        "to the CW313), the Husky plugged in, and **no other notebook holding it** - only one program can use the Husky at a time. The Setup cell then "
        "**builds and flashes** the lab firmware (`simpleserial-base-lab2`) onto the target by itself.")]
S += [P("What is different in the data:", h3)]
S += table([
    ["", "Recorded traces (SIMULATED)", "Live traces (HARDWARE)"],
    ["Length of a trace", "2000 samples", "**5000 samples** (`scope.adc.samples`)"],
    ["Samples per clock cycle", "4", "**4** (target clock 7.36 MHz, ADC 29.45 MHz) - the same"],
    ["Amplitude", "about -0.3 to +0.2", "about **-0.4 to +0.34** (standard deviation about 0.16)"],
    ["Where the interesting code starts", "from about sample 0", "near **sample 410**: start-up code runs first"],
    ["Speed of the multiply loop (`A *= 2;`)", "**15** cycles (60 samples) per trip", "**20** cycles (80 samples) per trip"],
    ["Speed of the divide loop (`A /= 3;`, A = 0x7FFFFFFF)", "**22** cycles falling to **16**", "**30** cycles falling to **23**"],
    ["How you change the code", "you cannot - fixed recordings", "**you can**: Explorer Step 7 edits the C code, rebuilds, reflashes and captures again"],
], [2.3 * inch, 2.1 * inch, W - 4.4 * inch], bold_first_col=True)
S += callout("tip", [
    "**Why are the loop speeds different?** The recorded traces were taken from a different firmware build, so the compiler laid the same C loop out differently. "
    "The loop still repeats a pattern, still scales with the count, and the divide still gets faster as `A` shrinks - those ideas are what the lab teaches, and they all "
    "hold on the real chip."], title="GOOD TO KNOW")

# ================================================================ 2. SETUP
S += [CondPageBreak(3.6 * inch)]
S += [H1("2  The Setup cell: what it should print")]
S += [P("A healthy run prints the lines below (abridged here - the real output also shows the full firmware build). The numbers that matter are in **bold** in the "
        "explanation underneath.")]
S += code("""
firmware working copy: ...\\firmware\\mcu\\simpleserial-base-lab2
INFO: Found ChipWhisperer
scope.gain.gain          changed from 0       to 22
scope.gain.db            changed from 15.0    to 25.09
scope.adc.samples        changed from 131124  to 5000
scope.clock.clkgen_freq  changed from 0       to 7363636.36
scope.clock.adc_freq     changed from 0       to 29454545.45
scope.io.hs2             changed from None    to clkgen
scope.trace.capture.trigger_source  changed from trace trigger, rule #0  to firmware trigger
Hardware ready - baseline simpleserial-base flashed.
""")
S += table([
    ["Line", "What it means"],
    ["`scope.gain.db ... to 25.09`", "The measurement amplifier is set to **25 dB**. This is the default and a good value; if your traces hit the +/-0.5 limit see section 5."],
    ["`scope.adc.samples ... to 5000`", "Every capture is **5000 samples** long."],
    ["`scope.clock.clkgen_freq ... 7363636`, `adc_freq ... 29454545`", "The Husky generates the target's clock (**7.36 MHz**) and samples at **4 times that** (29.45 MHz): **4 samples per clock cycle**."],
    ["`trigger_source ... firmware trigger`", "The scope starts recording when the target firmware raises its trigger pin - which is why the board must hold the lab firmware."],
    ["`Hardware ready - baseline simpleserial-base flashed.`", "The target was programmed. The next cell then prints `trace length: 5000` and `OK to continue!`."],
], [2.7 * inch, W - 2.7 * inch])
S += callout("ifnot", [
    "`OSError: Unable to communicate with found ChipWhisperer` - another program holds the Husky (often a second notebook). **Kernel > Shut Down All Kernels**, then run again. "
    "`Could not find ChipWhisperer` - the cable or a USB rule (Linux guide). `Verify FAILED` while flashing - the wrong board is on the CW313, or it is not seated; "
    "unplug and replug the Husky."])

# ================================================================ 3. FOUR TRACES
S += [CondPageBreak(6.2 * inch)]
S += [H1("3  The four traces: recorded next to a real chip")]
S += [P("The lab captures four short programs between two triggers and compares their power traces: **0** nothing, **1** twenty multiplies in a row, **2** a loop of 20 multiplies, "
        "**3** a loop of 20 divides. The picture shows the recorded trace (left) and a real capture (right) for each.")]
S += [FIG("sections.png", W, "Left: the recorded traces from Steps 1 - 6. Right: real captures of the same four programs. The live traces are denser (more samples) and start with "
          "about 400 samples of start-up activity before your code begins.")]
S += table([
    ["On a real chip", "What you should see"],
    ["Standard deviation of each trace", "about **0.16** (0.158 to 0.164 across the four)"],
    ["Largest value in a trace", "between about **-0.41** and **+0.34**. Anything stuck at +/-0.5 is clipping - section 5."],
    ["Repeatability", "the same program captured twice differs by only about **0.005** per sample (mean absolute difference), so differences between programs are real, not noise."],
    ["Sections 0 and 1", "no loop. They differ by only about **0.02** per sample before sample 400, and by about **0.11 to 0.12** per sample once the multiplies run."],
    ["Section 2 (loop of 20 multiplies)", "a repeating pattern of **20 cycles = 80 samples**, starting at about sample **406** and lasting about **1630 samples** (20.4 trips)."],
    ["Section 3 (loop of 20 divides)", "a pattern whose length **keeps shrinking**, from about **30 cycles** to about **23** over the 20 trips - the divide gets faster as `A` gets smaller."],
    ["After your code", "another repeating pattern of **18 cycles = 72 samples** (it begins near sample 990 in section 0, 1490 in section 1 and 3110 in section 3). It is __not__ your loop. "
                        "Step 7's measurement only accepts a loop that starts between sample 350 and 700, so it is not fooled by it."],
], [2.5 * inch, W - 2.5 * inch], bold_first_col=True)

# ================================================================ 4. EXPLORER STEP 7
S += [H1("4  Explorer Step 7: measure a loop you wrote yourself")]
S += [P("Step 7 of the **Lab 2_1A Explorer** is hardware only. You choose the C statement inside the loop and how many times it runs; the notebook writes it into the firmware, "
        "rebuilds, reflashes (about 10 seconds), captures a trace and measures the loop:")]
S += code("""
MY_OPERATION = "A *= 2;"      # the statement inside the loop
MY_COUNT     = 20             # how many trips
MY_A_START   = "0x2BAA"       # starting value of A
""")
S += [P("**Why not use the pulse finder from Step 4?** It was tuned on the smooth recorded traces and finds only a couple of pulses on a live trace. Step 7 uses a different "
        "measurement: it compares each block of `P` samples with the next block. Inside a loop the blocks repeat, so the match is above 0.9 **at the loop's trip length and nowhere else**.")]
S += [FIG("loop_found.png", 6.2 * inch, "Step 7 with `A *= 2;` x 20 on a real chip. The green band is the loop the measurement found (sample 410 to 2036); the lower plot shows "
          "the trip length in each 300-sample window: a steady **20 cycles** while the loop runs (red), scattered values outside it (grey).")]
S += callout("see", [
    "`every trip takes 80 samples = 20 clock cycles`, then `the loop runs from sample 410 to 2036 (1626 samples) = about 20.3 trips (you asked for 20)`. "
    "The largest swing printed above it is about 0.4; the ADC limit is 0.5."])
S += [P("**What we measured for each experiment** (one real kit; your numbers should match to within a cycle or so):", h3)]
S += table([
    ["You run", "Prediction", "Measured on a real Husky + SAM4S"],
    ["`\"A *= 2;\"`, `MY_COUNT` = 10, 20, 40", "the loop gets 2x and 4x longer",
     "**20 cycles (80 samples) per trip** every time; the loop starts near sample 410 and spans **10.3, 20.4 and 40.3 trips**"],
    ["`\"A += 2;\"`, `\"A ^= 0x55;\"`, `\"A *= 3;\"`", "maybe different cycle counts",
     "**all 20 cycles per trip** (20.4, 20.3, 20.3 trips): an add, an xor and a multiply take the same time here, so you **cannot tell them apart by timing**"],
    ["`\"A /= 3;\"`, `MY_A_START = \"0x7FFFFFFF\"`", "the trips shrink, like Step 5",
     "**30, 29, 28, 27, 26, 25, 24, 23 cycles** in successive windows"],
    ["`\"A /= 3;\"`, `MY_A_START = \"0x100\"`", "`A` is small from the start",
     "starts at about **23 cycles** and settles at **20** after a few trips: once `A` reaches 0 the divide is as fast as any other instruction"],
], [1.9 * inch, 1.6 * inch, W - 3.5 * inch])
S += [FIG("scaling.png", 5.6 * inch, "The loop's length scales with `MY_COUNT`: 826, 1628 and 3226 samples for 10, 20 and 40 trips - 80 samples (20 cycles) per trip."),
      FIG("divide.png", 5.9 * inch, "A constant loop stays at 20 cycles per trip. The divide of a big number starts at 30 and shrinks to 23; the divide of a small number settles at 20 within a few trips.")]
S += callout("tip", [
    "**For the divide loops the trip length is not constant**, so the single-period measurement (`measure_loop`) does not apply. The Step 7 cell notices this and prints the "
    "trip length of every window instead (`trip length per window (cycles): [30, 29, 29, ...]`)."], title="GOOD TO KNOW")

# ================================================================ 5. NOT LIKE THIS
S += [H1("5  When it does not look like this")]
S += table([
    ["You see", "What it means", "Try"],
    ["A solid band stuck at +/-0.5, and the printed largest swing is 0.5", "The signal is **bigger than the ADC can measure** (clipping). It happened on this kit once, after the measurement cable was moved.",
     "Reseat the **Pos** SMA cable at both ends (finger-tight). If needed `scope.gain.db = 15` (or 10) and capture again."],
    ["A nearly flat trace, or `no repeating loop found`", "The measurement cable is not connected, or not on the right connector.", "Check the **Pos** SMA at the Husky and at the CW313 (Lab 0 notebook, Assemble step 4; Linux guide 4.2, steps 2 and 3)."],
    ["`Timeout in OpenADC capture(), no trigger seen`", "The scope never saw the trigger. The target is not running the lab firmware (for example, Lab 2_1B's `basic-passwdcheck` is still on it) or `JP2` is wrong.",
     "Run the **Setup cell again** (it reflashes the lab firmware). Check `JP2` is on **T-GPIO4**."],
    ["`Unable to communicate with found ChipWhisperer`", "Another kernel holds the Husky. A failed connection also keeps the USB handle until its kernel stops.", "**Kernel > Shut Down All Kernels**, close other lab tabs, run again."],
    ["A number of trips not close to `MY_COUNT`", "A window edge, or a weak match.", "Re-run once; the green band in the plot must cover the whole loop."],
    ["The numbers differ a little from this guide", "Normal. Cable seating, gain and the compiler version move amplitudes and, rarely, cycle counts by a cycle or so.", "Compare the **pattern**: constant for `*`, `+`, `^`; shrinking for `/` with a big `A`."],
], [1.9 * inch, 2.7 * inch, W - 4.6 * inch])

# ================================================================ 6. REFERENCE
S += [H1("6  The bundled reference traces")]
S += [P("The captures behind this guide are in `jupyter/courses/sca101/traces/hardware_reference/` (float32 NumPy files, 5000 samples each). Step 7 of the Explorer plots them before "
        "you capture your own. Load one yourself with:")]
S += code("""
import numpy as np
x = np.load("traces/hardware_reference/lab2_1A_hw_mul_20.npy")      # 5000 samples, A *= 2; x 20
""")
S += table([
    ["File", "What it holds"],
    ["`lab2_1A_hw_section0.npy` ... `section3.npy`", "The four programs of the lab (empty, 20 multiplies, loop of 20 multiplies, loop of 20 divides) on a real chip."],
    ["`lab2_1A_hw_mul_10.npy`, `mul_20`, `mul_40`", "`A *= 2;` repeated 10, 20 and 40 times."],
    ["`lab2_1A_hw_add_20.npy`, `xor_20`, `mul3_20`", "`A += 2;`, `A ^= 0x55;` and `A *= 3;` repeated 20 times."],
    ["`lab2_1A_hw_div_big_20.npy`, `div_small_20`", "`A /= 3;` repeated 20 times, with `A` starting at `0x7FFFFFFF` and at `0x100`."],
], [3.1 * inch, W - 3.1 * inch])
S += [P("**Compare your own capture with a reference:** plot both (`plt.plot(x); plt.plot(mine)`), or run the notebook's `measure_loop(x)` on each. A healthy capture has the same "
        "loop start (about sample 410) and trip length (80 samples) as the matching reference.")]
S += [Spacer(1, 10)] + K.notice()

K.build(doc, S)
