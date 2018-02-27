#! /usr/bin/env bash

#set -v #set -x

### HB: ENV. VARS...
export HB_HOST=${HB_HOST:-localhost}
export HB_PORT=${HB_PORT:-8888}
export HB_URL="http://${HB_HOST}:${HB_PORT}"

################################################################
################################################################
function HB_SEND() {  # REQ
  local REQ="$1"
  wget -q -O- --header='Accept-Encoding: gzip, deflate' "${HB_URL}${REQ}" 2>/dev/null || curl -s -L -X GET -- "${HB_URL}${REQ}" 2>/dev/null
  return $?
}

function HB_SEND_MESSAGE() { # signal  timeout/interval
  HB_SEND "/$1?$2&appid=${APP_ID}&cache_buster=$(date +%N)"
  return $?
}

function HB_POST_MESSAGE() { # signal  timeout/interval
  local REQ="/$1?$2&appid=${APP_ID}&cache_buster=$(date +%N)"
  local DATA="{\"appid\":\"${APP_ID}\"}"
  wget -q -O- --header='Accept-Encoding: gzip, deflate' --header='Accept-Charset: UTF-8' --header='Content-Type: application/json' --post-data="${DATA}" "${HB_URL}${REQ}" 2>/dev/null || \
    curl -s -H "Accept: application/json" -H "Content-Type:application/json" -L -X POST --data "${DATA}"-- "${HB_URL}${REQ}" 2>/dev/null
  return $?
}

function HB_SEND_INIT() {  #  INTERVAL
  HB_POST_MESSAGE "hb_init" "$1"
  return $?
}

function HB_SEND_PING() {  #  INTERVAL [in ms]!
  HB_SEND_MESSAGE "hb_ping" "$1"
  return $?
}

function HB_SEND_DONE() {  #  INTERVAL
  HB_POST_MESSAGE "hb_done" "$1"
  return $?
}

################################################################
################################################################
function _hb_done() {
  local response=$(HB_SEND_DONE "$1")
  local _ret=$?
  if [[ ${_ret} -ne 0 ]]; then
    1>&2 echo "ERROR: cannot connect to the heartbeat server via [${HB_URL}]. Error exit code: [${_ret}]"
  else
    echo "OK: Heartbeat server done response: [${response}]"
  fi
  return ${_ret}
}

function _hb_init() { # send hb_init with given timeout and handle the server response
  local response=$(HB_SEND_INIT "$1")
  local _ret=$?
  if [[ ${_ret} -ne 0 ]]; then
    1>&2 echo "ERROR: cannot connect to the heartbeat server via [${HB_URL}]. Error exit code: [${_ret}]"
  else
    echo "OK: Heartbeat server init response: [${response}]"
  fi
  return ${_ret}
}

function _hb_ping() { # send hb_init with given timeout and handle the server response
  local response=$(HB_SEND_PING "$1")
  local _ret=$?
  if [[ ${_ret} -ne 0 ]]; then
    1>&2 echo "ERROR: cannot connect to the heartbeat server via [${HB_URL}]. Error exit code: [${_ret}]"
  else
    echo "OK: Heartbeat server ping response: [${response}]"
  fi
  return ${_ret}
}

function _hb_ping_loop() {
    local sleep_time
    local hb_ping_interval="$(bc <<<"scale=2;(${HB_PING_INTERVAL}/1000.0)")"
    echo "Waiting for BG process [${PID}]... while sending pings every [${HB_PING_INTERVAL}] ms..."

    local ret

    while ps -o pid | grep -q "^[[:space:]]*"${PID}"[[:space:]]*$"
    do
      sleep_time=$(HB_SEND_PING "${HB_PING_INTERVAL}")
      ret=$?
      if [[ ${ret} -ne 0 ]]; then
        1>&2 echo "WARNING: non-successful heartbeat server ping! Exit code: [${ret}], Response: [$sleep_time]!"
      fi

      sleep_time="$(bc <<<"scale=2;(${sleep_time}/1000.0)")"
      if [[ $? -ne 0 ]]; then
        1>&2 echo "ERROR: pong is not a number: [${sleep_time}]! Using fallback: [${hb_ping_interval}]."
        sleep_time="${hb_ping_interval}"
      fi

      sleep "$(bc <<<"scale=2;(${sleep_time}*950.0/1000.0)")" # sleep a bit less than promised or expected to...
    done
    return 0
}

function _hb_trap_handler() {
  echo "TRYING TO HANDLE AN EXIT SIGNAL: "
  if [[ ${PID} -ne 0 ]]; then
    echo "TRYING TO KILL the BG Main process [${PID}]: "
    kill -SIGTERM "${PID}"
    sleep 3
    kill -SIGKILL "${PID}"
    sleep 1
    echo "TRYING TO WAIT for the Main process [${PID}]: "
    wait "${PID}" # TODO: is this required?
    PID="0"
    echo "Sending HB DONE message!"
    _hb_done "${HB_DONE_TIMEOUT:-0}"
  fi

  exit 143; # 128 + 15 -- SIGTERM
}

