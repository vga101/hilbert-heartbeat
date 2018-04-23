#! /usr/bin/env bash

#set -v #set -x

### HB: ENV. VARS...
DEFAULT_URL="http://${HB_HOST:-127.0.0.1}:${HB_PORT:-8888}"
export HB_URL=${HB_URL:-$DEFAULT_URL}

################################################################
################################################################
function HB_SEND() {  # Send HTTP GET REQUEST with specified path to the HB server specified by HB_URL
  local REQ="$1"
  wget -t 2 -T 2 -q -O- --header='Accept-Encoding: gzip, deflate' "${HB_URL}${REQ}" 2>/dev/null || curl -s --connect-timeout 2 -m 4 -L -X GET -- "${HB_URL}${REQ}" 2>/dev/null
  return $?
}

function HB_SEND_MESSAGE() { # signal  timeout/interval - Send specified HB signal to HB server with specified timeout and global Application ID
  HB_SEND "/$1?$2&appid=${APP_ID}&cache_buster=$(date +%s_%N)"
  return $?
}

function HB_POST_MESSAGE() { # signal  timeout/interval - Send specified HB signal to HB server with specified timeout and global Application ID via HTTP POST. 
  local REQ="/$1?$2&appid=${APP_ID}&cache_buster=$(date +%s_%N)"
  local DATA="{\"appid\":\"${APP_ID}\"}"
  wget -t 2 -T 2 -q -O- --header='Accept-Encoding: gzip, deflate' --header='Accept-Charset: UTF-8' --header='Content-Type: application/json' --post-data="${DATA}" "${HB_URL}${REQ}" 2>/dev/null || \
    curl -s --connect-timeout 2 -m 4 -H "Accept: application/json" -H "Content-Type:application/json" -L -X POST --data "${DATA}" -- "${HB_URL}${REQ}" 2>/dev/null
  return $?
}

function HB_SEND_INIT() {  #  INTERVAL - send HB_INIT signal to HB server
  HB_POST_MESSAGE "hb_init" "$1"
  return $?
}

function HB_SEND_PING() {  #  INTERVAL - send HB_PING signal to HB server
  HB_SEND_MESSAGE "hb_ping" "$1"
  return $?
}

function HB_SEND_DONE() {  #  INTERVAL - send HB_DONE signal to HB server
  local t="$1"
  HB_POST_MESSAGE "hb_done" "${t:-0}"
  return $?
}

################################################################
################################################################
function _hb_done() { # send hb_done with optionally given timeout and handle the server response
  local _ret
  local response
  response=$(HB_SEND_DONE "$1")
  _ret=$?
  if [[ ${_ret} -ne 0 ]]; then
    1>&2 echo "ERROR: cannot connect to the heartbeat server via [${HB_URL}]. Cannot send DONE. Error exit code: [${_ret}]"
  else
    echo "OK: Heartbeat server done response: [${response}]"
  fi
  return ${_ret}
}

function _hb_init() { # send hb_init with given timeout and handle the server response
  local _ret
  local response
  response=$(HB_SEND_INIT "$1")
  _ret=$?
  if [[ ${_ret} -ne 0 ]]; then
    1>&2 echo "ERROR: cannot connect to the heartbeat server via [${HB_URL}]. Cannot send INIT. Error exit code: [${_ret}]"
  else
    echo "OK: Heartbeat server init response: [${response}]"
  fi
  return ${_ret}
}

function _hb_ping() { # send hb_ping with given timeout and handle the server response
  local _ret
  local response
  response=$(HB_SEND_PING "$1")
  _ret=$?
  if [[ ${_ret} -ne 0 ]]; then
    1>&2 echo "ERROR: cannot connect to the heartbeat server via [${HB_URL}]. Cannot send PING. Error exit code: [${_ret}]"
  else
    echo "OK: Heartbeat server ping response: [${response}]"
  fi
  return ${_ret}
}

