#!/bin/bash

DEFAULT_URL="http://${HB_HOST:-127.0.0.1}:${HB_PORT:-8888}"
export HB_URL=${HB_URL:-$DEFAULT_URL}

REQ="/status"
S=$(wget -q -O- --header='Accept-Encoding: gzip, deflate' "${HB_URL}${REQ}" 2>/dev/null || curl -s -L -X GET -- "${HB_URL}${REQ}" 2>/dev/null)

if [ $? -ne 0 ]; then
  echo "CRITICAL - cannot get heartbeat data"
  exit 2
fi

case "$S" in
OK*)
echo "$S"; exit 0;;

WARNING*)
echo "$S"; exit 1;;

CRITICAL*)
echo "$S"; exit 2;;
esac


#  echo "UNKNOWN - ${msg}"
echo "$S"; exit 3
