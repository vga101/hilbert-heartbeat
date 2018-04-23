#!/bin/bash

DEFAULT_URL="http://${HB_HOST:-127.0.0.1}:${HB_PORT:-8888}"
export HB_URL=${HB_URL:-$DEFAULT_URL}

function RET() {
  S="$@"

  case "$S" in
  OK*)
  echo "$S"; exit 0;;

  WARNING*)
  echo "$S"; exit 1;;

  CRITICAL*)
  echo "$S"; exit 2;;
  esac

  #  echo "UNKNOWN - ${msg}"
  echo "$S"; 
  exit 3
}

REQ="/status"

WGET=$(which wget 2>>/dev/null)
if [[ $? -eq 0 ]]; then
  S=$(${WGET} -q -t 2 -T 2 -O- --header='Accept-Encoding: gzip, deflate' "${HB_URL}${REQ}" 2>/dev/null)
  if [[ $? -eq 0 ]]; then
    RET "$S"
  fi
  RET "CRITICAL - cannot get heartbeat data with [${WGET}]"
fi

CURL=$(which curl 2>>/dev/null)
if [[ $? -eq 0 ]]; then
  S=$(${CURL} --connect-timeout 2 -m 4 -s -L -X GET -- "${HB_URL}${REQ}" 2>/dev/null)
  if [[ $? -eq 0 ]]; then
    RET "$S"
  fi
  RET "CRITICAL - cannot get heartbeat data with [${CURL}]"
fi

if [[ -z ${WGET} && -z ${CURL} ]]; then
  RET "CRITICAL - cannot find wget/curl tools!"
fi

RET "UNKNOWN - something went wrong while running [$0] on [$(hostname)] in [${PWD}] under [$(whoami)]!"
