#! /usr/bin/env bash

export APP_ID='test_bash'
#HB_PORT='8888'
export HB_HOST='localhost'

function hb_test() {
  echo "HB_URL: [${HB_URL}]"
  _hb_init 500
  _hb_ping 1000
  _hb_done 2
}

source ./hb.sh


