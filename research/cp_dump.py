#!/usr/bin/python3
#
# Copyright (C) 2022 Skip Hansen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# The latest version of this program may be found at
# https://github.com/skiphansen/sb9600_tools

import sys
import math
import argparse

Debug = False

RangeTbl = (
    ('29.7 - 50.0',-75.7e6),
    ('136 - 154',-53.9e6),
    ('148 - 172',-53.9e6),
    ('148 - 174',-53.9e6),
    ('150 - 174',-53.9e6),
    ('406 - 420',-53.9e6),
    ('420 - 430',-53.9e6),
    ('450 - 470',53.9e6),
    ('470 - 488',53.9e6),
    ('482 - 500',53.9e6),
    ('494 - 512',53.9e6),
    ('806 - 870',53.9e6)
)

pl_tones = {
    67.0:"XZ",
    69.3:"WZ",
    71.9:"XA",
    74.4:"WA",
    77.0:"XB",
    79.7:"WB",
    82.5:"YZ",
    85.4:"YA",
    88.5:"YB",
    91.5:"ZZ",
    94.8:"ZA",
    97.4:"ZB",
    100.0:"1Z",
    103.5:"1A",
    107.2:"1B",
    110.9:"2Z",
    114.8:"2A",
    118.8:"2B",
    123.0:"3Z",
    127.3:"3A",
    131.8:"3B",
    136.5:"4Z",
    141.3:"4A",
    146.2:"4B",
    151.4:"5Z",
    156.7:"5A",
    162.2:"5B",
    167.9:"6Z",
    173.8:"6A",
    179.9:"6B",
    186.2:"7Z",
    192.8:"7A",
    203.5:"M1",
    206.5:"8Z",
    210.7:"M2",
    218.1:"M3",
    225.7:"M4",
    229.1:"9Z",
    233.6:"M5",
    241.8:"M6",
    250.3:"M7",
    254.1:"0Z",
}

RefTbl = (('not used',0),('6.25 Khz',6250),('4.16667 Khz',4167),('5 Khz',5000))

CTbl = (-1,1,3,2)

def DumpHex(data,no_lf=False,with_adr=False,start_addr=0):
    DataLen = len(data)
    first = True
    Displayed = 0
    addr = start_addr
    for byte in data:
        if not first:
            print(' ',end='')
        elif with_adr:
            print(f'{addr:04x}: ',end='')
            addr += 16;

        first = False
        print(f'{byte:02X}',end='')
        Displayed += 1
        if Displayed == 16:
            Displayed = 0
            if not no_lf:
                print('')
                first = True

    if not no_lf and Displayed > 0:
        print('')

#f(vco) = ((((64 * A) + (63 * B)) * 3 ) + C(table)) * f(ref)
#low band: highside injection, add IF frequency of 75.7 Mhz
#VHF: highside injection, add IF frequency of 53.9 Mhz
#UHF: lowside injection, subtract IF frequency of 53.9 Mhz
def calc_fco(synth_bytes,LowBand):
    if Debug:
        print(f'Raw bytes: ',end='')
        DumpHex(synth_bytes)

    if synth_bytes[0] == 0 and synth_bytes[1] == 0 and synth_bytes[2] == 0:
        return 0
    A = synth_bytes[0] & 0x3f
    B = ((synth_bytes[0] & 0xc0) >> 6) + (synth_bytes[1] << 2)

    R = synth_bytes[2] & 0x3
    V = (synth_bytes[2] & 0xc) >> 2
    C = (synth_bytes[2] & 0x30) >> 4
    S = (synth_bytes[2] & 0xc0) >> 6
    if Debug:
        print(f'A {A} 0x{A:02x}, B {B} 0x{B:02x}, V {V}, R {R}, C {C}')
    fref = RefTbl[R][1]
    if Debug:
        print(f'fref {fref}')
    fvco = (64 * A) + (63 * B)
    if not LowBand:
        fvco *= 3
        #c bits are extender control for lowband C1 = 1 C0 = extender on/off
        if C == 0:
            print(f'Error: C value ({C}) is invalid!')
        c = CTbl[C]
        if Debug:
            print(f'c {c}')
        fvco += c
    fvco *= fref
    if Debug:
        print(f'fvco {fvco/1e6}')
    return fvco

def calc_rx(fvco,IfFreq):
    if fvco == 0:
        return fvco
    else:
        if Debug:
            print(f'calc_rx: IfFreq {IfFreq/1e6}')
        return fvco + IfFreq

def calc_tx(fvco,LowBand,Mhz800):
    if fvco == 0:
        return fvco
    elif LowBand:
        return 172.8e6- fvco
    elif Mhz800:
        return fvco * 2
    else:
        return fvco


def CalcPl(base,multiplier):
    freq = round((multiplier & 0x7fff) / base *10)
    freq /= 10

    if Debug:
        print(f'freq {freq}')

    return freq

