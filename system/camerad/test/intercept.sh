#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"

cd /data/tici_test_scripts/isp/interceptor/
gcc -Wno-int-to-pointer-cast -I. -Iprivate_include/ -fPIC -ldl -shared tmpioctl.c -o tmpioctl.so

cd $DIR/../
DISABLE_DRIVER=1 DISABLE_WIDE_ROAD=1 DEBUG_FRAMES=1 LOGPRINT=debug LD_PRELOAD=/data/tici_test_scripts/isp/interceptor/tmpioctl.so ./camerad
