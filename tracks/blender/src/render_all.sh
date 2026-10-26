#!/bin/bash
# renders shots given as args, then encodes each to mp4
B=~/Applications/Blender.app/Contents/MacOS/Blender
O="$(cd "$(dirname "$0")/.." && pwd)"
for s in "$@"; do
  rm -rf $O/frames/$s; mkdir -p $O/frames/$s
  $B -b -P $O/src/shots.py -- $s full 1920 1080 24 > $O/frames/$s.log 2>&1
  ffmpeg -loglevel error -y -framerate 30 -i $O/frames/$s/f_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 -preset slow -an -movflags +faststart $O/$s.mp4
  echo "$s done $(date +%T)" >> $O/frames/progress.txt
done