################################################################
function hb_list() {
  HB_SEND "/list?cache_buster=$(date +%N)"
  exit $?
}

################################################################
function hb_status() {
  if [[ -z "${APP_ID}" ]]; then
    HB_SEND "/status?cache_buster=$(date +%N)"
    exit $?
  fi

  HB_SEND "/status?appid=${APP_ID}&cache_buster=$(date +%N)"
  exit $?
}

################################################################
function hb() {  # CMD   TIME
  if [[ -z "${APP_ID}" ]]; then
      1>&2 echo "ERROR: please set [APP_ID]!"
      exit 1
  fi

  HB_SEND_MESSAGE "$@"
  exit $?
}

################################################################
function hb_init() {  # TIME
  if [[ -z "${APP_ID}" ]]; then
      1>&2 echo "ERROR: please set [APP_ID]!"
      exit 1
  fi

  _hb_init "$@"
  exit $?
}

################################################################
function hb_ping() {  # TIME
  if [[ -z "${APP_ID}" ]]; then
      1>&2 echo "ERROR: please set [APP_ID]!"
      exit 1
  fi

  _hb_ping "$@"
  exit $?
}

################################################################
function hb_done() {  # [TIME]
  if [[ -z "${APP_ID}" ]]; then
      1>&2 echo "ERROR: please set [APP_ID]!"
      exit 1
  fi

  _hb_done "$@"
  exit $?
}


################################################################
function hb_wrapper() {
  local response
  local _ret

  if [[ -z "${APP_ID}" ]]; then
      1>&2 echo "WARNING: please set [APP_ID], which is required for sending any HB!"
      echo "Starting in foreground: [$@]..."
      exec "$@"
      exit $?
  fi

  declare -g PID="0"

  export HB_SEND_INIT="${HB_SEND_INIT:-true}"
  export HB_INIT_TIMEOUT="${HB_INIT_TIMEOUT:-10000}"

  export HB_SEND_PING="${HB_SEND_PING:-false}"
  export HB_PING_INTERVAL="${HB_PING_INTERVAL:-9000}" # in ms

  export HB_SEND_DONE="${HB_SEND_DONE:-true}" # timeout: 0
  export HB_DONE_TIMEOUT="${HB_DONE_TIMEOUT:-0}"

  # hook hb_done on several signals/interrupt
  [[ "x${HB_SEND_DONE}" == "xtrue" ]] && trap '{ _hb_trap_handler ; exit 255 ; }' EXIT SIGTERM SIGINT SIGHUP

  # send initial INIT signal?  
  if [[ "x${HB_SEND_INIT}" == "xtrue" ]]; then 
    _hb_init "${HB_INIT_TIMEOUT}" # || exit $?
  fi

  # Main Application is run as follows:
  echo "Starting [$@] in background: "
  exec "$@" &
  PID="$!"
  echo "=> PID for BG process is [${PID}]"

  if [[ "x${HB_SEND_PING}" == "xfalse" ]]; then
    # no need in HB PINGs?
    echo "Switching [${PID}] to foreground!"
    wait "${PID}"
    _ret=$?
  else
    _hb_ping_loop
    _ret=$?
  fi

#  if [[ "x${HB_SEND_DONE}" == "xtrue" ]]; then
#    _hb_done "${HB_DONE_TIMEOUT}" # || exit $?
#  fi
  exit ${_ret}
}

################################################################
function hb_dummy() { # also send HB pings while main process runs in background...
  export HB_SEND_PING="${HB_SEND_PING:-true}"
  hb_wrapper "$@"
  exit $?
}

################################################################
################################################################

# Check the symbolic link to the script to
readonly CMD="$(basename "$0" '.sh' | grep -E '^hb')"
if [[ $? -ne 0 ]]; then
  1>&2 echo "ERROR: wrong command/link-name: [$0]!"
  exit 2
fi 

# check for such a known function
declare -f "${CMD}" &>/dev/null
if [[ $? -ne 0 ]]; then
  1>&2 echo "ERROR: unknown command: [${CMD}]!"
  exit 2
fi 

# possible CMDs:

# Standard HB API:
# * hb             hb_message TIMEOUT
# * hb_init/ping   TIMEOUT
# * hb_done        [TIMEOUT]

# Wrappers:
# * hb_dummy       _APP_EXEC_LINE_
# * hb_wrapper     _APP_EXEC_LINE_

# Sample helpers for our HB Server implemntation written in Python3:
# * hb_list
# * hb_status

# echo "CMD: [$CMD]"

${CMD} "$@"
exit $?
