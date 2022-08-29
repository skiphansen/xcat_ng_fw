#!/bin/env python3
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
import argparse

log = False

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

RefTbl = (('not used',0),('6.25 Khz',6250),('4.16667 Khz',4167),('5 Khz',5000))

CTbl = (-1,1,0,2)
LowBand = False
Mhz800 = False
IfFreq = 0

#f(vco) = ((((64 * A) + (63 * B)) * 3 ) + C(table)) * f(ref)
#low band: highside injection, add IF frequency of 75.7 Mhz
#VHF: highside injection, add IF frequency of 53.9 Mhz
#UHF: lowside injection, subtract IF frequency of 53.9 Mhz
def calc_fco(synth_bytes):
    if log:
        print(f'Raw bytes 0x{synth_bytes[0]:02x} 0x{synth_bytes[1]:02x} 0x{synth_bytes[2]:02x}')

    A = synth_bytes[0] & 0x3f
    B = ((synth_bytes[0] & 0xc0) >> 6) + (synth_bytes[1] << 2)

    R = synth_bytes[2] & 0x3
    V = (synth_bytes[2] & 0xc) >> 2
    C = (synth_bytes[2] & 0x30) >> 4
    S = (synth_bytes[2] & 0xc0) >> 6
    if log:
        print(f'A {A} 0x{A:02x}, B {B} 0x{B:02x}, V {V}, R {R}, C {C}')
    fref = RefTbl[R][1]
    if log:
        print(f'fref {fref}')
    fvco = (64 * A) + (63 * B)
    if not LowBand:
        fvco *= 3
        #c bits are extender control for lowband C1 = 1 C0 = extender on/off
        c = CTbl[C]
        if log:
            print(f'c {c}')
        fvco += c
    fvco *= fref
    if log:
        print(f'fvco {fvco/1e6}')
    return fvco

def calc_rx(fvco):
    if fvco == 0:
        return fvco
    else:
        return fvco + IfFreq

def calc_tx(fvco):
    if fvco == 0:
        return fvco
    elif LowBand:
        return 172.8e6- fvco
    elif Mhz800:
        return fvco * 2
    else:
        return fvco


args = len(sys.argv)

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--File",help="raw code plug to dump")
args = parser.parse_args()

parser.add_argument("--Test",help="Run internal test",action="store_true")
args = parser.parse_args()
if args.File:
    print(f'dumping {args.File}')

    try:
        fp = open(args.File,mode='rb')
    except OSError as err:
        print(err)
        exit(code=err.errno)

    while True:
        if args.File.endswith('.RDT'):
            ignored = fp.read(1)
        plug = fp.read()
        if not plug:
            break;
        length = ((plug[0] << 8) + plug[1]) + 1
        saved_sum = (plug[2] << 8) + plug[3]

        if length != 2048 and length != 8192:
            print(f'Invalid length {length}, must be 2048 or 8192')
            break
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

        print(f'SB9600 address 0x{plug[7]:02x}')
        modes = plug[8]
        if modes == 0:
            print(f'No modes defined ?!?')
            break

        s=''
        if modes > 1:
            s='s'
        print(f'{plug[8]} mode{s}:')
        ModeLen = plug[9]
        print(f'Mode table has {ModeLen} bytes entries')

        RadioRange = plug[0x2001 - 1]
        if RadioRange < 1 or RadioRange > 0xc:
            print(f'Invalid radio range 0x{RadioRange:02x} ?!?')
            break
        print(f'Radio range {RangeTbl[RadioRange-1][0]} Mhz')
        IfFreq = RangeTbl[RadioRange-1][1]
        LowBand = (RadioRange == 1)
        Mhz800 = (RadioRange == 0xc)

        mode = 1
        while mode <= modes:
            i = 0x100 + ((mode - 1) * ModeLen)
            fvco = calc_fco((plug[i],plug[i + 1],plug[i+2]))
            frx = calc_rx(fvco)
            fvco = calc_fco((plug[i+3],plug[i + 4],plug[i+5]))
            ftx = calc_tx(fvco)
            if ftx != 0 or frx != 0:
                print(f'Mode {mode}:')
                if frx != 0:
                    print(f'frx {frx/1e6}')
                if ftx != 0:
                    print(f'ftx {ftx/1e6}')
                print('')
            mode += 1

    fp.close()
                
