# Builds render/<track>/index.html from the shared spine + tracks/<track>/status.json, then (optionally) renders it.
# usage: python3 build.py <track> [--render]
import json, os, shutil, subprocess, sys, time
L = os.path.dirname(os.path.abspath(__file__))
track = sys.argv[1]
T = json.load(open(f'{L}/spine/timing.json'))
st = json.load(open(f'{L}/tracks/{track}/status.json'))
out = f'{L}/render/{track}'
shutil.rmtree(out, ignore_errors=True)
shutil.copytree(f'{L}/spine/assets', f'{out}/assets')
os.makedirs(f'{out}/assets/bg', exist_ok=True)

def sh(*a): subprocess.check_call(a)
FIT = 'scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080'

bg = []
for s in T['shots']:
    i, d = s['id'], s['dur']
    shot = st['shots'][i]
    src = f'{L}/tracks/{track}/{shot["file"]}'
    if shot['kind'] == 'video':
        # fit to frame; stretch short clips up to 1.6x, then hold the last frame
        n = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src]))
        k = min(1.6, max(1.0, d / n))
        sh('ffmpeg', '-loglevel', 'error', '-y', '-i', src, '-an', '-vf',
           f'{FIT},setpts={k:.3f}*PTS,fps=30,tpad=stop_mode=clone:stop_duration={d}', '-t', str(d),
           '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', f'{out}/assets/bg/{i}.mp4')
        bg.append(f'<video id="bg-{i}" class="clip fill bgv" data-start="{s["start"]}" data-duration="{d}" data-track-index="0" muted playsinline src="assets/bg/{i}.mp4"></video>')
    else:
        sh('ffmpeg', '-loglevel', 'error', '-y', '-i', src, '-vf', 'scale=2112:1188:force_original_aspect_ratio=increase,crop=2112:1188', '-q:v', '2', f'{out}/assets/bg/{i}.jpg')
        bg.append(f'<div id="bg-{i}" class="clip fill" data-start="{s["start"]}" data-duration="{d}" data-track-index="0"><img id="kb-{i}" class="kb" src="assets/bg/{i}.jpg" alt=""></div>')

narr = ''
if st.get('narrator'):
    shutil.copy(f'{L}/tracks/{track}/{st["narrator"]}', f'{out}/assets/narrator.mp4')
    narr = f'<div id="nar-wrap" class="nar"><video id="nar" class="clip" data-start="0" data-duration="{T["total"]}" data-track-index="2" muted playsinline src="assets/narrator.mp4"></video></div>'

sh_ = {s['id']: s for s in T['shots']}
def at(i, off): return round(sh_[i]['start'] + off, 2)

vo = ''.join(f'<audio id="vo-{s["id"]}" class="clip" data-start="{s["vo_start"]}" data-duration="{s["vo_dur"]}" data-track-index="3" data-volume="1" src="assets/vo/{s["id"]}.wav"></audio>' for s in T['shots'])
sfx = [('s2', 1.5, 'ping', .4), ('s3', 2.6, 'notification', .45), ('s4', 3.3, 'click', .4), ('s5', 1.6, 'pop', .4)]
# music and sfx are optional (their licences don't allow redistributing the raw files)
has = lambda f: os.path.exists(f'{L}/spine/assets/{f}')
sfx = [c for c in sfx if has(f'sfx/{c[2]}.mp3')]
sfx = ''.join(f'<audio id="fx{n}" class="clip" data-start="{at(i, o)}" data-duration="1" data-track-index="{5 + n}" data-volume="{v}" src="assets/sfx/{f}.mp3"></audio>' for n, (i, o, f, v) in enumerate(sfx))

music = f'<audio id="music" class="clip" data-start="0" data-duration="{T["total"]}" data-track-index="4" data-volume="0.13" src="assets/music.mp3"></audio>' if has('music.mp3') else ''

# seeded QR (29x29 + finders)
seed = [101]
def rnd():
    seed[0] = (seed[0] * 1103515245 + 12345) % 2**31; return seed[0] / 2**31
def finder(x, y, cx, cy):
    dx, dy = x - cx, y - cy
    if dx < -1 or dx > 7 or dy < -1 or dy > 7: return None
    if dx < 0 or dx > 6 or dy < 0 or dy > 6: return False
    return max(abs(dx - 3), abs(dy - 3)) != 2
