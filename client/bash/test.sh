#! /usr/bin/env bash

export APP_ID='test_bash'
#HB_PORT='8888'
export HB_HOST='localhost'

# disable the default main-entry of ./heartbeat.sh
export HB_BASH_LIBRARY=1
source ./heartbeat.sh

function main() {  # do basic interaction with the HB-server
  echo "APP_ID: [${APP_ID}]"
  echo "HB_URL: [${HB_URL}]"
  _hb_init 100
  _hb_ping 100
  sleep 0.1
  _hb_ping 666
  sleep 6.0
  _hb_done 0
  return $?
}

main "$@"
exit $?


