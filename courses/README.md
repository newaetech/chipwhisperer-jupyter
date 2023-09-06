
## Courses

### SCA101: Introduction to Power Analysis Attacks

* **Lab 2-1A**: Instruction Power Differences
* **Lab 2-1B**: Power Analysis for Password Bypass
* **Lab 3-1**: Large hamming Weight Swings
* **Lab 3-2**: Recovering an AES Key from a Single Bit
* **Lab 3-3**: Recovery an AES key from a Power measurement (DPA)
* **Lab 4-1**: Showing the Hamming Weight relationship of data & power.
* **Lab 4-2**: Correlation Power Analysis
* **Lab 4-3**: Using ChipWhisperer for CPA Attacks
* **Lab 5-1**: ChipWhisperer CPA Attacks in Practice
* **Lab 6-4**: Triggering on UART

### SCA201: Power Analysis Attacks on AES Implementations
* **Lab 1-1A**: Resynchornizing Traces with Sum of Absolute Differences
* **Lab 1-1B**: Resynchornizing Traces with Dynamtic Time Warp
* **Lab 2-1**: CPA on a 32-bit AES Implementation
* **Lab 2-2**: CPA on a Hardware AES Implementation: Last-Round State
* **Lab 2-3**: CPA on a Hardware AES Implementation: Mix-Columns
* **Lab 3-1A**: AES-256 Bootloader Attack
* **Lab 3-B**: AES-256 Bootloader with Reverse Engineering using Power Analysis

### SCA202: Power Analysis on Asymmetric Implementations
* Power Analysis on 8-bit RSA Implementation (OLD VERSION IN REPO NOW)
* Power Analysis on MBED-TLS RSA Implementation (NOT IN REPO YET)
* Power Analysis on software ECC Implementation (NOT IN REPO YET)

### SCA203: Leakage Assesement
**NOTE: These labs are not here yet - but material is in the repo for some of this in sca203 folder**
* Introduction to Leakage Assessment
* Non-Specific TVLA on AES
* Specific TVLA on AES
* TVLA for Reverse Engineering
* TVLA on ECC

### SCA204: Power Analysis on Hardware ECC
* **Part 1**: Introduction to Hardware ECC Attacks
* **Part 2**: Improving the Attack
* **Part 3**: Countermeasures
* **Part 4**: More Countermeasures and Unintended Consequences
* **Part 5**: TVLA

### SCA205: Power Analysis on Software ECC
* **Part 1**: Breaking software ECC with TraceWhisperer
* **Part 2**: Breaking software ECC without TraceWhisperer
* **Part 3**: Breaking software ECC with TraceWhisperer *and* SAD

### FAULT101
* **Lab 1-1**: Introduction to Clock Glitching
* **Lab 1-2**: Clock Glitching to Bypass Password
* **Lab 1-3**: Clock Glitching to Dump Memory
* **Lab 1-4**: Authentication Bypass on AES Bootloader
* **Lab 2-1**: Introduction to Voltage Glitching
* **Lab 2-2**: Voltage Glitching to Bypass Password
* **Lab 2-3**: Voltage Glitching to Dump Memory

### FAULT201
* **Lab 1-1A**: Introduction to AES Fault Attacks
* **Lab 1-1B**: AES Loop Skip Fault Attack
* **Lab 1-2**: 1.5 Round AES Fault Attack
* **Lab 1-3A**: DFA Attack Against Final MixColumns
* **Lab 1-3B**: DFA Attack on AES
* **Lab 2-1**: Fault Attack on RSA


## Naming Notes

### Prefix

sca: Side Channel (Power) Analysis courses
fault: Fault Injection (Glitching) courses

### Numbering

* 1xx: Fundamentals. A 101 course is a prerequisite for all higher course.
* 2xx: Advanced topics. Dependencies noted in the labs/courses themselves.
* appx: Applications. Dependencies noted in the labs/courses themselves.

### Getting Started

We recommend going through sca101 before fault101, at least Lab 1_X and Lab 2_X. This will introduce you to the required ChipWhisperer software.
