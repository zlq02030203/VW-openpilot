#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "converting videos to mpeg4"
mkdir -p out/

for f in *.mkv; do
  ffmpeg -y -i "$f" -vf scale=2160:1080 -r 20 -c:v h264 -b:v 2000k -pix_fmt yuv420p -strict -2 "out/$f"
done;

echo "Success!"
