## Side Channel Analysis 201 (SCA201) Labs

This group of labs can be completed with the following hardware (see table below for lab/hardware compatability): 

* **Group A HW**: CW-Lite (XMEGA or ARM), SCAPACK-L1, SCAPACK-L2, CW1200 ($250 - $3800)
* **CW-Nano**: ChipWhisperer-Nano ($50)
* **Simulator**: Pre-recorded power traces (FREE)

The lab numbers follow slide sets from the ChipWhisperer.io training.

|            Lab Name                                             |       Simulator        |    CW-Nano           |             Group A HW    |
|-----------------------------------------------------------------|------------------------|------------------------|-------------------------|
| **1.1A:** Resychronizing Traces with Sum of Absolute Difference | <p align="center"> ✅  | <p align="center"> ✅  | <p align="center"> ✅  |
| **1.1B:** Alternative Trace Resychronization                    | <p align="center"> ✅  | <p align="center"> ✅  | <p align="center"> ✅  |
| **2.1:**  CPA on 32bit AES                                      | <p align="center"> ✅  | <p align="center"> ✅  | <p align="center"> ✅  |
| **2.2:**  CPA on Hardware AES Implementation                    | <p align="center"> ✅  | <p align="center"> ✅  | <p align="center"> ✅  |
| **2.3:**  CPA on User FPGA AES Implementation                   | <p align="center"> ❌  | <p align="center"> ❌  | <p align="center"> ✅  |
| **3.1A:** AES256 Bootloader Attack (Basic)                      | <p align="center"> ❌  | <p align="center"> ❌  | <p align="center"> ✅  |
| **3.1B:** AES256 Bootloader Attack (Advanced)                   | <p align="center"> ❌  | <p align="center"> ❌  | <p align="center"> ✅  |


The following labs have additional hardware **requirements** in addition to the hardware listed above:

|            Lab Name                                |   Hardware Required    |  Included With                                       |
|----------------------------------------------------|------------------------|------------------------------------------------------|
| **2.1**   CPA on 32bit AES                         |      ARM Target        | CW-Lite w/ARM Target, SCAPACK-L1, SCAPACK-L2, CW1200 |
| **2.2**   CPA on Hardware AES Implementation       |   CW308T_STM32F4HWC    | Standalone, available via Mouser                     |
| **2.3**   CPA on User FPGA AES Implementation      |      CW308T_S6LX9      | Standalone, available via Mouser                     |

Prerequisites:
* SCA101