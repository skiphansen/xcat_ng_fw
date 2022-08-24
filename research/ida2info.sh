#!/bin/sh
#set -x

if [ $# -ne 2 ]; then
   echo "Usage ida2info.sh <ida pro list file> <NFO file to generate>"
   exit 1
fi

if [ ! -e $1 ]; then
   echo "$1 not found"
   exit 1
fi

iconv -f WINDOWS-1256  -c -t US-ASCII//IGNORE -o 1.tmp $1

script_dir=`dirname $0`
${script_dir}/ida2nfo.py 1.tmp $2
rm *.tmp

