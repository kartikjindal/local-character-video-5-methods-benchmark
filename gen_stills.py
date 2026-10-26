# Track 2: realistic stills with RealVisXL (SDXL) on the Mac GPU. Fixed cast text + fixed seeds per shot.
# usage: .venv-ai/bin/python gen_stills.py [shot ids...] [--seeds 2]
import json, os, sys, time
os.environ.setdefault('PYTORCH_ENABLE_MPS_FALLBACK', '1')
import torch
from diffusers import StableDiffusionXLPipeline, AutoencoderKL, DPMSolverMultistepScheduler

L = os.path.dirname(os.path.abspath(__file__))
OUT = f'{L}/tracks/aistill/candidates'
os.makedirs(OUT, exist_ok=True)

AARAV = 'Aarav, a 26 year old Indian man, short neat black hair, light stubble, navy blazer over a white shirt'
STYLE = 'photorealistic, candid documentary photo, 35mm lens, natural light, shallow depth of field, sharp focus, realistic skin texture, modern Bangalore tech office'
NEG = 'cartoon, illustration, 3d render, anime, deformed hands, extra fingers, distorted face, text, watermark, logo, blurry, lowres, oversaturated'
SHOTS = {
    's1': f'{AARAV}, sitting on a sofa in a small sunlit apartment in the early morning, looking down at his smartphone with a hopeful smile, coffee mug on the table, {STYLE}',
    's2': f'{AARAV}, standing at a white corporate reception desk, holding out his smartphone screen toward a receptionist, Indian woman receptionist in a maroon cardigan with a lanyard holding a scanner, busy lobby with other candidates in the background, {STYLE}',
    's3': f'{AARAV}, seated in a modern office waiting lounge among other young job candidates, looking down at his smartphone in his hands, {STYLE}',
    's4': f'{AARAV}, seen from the side across a table in a glass-walled meeting room, interviewed by two panelists, an Indian woman with glasses in a grey blazer and an Indian man with a beard in a light blue shirt with a laptop, {STYLE}',
    's5': f'{AARAV}, walking out of a glass office building entrance into bright daylight, smiling, smartphone in hand, laptop bag on shoulder, {STYLE}',
    'presenter': 'head and shoulders portrait of a friendly Indian man presenter in his 30s, short neat dark hair, clean shaven, teal blazer, looking straight at the camera, mouth closed, neutral soft grey studio background, even soft lighting, photorealistic, sharp focus',
}

ids = [a for a in sys.argv[1:] if not a.startswith('--') and not a.isdigit()] or list(SHOTS)
nseeds = int(sys.argv[sys.argv.index('--seeds') + 1]) if '--seeds' in sys.argv else 2

t0 = time.time()
vae = AutoencoderKL.from_pretrained('madebyollin/sdxl-vae-fp16-fix', torch_dtype=torch.float16)
pipe = StableDiffusionXLPipeline.from_pretrained('SG161222/RealVisXL_V4.0', vae=vae, torch_dtype=torch.float16, variant='fp16')
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True)
pipe.to('mps')
pipe.set_progress_bar_config(disable=True)
log = []
for sid in ids:
    w, h = (1024, 1024) if sid == 'presenter' else (1344, 768)
    for k in range(nseeds):
        seed = 1000 + k * 7 + list(SHOTS).index(sid)
        t1 = time.time()
        img = pipe(SHOTS[sid], negative_prompt=NEG, width=w, height=h, num_inference_steps=30, guidance_scale=5.5,
                   generator=torch.Generator('cpu').manual_seed(seed)).images[0]
        p = f'{OUT}/{sid}-seed{seed}.png'
        img.save(p)
        log.append({'shot': sid, 'seed': seed, 'secs': round(time.time() - t1, 1), 'file': p})
        print(log[-1], flush=True)
json.dump({'total_min': round((time.time() - t0) / 60, 1), 'images': log}, open(f'{OUT}/log-{int(t0)}.json', 'w'), indent=1)
