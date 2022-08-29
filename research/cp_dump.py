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

        modes = plug[8]
        if modes == 0:
            print(f'Code plug defines no modes?!?')
            exit(0)

        print(f'SB9600 address 0x{plug[7]:02x}')
        s=''
        if modes > 1:
            s='s'
        print(f'{plug[8]} mode{s}:')
        print(f'Mode table has {plug[9]} bytes entries')

        #f(vco) = ((((64 * A) + (63 * B)) * 3 ) + C(table)) * f(ref)
        #low band: highside injection, add IF frequency of 75.7 Mhz
        #VHF: highside injection, add IF frequency of 53.9 Mhz
        #UHF: lowside injection, subtract IF frequency of 53.9 Mhz

        #N = fvco / refreq
        #c = N % 3; N1 = N / 3;

        # assume low band for now

        ref_freq = 0
        #frx = fvco - 75700000;
        #fvco = ((64 * txa) + (63 * txb)) * refreq;
        #ftx = 172800000 - fvco;



    fp.close()

                
