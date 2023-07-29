#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "converting videos"
mkdir -p out/

# Place videos in selfdrive/assets/videos and upload out/ to ces azure bucket

for f in *.mp4; do
#  ffmpeg -y -i "$f" -vf scale=2160:1080 -r 20 -f rawvideo -c:v h264 -b:v 4000k -pix_fmt yuv420p -strict -2 "out/$f.hevc"
  fmpeg -y -i "$f" -vf scale=2160:1080 -r 20 -f rawvideo -c:v h264 -crf 20 -pix_fmt yuv420p -strict -2 "out/$f.hevc"
done;

echo "Success!"
