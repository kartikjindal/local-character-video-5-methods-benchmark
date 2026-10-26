#!/bin/zsh
# Approach 5: lip-sync the presenter face to the shared narration with SadTalker (patched for Apple GPUs).
cd "$(dirname "$0")"
rm -rf tracks/narrator/out
cd SadTalker && PYTORCH_ENABLE_MPS_FALLBACK=1 ../.venv-talk/bin/python inference.py \
  --driven_audio ../spine/assets/narration-full.wav --source_image ../tracks/narrator/presenter.png \
  --result_dir ../tracks/narrator/out --still --preprocess crop --enhancer gfpgan --size 256
f=$(ls ../tracks/narrator/out/*.mp4 | head -1)
ffmpeg -loglevel error -y -i "$f" -an -c:v libx264 -crf 16 -pix_fmt yuv420p ../tracks/narrator/narrator.mp4