q = ''
for y in range(29):
    for x in range(29):
        v = next((f for f in (finder(x, y, a, b) for a, b in ((0, 0), (22, 0), (0, 22))) if f is not None), None)
        if v is None and (x == 6 or y == 6): v = (x + y) % 2 == 0
        if v is None: v = rnd() < 0.5
        if v: q += f'<rect x="{x}" y="{y}" width="1" height="1"/>'

html = f'''<!doctype html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=1920, height=1080">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
:root {{ --teal:#2ee6c5; --ink:#eef2f8; --mute:#9aa6bd; }}
body {{ margin:0; background:#0a0f1e; }}
#root {{ position:relative; width:1920px; height:1080px; overflow:hidden; background:#0a0f1e; font-family:Inter, sans-serif; color:var(--ink); }}
.fill {{ position:absolute; inset:0; }}
.bgv {{ width:1920px; height:1080px; object-fit:cover; }}
.kb {{ position:absolute; left:-96px; top:-54px; width:2112px; height:1188px; object-fit:cover; }}
.scrim {{ position:absolute; inset:0; background:linear-gradient(90deg, rgba(8,12,24,0) 40%, rgba(8,12,24,.55) 70%, rgba(8,12,24,.8) 100%), linear-gradient(180deg, rgba(8,12,24,.55) 0%, rgba(8,12,24,0) 18%); z-index:5; }}
.bug {{ position:absolute; left:96px; top:62px; font:700 34px Outfit, sans-serif; letter-spacing:.12em; z-index:20; text-shadow:0 2px 12px rgba(0,0,0,.6); }}
.bug b {{ color:var(--teal); }}
.tag {{ position:absolute; right:96px; top:62px; font:600 24px 'JetBrains Mono', monospace; color:#fff; background:rgba(8,12,24,.6); padding:8px 16px; border-radius:10px; z-index:20; }}
.card {{ position:absolute; right:110px; width:560px; padding:30px 34px; border-radius:24px; background:rgba(12,18,34,.82); border:1px solid rgba(255,255,255,.12); box-shadow:0 30px 80px rgba(0,0,0,.5); z-index:10; }}
.card h6 {{ margin:0; font:700 22px 'JetBrains Mono', monospace; letter-spacing:.1em; color:var(--teal); text-transform:uppercase; }}
.card h3 {{ margin:10px 0 0; font:700 40px/1.15 Outfit, sans-serif; }}
.card p {{ margin:10px 0 0; font:500 28px/1.35 Inter, sans-serif; color:#d6deec; }}
.row {{ display:flex; justify-content:space-between; font:500 28px Inter, sans-serif; padding:12px 0; border-top:1px solid rgba(255,255,255,.1); margin-top:10px; }}
.row span {{ font:600 28px 'JetBrains Mono', monospace; color:var(--teal); }}
.btn {{ display:inline-block; margin-top:20px; padding:14px 30px; border-radius:14px; background:var(--teal); color:#062a24; font:800 30px Outfit, sans-serif; }}
.qr {{ display:block; width:220px; height:220px; margin-top:18px; background:#fff; border-radius:12px; }}
.ok {{ color:var(--teal); }}
.nar {{ position:absolute; left:96px; bottom:80px; width:330px; height:330px; border-radius:50%; overflow:hidden; border:5px solid var(--teal); box-shadow:0 20px 60px rgba(0,0,0,.6); z-index:15; }}
.nar video {{ width:100%; height:100%; object-fit:cover; }}
.end {{ position:absolute; left:0; right:0; top:420px; text-align:center; z-index:12; }}
.end .w {{ font:700 140px/1 Outfit, sans-serif; letter-spacing:.08em; text-shadow:0 10px 40px rgba(0,0,0,.6); }}
.end .w b {{ color:var(--teal); }}
.end .t {{ font:600 56px Outfit, sans-serif; margin-top:20px; text-shadow:0 6px 30px rgba(0,0,0,.6); }}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{T["total"]}" data-width="1920" data-height="1080">
{chr(10).join(bg)}
<div class="scrim"></div>
<div class="bug"><b>T</b>RINEXA</div>
<div class="tag">{st.get("label", track)}</div>
{narr}
<div id="o1" class="card" style="top:250px"><h6>Call letter</h6><h3>#101 · Aarav Mehta</h3><p>Sat 14 Dec · 09:00 · Tower B</p><svg class="qr" viewBox="-2 -2 33 33" shape-rendering="crispEdges"><g fill="#111">{q}</g></svg></div>
<div id="o2" class="card" style="top:330px"><h6>Reception · scan</h6><h3 class="ok">✓ Verified</h3><div class="row">#101 Aarav Mehta <span>08:52</span></div><div class="row">Status <span>checked in</span></div></div>
<div id="o3" class="card" style="top:300px"><h6>Trinexa · now</h6><h3>Please proceed to Room 4</h3><p>Round 1 · Technical<br>Panel: Neha S., Vikram R.</p></div>
<div id="o4" class="card" style="top:280px"><h6>Room 4 · scorecard</h6><div class="row">Problem solving <span>4 / 5</span></div><div class="row">APIs &amp; SQL <span>4 / 5</span></div><div class="row">Communication <span>5 / 5</span></div><div id="o4b" class="btn">Select</div></div>
<div id="o5" class="card" style="top:300px"><h6>Webhook · signed</h6><h3>#101 → Client HR system</h3><div class="row">Interview status <span>cleared</span></div><div class="row">Sync <span class="ok">✓ delivered</span></div></div>
<div id="end" class="end"><div class="w"><b>T</b>RINEXA</div><div class="t">Save Your Saturdays.</div></div>
{vo}
{music}
{sfx}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(f'tl.fromTo("#kb-{s["id"]}", {{ scale: 1 }}, {{ scale: 1.07, duration: {s["dur"]}, ease: "none" }}, {s["start"]});' for s in T['shots'] if st['shots'][s['id']]['kind'] != 'video')}
const IN = (sel, t) => tl.fromTo(sel, {{ opacity: 0, x: 60, filter: "blur(8px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.5, ease: "expo.out" }}, t);
const OUT = (sel, t) => tl.to(sel, {{ opacity: 0, x: 40, duration: 0.25, ease: "power3.in" }}, t);
IN("#o1", {at('s1', 1.6)}); OUT("#o1", {at('s1', 6.2)});
IN("#o2", {at('s2', 1.5)}); OUT("#o2", {at('s2', 5.0)});
IN("#o3", {at('s3', 2.6)}); OUT("#o3", {at('s3', 6.2)});
IN("#o4", {at('s4', 1.4)}); OUT("#o4", {at('s4', 5.4)});
tl.fromTo("#o4b", {{ scale: 1 }}, {{ scale: 0.94, duration: 0.1, yoyo: true, repeat: 1, immediateRender: false }}, {at('s4', 3.3)});
IN("#o5", {at('s5', 1.6)}); OUT("#o5", {at('s5', 3.9)});
tl.fromTo("#end", {{ opacity: 0, filter: "blur(10px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.5, ease: "power4.out" }}, {at('s5', 4.1)});
window.__timelines["main"] = tl;
</script></body></html>'''
open(f'{out}/index.html', 'w').write(html)
print('built', out)

if '--render' in sys.argv:
    t0 = time.time()
    r = subprocess.run(['npx', 'hyperframes', 'render', '--quality', 'high', '--output', f'{L}/results/{track}.mp4'], cwd=out, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    open(f'{out}/render.log', 'w').write(r.stdout + r.stderr)
    print('render exit', r.returncode, round(time.time() - t0), 's')
    if r.returncode == 0:
        os.makedirs(f'{L}/results/thumbs', exist_ok=True)
        for s in T['shots']:
            sh('ffmpeg', '-loglevel', 'error', '-y', '-ss', str(s['start'] + s['dur'] * 0.55), '-i', f'{L}/results/{track}.mp4',
               '-frames:v', '1', '-vf', 'scale=480:-1', '-q:v', '3', f'{L}/results/thumbs/{track}-{s["id"]}.jpg')
        st['version'] = int(time.time())
        json.dump(st, open(f'{L}/tracks/{track}/status.json', 'w'), indent=1)
    sys.exit(r.returncode)