def DumpPlDpl(mode_data,plug,BigEEPROM):
    PlTbl = (plug[0x18] << 8) + plug[0x19]
    tbl_index = mode_data[6]
    offset = PlTbl + (tbl_index - 1)  * 4
    rx_value = (plug[offset] << 8) + plug[offset+1]
    tx_value = (plug[offset+2] << 8) + plug[offset+3]

    if Debug:
        print(f'PlTbl 0x{PlTbl:04x}')
        print(f'rx_index {rx_index}')
        print(f'rx_value {rx_value}')
        print(f'tx_index {tx_index}')
        print(f'tx_value {tx_value}')

    if rx_value > 0 and rx_value < 0xf000:
        RxPl = CalcPl(61.22666,rx_value)
        print(f'  Rx PL {RxPl}',end='')
        pl_code = pl_tones.get(RxPl)
        if pl_code:
            print(f' ({pl_code})',end="")
        print('')

    if tx_value > 0 and tx_value < 0xf000:
        TxPl = CalcPl(17.70666,tx_value)
        print(f'  Tx PL {TxPl}',end="")
        pl_code = pl_tones.get(TxPl)
        if pl_code:
            print(f' ({pl_code})',end="")
        print('')


def DumpScanlist(scanlist):
    mode = 1
    First = True
    for byte in scanlist:
        mask = 0x80
        while mask != 0:
            if byte & mask:
                if not First:
                    print(', ',end='')
                First = False
                print(f'{mode}',end='')
            mask >>= 1
            mode += 1
    print('')

def DumpMplTbl(plug):
    PlTbl = (plug[0x18] << 8) + plug[0x19]
    Entries = plug[0x1a]

    i = 0
    print('MPL table:')
    while i < Entries:
        print(f'  {i + 1}: Rx ',end='')
        offset = PlTbl + (i  * 4)
        rx_value = (plug[offset] << 8) + plug[offset+1]
        tx_value = (plug[offset+2] << 8) + plug[offset+3]
        if rx_value == 0:
            print(f'CSQ',end='')
        elif rx_value > 0 and rx_value < 0xf000:
            RxPl = CalcPl(61.22666,rx_value)
            print(f'PL {RxPl}',end='')
            pl_code = pl_tones.get(RxPl)
            if pl_code:
                print(f' ({pl_code})',end="")
            
        if tx_value == 0:
            print(f', Tx CSQ')
        elif tx_value < 0xf000:
            TxPl = CalcPl(17.70666,tx_value)
            print(f', Tx PL {TxPl}',end="")
            pl_code = pl_tones.get(TxPl)
            if pl_code:
                print(f' ({pl_code})',end="")
            print('')
        i += 1

