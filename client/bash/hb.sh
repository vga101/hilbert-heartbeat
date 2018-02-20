#!/bin/bash

if [ -z "${APP_ID}" ]; then
  exit 1
fi

### HB: SET VARS...
export HB_HOST=${HB_HOST:-localhost}
export HB_PORT=${HB_PORT:-8888}
export HB_URL="http://${HB_HOST}:${HB_PORT}"

REQ="/$1?$2&appid=${APP_ID}"

wget -q -O/dev/null "${HB_URL}${REQ}" 2>/dev/null || \
  curl -s -L -XGET -- "${HB_URL}${REQ}" 2>/dev/null

exit $?

# 2>/tmp/hb_sh_errs
