#!/usr/bin/env python3
import urllib.request
import requests
import os
import shutil
from common.basedir import BASEDIR

AZ_BASEDIR = "https://commadataci.blob.core.windows.net/cesdemo"
MANIFEST = f"{AZ_BASEDIR}/manifest.txt"
VIDEOS_PATH = f"{BASEDIR}/selfdrive/assets/videos/out"


print("downloading videos")
os.makedirs(VIDEOS_PATH, exist_ok=True)

manifest = requests.get(MANIFEST)
manifest = manifest.content.decode('utf-8').split('\n')
manifest = [f.replace('out/', '') for f in manifest]

for f in manifest:
  print(f'Downloading {f}')
  file_path = os.path.join(VIDEOS_PATH, f)
  urllib.request.urlretrieve(os.path.join(AZ_BASEDIR, "out", f), file_path)

for f in os.listdir(VIDEOS_PATH):
  if f not in manifest:
    print(f'Removing {f}')
    os.remove(os.path.join(VIDEOS_PATH, f), )