function _hb_ping_loop() {  # send hb_pings in a loop (with BG application is running), with timeout given by $HB_PING_INTERVALsleep according to those timeouts or server responses. Requires external calculator tool: `bc` to convert [ms] to [seconds]
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

# NOTE: the collowing is due to https://stackoverflow.com/a/2183063
function _trap_handler_setup() {  # setup signal handlers
  local func="$1"
  shift
  local varname="$1"
  shift
  for sig ; do
    trap "${func} ${varname} ${sig}" "${sig}"
  done
  return 0
}

function _hb_trap_handler() {  # EXIT signal handler to send HB_DONE (if necessary) and make sure to terminate BG application
  ### Usage example:
  # _trap_handler_setup "_hb_trap_handler" "PID" 0 # 1 2 3 13 15
  # echo "TRYING TO WAIT for the Main process [${PID}]: "
  # wait "${PID}"
  # _ret=$?
  # PID=0
  # exit ${_ret}

  rv=$?
#  echo "Ret. code: [$rv]?"
  local var="$1" # NOTE: **Name** of global variable with PID of BG process
  local pid=${!var} # NOTE: current value of PID
  shift
  local sig="$1" # signal to handle
  shift
  echo "PID of BG process: [${pid}]. TRYING TO HANDLE SIGNAL [${sig}]: "


  if [[ ${pid} -ne 0 ]]; then
    if [[ "${sig}" -ne 0 ]]; then
      echo "TRYING TO PASS the signal [${sig}] the BG process: "
      kill "-${sig}" "${pid}" && sleep 1
    fi

    echo "TRYING TO KILL the BG Main process: "
    kill "${pid}" && sleep 1
    kill -SIGKILL "${pid}"
  fi

  echo "Sending HB DONE message!"
  _hb_done "${HB_DONE_TIMEOUT:-0}"
#  echo "Ret. code: [$rv]!"
#  exit ${rv}
}


################################################################
################################################################
function hb_list() { # Query HB server for current applications
  HB_SEND "/list?cache_buster=$(date +%s_%N)"
  exit $?
}

function hb_status() { # [APP_ID] Query HB server for the host status or the status of individual application (if specified)
  if [[ -z "${APP_ID}" ]]; then
    HB_SEND "/status?cache_buster=$(date +%s_%N)"
    exit $?
  fi

  HB_SEND "/status?appid=${APP_ID}&cache_buster=$(date +%s_%N)"
  exit $?
}

################################################################
function hb() {  # CMD   TIME - Send generic HB command (with a timeout) via HTTP GET. NOTE: this is deprecated! Please switch to using high-level helpers/functions!
  if [[ -z "${APP_ID}" ]]; then
      1>&2 echo "ERROR: please set [APP_ID]!"
      exit 1
  fi

  HB_SEND_MESSAGE "$@"
  exit $?
}

function hb_init() {  # TIME  # send hb_init with given timeout & globally specified appliction ID and handle the server response
  if [[ -z "${APP_ID}" ]]; then
      1>&2 echo "ERROR: please set [APP_ID]!"
      exit 1
  fi

  _hb_init "$@"
  exit $?
}

function hb_ping() {  # TIME # send hb_ping with given timeout & globally specified appliction ID and handle the server response
  if [[ -z "${APP_ID}" ]]; then
      1>&2 echo "ERROR: please set [APP_ID]!"
      exit 1
  fi

  _hb_ping "$@"
  exit $?
}

function hb_done() {  # [TIME] # send hb_done with optionally given timeout & globally specified appliction ID and handle the server response
  if [[ -z "${APP_ID}" ]]; then
      1>&2 echo "ERROR: please set [APP_ID]!"
      exit 1
  fi

  _hb_done "$@"
  exit $?
}


################################################################
function hb_wrapper() { # _BG_APP_EXEC_LINE_. High-level helper: can send all HB signals and wait in FG, while some application is running in BG. Behaviour is controlled via env.vars.
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
  if [[ "x${HB_SEND_DONE}" == "xtrue" ]]; then
    _trap_handler_setup "_hb_trap_handler" "PID" 0 # 1 2 3 13 15
  fi

  # send initial INIT signal?  
  if [[ "x${HB_SEND_INIT}" == "xtrue" ]]; then 
    _hb_init "${HB_INIT_TIMEOUT}" # || exit $?
  fi

  # Main Application is run as follows:
  echo "Starting [$@] in background: "
  exec "$@" &
  PID="${!}"
  echo "=> PID for BG process is [${PID}]"

  if [[ "x${HB_SEND_PING}" == "xfalse" ]]; then
    # no need in HB PINGs?
    echo "Switching [${PID}] to foreground!"
  else
    _hb_ping_loop
  fi
  echo "TRYING TO WAIT for the Main process [${PID}]: "
  wait "${PID}"
  _ret=$?
  PID=0

#  if [[ "x${HB_SEND_DONE}" == "xtrue" ]]; then
#    _hb_done "${HB_DONE_TIMEOUT}" # || exit $?
#  fi
  exit ${_ret}
}

################################################################
function hb_dummy() { # _BG_APP_EXEC_LINE_. High-level helper which makes sure to send HB pings while main process runs in BG...
  export HB_SEND_PING="${HB_SEND_PING:-true}"
  hb_wrapper "$@"
  exit $?
}

################################################################
function _default_main_entry() {  # do the trick a-la busybox executable sharing (using links)

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
  # * hb_dummy       _BG_APP_EXEC_LINE_
  # * hb_wrapper     _BG_APP_EXEC_LINE_

  # Sample helpers for our HB Server implemntation written in Python3:
  # * hb_list
  # * hb_status

  # echo "Running: [$CMD]"

  ${CMD} "$@"
  exit $?
}

################################################################
################################################################
[[ ! -v HB_BASH_LIBRARY ]] && _default_main_entry "$@"
