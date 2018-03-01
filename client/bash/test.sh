#! /usr/bin/env bash

export APP_ID='test_bash'
#HB_PORT='8888'
export HB_HOST='localhost'

# disable the default main-entry of ./heartbeat.sh
export HB_BASH_LIBRARY=1
source ./heartbeat.sh

function hb_test() {
  echo "HB_URL: [${HB_URL}]"
  _hb_init 500
  _hb_ping 1000
  _hb_done 2
}

hb_test "$@"
exit $?