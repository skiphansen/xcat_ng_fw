Details here have been worked out by members of the group.  The data is 
incomplete, and of course may contain errors.

# Memory Map

## Overview

| Start | End | Contents |
| -|-|-|
| 0000|0027 | MPU control registers |
| 0028|003F | Nothing |
| 0040|013F | MPU on-board RAM |
| 0140|3FFF | Nothing |
| 4000|4007 | Synthesizer registers, latch U503 (usually written thrice: once with desired bit pattern, then again with A3=STROBE, then again without A3) [write only] |
| 4008|7FFF | Nothing |
| 8000|BFFF | Code plug (observed: 2k: -87FF, 8k: -9FFF; presumably a 16k would be -BFFF) |
| C000 | | Write: Audio Control Bus, latch U504 |
| C000|CFFF | Read: Firmware EPROM |

### Audio control bus bitmap

| Bit | Mask | Function |
| --- | -|--- |
| 0 | 0x01|Option RX through de-emphasis filter (inverted at switch) |
| 1 | 0x02|Option RX flat (inverted) |
| 2 | 0x04|Option TX through splatter filter (inverted) |
| 3 | 0x08|Option TX flat |
| 4 | 0x10|(Audio?) Preamp /WE (active low) |
| 5 | 0x20|Squelch LSB (controls Q203) |
| 6 | 0x40|Squelch MSB (controls Q202) |
| 7 | 0x80| Mic Mute (inverted) |

## Port 2 bits
| Bit | Mask | | Function |
| --- | -|--- |
| 0 | 0x01|in |Busy in |
| 1 | 0x02| out | Busy out |
| 2 | 0x04|out|
| 3 | 0x08||
| 4 | 0x10|out|
| 5 | 0x20|out|
| 6 | 0x40||
| 7 | 0x80|out|

## Code Plug layout

| Start | End | ||
| -| -|- | -|-
| 0 | 1 | Last Adr |Offset of last byte in plug MSB, LSB  (observed: 2k: 07FF, 8k: 1FFF; presumably a 16k would be 0x3FFF) |
| 2 | 3 | Checksum |Simple 16 bit checksum of plug contents of 16 bit words from 0004-end
| 8 | 8 | NumModes | Number of active modes |
| 0x100 | | Start of Mode table |


## Mode table

| Start | End | ||
| -| -|- | -|-
|0x00 | 0x02|   RX synthesizer programming bits|
|0x03 | 0x05|   TX synthesizer programming bits|
| 0x06 | 0x06 | Something PL-related |
| 0x17  ||Last byte |Details here have been worked out by members of the group.  The data is 
incomplete, and of course may contain errors.

# Memory Map

## Overview

| Start | End | Contents |
| -|-|-|
| 0000|0027 | MPU control registers |
| 0028|003F | Nothing |
| 0040|013F | MPU on-board RAM |
| 0140|3FFF | Nothing |
| 4000|4007 | Synthesizer registers, latch U503 (usually written thrice: once with desired bit pattern, then again with A3=STROBE, then again without A3) [write only] |
| 4008|7FFF | Nothing |
| 8000|BFFF | Code plug (observed: 2k: -87FF, 8k: -9FFF; presumably a 16k would be -BFFF) |
| C000 | | Write: Audio Control Bus, latch U504 |
| C000|CFFF | Read: Firmware EPROM |

### Audio control bus bitmap

| Bit | Mask | Function |
| --- | -|--- |
| 0 | 0x01|Option RX through de-emphasis filter (inverted at switch) |
| 1 | 0x02|Option RX flat (inverted) |
| 2 | 0x04|Option TX through splatter filter (inverted) |
| 3 | 0x08|Option TX flat |
| 4 | 0x10|(Audio?) Preamp /WE (active low) |
| 5 | 0x20|Squelch LSB (controls Q203) |
| 6 | 0x40|Squelch MSB (controls Q202) |
| 7 | 0x80| Mic Mute (inverted) |

## Port 2 bits
| Bit | Mask | | Function |
| -| -|-|-|
| 0 | 0x01|in |Busy in |
| 1 | 0x02| out | Busy out |
| 2 | 0x04|out|
| 3 | 0x08||
| 4 | 0x10|out|
| 5 | 0x20|out|
| 6 | 0x40||
| 7 | 0x80|out|

## Code Plug layout

| Start | End | ||
| -| -|- | -|
| 0 | 1 | Last Adr |Offset of last byte in plug MSB, LSB  (observed: 2k: 07FF, 8k: 1FFF; presumably a 16k would be 0x3FFF) |
| 2 | 3 | Checksum |Simple 16 bit checksum of plug contents of 16 bit words from 0004-end
| 8 | 8 | NumModes | Number of active modes |
| 9 | 9 | ModeTblEntryLen | The number of bytes in a single mode in the mode table<br>this is 24 (0x18) in all known examples|
| 0x100 | | Start of Mode table |


## Mode table

Note the 
| Start | End | ||
| -| -|- | -|
|0x00 | 0x02|   RX synthesizer programming bits|
|0x03 | 0x05|   TX synthesizer programming bits|
| 0x06 | 0x06 | Something PL-related |
| 0x17  ||Last byte (when ModeTblEntryLen is 24) |

