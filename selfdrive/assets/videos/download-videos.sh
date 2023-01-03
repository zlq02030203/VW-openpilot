#!/bin/bash
set -e
cd "$(dirname "$0")"

AZ_BASEDIR="https://commadataci.blob.core.windows.net/cesdemo"
MANIFEST="$AZ_BASEDIR/manifest.txt"

echo "downloading videos"
mkdir -p out/

videos=$(curl -w '\n' -s "$MANIFEST" --fail)

#while read -r line; do
#  if [ -n "$line" ]; then
#    wget "$AZ_BASEDIR/$line" -O "./$line"
#  fi
#done <<< "$videos"

for f in out/*; do
  echo "$f"
  echo "$videos"
  if ! grep -q "$string" <<< "$videos"; then
    echo "Removing $f"
    rm "$f"
  fi
done;

echo "Success!"
