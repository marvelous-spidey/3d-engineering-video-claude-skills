"""scene_check.py - build a scene without rendering and print what stills cannot show. Free, runs on CPU in a few seconds.
  python3 scene_check.py <scene.py>

1. size: objects, materials, keyframes
2. camera: the largest step per frame and the largest change of step. One frame with a much larger step than both neighbours is a jump
   (expected at a hard cut, a bug anywhere else).
3. things fixed to the screen (children of the camera: counters, dials, titles): when each one is visible. COMES BACK means it is
   visible in more than one stretch, usually a pop() whose last key lies after the vanish() that should have removed it.
   STAYS TO THE END is fine only for the closing card.
4. flashes: objects whose size peaks for one or two frames (explosions, sparks). Preview each kind at its peak second, at full size:
   a still taken a few frames away shows the dim phase and hides a flash that is too large.
"""
import os, sys
_scene = os.path.abspath(sys.argv[1]); __file__ = _scene
sys.argv = [_scene, 'none', '270', '480', '4', '/tmp/scene_check']
exec(open(_scene, encoding='utf8').read())
_NF = int(round(DUR * FPS))
def _curves(o, path): return sorted((c for c in fcurves_of(o) if c.data_path == path), key=lambda c: c.array_index)
def _sec(f): return round((f - 1) / FPS, 2)
print('\n== scene_check:', os.path.basename(_scene), f'{DUR:.2f} s, {_NF} frames')
_ids = list(bpy.data.objects) + [m.node_tree for m in bpy.data.materials if m.node_tree]
print('1. objects', len(bpy.data.objects), '| materials', len(bpy.data.materials), '| keyframes', sum(len(c.keyframe_points) for i in _ids for c in fcurves_of(i)))
_cc = _curves(cam, 'location')
if len(_cc) == 3:
    _p = [Vector([c.evaluate(f) for c in _cc]) for f in range(1, _NF + 1)]; _st = [(_p[i + 1] - _p[i]).length for i in range(_NF - 1)]
    _top = sorted(range(len(_st)), key=lambda i: -_st[i])[:5]
    print('2. camera: largest steps (units per frame, second):', [(round(_st[i], 3), _sec(i + 1)) for i in _top])
    _jump = [i for i in range(1, len(_st) - 1) if _st[i] > 0.02 and _st[i] > 4 * max(_st[i - 1], _st[i + 1], 1e-4)]
    print('   single-frame jumps (fine at a hard cut):', [(_sec(i + 1), round(_st[i], 2)) for i in _jump] or 'none')
else: print('2. camera: location is not animated')
def _runs(vis):
    out = []
    for f, v in enumerate(vis, 1):
        if v and out and out[-1][1] == f - 1: out[-1][1] = f
        elif v: out.append([f, f])
    return out
_hud = sorted((o for o in bpy.data.objects if o.parent == cam and _curves(o, 'scale')), key=lambda o: o.name)
print('3. fixed to the screen:', len(_hud), 'animated children of the camera')
for o in _hud:
    cs = _curves(o, 'scale'); r = _runs([min(abs(c.evaluate(f)) for c in cs) > 0.01 for f in range(1, _NF + 1)])
    if not r: print(f'   {o.name:20s} never visible'); continue
    note = ('COMES BACK ' if len(r) > 1 else '') + ('STAYS TO THE END' if r[-1][1] >= _NF else '')
    print(f'   {o.name:20s} ' + ', '.join(f'{_sec(a):.2f}-{_sec(b):.2f}s' for a, b in r[:4]) + (' ...' if len(r) > 4 else '') + '  ' + (note or 'ok'))
_fl = {}
for o in bpy.data.objects:
    cs = _curves(o, 'scale')
    if not cs or max(len(c.keyframe_points) for c in cs) < 4: continue
    s = [max(abs(c.evaluate(f)) for c in cs) for f in range(1, _NF + 1)]
    pk = [f for f in range(3, _NF - 2) if s[f] > 0.05 and s[f] >= s[f - 1] and s[f] >= s[f + 1] and s[f] > 2.0 * max(s[f - 2], s[f + 2])]
    if pk: _fl[o.name] = [(f + 1, s[f]) for f in pk]
print('4. flashes (size peaks for 1-2 frames):', len(_fl), 'objects')
_grp = {}
for n, pk in _fl.items(): _grp.setdefault(n.rstrip('0123456789_.'), []).append((n, pk))
for g, items in sorted(_grp.items()):
    n, pk = max(items, key=lambda it: max(v for _, v in it[1])); f, v = max(pk, key=lambda q: q[1])
    print(f'   {g:20s} {len(items)} objects, {sum(len(p) for _, p in items)} peaks; largest: {n} scale {v:.2f} at {_sec(f):.2f}s (frame {f})')
if _fl: print('   -> take a full-size still at each of those seconds before renting the GPU')
