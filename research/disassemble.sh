#!/bin/sh

#set -x

if [ $# -ne 1 ]; then
   echo "which image (must end in .bin)?"
   exit 1
fi

if [ ! -e $1 ]; then
   echo "$1 not found"
   exit 1
fi

echo $1 | grep \.bin

if [ $? -ne 0 ]; then
    echo "Error, input file must bin binary (with extension .bin)"
    exit 1
fi

base_name=`basename $1 .bin`

if [ -e ${base_name}.lst ]; then
    rm ${base_name}.bak
    mv ${base_name}.lst ${base_name}.bak
fi

if [ ! -e ${base_name}.nfo ]; then
    cp ../template.nfo ${base_name}.nfo
    touch comments.nfo
fi

${F9DASM_PATH}f9dasm -info ${base_name}.nfo -out ${base_name}.lst $1

