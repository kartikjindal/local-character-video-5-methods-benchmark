# Report: five free, local ways to put people in a product video

**Question:** can we show real-looking characters in a Trinexa explainer, for free, on one Mac?
**Method:** one 30-second story, one voice, one set of app overlays. Only the way the people are made changes. Five approaches were built end to end and are compared below.
**Short answer:** yes. AI images (SDXL) give the best realism per minute. AI video (LTX-Video) is the only approach where people really move, but on this Mac it's slow and breaks on crowds and big motion. Use it for 2–3 hero shots, not a whole film.

---

## 1. The test

| | |
|---|---|
| Story | Aarav's walk-in interview day: call letter → QR scan at reception → phone buzz in the lounge → interview → hand-off to the client's HR system |
| Length | 30.4 s, 5 shots (6.5 / 5.3 / 6.5 / 5.7 / 6.4 s) |
| Voice | Kokoro TTS `am_michael`, 1.06×, generated locally, shared by all five |
| Overlays | The same Trinexa cards (QR call letter, scan, notification, scorecard, webhook) in every version |
| Assembly | HyperFrames (HTML + GSAP → MP4), `build.py`, one template for all five |
| Fairness | Same script, timing, voice, overlays, music bed and output length (30.4 s, 1920×1080). Only the people layer differs. |

The storyboard is in [`storyline.json`](storyline.json) and [`spine/timing.json`](spine/timing.json).

## 2. The machine

| Part | Spec |
|---|---|
| Mac | MacBook Pro, Apple **M1 Max** |
| CPU | 10 cores (8 performance + 2 efficiency) |
| GPU | **32-core Apple GPU**, Metal 4. Used through PyTorch's `mps` backend and Blender's Metal renderer |
| Memory | **64 GB** unified (CPU and GPU share it) |
| OS | macOS 26.5.1 |
| Also running | IntelliJ, a Linux VM and Cursor stayed open throughout. This matters for the memory numbers in §5. |
| Network | Hugging Face at 0.5–1.5 MB/s at first, **4.6 MB/s** after switching connection; GitHub/blender.org at 6.7 MB/s |

There is no NVIDIA GPU, so no CUDA. Every "GPU" in this report means the Apple GPU.

## 3. Results at a glance

![comparison](docs/comparison.jpg)
*Rows, top to bottom: stock, AI images, AI video, Blender, narrator. Columns: shots 1–5.*

| # | Approach | Tools | Output | GPU used? | Time on this Mac* |
|---|---|---|---|---|---|
| 1 | Free stock | Wikimedia Commons + Openverse search, ffmpeg | [`results/stock.mp4`](results/stock.mp4) | No | **~22 min** sourcing + 1.3 min render |
| 2 | AI images | RealVisXL V4 (SDXL) via 🤗 diffusers | [`results/aistill.mp4`](results/aistill.mp4) | **Yes**, MPS fp16 | **~28 min** for 16 images (~2 min each) + 1.5 min render |
| 3 | AI video | LTX-Video 0.9.5 (2B) image-to-video, animating track 2's stills | [`results/aivideo.mp4`](results/aivideo.mp4) | **Yes**, MPS fp32 | **~87 min** for 5 clips (11–26 min each) + 1 min render |
| 4 | 3D | Blender 4.5 EEVEE + Quaternius CC0 rigged characters | [`results/blender.mp4`](results/blender.mp4) | **Yes**, Metal | **~35 min** (14 min of it rendering) + 1.1 min render |
| 5 | Talking narrator | SadTalker (lip-sync) + GFPGAN (face clean-up); presenter face from SDXL | [`results/narrator.mp4`](results/narrator.mp4) | **Partly**: lip-sync on GPU, clean-up on CPU | **~52 min** + 1 min render |

\* Compute time after the models were downloaded. Setup and download time are in §6.

To see them side by side, run `python3 -m http.server 8777 --bind 127.0.0.1` in the repo root and open http://127.0.0.1:8777. The dashboard shows the storyboard, every shot thumbnail, all five players with a "Play all together" button, and each track's tools, licence and weaknesses.

## 4. Evaluation

Each approach is scored 1–5 by me (the builder) after looking at every shot. The criteria are as follows.
- **Realism:** does it look like real people?
- **Consistency:** is Aarav the same person in all five shots?
- **Motion:** do the people move?
- **Story fit:** does each shot show what the storyboard asked for?
- **Speed:** compute time for 30 s on this Mac.
- **Reliability:** how often it produced a usable shot without rescue.
- **Licence clarity:** how simple the terms are for commercial use.

