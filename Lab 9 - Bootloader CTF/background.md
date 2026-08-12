
# NAE-27000-Bootloader

* Team of 2
* Highly secure device
* Goal is to recover firmware running on device
* Initial work discovered the following:

* Set bootloader pin high to go into bootloader
* 38400bps 8n1 UART
* Password and lock bit protected
* Teammate will handle lock bit
* Your goal is to recover password
* Need to find password before bypassing lock bit

* All data is sent in big endian format


## Commands

### List

* 0x10: RAM Write
* 0x20: Flash SUM
* 0x30: Bootloader info read
* 0x40: Flash Erase
* 0x60: Flash protect set

### RAM Write (0x10)

| Byte Number(s) |     User     |  Bootloader  |
| --- |--------------|--------------|
| 1 | Command Byte (0x10) |        
| 2 |              | Ack Response A |
|  3 - 14 | Password (12 bytes) |  |
| 15 | Password Checksum (1 byte) |  |
| 16 |              | Ack Response B    |
| 17 - 18 | Byte Count |  |
| 19 | Checksum for byte count |  |
| 20 | | Ack Response B |
| 21 - m | Data | |
| m + 1 | Checksum for data | |
| m + 2 | | Ack Response B |
| m + 3 | Jump to RAM |

Writes memory into up to 5kB of RAM dedicated to the bootloader. After this command finishes,
execution jumps to the beginning of this RAM. The beginning of this memory is at 0x2000 EC00.

The size and address of this memory can be verified using the BOOTLOADER_INFO (0x30) command.

#### Ack A

| Value | Result |
| ----- | ----- |
| 0x10 | Success |
| 0x11 | General Error |
| 0x16 | Protection Applied Error | 
| 0x18 | Checksum Error |


#### Ack B

| Value | Result |
| ----- | ----- |
| 0x10 | Success |
| 0x11 | General Error |
| 0x18 | Checksum Error |

### Flash Sum (0x20)

| Byte Number(s) |     User     |  Bootloader  |
| --- |--------------|--------------|
| 1 | Command Byte (0x20) |        
| 2 |              | Ack Response |
| 3 - 4 ||  Sum (2 bytes) | |
| 5 | | Checksum for bytes 3 and 4 | 

Calculates the 16-bit unsigned sum of the value of user flash memory. Can be used as a pseudo-checkcode
for firmware.

#### Ack 

| Value | Result |
| ----- | ----- |
| 0x20 | Success |
| 0x21 | General Error |
| 0x28 | Checksum Error |

### Bootloader Info Read (0x30)


| Byte Number(s) |     User     |  Bootloader  |
| --- |--------------|--------------|
| 1 | Command Byte (0x30) |        
| 2 |              | Ack Response |
| 3 - 15 | |  Info |

Read the following information about the bootloader/device:

Flash start address (4 bytes)
Flash size (4 bytes)
Bootloader RAM start address (4 bytes)
Bootloader RAM length (4 bytes)
Bootloader lock state (1 byte)

#### Ack 

| Value | Result |
| ----- | ----- |
| 0x30 | Success |
| 0x31 | General Error |
| 0x38 | Checksum Error |


### Flash Erase (0x40)


| Byte Number(s) |     User     |  Bootloader  |
| --- |--------------|--------------|
| 1 | Command Byte (0x40) |        
| 2 |              | Ack Response |
| 3  | Erase Confirm (0x54) |  |
| 4  |  | Ack Response |

Erases flash memory. This clears both the password and lock bit as well.

#### Ack 

| Value | Result |
| ----- | ----- |
| 0x40 | Success |
| 0x41 | General Error |
| 0x48 | Checksum Error |


### Flash Protect Set (0x60)

| Byte Number(s) |     User     |  Bootloader  |
| --- |--------------|--------------|
| 1 | Command Byte (0x60) |        
| 2 |              | Ack Response |
|  3 - 14 | Password (12 bytes) |  |
| 15 | Password Checksum (1 byte) |  |
| 16 |              | Ack Response    |

Sets the lock bit for the bootloader, disabling the mem write command.

#### Ack 

| Value | Result |
| ----- | ----- |
| 0x60 | Success |
| 0x61 | General Error |
| 0x68 | Checksum Error |

