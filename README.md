# xcat_ng_fw

Firmware for the next generation Xcat code plug replacement project for Syntor X and X9000 radios

https://github.com/skiphansen/xcat_ng_fw

## Status

Currently this is just the Blinky example from [the pico examples](https://github.com/raspberrypi/pico-examples) with
Cmake files changes to decouple it from the example repo.

## Building the firmware

1. [Install Raspberry Pi Pico SDK](https://github.com/raspberrypi/pico-sdk)
2. Clone this repository
3. cd into xcat_ng_fw/SyntorX
4. Create a build directory
5. cd into the build directory
6. Create make files using Cmake
7. Run make

```
skip@Dell-7040:~/xcat$ git clone https://github.com/skiphansen/xcat_ng_fw
Cloning into 'xcat_ng_fw'...
remote: Enumerating objects: 4, done.
remote: Counting objects: 100% (4/4), done.
remote: Compressing objects: 100% (4/4), done.
remote: Total 4 (delta 0), reused 0 (delta 0), pack-reused 0
Unpacking objects: 100% (4/4), 12.52 KiB | 3.13 MiB/s, done.
skip@Dell-7040:~/xcat$ cd xcat_ng_fw/SyntorX/
skip@Dell-7040:~/xcat/xcat_ng_fw/SyntorX$ mkdir build
skip@Dell-7040:~/xcat/xcat_ng_fw/SyntorX$ cd build/
skip@Dell-7040:~/xcat/xcat_ng_fw/SyntorX/build$ cmake ..
Using PICO_SDK_PATH from environment ('/home/skip/pico/pico-sdk')
PICO_SDK_PATH is /home/skip/pico/pico-sdk
Defaulting PICO_PLATFORM to rp2040 since not specified.
Defaulting PICO platform compiler to pico_arm_gcc since not specified.
-- Defaulting build type to 'Release' since not specified.
PICO compiler is pico_arm_gcc
-- The C compiler identification is GNU 9.2.1
-- The CXX compiler identification is GNU 9.2.1
-- The ASM compiler identification is GNU
-- Found assembler: /usr/bin/arm-none-eabi-gcc
Build type is Release
Defaulting PICO target board to pico since not specified.
Using board configuration from /home/skip/pico/pico-sdk/src/boards/include/boards/pico.h
-- Found Python3: /usr/bin/python3.8 (found version "3.8.10") found components: Interpreter 
TinyUSB available at /home/skip/pico/pico-sdk/lib/tinyusb/src/portable/raspberrypi/rp2040; enabling build support for USB.
cyw43-driver available at /home/skip/pico/pico-sdk/lib/cyw43-driver
lwIP available at /home/skip/pico/pico-sdk/lib/lwip
-- Configuring done
-- Generating done
-- Build files have been written to: /home/skip/xcat/xcat_ng_fw/SyntorX/build
skip@Dell-7040:~/xcat/xcat_ng_fw/SyntorX/build$ make
Scanning dependencies of target ELF2UF2Build
[  1%] Creating directories for 'ELF2UF2Build'
[  2%] No download step for 'ELF2UF2Build'

... lots of output deleted ...

[100%] Linking CXX executable pioasm
[100%] Built target pioasm
[ 98%] No install step for 'PioasmBuild'
[100%] Completed 'PioasmBuild'
[100%] Built target PioasmBuild
skip@Dell-7040:~/xcat/xcat_ng_fw/SyntorX/build$
```


