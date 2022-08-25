#!/usr/bin/python3
# lst2nfo <list file generated by f9dasm> <nfo file to generate>
import sys
import re

args = len(sys.argv)

if args != 3:
    print('Usage:')
    print('  lst2nfo <list file generated by f9dasm> <nfo file to generate>')
    sys.exit()

in_file = sys.argv[1]
out_file = sys.argv[2]

try:
    fp_in = open(in_file,mode='r')
    fp_out = open(out_file,mode='w')
except OSError as err:
    print(err)
    exit(code=err.errno)

address=''
while True:
    line = fp_in.readline()
    if not line:
        break;
    line=line.rstrip()
    #print(f'line "{line}"')
    if address == '':
        m = re.match(r'.*ORG     \$([0-9A-F]{4})$',line)
        if m:
            address=m.group(1)
            adr=address
            #print(f'address set to "{address}"')

    m = re.match(r'.*;(.*)',line)
    if m:
        comment=m.group(1)
        #print(f'comment "{comment}"')
        m = re.match(r'.*;([0-9A-F]{4}): (.*)',line)
        if m:
            address=m.group(1)
            comment=m.group(2)

        #print(f'comment "{comment}"')

        m = re.match(r'^([0-9A-F]{2})((?: [0-9A-F]{2}){0,}) {0,}(.*)$',comment)
        if m:
            comment=m.group(3)
            if comment == '':
                #print('stripped')
                pass

        if address != '' and comment != '':
            out_line=f'lcomment {address} {comment}\n'
            #print(f'writing {out_line}',end='')
            fp_out.write(out_line)
                
