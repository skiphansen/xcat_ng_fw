#!/bin/sh

#set -x

usage() {
   echo "Usage: disassemble [--pretty] <imagefile>"
   echo 'Note: The extension of the imagefile must be ".bin"'
   exit 1
}

if [ $# -lt 1 ]; then
    usage
fi
extra_opts=""

while [ -n "$1" ]; do
    case "$1" in
        --pretty) extra_opts="-noaddr -nohex" ;;
        -*) usage;;
        *) break ;;
    esac
    shift
done

if [ $# -ne 1 ]; then
    usage
fi

(echo $1 | grep \.bin) > /dev/null
if [ $? -ne 0 ]; then
    echo "Error, input file have .bin extension"
    exit 1
fi

if [ ! -e $1 ]; then
   echo "\"$1\" not found"
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

${F9DASM_PATH}f9dasm -info ${base_name}.nfo -out ${base_name}.tmp ${extra_opts} $1
sed 's/^; -$/;/g' ${base_name}.tmp > ${base_name}.lst
rm ${base_name}.tmp