def DumpCp(args,filename):
    BigEEPROM = False
    LowBand = False
    Mhz800 = False
    empty_scan_list = bytearray(b'\0') * 8
    empty_syn = b'\0' * 3

    if filename.lower().endswith('.rdt'):
        RtdFile = True
    else:
        RtdFile = False
        if args.Band == None:
            print('Error: Band ?')
            return True

        Band = args.Band.lower()
        if Band == 'low':
        # set band for 29.7 - 50.0
            RadioRange = 1
        elif Band == 'vhf':
        # set band for 136 - 154
            RadioRange = 2
        elif Band == 'uhf':
        # set band for 450 - 470
            RadioRange = 8
        elif Band == '800':
            print('Sorry 800 Mhz is not supported')
            return False
        else:
            print('Error: invalid Band "{args.Band}"')
            return True

    print(f'dumping {filename}')

    try:
        fp = open(filename,mode='rb')
    except OSError as err:
        print(err)
        exit(code=err.errno)

    while True:
        if RtdFile:
            ignored = fp.read(1)
        plug = fp.read()
        if not plug:
            break;
        length = ((plug[0] << 8) + plug[1]) + 1
        saved_sum = (plug[2] << 8) + plug[3]

        if length == 8192:
            BigEEPROM = True
        elif length != 2048:
            print(f'Invalid length {length}, must be 2048 or 8192')
            break
        if RtdFile:
            rss_data = plug[8192:]
            plug=plug[0:length]
            if Debug:
                print(f'plug:')
                DumpHex(plug,with_adr=True)
                print(f'rss_data ({len(rss_data)} bytes):')
                DumpHex(rss_data,with_adr=True)
            RadioRange = rss_data[0]
            if RadioRange < 1 or RadioRange > 0xc:
                print(f'Invalid radio range 0x{RadioRange:02x} ?!?')
                return

            CustNameLen = rss_data[2]
            if CustNameLen > 0:
                Customer = rss_data[3:CustNameLen+3].decode()
                print(f'Customer: "{Customer}"')

        print(f'EEPROM length {length}, checksum 0x{saved_sum:04x}')
        adr = 4
        sum = 0
        while adr < length:
            word = (plug[adr] << 8) + plug[adr + 1]
            sum = sum + word
            adr += 2
        sum = sum & 0xffff
        if sum != saved_sum:
            print(f'Invalid checksum 0x{sum:04x}, expected 0x{saved_sum:04x}')
            break
        else:
            print('Checksum is valid')

        if BigEEPROM:
            sn_adr = 0x1ff2
        else:
            sn_adr = 0x7f2
        SerialNum = plug[sn_adr:sn_adr+10].decode()
        if len(SerialNum) > 0:
            print(f'Radio serial number: {SerialNum}')

        print(f'SB9600 address 0x{plug[7]:02x}')

        modes = plug[8]
        if modes == 0:
            print(f'No modes are defined ?!?')
            return

        s=''
        if modes > 1:
            s='s'
        print(f'{plug[8]} active mode{s}')
        ModeLen = plug[9]
        print(f'Mode table has {ModeLen} bytes entries.')
        print(f'Minimum alert tone volume level {plug[0xa]}')
        print(f'Default squelch level {plug[0xb]}')
        print(f'Home mode {plug[0xe]}')
        if plug[0x40] & 0x80:
            print(f'Siren/PA is configured (0x{plug[0x40]:02x})')

        print(f'Radio range {RangeTbl[RadioRange-1][0]} Mhz')
        IfFreq = RangeTbl[RadioRange-1][1]
        LowBand = (RadioRange == 1)
        Mhz800 = (RadioRange == 0xc)

        mode = 0
        while mode <= modes:
            i = 0x100 + (mode * ModeLen)
            mode += 1
            mode_data = plug[i:i+ModeLen]
            #print(f'Mode data:')
            #DumpHex(mode_data)
            if mode_data[0:3] == empty_syn:
            # No Rx frequency, ununsed mode 
                continue
            if Debug:
                print(f'Mode {mode}:')
                DumpHex(mode_data)
            fvco = calc_fco(mode_data[0:3],LowBand)
            frx = calc_rx(fvco,IfFreq)
            if Debug:
                print(f'frx {frx/1e6}')
                print('')
            fvco = calc_fco(mode_data[3:6],LowBand)
            ftx = calc_tx(fvco,LowBand,Mhz800)
            if Debug:
                print(f'ftx {ftx/1e6}')
                print('')
            fvco = calc_fco(mode_data[13:16],LowBand)
            ftalk_around = calc_tx(fvco,LowBand,Mhz800)
            if Debug:
                print(f'ftalk_around {ftalk_around/1e6}')
                print('')
            elif ftx != 0 or frx != 0 or ftalk_around != 0:
                print(f'Mode {mode}:')
                if frx != 0:
                    print(f'  frx {frx/1e6}')
                if ftx != 0:
                    print(f'  ftx {ftx/1e6}')
                if ftalk_around != 0:
                    print(f'  ftalk_around {ftalk_around/1e6}')

            if mode_data[6] != 0:
            # A PL or DPL is programmed
                DumpPlDpl(mode_data,plug,BigEEPROM)
            if mode_data[7] != 0:
                if mode_data[7] & 0x80:
                    print('  PTT disabled')
                else:
                    minutes = 0
                    seconds = (mode_data[7] & 0x7f) * 5
                    if seconds > 59:
                        minutes = math.floor(seconds / 60)
                        seconds -= minutes * 60
                    print(f'  Tx timeout {minutes}:{seconds:02d}')

            scanlist=mode_data[16:25]
            scan_enable = mode_data[0x8] & 0x3
            if mode_data[0xb] != 0 or mode_data[0xc] != 0 or bytearray(scanlist) != empty_scan_list and scan_enable != 0:
                if scan_enable == 3:
                    print(f'  Operator selected scanning:')
                elif scan_enable == 2:
                    print('   Scanning:')
                else:
                    print(f' Error: scan_enable invalid {scan_enable}')

                if mode_data[0xb] != 0 and mode_data[0xc] != 0:
                        print(f'    P1 mode {mode_data[0xb]}, P2 mode {mode_data[0xc]}')
                elif mode_data[0xb] != 0:
                    print(f'    P1 mode {mode_data[0xb]}')
                elif mode_data[0xc] != 0:
                    print(f'    P2 mode {mode_data[0xc]}')

                if bytearray(scanlist) != empty_scan_list:
                    print('    NP modes: ',end='')
                    DumpScanlist(scanlist)

        if plug[0x1a] != 0:
            DumpMplTbl(plug)

    fp.close()

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--Debug',action='store_true')
parser.add_argument("--Band",help='radio band from .bin file ("low", "vhf", "uhf", or "800")',type=str)
parser.add_argument('file',nargs='+')
args = parser.parse_args()

parser.add_argument("--Test",help="Run internal test",action="store_true")
args = parser.parse_args()

if args.Debug:
    Debug = True

while len(args.file) > 0:
    DumpCp(args,args.file[0])
    args.file = args.file[1:len(args.file)]
                
