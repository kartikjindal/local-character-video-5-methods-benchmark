# Track 3: animate the track-2 stills with LTX-Video 0.9.5 (2B) image-to-video on the Mac GPU.
# usage: .venv-ai/bin/python gen_video.py [shot ids...] [--frames 97] [--steps 30] [--smoke]
import json, os, sys, time
os.environ.setdefault('PYTORCH_ENABLE_MPS_FALLBACK', '1')
import torch
from PIL import Image
from diffusers import LTXImageToVideoPipeline
from diffusers.utils import export_to_video
from transformers import T5EncoderModel

L = os.path.dirname(os.path.abspath(__file__))
OUT = f'{L}/tracks/aivideo'
os.makedirs(OUT, exist_ok=True)
arg = lambda k, d: int(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
FRAMES, STEPS = arg('--frames', 97), arg('--steps', 30)
W, H = 768, 448
MOTION = {
    's1': 'A young Indian man in a navy blazer sits on a sofa, looks down at his smartphone and slowly smiles, small natural head movement, soft morning light, static camera, realistic video',
    's2': 'At a busy office reception, a young Indian man holds out his phone, the receptionist scans it, people walk past in the background, slow camera push in, realistic video',
    's3': 'In an office waiting lounge, a young Indian man looks down at his phone as it buzzes, other candidates shift slightly around him, gentle camera drift, realistic video',
    's4': 'In a glass meeting room, two interviewers talk and nod while the young Indian candidate answers and gestures with his hands, subtle camera movement, realistic video',
    's5': 'A young Indian man in a navy blazer walks out of a glass office building toward the camera in daylight, smiling, the camera slowly tracks back, realistic video',
}
NEG = 'worst quality, inconsistent motion, blurry, jittery, distorted, deformed face, warped hands, morphing'
ids = [a for a in sys.argv[1:] if a in MOTION] or list(MOTION)

t0 = time.time()
pipe = LTXImageToVideoPipeline.from_pretrained('Lightricks/LTX-Video-0.9.5', text_encoder=None, torch_dtype=torch.float32)
# encode every prompt once on the CPU, then drop the 19 GB T5 so the GPU run doesn't swap
pipe.text_encoder = T5EncoderModel.from_pretrained('city96/t5-v1_1-xxl-encoder-bf16', torch_dtype=torch.float32)
emb = {}
with torch.no_grad():
    for sid in ids:
        emb[sid] = pipe.encode_prompt(MOTION[sid], NEG, do_classifier_free_guidance=True, device='cpu')
pipe.text_encoder = None
import gc; gc.collect()
pipe.to('mps')
pipe.vae.enable_tiling()
log = []
for sid in ids:
    img = Image.open(f'{L}/tracks/aistill/{sid}.png').convert('RGB').resize((W, H), Image.LANCZOS)
    t1 = time.time()
    pe, pm, ne, nm = (t.to('mps') for t in emb[sid])
    frames = pipe(image=img, prompt_embeds=pe, prompt_attention_mask=pm, negative_prompt_embeds=ne, negative_prompt_attention_mask=nm, width=W, height=H, num_frames=FRAMES,
                  num_inference_steps=STEPS, guidance_scale=3.0, generator=torch.Generator('mps').manual_seed(42)).frames[0]
    name = f'{sid}-smoke.mp4' if '--smoke' in sys.argv else f'{sid}.mp4'
    export_to_video(frames, f'{OUT}/{name}', fps=24)
    log.append({'shot': sid, 'secs': round(time.time() - t1, 1), 'frames': FRAMES, 'steps': STEPS, 'file': name})
    print(log[-1], flush=True)
json.dump({'total_min': round((time.time() - t0) / 60, 1), 'clips': log}, open(f'{OUT}/log-{int(t0)}.json', 'w'), indent=1)
