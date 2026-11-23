"""Build the scene without rendering and check the things a still cannot show: camera steps, mechanical clearances, part switches."""
import sys, os
sys.argv = ['engine_video.py', 'none', '405', '720', '8', 'st']
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'engine_video.py'), encoding='utf8').read())
def fcv(o, path, idx, f):
    for c in fcurves_of(o):
        if c.data_path == path and c.array_index == idx: return c.evaluate(f)
    return getattr(o, path)[idx]
# 1. camera: step per frame
steps = []
for f in range(1, NF):
    a = Vector([fcv(cam, 'location', i, f) for i in range(3)]); b = Vector([fcv(cam, 'location', i, f + 1) for i in range(3)])
    steps.append(((b - a).length, f))
big = sorted(steps, reverse=True)[:6]
print('camera: largest steps per frame (units, frame, s):', [(round(d, 2), f, round((f - 1) / FPS, 2)) for d, f in big])
jerk = [(abs(steps[i + 1][0] - steps[i][0]), steps[i][1]) for i in range(len(steps) - 1)]
print('camera: largest change of step between frames:', [(round(d, 2), f, round((f - 1) / FPS, 2)) for d, f in sorted(jerk, reverse=True)[:6]])
# 2. mechanics
print('piston crown: highest %.3f (deck %.2f), lowest skirt %.3f (crankcase roof 1.24)' % (max(max(v) for v in pz) + 0.30, DECK, min(min(v) for v in pz) - 0.26))
for i in range(4):
    for s_ in (-1, 1):
        cl = [(vz[(i, s_)][f] - (pz[i][f] + 0.30), f) for f in range(NF)]; m = min(cl)
        hit = [f for c, f in cl if c < 0]
        print(f'  cyl {i + 1} {"exhaust" if s_ == 1 else "intake "}: smallest valve-to-piston gap {m[0]:+.3f} at {m[1] / FPS:.2f}s' + (f'; touching {hit[0] / FPS:.2f}-{hit[-1] / FPS:.2f}s' if hit else ''))
print('cue: valve strike at %.2fs, spark at %.2fs' % (t_hit, t_hit))
rev = [(TH[f] - TH[f - 1]) / (2 * PI) * FPS for f in range(1, NF + 1)]
print('engine speed on screen: max %.2f rev/s, min %.2f; backwards frames: %d' % (max(rev), min(rev), sum(1 for r in rev if r < -1e-6)))
for name, t in (('idle', 3.0), ('boost', 16.0), ('stopped (repair)', 20.5), ('stall', 35.5), ('9000', 45.5), ('slow motion', 47.3), ('after strike', 48.6), ('knock', 58.0), ('full', 66.5), ('end', 74.5)):
    print(f'   {name:18s} {t:5.1f}s  {rev[int(t * FPS)]:.2f} rev/s')
# 3. who is on the engine when
def on(o, t): f = fr(t); return all(abs(fcv(o, 'scale', i, f)) > 0.5 for i in range(3))
def at(o, t): f = fr(t); return tuple(round(fcv(o, 'location', i, f), 2) for i in range(3))
for t in (5.0, 19.0, 21.5, 24.0, 24.9, 27.0, 30.9, 33.0, 38.0, 40.0, 50.0, 56.0, 62.5, 70.0):
    print(f'  {t:5.1f}s stock piston {on(P_stock[0], t)!s:5} forged {on(P_forged[0], t)!s:5} bolts {on(bolts[0], t)!s:5} studs {on(studs[0], t)!s:5} sleeves {on(sleeves[0], t)!s:5} headA z {at(HA["root"], t)[1:]}  headB {at(HB["root"], t)[1:]} boost {at(BOOST, t)[1:]} IC {on(IC, t)!s:5} cart {on(E85, t)}')
# 4. HUD timetable
print('objects', len(bpy.data.objects), 'materials', len(bpy.data.materials), 'fcurve keys', sum(len(c.keyframe_points) for o in list(bpy.data.objects) + [m.node_tree for m in bpy.data.materials if m.node_tree] for c in fcurves_of(o)))
# 5. screen-fixed labels: when is each one visible? A label that never goes away, or comes back, shows up here (pop() and vanish() keys in the wrong order)
def sc_at(o, f): return [c.evaluate(f) for c in fcurves_of(o) if c.data_path == 'scale'][:1]
for o in sorted([o for o in bpy.data.objects if o.name.startswith('HUD_') and o.parent == cam], key=lambda o: o.name):
    on = [f for f in range(1, NF + 1) if sc_at(o, f) and sc_at(o, f)[0] > 0.01]
    if on: print(f'  {o.name:14s} visible {(on[0] - 1) / FPS:6.2f}-{(on[-1] - 1) / FPS:6.2f}s', 'ok' if len(on) == on[-1] - on[0] + 1 else 'COMES BACK', '' if on[-1] < NF or o.name in ('HUD_final', 'HUD_x6') else 'NEVER LEAVES')