| Criterion | 1 · Stock | 2 · AI images | 3 · AI video | 4 · Blender | 5 · Narrator |
|---|---|---|---|---|---|
| Realism | **5** (real photos) | 4 | 4 | 2 | 3 |
| Consistency | 1 | 4 | 4 | **5** | **5** |
| Motion | 1 (camera only) | 1 (camera only) | **4** | 3 | 2 (head only) |
| Story fit | 2 | **4** | 3 | **4** | n/a (adds a presenter) |
| Speed | 4 | 4 | 1 | 3 | 2 |
| Reliability | 4 | **5** | 2 | 4 | 3 |
| Licence clarity | 3 (attribution, CC BY-SA) | 4 | 3 (RAIL-M use limits) | **5** (CC0) | 4 |
| **Average** | 2.9 | **3.7** | 3.0 | 3.7 | 3.2 |

Blender ties AI images on average only because consistency and licence clarity count as much as realism. For "real-looking people", AI images win clearly.

### 1 · Free stock (Wikimedia / Openverse). Verdict: weak for a story
- No usable free **video** of offices, receptions or interviews exists on Commons. Hits were under 720p or were news footage, so all five shots are real **photos** with a slow camera push.
- A different person appears in every shot, and most aren't Indian. One shot is a bus terminal standing in for a lounge, and the s1 subject is seen from behind.
- Real and legally clean, with credits in [`tracks/stock/CREDITS.md`](tracks/stock/CREDITS.md), but it can't tell *Aarav's* story.
- Pexels has much better free video, but needs a (free) API key, which this POC didn't use.

### 2 · AI images (SDXL, local). Verdict: best value ⭐
- Photo-realistic Indian cast, and the same Aarav (navy blazer, white shirt) in most shots, from one fixed character description plus fixed seeds. All 10 candidates are in [`docs/aistill-candidates.jpg`](docs/aistill-candidates.jpg).
- Steady ~2 min per 1344×768 image on the GPU. 2 candidates per shot was enough to pick a good one every time.
- **Weaknesses:**
  - Stills only; motion comes from the camera.
  - Identity drifts when a scene gets busy: in s4 Aarav gained glasses and a beard.
  - Prompts are followed loosely: in s2 there is no receptionist actually scanning.
  - s3 had to be mirrored so the UI card wouldn't cover his face.

### 3 · AI video (LTX-Video, local). Verdict: alive, but slow and fragile
- When it works it's the most convincing approach: Aarav smiles at his phone (s1) and talks and gestures in the interview (s4). See [`docs/aivideo-s1-good.jpg`](docs/aivideo-s1-good.jpg) and [`docs/aivideo-s4-good.jpg`](docs/aivideo-s4-good.jpg).
- **It fails on crowds and big motion.**
  - s2: the reception crowd melts into a blur after ~3 s ([`docs/aivideo-s2-melt.jpg`](docs/aivideo-s2-melt.jpg)).
  - s5: walking out, his body warps and smears ([`docs/aivideo-s5-warp.jpg`](docs/aivideo-s5-warp.jpg)).
  - Both were rescued by using only the clean first 2.6 / 3.1 s, played forward then backward (`s2-clean.mp4`, `s5-clean.mp4`). The raw clips are kept next to them.
- Minor issues: in s3 the camera drifts and a ghost figure appears late; in s4 the tie colour drifts.
- It generates at 768×448 and is upscaled to 1080p, so it's softer than the stills.
- **Speed is the real problem.** See §5.

### 4 · Blender 3D. Verdict: consistent and fully controllable, but not realistic
- Every shot does exactly what the storyboard says: sitting with a phone, holding it to a scanner, the phone buzzing, the interview, walking out. Characters are rigged and animated, and nobody is in a T-pose.
- They're low-poly, game-style people (Quaternius, CC0). Faces have no expressions and there's no lip-sync. The same three base models are recoloured for everyone, and the sets are untextured primitives.
- The free, no-login options for realistic humans were all ruled out: Mixamo needs an Adobe login, and MetaHuman/Character Creator aren't free.

### 5 · Talking narrator (SadTalker). Verdict: a nice guide, not a lead
- A fictional SDXL presenter's face lip-syncs to the exact narration, frame-accurate over the full 30.4 s ([`docs/narrator-lipsync.jpg`](docs/narrator-lipsync.jpg)).
- Only the head moves (lips, blinks, small nods). The output is 512×512, so it only works small, as a corner bubble.
- The first presenter was a woman, which didn't match the male voice, so it was regenerated as a man.

## 5. GPU, CPU, memory: what actually happened

