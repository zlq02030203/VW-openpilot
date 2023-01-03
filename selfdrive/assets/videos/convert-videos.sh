#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "converting videos to mpeg4"
mkdir -p out/

for f in *.mkv; do
  ffmpeg -y -i "$f" -vf scale=2160:1080 -r 20 -c:v h264 -b:v 2000k -pix_fmt yuv420p -strict -2 "out/$f.mp4"
#  ffmpeg -y -i "$f" -vf scale=2160:1080 -r 20 -c:v h264 -b:v 2000k -pix_fmt yuv420p -strict -2 "out/$f.mp4"
#  ffmpeg -y -i "$f" -vf scale=2160:1080 -r 20 -f rawvideo -c:v h264 -b:v 2000k -pix_fmt yuv420p -movflags +faststart -an "out/$f"
#  ffmpeg -y -i "$f" -vf scale=1280:720 -r 30 -vcodec libx264rgb -b:v 1000k -an -movflags faststart -t 10 "out/$f"
#  ffmpeg -y -i "$f" -vf scale=2160:1080 -r 30 -c:v libvpx-vp9 -b:v 2000k -pix_fmt yuv420p -strict -2 -preset ultrafast "out/$f"
done;

echo "Success!"
