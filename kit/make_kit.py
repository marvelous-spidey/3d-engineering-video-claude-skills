"""Build explainer_kit.py from the proven video #1 script (helpers are copied verbatim, scene-specific parts are left out)."""
import re, sys
src = open(sys.argv[1], encoding='utf8').read().split('\n')
def at(marker, start=0):
    return next(i for i in range(start, len(src)) if marker in src[i])
a0 = at('================ animation helpers'); a1 = at('================ materials')
b0 = at('def soil_material():'); b1 = at('M_soil = soil_material()')
c0 = at('================ world + light'); c1 = at('================ cues')
d0 = at('================ camera moves'); d1 = at('HERO_A = ')
e0 = at('================ render') + 1
base = [l for l in src if re.match(r"M_(pvc|bore|white|yellow|plate|ink|wood|sign|conc|steel|skin|vest|stripe|helmet|pants) = ", l)]
head = '''"""explainer_kit.py - shared helpers for code-built 3D explainer shorts (Blender 5.3 as the bpy module).

Use it with exec(): the scene script first defines FPS, DUR, OFFSET and WORDS ([[sentence_id, word, start, end], ...],
voice-over time in seconds), then runs  exec(open('explainer_kit.py').read()).  After building the scene it calls render_main().

  python scene.py still <rx> <ry> <spp> <out_dir> <t1> <t2> ...     (times in seconds)
  python scene.py anim  <rx> <ry> <spp> <out_dir> <f0> <f1> [step]  (frames, 1-based; skips files that exist)
  python scene.py blend <rx> <ry> <spp> <out.blend>
  python scene.py list  <rx> <ry> <spp> <out_dir> <frames.txt> [k0] [step]   (re-render listed frames, overwriting)
Env: KIT_DEVICE=CPU|GPU, KIT_FMT=PNG|JPEG, KIT_PERSIST=0|1 (persistent data; default 0), SEPTIC_FONT=<path to a .ttf/.otf for in-scene text>.
Helpers copied from video #1 (septic_video.py); see pipeline-runbook.md for what each one does.
"""
import bpy, bmesh, math, random, sys, time, os
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
MODE = argv[0]; RX, RY, SPP = int(argv[1]), int(argv[2]), int(argv[3]); OUT = argv[4]; REST = argv[5:]
DEVICE = os.environ.get('KIT_DEVICE', os.environ.get('SEPTIC_DEVICE', 'CPU'))
LAST = int(round(DUR * FPS)); ASPECT = 1080 / 1920
def fr(t): return t * FPS + 1.0

def _nw(w): return ''.join(ch for ch in w.lower() if ch.isalpha())
def T(sid, word=None, nth=1, end=False):
    """Video time (s) of a sentence (start, or end with end=True) or of the nth `word` inside it. Cues stay valid when the script is re-timed."""
    ws = [w for w in WORDS if w[0] == sid]
    if word is not None: ws = [[w for w in ws if _nw(w[1]) == _nw(word)][nth - 1]]
    return (ws[-1][3] if end else ws[0][2]) + OFFSET

random.seed(11)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; col = sc.collection
Z = (0.001, 0.001, 0.001)
'''
render = ['def render_main():', '    """Set up Cycles and run the mode given on the command line. Call it once the scene is built."""'] + ['    ' + l if l.strip() else '' for l in src[e0:]]
render = [l.replace("os.environ.get('SEPTIC_FMT', 'PNG')", "os.environ.get('KIT_FMT', os.environ.get('SEPTIC_FMT', 'PNG'))") for l in render]
render = '\n'.join(render)
# video #2: with persistent data, Cycles kept stale geometry for animated objects in some render processes (parts rendered black or
# lagged for a frame). Off by default; the full scene is synced for every frame, which cost about 20% more time on an L40S.
_a = "    sc.render.use_persistent_data = True\n"; assert render.count(_a) == 1
render = render.replace(_a, "    sc.render.use_persistent_data = os.environ.get('KIT_PERSIST', '0') == '1'      # off by default: stale-state glitches in multi-process renders (video #2)\n")
_c = "    elif MODE == 'blend':\n"; assert render.count(_c) == 1
render = render.replace(_c, """    elif MODE == 'list':                                        # list <rx> <ry> <spp> <out_dir> <file with frame numbers> [k0] [step]: (re)render those frames, overwriting
        os.makedirs(OUT, exist_ok=True); fl = [int(v) for v in open(REST[0]).read().split()]; n = 0
        k0 = int(REST[1]) if len(REST) > 1 else 0; kn = int(REST[2]) if len(REST) > 2 else 1
        for f in fl[k0::kn]:
            path = os.path.join(OUT, f'f_{f:05d}.{EXT}'); tf = time.time(); sc.frame_set(f); sc.render.filepath = path
            bpy.ops.render.render(write_still=True); n += 1
            if n % 10 == 1: print(f'FRAME {f} {time.time() - tf:.2f}s', flush=True)
        print(f'LIST: {n} frames in {time.time() - t_all:.1f}s', flush=True)
""" + _c)
render = render.split('\n')
parts = [head] + src[a0:a1] + ['# base materials used by the helpers'] + base + [''] + src[b0:b1] + ['M_soil = soil_material(); M_grass = grass_material(); M_gravel = gravel_material()', ''] + src[c0:c1] + src[d0:d1] + [''] + render
open(sys.argv[2], 'w', encoding='utf8').write('\n'.join(parts).rstrip() + '\n')
print('kit lines:', sum(p.count('\n') + 1 for p in parts), '| base materials:', len(base))