| Step | Device | Measured |
|---|---|---|
| SDXL image, 1344×768, 30 steps | GPU (MPS, fp16 + fp16-fix VAE) | 108–131 s per image, average 119 s |
| LTX-Video, denoising (121 frames, 30 steps) | GPU (MPS) | **27–29 s per clip** (~1 step/s). Fast. |
| LTX-Video, decoding + memory swap | GPU + swap | **650–1,540 s per clip**. This is where the time goes. |
| LTX-Video, quick test (49 frames, 20 steps) | GPU | 33 s denoise, 278 s total |
| Blender EEVEE, 878 frames at 1080p, 24 samples | GPU (Metal) | 14 min |
| SadTalker face renderer, 380 steps | **CPU**: 24.1 s/step (projected 2.5 h, aborted) → **GPU**: 1.85 s/step | 11.7 min on GPU (≈13× faster) |
| GFPGAN face clean-up, 760 frames | CPU | 39.4 min (~3.1 s/frame) |
| HyperFrames render, 30.4 s at 1080p | CPU + headless Chrome | 63–93 s per video |

**Bottlenecks and how each was handled:**
1. **Memory and swap (AI video).** The T5-XXL text encoder alone is 19 GB at fp32, and the IDE and VM were also running. Swap hit **32 GB**, and clip 3 took 26 min instead of ~12. Fix: encode the prompts once on the CPU, then unload T5 before generating. That brought swap to 17.5 GB, but clip 4 still took 23 min. **Closing other apps is the biggest single speed-up.**
2. **No bf16 on M1.** LTX-Video's documented bf16 path failed ("Input type (float) and bias type (BFloat16) should be the same"), so it runs in fp32: 2× the memory and slower.
3. **A CPU random generator fed to the GPU** crashed the decode step. Fixed with `torch.Generator('mps')`.
4. **SadTalker on the Apple GPU.** Its pinned PyTorch 2.1 has no Conv3D on MPS, so it fell back to the CPU (2.5 h projected). Fixed by upgrading to PyTorch 2.5.1 and patching 3 files ([`patches/sadtalker-apple-gpu.patch`](patches/sadtalker-apple-gpu.patch)), which made it **13× faster**. GFPGAN has no Apple-GPU path, so the clean-up stays on the CPU.
5. **Network.** At 0.5–1.5 MB/s the 25 GB of models would have taken ~4 h. Switching connection (4.6 MB/s) and running downloads in parallel cut that to about 1 h. Using a 9.5 GB bf16 copy of T5 instead of the 19 GB fp32 original also halved that download.
6. **Install friction.** The Homebrew Blender cask wanted `sudo`, so Blender was installed from the blender.org DMG into `~/Applications` instead. SadTalker needed `setuptools<70` and a torchvision import fix in `basicsr`.

## 6. Setup cost (one time)

| Item | Size |
|---|---|
| RealVisXL V4 (SDXL fp16) + fp16-fix VAE | ~7.3 GB |
| LTX-Video 0.9.5 transformer + VAE | 6.3 GB |
| T5-XXL encoder (bf16 copy, `city96/t5-v1_1-xxl-encoder-bf16`) | 9.5 GB |
| SadTalker + GFPGAN/facexlib weights | ~1.7 GB |
| Blender 4.5 | ~0.4 GB |
| PyTorch and Python libraries (2 environments) | ~3 GB |
| **Total** | **~28 GB**, all cached for reuse |

Cost: **$0**. Every model and tool is free and ran locally; no paid API was used.

## 7. Recommendation for the real Trinexa film

1. **AI images for most character shots**: realistic, consistent, ~2 min per shot.
2. **AI video for 2–3 hero moments only**: one person, small motion (a smile at the phone, a nod in the interview). Generate 2–3 seeds per shot, keep the first clean seconds, and close other apps first.
3. **Keep the app UI as designed screens** (as in the existing film). The people are context; the product is the star.
4. Optional: the **narrator bubble** for an intro or outro.
5. Avoid stock for story shots unless a Pexels key is added, and keep Blender for when exact staging matters more than realism.

**If speed matters:** a cloud GPU (one NVIDIA A100/H100 hour) would generate the AI video in minutes rather than ~90 minutes, but it's no longer free. On this Mac, plan on ~15 min per 5-second AI clip.

## 8. Licences and what's not in this repo

- **Stock photos:** CC0 / CC BY / CC BY-SA. Attribution is in [`tracks/stock/CREDITS.md`](tracks/stock/CREDITS.md).
- **Blender characters:** Quaternius, CC0 ([`tracks/blender/CREDITS.md`](tracks/blender/CREDITS.md)).
- **Models:**
  - RealVisXL V4: CreativeML Open RAIL++-M.
  - LTX-Video 0.9.5: Open RAIL-M (commercial use allowed, with use restrictions).
  - SadTalker and GFPGAN: Apache-2.0.
  - Kokoro TTS: Apache-2.0.
- **All AI faces are fictional.**
- **Not included in this repo:**
  - the model weights (download them; see README);
  - the SadTalker source (clone it and apply the patch);
  - the raw background music and sound-effect files (their licences don't allow redistributing the files themselves).

  The rendered MP4s in `results/` include the background music bed: "Happy Beats / Business Moves" by ende.app.
