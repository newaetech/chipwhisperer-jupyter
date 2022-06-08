<<<<<<< HEAD
# ChipWhisperer

[![Documentation Status](https://readthedocs.org/projects/chipwhisperer/badge/?version=latest)](https://chipwhisperer.readthedocs.io/en/latest/?badge=latest) | [![Notebook Tests](https://github.com/newaetech/ChipWhisperer-Test-Results/blob/main/.github/badges/hardware_tests.svg)](https://github.com/newaetech/ChipWhisperer-Test-Results/blob/main/tutorials/results.yaml)

[![Discord](https://img.shields.io/discord/747196318044258365?logo=discord)](https://discord.gg/chipwhisperer) | [Hardware Docs](https://rtfm.newae.com) | [Documentation](https://chipwhisperer.readthedocs.io) | [Forum](http://forum.newae.com) | [Store](https://store.newae.com) | [NewAE](http://newae.com)


ChipWhisperer is an open source toolchain dedicated to hardware security research. This toolchain consists of several layers of open source components:
* __Hardware__: The ChipWhisperer uses a _capture_ board and a _target_ board. Schematics and PCB layouts for the ChipWhisperer-Lite capture board and a number of target boards are freely available.
* __Firmware__: Three separate pieces of firmware are used on the ChipWhisperer hardware. The capture board has a USB controller (in C) and an FPGA for high-speed captures (in Verilog) with open-source firmware. Also, the target device has its own firmware; this repository includes many firmware examples for different targets.
* __Software__: The ChipWhisperer software includes a Python API for talking to ChipWhisperer hardware (ChipWhisperer Capture) and a Python API 
for processing power traces from ChipWhisperer hardware (ChipWhisperer Analyzer). You can find documentation for our Python API at
chipwhisperer.readthedocs.io

---

## Getting Started
First time using ChipWhisperer? Check out these links:
* [Getting started](https://chipwhisperer.readthedocs.io/en/latest/getting-started.html)
* [Installing ChipWhisperer](https://chipwhisperer.readthedocs.io/en/latest/index.html#install) if you're trying to set up this software package
* [Hardware Docs](https://rtfm.newae.com) for hardware information. Also has helpful comparison between different NewAE products.

## ChipWhisperer 5.5: All-in-one installer, Serial Port, ECC, and Segmented Capture

ChipWhisperer 5.5 has brought some exciting new features that make it easier to use and allow you to do some cool new things:

1. The ChipWhisperer Windows installer now includes everything you need to use ChipWhisperer, including
Python/Juptyer, Git, Make, and compilers! For more information, check out our [Windows installer page](https://chipwhisperer.readthedocs.io/en/latest/windows-install.html) on ReadTheDocs.
1. ChipWhisperer capture devices (CWLite, Nano, Pro, etc.) have gotten a new firmware update that gives them a
USB-CDC serial port for talking over USART. This means you can use your favourite serial program, such as PuTTy,
to talk to and listen to the target's USART communication. For more info, see our [rtfm serial port page](https://rtfm.newae.com/Serial%20Ports/).
1. We've recently added two ECC power analysis attack notebooks. One attacks a hardware ECC implementation running on the CW305
and the other attacks a software ECC implementation running on a microcontroller. Both can be found in `jupyter/demos`.
1. There's a new segmented capture mode that allows you to fill the ChipWhisperer capture buffer with multiple power traces
before transferring data to the PC. This greatly reduces the overhead on trace transfer, allowing capture speeds
of 1000+ captures/second for FPGA AES implementations. See our [API documentation](https://chipwhisperer.readthedocs.io/en/latest/scope-api.html#chipwhisperer.capture.scopes._OpenADCInterface.TriggerSettings.fifo_fill_mode) to see how to use it.

Also, if you haven't checked it out yet, ChipWhisperer 5.4 included TraceWhisperer, which allows you to use Arm trace to
timestamp microcontroller operations/functions in your powertrace. It requires a CW305 or PhyWhisperer. For more information, see
https://github.com/newaetech/DesignStartTrace.

## GIT Source
Note all development occurs on the [develop](https://github.com/newaetech/chipwhisperer/tree/develop) branch. If you are looking for bleeding edge it's NOT on master - we push each release (and possibly any critical changes) to master. This means that "master" always gives you the latest known-working branch, but there may be new features on the "develop" branch.

## Help!
Stuck? If you need a hand, there are a few places you can ask for help:
* The [NewAE Forum](https://forum.newae.com/) is full of helpful people that can point you in the right direction
* If you find a bug, let us know through the [issue tracker](https://github.com/newaetech/chipwhisperer/issues)

---

ChipWhisperer is a trademark of NewAE Technology Inc., registered in the US, Europe, and China.
=======
# ChipWhisperer Jupyter Notebook Repository

Welcome to the ultimate collection of ChipWhisperer Jupyter notebooks.

## Repo Contents

This repository serves multiple purposes:

* Courses (see `courses`) in Side-Channel Analysis (SCA) along with Fault Injection. These are organized to align with commercial course content on [ChipWhisperer.io](https://www.ChipWhisperer.io), but many are stand-alone and can serve as a self-taught course.

   * Course notebooks are open-source and you can follow along at your own pace too!
   
   * See [ChipWhisperer.io](https://www.ChipWhisperer.io) for more details.

* Experiments (see `experiments`) showcasing various things you can do with the ChipWhisperer platform. These notebooks may have less background, often require certain hardware to perform the experiments, and may be in a work in progress state.

* Demos (see `demos`) of various features and targets, such as ChipWhisperer-Pro streaming mode being used to capture long power traces, or hardware AES running on the CW305 FPGA board.

* Many notebooks have been overhauled and renamed - if you're looking for the previous version, see the `archive` directory (preserved here to keep links less broken on the internet).

## Getting Started
What do you want to do now? If you're just getting to know ChipWhisperer, check out the following:

## Getting Started
First time using ChipWhisperer? Check out these links:
* [Getting Started](https://chipwhisperer.readthedocs.io/en/latest/getting-started.html) if you have no idea where to start
* [Installing ChipWhisperer](https://chipwhisperer.readthedocs.io/en/latest/installing.html) if you're trying to set up this software package
* `0 - Introduction to Jupyter Notebooks.ipynb` and `1 - Connecting to Hardware.ipynb` also serve as introductions to interacting with Jupyter Notebooks and the ChipWhisperer hardware.

## Getting Support

Having trouble? Here are some quick ways to get help:

* If you have a general question or problem, please head over to [forum.newae.com](https://forum.newae.com) which is our primary support method.
* If you've found a specific bug, please raise a GITHub issue.
* If you want more hands-on help, part of our training offerings on [ChipWhisperer.io](https://ChipWhisperer.io) offer more interactive help (including a private forum section).

## Re-Use in Teaching & Academic Environments

These notebooks are distributed under the open-source GPL license (as is the rest of ChipWhisperer). This means you can distribute and modify this material (even for commercial trainings), **provided you maintain references to this repository and the original authors, and also offer your derived material under the same conditions**.

If you would like to re-use this content commercially under different license conditions, please contact `sales -AT- newae.com`. Note that as a public project, we also have user-contributed content which we may not own the original copyright for.

This material is Copyright (C) NewAE Technology Inc., 2015-2020. ChipWhisperer is a trademark of NewAE Technology Inc., claimed in all jurisdictions, and registered in at least the United States of America, European Union, and Peoples Republic of China.
>>>>>>> 347ae9210c229196549bf69594afec4618a84a77
