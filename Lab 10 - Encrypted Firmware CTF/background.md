
# NAE-12340

5 years ago, you purchased a moderatly priced fridge. While you've been mostly happy with the performance
of your fridge, you've found that it appears to occasionally undershoot your target temperature
to the point of freezing some of the things in your fridge. You've ruled out a temperature sensor
issue, leading you to believe that something in the control code for the fridge is causing
the aggressive cooling.

Being a modern fridge, your appliance has a firmware update mechanism using an off the shelf USB to UART converter, plus a new firmware update! This update is triggered by
holding two of the buttons until the display flashes. Unfortunately, this new firmware doesn't appear to fix the issue. Even worse, the updates appear to be encrypted! You've decided to
try breaking the encryption on your fridge to allow you to fix the firmware yourself.

Opening your fridge, you've found that it uses an ATSAM4S microcontroller. You've taken this microcontroller off the fridge's PCB and mounted
it on one of NewAE's SAM4S target boards for easy side channel analysis. In some initial testing, you've found that this firmware
update is done at 8N1 38400bps UART and that PA8 is set low to enter the bootloader. You found that PA9 is used as an additional reset pin by holding it for the
required time. This means that you can trigger the bootloader by setting PA9 low and resetting the SAM4S.