"""Cara kerja kolam renang (ID, 9:16, 68.4 s) - example job for kit v1.0. Scene and animation are built from code; every cue follows
the voice-over word timings in words.json, so re-timing the narration moves the animation with it.

Make a runnable job folder first (copies the kit code next to this script):   bash kit/newjob.sh examples/video02-swimming-pool-id
  python3 pool_video.py still 270 480 4 out_dir 3.6 27.2 47.6     quick stills at those seconds (CPU)
  python3 pool_video.py anim 1080 1920 64 frames 1 2052 [step]    all frames (box/render.sh calls this)
  python3 pool_video.py blend 1080 1920 64 pool.blend             save the scene for Blender
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from kitjob import FPS, OFFSET, WORDS, DUR                     # job.env + words.json (TAIL=1.62 -> 68.4 s)
exec(open(os.path.join(HERE, 'explainer_kit.py'), encoding='utf8').read())
exec(open(os.path.join(HERE, 'scene_extras.py'), encoding='utf8').read())
rnd = random.Random(7)

# ================================================================ scene helpers
orbit = hero_pose                                                         # orbit(azimuth, elevation, distance, target); azimuth 90 = straight on

# ================================================================ materials
M_arrow = new_mat('arrow', (1.0, 1.0, 1.0), 0.5, emit=0.9)
M_dirt = new_mat('dirt', (0.22, 0.10, 0.05), 0.97); M_mud = new_mat('mud', (0.17, 0.10, 0.05), 0.45, spec=0.5)
M_wet = new_mat('wet_soil', (0.05, 0.032, 0.022), 0.5, spec=0.4, alpha=0.0)
M_hose = new_mat('hose', (0.10, 0.48, 0.26), 0.6); M_stream = new_mat('stream', (0.45, 0.80, 1.0), 0.2, emit=0.7)
M_duck = new_mat('duck', (1.0, 0.78, 0.04), 0.35, spec=0.5); M_beak = new_mat('beak', (1.0, 0.36, 0.04), 0.5)
M_rebar = new_mat('rebar', (0.62, 0.20, 0.09), 0.55, spec=0.4); M_shell = new_mat('shell', (0.54, 0.54, 0.52), 0.92)
M_wetconc = new_mat('wet_concrete', (0.50, 0.50, 0.49), 0.5, emit=0.05)
M_deck = new_mat('deck', (0.83, 0.76, 0.63), 0.85); M_housewall = new_mat('house_wall', (0.94, 0.89, 0.78), 0.9)
M_roof = new_mat('roof', (0.70, 0.25, 0.11), 0.8); M_window = new_mat('window', (0.50, 0.75, 0.95), 0.2, emit=0.25)
M_fence = new_mat('fence', (0.90, 0.90, 0.86), 0.9); M_trunk = new_mat('trunk', (0.30, 0.21, 0.14), 0.95)
M_leaf = new_mat('leaf', (0.20, 0.38, 0.13), 0.95); M_palm = new_mat('palm', (0.24, 0.47, 0.14), 0.8)
M_water0 = water_material('water_hole', (0.12, 0.52, 0.82), 0.66)         # water in the bare hole (turns to mud)
M_water = water_material('water_pool', (0.10, 0.55, 0.85), 0.60)          # water in the finished shell

# ================================================================ pool geometry (metres; the cut face is y = 0)
X0, X1, Y1 = -4.0, 4.0, 4.0                    # inner faces: 8 m long, 4 m wide (the front wall is cut away)
ZS, ZD, TH, WL = -1.2, -1.8, 0.22, -0.14       # floor at the shallow / deep end, shell thickness, water level (mean depth 1.5 m -> 48 m3)
def zf(x): return ZS + (ZD - ZS) * (x - X0) / (X1 - X0)      # inner floor height
def zo(x): return zf(x) - TH                                # underside of the shell
XA, XB, YB = X0 - TH, X1 + TH, Y1 + TH                       # outer faces
CAV = [(XA, 0.5), (XA, zo(XA)), (XB, zo(XB)), (XB, 0.5)]     # excavation profile

soil = box('ENV_soil', -150, 150, 0.0, 400.0, -90.0, 0.0, M_soil)
cutter = prism('cutter', CAV, -0.5, YB, M_conc)
mod = soil.modifiers.new('cut', 'BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.object = cutter; mod.solver = 'EXACT'
bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(soil.evaluated_get(dg)); soil.modifiers.clear(); soil.data = me
bpy.data.objects.remove(cutter, do_unlink=True)

# ================================================================ cues (seconds of video time, looked up by sentence and word)
T_DIG0 = 0.42; T_DIG1 = T('S01', 'halaman') + 0.25; T_FILL0 = T('S01', 'isi'); T_FILL1 = T('S01', 'air', end=True) + 0.1
T_YAY = T('S01', 'selamat'); T_BUT = T('S02'); T_SEEP = T('S02', 'airnya'); T_FALL = T('S02', 'dindingnya'); T_MUD = T('S02', 'lumpur', end=True)
T_FIX = T('S03'); T_RB0 = T('S03', 'besi'); T_RB1 = T('S03', 'keranjang', end=True) + 0.15; T_POUR = T('S03', 'dicor') - 0.1
T_BOWL = T('S03', 'Jadilah'); T_STRONG = T('S04'); T_TON = T('S04', 'lima'); T_DAYS = T('S05'); T_GREEN = T('S05', 'airnya'); T_ALGAE = T('S05', 'Ganggang')
T_MOVE = T('S06'); T_PUMP = T('S06', 'Pompa'); T_SAND = T('S06', 'pasir'); T_STUCK = T('S06', 'kotoran'); T_PASS = T('S06', 'air'); T_FILTER = T('S06', 'Itulah')
T_GERM = T('S08'); T_SMALL = T('S08', 'kecil'); T_GROW = T('S08', 'dan'); T_THEM = T('S08', 'Untuk'); T_CHEM = T('S08', 'kimia'); T_KAP = T('S08', 'sedikit')
T_SMELL = T('S09'); T_DIRTY = T('S09', 'Justru'); T_REACT = T('S09', 'bereaksi'); T_SWEAT = T('S09', 'keringat'); T_PEE = T('S09', 'pipis')
T_TRAP = T('S10'); T_DRAIN = T('S10', 'kuras') - 0.25; T_BALLAST = T('S10', 'Lima'); T_GONE = T('S10', 'hilang'); T_GW = T('S10', 'kalau')
T_LIFT = T('S10', 'terdorong'); T_UP = T('S10', 'naik'); T_LIKE = T('S10', 'seperti'); T_PUSH = T('S10', 'ditekan'); T_TUB = T('S10', 'mandi')
T_ODD = T('S11'); T_LEAK = T('S11', 'sengaja'); T_VALVE = T('S11', 'Katup'); T_OPEN = T('S11', 'membuka'); T_PRESS = T('S11', 'menekan')
T_IN = T('S11', 'air', 2); T_SAFE = T('S11', 'selamat'); T_NAME = T('S11', 'Namanya'); T_TILE = T('S12', 'keramik') - 0.15; T_LAMP = T('S12', 'lampu')
T_DUCK = T('S12', 'bebek'); T_NOW = T('S12', 'Sekarang'); T_END = T('S12', 'selamat'); T_SPLASH = T('S12', 'renang')

# ================================================================ backyard
GX = XB + 0.55; GY = YB + 0.55                                             # outer edge of the ring around the pool
box('ENV_lawn_L', -60, -GX, 0.0, 22.0, 0.0, 0.012, M_grass); box('ENV_lawn_R', GX, 60, 0.0, 22.0, 0.0, 0.012, M_grass)
box('ENV_lawn_B', -GX, GX, GY, 22.0, 0.0, 0.012, M_grass)
edge_l = hinge('EDGE_l', -GX, XA, 0.0, GY, 0.0, 0.012, M_grass, (-GX, 0, 0)); edge_r = hinge('EDGE_r', XB, GX, 0.0, GY, 0.0, 0.012, M_grass, (GX, 0, 0))
edge_b = hinge('EDGE_b', XA, XB, YB, GY, 0.0, 0.012, M_grass, (0, GY, 0))
HX0, HX1, HY0, HY1, HH = -9.0, 4.5, 12.0, 19.0, 3.1                         # house: single storey, ridge parallel to the cut face
box('HOUSE_body', HX0, HX1, HY0, HY1, 0.0, HH, M_housewall); box('HOUSE_plinth', HX0 - 0.1, HX1 + 0.1, HY0 - 0.1, HY1, 0.0, 0.45, M_deck)
ym = (HY0 + HY1) / 2; rl = math.hypot(ym - HY0 + 1.0, 2.3); ra = math.atan2(2.3, ym - HY0 + 1.0)
for sgn, nm in ((1, 'front'), (-1, 'back')):
    r_ = box('HOUSE_roof_' + nm, HX0 - 0.8, HX1 + 0.8, -rl / 2, rl / 2, -0.09, 0.09, M_roof, origin='center')
    r_.location = ((HX0 + HX1) / 2, ym - sgn * (ym - HY0 + 1.0) / 2, HH - 0.1 + 1.15); r_.rotation_euler = (sgn * ra, 0, 0)
for xs in (HX0, HX1 - 0.25): prism_yz('HOUSE_gable', [(HY0, HH), (HY1, HH), (ym, HH + 2.2)], xs, xs + 0.25, M_housewall)
box('HOUSE_terrace', -6.5, 1.5, HY0 - 2.8, HY0, 0.0, 0.30, M_deck)
tr = box('HOUSE_terrace_roof', -6.9, 1.9, -1.7, 1.7, -0.07, 0.07, M_roof, origin='center'); tr.location = (-2.5, HY0 - 1.45, 2.75); tr.rotation_euler = (math.radians(12), 0, 0)
for xs in (-6.3, 1.3): box('HOUSE_post', xs - 0.09, xs + 0.09, HY0 - 2.7, HY0 - 2.52, 0.3, 2.45, M_wood)
windows = [box('HOUSE_win', xs, xs + 1.5, HY0 - 0.04, HY0, 1.0, 2.3, M_window) for xs in (-8.1, -5.4, 2.4)]
box('HOUSE_door', -1.9, -0.8, HY0 - 0.05, HY0, 0.45, 2.55, M_wood); box('HOUSE_door_glass', -3.7, -2.1, HY0 - 0.04, HY0, 0.5, 2.5, M_window)
box('ENV_fence', -60, 60, 22.0, 22.3, 0.0, 1.9, M_fence); box('ENV_fence_cap', -60, 60, 21.95, 22.35, 1.9, 2.0, M_deck)
for x, y, h, r in ((-13.5, 9.0, 3.4, 1.7), (9.5, 12.5, 3.0, 1.5), (13.0, 7.0, 3.6, 1.8), (-17, 18, 3.2, 1.6), (17, 19, 3.2, 1.6), (-24, 12, 3.8, 2.0), (24, 14, 3.5, 1.8)): tree(x, y, h, r)
for x, y in ((-30, 27), (-21, 29), (-12, 27.5), (-3, 29), (6, 27.5), (15, 29), (24, 27.5), (33, 29)): tree(x, y, 4.2, 2.3)
palm(-10.6, 10.2, 5.4, 0.6); palm(6.9, 15.5, 6.2, -0.5); palm(-7.2, 7.4, 4.3, -0.4)
for x, y in ((-6.9, 9.0), (1.9, 9.0), (-2.3, 9.05)):                                   # potted plants on the terrace edge
    cyl('POT', (x, y, 0.30), 0.22, 0.36, M_roof, seg=10, r2=0.28); sphere('POT_plant', (x, y, 0.95), 0.36, M_leaf, seg=8, smooth=False)

# ================================================================ S01-S02: the bare hole, water, seepage, collapse
ZB = zo(XB)                                                                             # lowest point of the excavation
plug = prismp('DIG_plug', [(XA, 0.0), (XA, zo(XA)), (XB, ZB), (XB, 0.0)], 0.004, YB, M_soil, pivot=(0.0, ZB))
key(plug, 'scale', T_DIG0, (1, 1, 1)); key(plug, 'scale', T_DIG1, (1, 1, 0.001), ip='CONSTANT'); key(plug, 'scale', T_DIG1 + 0.02, Z, ip='CONSTANT')
cap = box('DIG_cap', XA, XB, 0.0, YB, 0.0, 0.012, M_grass); show(cap, 0.0, T_DIG0)
mound = sphere('DIG_mound', (3.3, 6.5, 0.0), 1.25, M_dirt, sx=1.0, sy=0.9, sz=0.5, seg=10, smooth=False)
hidden_until(mound, T_DIG0); key(mound, 'scale', T_DIG0, (0.05, 0.05, 0.02)); key(mound, 'scale', T_DIG1, (1.0, 0.9, 0.5)); vanish(mound, T_BOWL + 0.2, 0.3)
lvl0 = level_box('LVL_hole', -6.0); water0 = water_body('WATER_hole', [(XA, 0.0), (XA, zo(XA)), (XB, ZB), (XB, 0.0)], 0.0, YB, M_water0, lvl0)
Z_PUD = ZB + 0.30
level(lvl0, [(T_FILL0, ZB - 0.05), (T_FILL1, -0.16), (T_BUT + 0.2, -0.16), (T_FALL, -1.15), (T_MUD, Z_PUD), (T_FIX, Z_PUD), (T_FIX + 0.4, ZB - 0.3)])
tint(M_water0, [(T_BUT, (0.12, 0.52, 0.82), 0.66), (T_FALL + 0.5, (0.30, 0.22, 0.12), 0.90)])
hose = tube('HOSE', smooth_path([(-2.6, 11.6, 0.5), (-2.9, 10.2, 0.06), (-1.2, 8.3, 0.05), (-2.6, 6.4, 0.05), (-1.4, 5.0, 0.05), (-1.5, 4.5, 0.32), (-1.5, 4.1, 0.34)], 6), 0.045, M_hose, res=3)
vanish(hose, T_BOWL, 0.3)
stream = tube('HOSE_stream', smooth_path([(-1.5, 4.1, 0.34), (-1.5, 3.7, 0.25), (-1.5, 3.4, -0.3), (-1.5, 3.25, -1.2)], 5), 0.05, M_stream, res=3); show(stream, T_FILL0 - 0.1, T_FILL1 + 0.15)
duck = empty('DUCK', (1.2, 1.6, -0.16))
sphere('DUCK_body', (0, 0, 0.07), 0.20, M_duck, sx=1.25, sy=0.9, sz=0.8, parent=duck); sphere('DUCK_head', (-0.19, 0, 0.30), 0.125, M_duck, parent=duck)
cyl('DUCK_beak', (-0.29, 0, 0.29), 0.05, 0.11, M_beak, seg=8, r2=0.01, parent=duck).rotation_euler = (0, math.radians(-90), 0)
for sy in (-0.07, 0.07): sphere('DUCK_eye', (-0.27, sy, 0.35), 0.022, M_ink, seg=6, parent=duck)
hidden_until(duck, T_YAY); key(duck, 'location', T_YAY, (1.2, 1.6, 1.3)); appear(duck, T_YAY, 0.25, s=(1, 1, 1)); key(duck, 'location', T_YAY + 0.4, (1.2, 1.6, -0.16))
for t, z in ((T_BUT + 0.2, -0.16), (T_FALL, -1.15), (T_MUD, Z_PUD)): key(duck, 'location', t, (1.2 + (2.2 if t > T_BUT + 1 else 0), 1.6, z), ip='LINEAR')
key(duck, 'rotation_euler', T_FALL, (0, 0, 0)); key(duck, 'rotation_euler', T_MUD, (math.radians(14), math.radians(-24), 0.6)); vanish(duck, T_FIX, 0.2)
stk1 = label('STK_yay', [('SELAMAT!', 0.64, M_ink)], pos=(1.3, 1.5, 2.1), plate=M_yellow, billboard=True); hidden_until(stk1, T_YAY); appear(stk1, T_YAY, 0.28, s=(1, 1, 1)); vanish(stk1, T_BUT - 0.05, 0.15)
stain = [patch('STAIN_b', [(XA, zo(XA)), (XB, ZB), (XB + 0.2, ZB - 1.3), (0.8, -3.75), (XA - 0.2, zo(XA) - 1.2)], M_wet),
         patch('STAIN_l', [(XA, -0.12), (XA, zo(XA)), (XA - 0.2, zo(XA) - 1.2), (XA - 1.35, -1.5), (XA - 1.0, -0.12)], M_wet),
         patch('STAIN_r', [(XB, -0.12), (XB + 1.1, -0.12), (XB + 1.5, -1.8), (XB + 0.2, ZB - 1.3), (XB, ZB)], M_wet)]
for s_ in stain: show(s_, T_BUT, T_POUR + 1.2)
for t, a in ((T_BUT, 0.0), (T_FALL, 0.55), (T_FIX, 0.6), (T_POUR + 1.2, 0.0)): key_input(bsdf_of(M_wet).inputs['Alpha'], t, a)
slumps = [prismp('SLUMP_l', [(XA, zo(XA)), (XA + 2.3, zo(XA + 2.3)), (XA, zo(XA) + 1.0)], 0.0, YB, M_mud, pivot=(XA, zo(XA))),
          prismp('SLUMP_r', [(XB, ZB), (XB, ZB + 1.35), (XB - 2.6, zo(XB - 2.6))], 0.0, YB, M_mud, pivot=(XB, ZB))]
sb = prism_yz('SLUMP_b', [(YB, zo(0)), (YB, zo(0) + 1.1), (YB - 2.0, zo(0))], XA, XB, M_mud, tilt=math.asin((ZS - ZD) / (X1 - X0)), pivot=(YB, zo(0))); slumps.append(sb)
for k, s_ in enumerate(slumps):
    full = tuple(s_.scale); hidden_until(s_, T_FALL); key(s_, 'scale', T_FALL + 0.12 * k, (0.03, 1, 0.03))
    key(s_, 'scale', T_FALL + 0.75 + 0.12 * k, full); key(s_, 'scale', T_FIX, full); key(s_, 'scale', T_FIX + 0.35, Z)
for e_, ax, deg in ((edge_l, 1, 34), (edge_r, 1, -34), (edge_b, 0, 30)):
    key(e_, 'rotation_euler', T_FALL, 0.0, index=ax); key(e_, 'rotation_euler', T_FALL + 0.6, math.radians(deg), index=ax)
    key(e_, 'rotation_euler', T_FIX, math.radians(deg), index=ax); key(e_, 'rotation_euler', T_FIX + 0.35, 0.0, index=ax)

# ================================================================ S03-S04: rebar cage, concrete shell, deck, water, weight
bars = []
def bar(pts): bars.append(tube('REBAR', pts, 0.024, M_rebar, res=1))
for i in range(16): x = X0 + 0.25 + 0.5 * i; bar([(x, -0.004, zf(x) - TH / 2), (x, Y1 + TH / 2, zf(x) - TH / 2)])
for y in (0.6, 1.4, 2.2, 3.0, 3.8): bar([(XA + TH / 2, y, zf(XA) - TH / 2), (XB - TH / 2, y, zf(XB) - TH / 2)])
for xw, zb, zs in ((XA + TH / 2, zf(X0), (-0.30, -0.80)), (XB - TH / 2, zf(X1), (-0.30, -0.80, -1.30))):
    for y in (0.6, 1.4, 2.2, 3.0, 3.8): bar([(xw, y, zb - TH / 2), (xw, y, -0.04)])
    for z in zs: bar([(xw, -0.004, z), (xw, Y1 + TH / 2, z)])
for i in range(8): x = X0 + 0.5 + i; bar([(x, Y1 + TH / 2, zf(x) - TH / 2), (x, Y1 + TH / 2, -0.04)])
for z in (-0.30, -0.80): bar([(XA + TH / 2, Y1 + TH / 2, z), (XB - TH / 2, Y1 + TH / 2, z)])
for k, b_ in enumerate(bars): t0 = T_RB0 + (T_RB1 - T_RB0 - 0.35) * k / (len(bars) - 1); extend(b_, t0, t0 + 0.35)
sh_floor = prismp('SHELL_floor', [(XA, zo(XA)), (XB, zo(XB)), (XB, zf(XB)), (XA, zf(XA))], 0.0, YB, M_shell, pivot=(0.0, zo(0)))
sh_l = prismp('SHELL_wall_l', [(XA, zf(XA)), (X0, zf(X0)), (X0, 0.0), (XA, 0.0)], 0.0, YB, M_shell, pivot=(XA + TH / 2, zf(X0)))
sh_r = prismp('SHELL_wall_r', [(X1, zf(X1)), (XB, zf(XB)), (XB, 0.0), (X1, 0.0)], 0.0, YB, M_shell, pivot=(XB - TH / 2, zf(XB)))
sh_b = prismp('SHELL_wall_b', [(X0, zf(X0)), (X1, zf(X1)), (X1, 0.0), (X0, 0.0)], Y1, YB, M_shell, pivot=(0.0, zf(X1)))
grow(sh_floor, T_POUR + 0.15, T_POUR + 0.65, axis=0)
for k, s_ in enumerate((sh_l, sh_r, sh_b)): grow(s_, T_POUR + 0.55 + 0.1 * k, T_POUR + 1.15 + 0.1 * k, axis=2)
boom = tube('POUR_hose', smooth_path([(13.0, 9.0, 0.3), (10.0, 7.5, 4.6), (5.0, 4.5, 4.2), (1.6, 2.4, 2.2), (1.3, 2.2, 1.0)], 6), 0.11, M_ink, res=3)
show(boom, T_POUR - 0.35, T_BOWL + 0.1)
pour = tube('POUR_stream', [(1.3, 2.2, 1.0), (1.25, 2.15, zf(1.3) + 0.05)], 0.13, M_wetconc, res=3); show(pour, T_POUR, T_POUR + 1.15)
deck = [box('DECK_l', -GX, XA, 0.0, GY, 0.0, 0.055, M_deck), box('DECK_r', XB, GX, 0.0, GY, 0.0, 0.055, M_deck), box('DECK_b', XA, XB, YB, GY, 0.0, 0.055, M_deck)]
for k, d_ in enumerate(deck): hidden_until(d_, T_BOWL); appear(d_, T_BOWL + 0.12 * k, 0.3, s=(1, 1, 1), over=1.04)
for e_ in (edge_l, edge_r, edge_b): key(e_, 'scale', T_BOWL + 0.1, (1, 1, 1), ip='CONSTANT'); key(e_, 'scale', T_BOWL + 0.12, Z, ip='CONSTANT')
POOL = empty('POOL', (XA, 0.0, zo(XA)))                                                # everything that moves when the empty shell floats
pool_parts = [sh_floor, sh_l, sh_r, sh_b] + deck + bars
lvl = level_box('LVL_pool', -6.0); water = water_body('WATER_pool', [(X0, 0.0), (X0, zf(X0)), (X1, zf(X1)), (X1, 0.0)], 0.0, Y1, M_water, lvl)
tag_ton = label('TAG_ton', [('4 × 8 m  ·  48.000 liter', 0.30, M_white), ('±48 TON', 0.58, M_yellow)], pos=(0.0, 2.0, 2.0), billboard=True)
hidden_until(tag_ton, T_TON); appear(tag_ton, T_TON, 0.3, s=(1, 1, 1)); vanish(tag_ton, T_DAYS - 0.1, 0.18)
press = [arrow('PRESS_l', (X0 + 1.5, 0.9, -0.75), (X0 + 0.12, 0.9, -0.75)), arrow('PRESS_r', (X1 - 1.6, 0.9, -1.0), (X1 - 0.12, 0.9, -1.0)),
         arrow('PRESS_d1', (-1.6, 0.9, zf(-1.6) + 1.1), (-1.6, 0.9, zf(-1.6) + 0.1)), arrow('PRESS_d2', (1.4, 0.9, zf(1.4) + 1.2), (1.4, 0.9, zf(1.4) + 0.1))]
for k, a_ in enumerate(press):
    hidden_until(a_, T_TON - 0.5); appear(a_, T_TON - 0.5 + 0.08 * k, 0.25, s=(1, 1, 1)); pulse(a_, T_TON, T_DAYS - 0.3, 0.6, 0.16, s=(1, 1, 1)); vanish(a_, T_DAYS - 0.2, 0.15)
level(lvl, [(T_STRONG + 0.1, ZD - 0.3), (T_TON + 0.25, WL)])

# ---------------------------------------------------------------- the mascot (series character): digs, cheers, despairs
mascot, arm_l, arm_r = make_char('MASCOT', (-2.6, 5.35, 0.02))
shovel = empty('SHOVEL', (0, -0.07, -0.30), parent=arm_r)
cyl('SHOVEL_handle', (0, 0, 0), 0.022, 0.95, M_wood, seg=8, down=True, parent=shovel); box('SHOVEL_blade', -0.10, 0.10, -0.012, 0.012, -1.22, -0.93, M_steel, parent=shovel)
arm(arm_r, 0.0, -110); arm(arm_r, T_DIG0, -110)
for k in range(3): arm(arm_r, T_DIG0 + 0.18 + 0.36 * k, -25); arm(arm_r, T_DIG0 + 0.36 + 0.36 * k, -95)
arm(arm_r, T_FILL0, -60); vanish(shovel, T_FILL0, 0.2); arm(arm_r, T_FILL0 + 0.3, -8); arm(arm_l, T_FILL0 + 0.3, 8)
def both(t0, t1, deg=150, dn=0.35):
    """Both arms up between t0 and t1."""
    for a, sg in ((arm_l, 1), (arm_r, -1)): arm(a, t0 - 0.02, 8 * sg); arm(a, t0 + 0.25, deg * sg); arm(a, t1, deg * sg); arm(a, t1 + dn, 8 * sg)
def one(a, t0, t1, deg, dn=0.35):
    sg = 1 if a is arm_l else -1; arm(a, t0 - 0.02, 8 * sg); arm(a, t0 + 0.25, deg * sg); arm(a, t1, deg * sg); arm(a, t1 + dn, 8 * sg)
both(T_YAY, T_BUT + 0.1); both(T_FALL + 0.3, T_FIX + 0.1, 165); one(arm_r, T_RB0, T_POUR, 70)

# ================================================================ S05-S09: green water, pump + sand filter, skimmer, germs, chlorine, smell

M_drop = new_mat('drop_clean', (0.45, 0.86, 1.0), 0.2, emit=1.0); M_drop_g = new_mat('drop_green', (0.45, 0.80, 0.25), 0.3, emit=0.8)
M_algae = new_mat('algae', (0.30, 0.75, 0.10), 0.5, emit=0.5); M_germ = new_mat('germ', (0.90, 0.20, 0.62), 0.4, emit=0.5); M_germ_s = new_mat('germ_small', (1.0, 0.15, 0.65), 0.3, emit=1.8)
M_tank = new_mat('tank', (0.10, 0.36, 0.74), 0.35, spec=0.5); M_tank_in = new_mat('tank_inside', (0.06, 0.12, 0.22), 0.6)
M_tankw = new_mat('tank_water', (0.10, 0.55, 0.85), 0.2, emit=0.15); M_sand = new_mat('sand', (0.80, 0.68, 0.42), 0.9); M_sand2 = new_mat('sand2', (0.70, 0.57, 0.33), 0.9)
M_grime = new_mat('grime', (0.26, 0.17, 0.08), 0.9); M_plastic = new_mat('plastic', (0.94, 0.95, 0.96), 0.3, spec=0.5); M_mouth = new_mat('skimmer_mouth', (0.05, 0.16, 0.30), 0.4)
M_leafs = [new_mat('leaf_a', (0.90, 0.45, 0.08), 0.7), new_mat('leaf_b', (0.86, 0.72, 0.12), 0.7), new_mat('leaf_c', (0.45, 0.62, 0.14), 0.7)]
M_stink = new_mat('stink', (0.78, 0.86, 0.20), 0.5, emit=0.9, alpha=0.85); M_pee = new_mat('pee', (1.0, 0.84, 0.05), 0.3, emit=0.9, alpha=0.72)
M_cap1 = new_mat('swim_cap1', (0.90, 0.20, 0.20), 0.4); M_cap2 = new_mat('swim_cap2', (0.20, 0.55, 0.90), 0.4); M_cap3 = new_mat('swim_cap3', (0.20, 0.72, 0.45), 0.4)
M_gran = new_mat('granule', (1.0, 1.0, 1.0), 0.4, emit=0.6)

# ---- S05: days pass, leaves land, the water turns green
days = [label('DAY_%d' % d, [('HARI %d' % d, 0.42, M_white)], pos=(-2.3, 2.0, 2.1), billboard=True) for d in (1, 3, 5)]
for k, d_ in enumerate(days): show(d_, T_DAYS + 0.34 * k, T_DAYS + 0.34 * (k + 1) if k < 2 else T_GREEN + 0.95)
GREEN, MID, BLUE = (0.17, 0.40, 0.08), (0.13, 0.46, 0.24), (0.10, 0.55, 0.85)
tint(M_water, [(T_GREEN, BLUE, 0.60), (T_GREEN + 1.0, GREEN, 0.82), (T_STUCK, GREEN, 0.82), (T_FILTER + 0.6, MID, 0.68), (T_KAP + 0.3, MID, 0.68), (T_KAP + 1.3, BLUE, 0.58)])
specks = []
for k in range(70):
    x = rnd.uniform(X0 + 0.3, X1 - 0.3); o = sphere('ALGAE', (x, rnd.uniform(0.25, 3.7), rnd.uniform(zf(x) + 0.12, WL - 0.12)), rnd.uniform(0.04, 0.075), M_algae, seg=6)
    pop(o, (T_GREEN + 0.3 + 1.9 * k / 34) if k < 35 else (T_GROW + 1.3 * (k - 35) / 34), 0.25); vanish(o, T_KAP + 0.45 + 0.012 * k, 0.15); specks.append(o)
leaves = []
for k in range(7):
    p0 = (rnd.uniform(-3.2, 2.6), rnd.uniform(0.5, 3.4), WL + 0.012); o = sphere('LEAF', (p0[0], p0[1], 2.6), 0.17, M_leafs[k % 3], sx=1.0, sy=0.55, sz=0.07, seg=8)
    o.rotation_euler = (0, 0, rnd.uniform(0, 6)); s0 = tuple(o.scale); hidden_until(o, T_DAYS); key(o, 'scale', T_DAYS + 0.1 * k, s0, ip='CONSTANT'); ta = T_MOVE + 0.35 + 0.16 * k
    travel(o, [(T_DAYS + 0.1 * k, (p0[0] - 0.5, p0[1], 2.6)), (T_DAYS + 0.1 * k + 0.55, p0), (ta, (p0[0] + 0.25, p0[1], p0[2])), (ta + 1.25, (X1 - 0.1, 0.42, WL + 0.012))])
    key(o, 'scale', ta + 1.2, s0); key(o, 'scale', ta + 1.4, Z); leaves.append(o)
one(arm_l, T_GREEN + 0.5, T_ALGAE + 1.2, 150)

# ---- S06: equipment pad, pump, sand filter (cut open), pipes, skimmer, main drain
X_DR, X_V = 3.55, 2.70; CX, ZT0, ZT1, HW, ZSAND = 7.25, 0.08, 1.56, 0.52, 0.88        # drain, valve; filter tank section
eq = [box('EQ_pad', 5.2, 8.6, 0.0, 1.8, 0.012, 0.08, M_shell), box('PUMP_base', 5.5, 6.38, 0.08, 0.55, 0.08, 0.17, M_ink)]
for nm, x, r, h, m_ in (('PUMP_motor', 5.55, 0.19, 0.55, M_ink), ('PUMP_head', 6.08, 0.25, 0.24, M_tank)):
    c_ = cyl(nm, (x, 0.30, 0.40), r, h, m_, seg=14); c_.rotation_euler = (0, math.radians(90), 0); eq.append(c_)
for k, o in enumerate(eq): pop(o, T_MOVE + 0.05 + 0.1 * k)
tank = prism('TANK_body', capsule(CX, ZT0, ZT1, HW), 0.0, 0.95, M_tank)
tank_in = patch('TANK_inside', capsule(CX, ZT0 + 0.07, ZT1 - 0.07, HW - 0.07, 0.12), M_tankw, y=-0.006)
hi = HW - 0.07
sand = patch('TANK_sand', [(CX - hi + 0.12, ZT0 + 0.07), (CX - hi, ZT0 + 0.19), (CX - hi, ZSAND), (CX + hi, ZSAND), (CX + hi, ZT0 + 0.19), (CX + hi - 0.12, ZT0 + 0.07)], M_sand2, y=-0.012)
grime = patchp('TANK_grime', [(CX - hi, ZSAND - 0.01), (CX + hi, ZSAND - 0.01), (CX + hi, ZSAND + 0.075), (CX - hi, ZSAND + 0.075)], M_grime, -0.018, (CX, ZSAND - 0.01))
grains = []
for row in range(8):
    for i in range(10):
        gx = CX - 0.405 + 0.09 * i + (0.045 if row % 2 else 0.0); gz = 0.205 + 0.088 * row
        if abs(gx - CX) < hi - 0.03: grains.append(sphere('GRAIN', (gx, -0.055, gz), rnd.uniform(0.040, 0.047), M_sand if (row + i) % 3 else M_sand2, seg=8))
coll = tube('TANK_collector', [(CX - 0.34, -0.115, 0.27), (CX + hi, -0.115, 0.27)], 0.032, M_plastic, res=2)
for o in (tank, tank_in, sand, coll, *grains): show(o, T_MOVE + 0.3)
hidden_until(grime, T_STUCK); key(grime, 'scale', T_STUCK, (1, 1, 0.02)); key(grime, 'scale', T_PASS + 0.6, (1, 1, 1))
tint(M_tankw, [(T_MOVE, GREEN, 1.0), (T_KAP + 0.3, GREEN, 1.0), (T_KAP + 1.3, BLUE, 1.0)])
P_SUC = [(4.50, 0, -0.93), (4.50, 0, -2.75), (5.75, 0, -2.75), (5.75, 0, 0.36)]; P_DRN = [(X_DR, 0, zo(X_DR) + 0.02), (X_DR, 0, -2.75), (4.50, 0, -2.75)]
P_P2F = [(6.22, 0, 0.52), (6.22, 0, 1.84), (CX, 0, 1.84), (CX, 0, ZT1 - 0.05)]
P_RET = [(CX + hi, 0, 0.30), (8.3, 0, 0.30), (8.3, 0, -3.35), (-4.9, 0, -3.35), (-4.9, 0, -0.80), (X0 + 0.1, 0, -0.80)]
pipes = [pipe('PIPE_suction', P_SUC, 0.09), pipe('PIPE_drain', P_DRN, 0.09), pipe('PIPE_to_filter', P_P2F, 0.09), pipe('PIPE_return', P_RET, 0.09)]
for k, pp in enumerate(pipes): extend(pp, T_MOVE + 0.25 + 0.12 * k, T_MOVE + 1.05 + 0.2 * k)
T_STOP = T_TRAP - 0.2                                                           # the pump runs until the pool is drained
flow('FLOW_suc', front(P_SUC), T_PUMP - 0.2, T_STOP, m=M_drop_g); flow('FLOW_drn', front(P_DRN), T_PUMP - 0.2, T_STOP, m=M_drop_g)
flow('FLOW_p2f', front(P_P2F), T_PUMP, T_STOP, m=M_drop_g); flow('FLOW_ret', front(P_RET), T_PASS - 0.3, T_STOP, speed=3.2, gap=1.0)
for k in range(9):                                                              # dirt arrives with the water and stays on top of the sand
    gx = CX - 0.36 + 0.09 * k; o = sphere('DIRT', (CX, -0.13, ZT1 - 0.2), rnd.uniform(0.034, 0.05), M_grime, sx=1.2, sz=0.8, seg=6); s0 = tuple(o.scale); ta = T_STUCK - 0.75 + 0.07 * k
    hidden_until(o, ta); key(o, 'scale', ta, s0, ip='CONSTANT'); travel(o, [(ta, (CX, -0.13, ZT1 - 0.2)), (ta + 0.3, (gx, -0.13, 1.15)), (ta + 0.75, (gx, -0.13, ZSAND + 0.03))])
for k, gx in enumerate((CX - 0.27, CX, CX + 0.27)):                             # clean water goes on through the sand and out
    flow('FLOW_clean%d' % k, [(gx, -0.135, ZSAND - 0.03), (gx + 0.045, -0.135, 0.56), (gx, -0.135, 0.30), (CX + hi, -0.135, 0.30)], T_PASS - 0.1 + 0.1 * k, T_STOP, speed=0.75, gap=0.34, r=0.018)
tag_filter = label('TAG_filter', [('FILTER PASIR', 0.14, M_white)], pos=(CX - 0.05, 0.1, 2.24), billboard=True); pop(tag_filter, T_FILTER, 0.3); vanish(tag_filter, T_GERM + 0.35, 0.18)
skim = [patch('SKIM_body', [(XB, -0.97), (XB + 0.58, -0.97), (XB + 0.58, -0.03), (XB, -0.03)], M_plastic, y=-0.006),
        patch('SKIM_water', [(XB + 0.06, -0.91), (XB + 0.52, -0.91), (XB + 0.52, -0.15), (XB + 0.06, -0.15)], M_tankw, y=-0.012),
        patch('SKIM_throat', [(X1 - 0.02, -0.34), (XB + 0.07, -0.34), (XB + 0.07, -0.13), (X1 - 0.02, -0.13)], M_tankw, y=-0.014),
        box('SKIM_mouth', X1 - 0.012, X1, 0.12, 0.85, -0.36, -0.06, M_mouth)]
for i in range(5): skim.append(tube('SKIM_basket', [(XB + 0.10, -0.03, -0.86 + 0.08 * i), (XB + 0.48, -0.03, -0.86 + 0.08 * i)], 0.012, M_plastic, res=1))
for i in range(5): skim.append(tube('SKIM_basket', [(XB + 0.11 + 0.09 * i, -0.03, -0.88), (XB + 0.11 + 0.09 * i, -0.03, -0.52)], 0.012, M_plastic, res=1))
skim += [box('DRAIN_grate', X_DR - 0.22, X_DR + 0.22, 0.0, 0.5, zf(X_DR) - 0.01, zf(X_DR) + 0.035, M_ink),
         patch('DRAIN_sleeve', [(X_DR - 0.09, zo(X_DR)), (X_DR + 0.09, zo(X_DR)), (X_DR + 0.09, zf(X_DR)), (X_DR - 0.09, zf(X_DR))], M_plastic, y=-0.006)]
for o in skim: show(o, T_MOVE + 0.2)
tag_skim = label('TAG_skimmer', [('SKIMMER', 0.40, M_white)], pos=(XB + 0.3, 0.3, 1.25), billboard=True); pop(tag_skim, T_MOVE + 0.55, 0.28); vanish(tag_skim, T_PUMP + 0.5, 0.18)

# ---- S08: germs slip through the sand, algae keep growing, a little chlorine
for k in range(7):                                                              # tiny germs zigzag down between the grains (seen in the close-up)
    gx = CX - 0.36 + 0.105 * k; o = sphere('GERM_small', (gx, -0.14, ZSAND + 0.2), 0.024, M_germ_s, seg=8); ta = T_GERM + 0.25 + 0.2 * k; show(o, ta, ta + 2.35)
    pts = [(ta, (gx, -0.14, ZSAND + 0.2))] + [(ta + 0.3 + 0.2 * j, (gx + (0.045 if j % 2 else 0.0), -0.14, ZSAND - 0.06 - 0.088 * j)) for j in range(8)] + [(ta + 2.3, (CX + hi, -0.14, 0.27))]
    travel(o, pts)
germs = []
for k in range(9):
    x = -3.3 + 0.8 * k; g_ = empty('GERM', (x, rnd.uniform(0.7, 3.2), rnd.uniform(zf(x) + 0.35, WL - 0.3))); sphere('GERM_body', (0, 0, 0), 0.11, M_germ, seg=10, parent=g_)
    for j in range(6): a = j * math.tau / 6; sphere('GERM_bump', (0.11 * math.cos(a), 0, 0.11 * math.sin(a)), 0.04, M_germ, seg=6, parent=g_)
    pop(g_, T_GERM + 0.1 * k); pulse(g_, T_GROW, T_KAP + 0.4, 0.5, 0.2, s=(1, 1, 1)); vanish(g_, T_KAP + 0.5 + 0.07 * k, 0.14); germs.append(g_)
tub = [cyl('KAPORIT_tub', (-1.3, 4.75, 0.055), 0.26, 0.44, M_plastic, seg=16), cyl('KAPORIT_lid', (-1.3, 4.75, 0.495), 0.27, 0.06, M_tank, seg=16)]
for o in tub: pop(o, T_THEM)
tag_kap = label('TAG_kaporit', [('KAPORIT', 0.22, M_white)], pos=(-1.3, 4.6, 1.05), billboard=True); pop(tag_kap, T_THEM + 0.15, 0.25); vanish(tag_kap, T_SMELL - 0.1, 0.15)
scoop = cyl('KAPORIT_scoop', (-1.3, 4.75, 0.75), 0.11, 0.13, M_tank, seg=12); pop(scoop, T_CHEM - 0.1, 0.2); vanish(scoop, T_KAP + 0.95, 0.15)
key(scoop, 'location', T_CHEM + 0.1, (-1.3, 4.75, 0.75)); key(scoop, 'location', T_KAP, (-0.7, 3.3, 1.15)); key(scoop, 'rotation_euler', T_KAP - 0.05, (0, 0, 0)); key(scoop, 'rotation_euler', T_KAP + 0.2, (math.radians(125), 0, 0))
for k in range(18):
    p1 = (rnd.uniform(-2.8, 1.6), rnd.uniform(1.0, 3.2), WL); o = sphere('GRANULE', (-0.7, 3.2, 1.05), 0.05, M_gran, seg=6); ta = T_KAP + 0.15 + 0.02 * k; show(o, ta, ta + 1.25)
    travel(o, [(ta, (-0.7, 3.2, 1.05)), (ta + 0.4, p1), (ta + 1.2, (p1[0], p1[1], WL - 0.7))])
one(arm_r, T_CHEM, T_KAP + 0.8, 120)

# ---- S09: the smell = chlorine that already reacted with sweat and urine
swimmers = []
for k, (x, y, m_) in enumerate(((-2.5, 1.7, M_cap1), (0.2, 2.7, M_cap2), (2.4, 1.4, M_cap3))):
    r_, al_, ar_ = make_char('SWIM%d' % k, (x, y, WL - 1.40), vest=m_, helmet=False); sphere('SWIM_cap', (0, 0, 1.69), 0.16, m_, sz=0.75, seg=12, parent=r_)
    pop(r_, T_SMELL - 0.25 + 0.12 * k, 0.3); vanish(r_, T_TRAP - 0.15 + 0.05 * k, 0.15); swimmers.append((r_, al_, ar_))
    for t in (T_SMELL + 0.4 * k, T_DIRTY + 0.3 * k): key(r_, 'location', t, (x, y, WL - 1.40)); key(r_, 'location', t + 0.45, (x, y, WL - 1.30)); key(r_, 'location', t + 0.9, (x, y, WL - 1.40))
for a, sg in ((swimmers[0][1], 1), (swimmers[0][2], -1)): arm(a, T_SMELL + 0.2, 8 * sg); arm(a, T_SMELL + 0.6, 150 * sg); arm(a, T_REACT, 150 * sg)
stinks = []
for k, x in enumerate((-3.1, -1.5, 0.1, 1.5, 3.0)):
    y = 0.9 + 0.5 * (k % 2); pts = [(x + 0.16 * math.sin(j * 1.1 + k), y, WL + 0.15 + 0.16 * j) for j in range(10)]; o = tube('STINK', pts, 0.035, M_stink, res=2, origin=pts[0]); o.visible_shadow = False
    extend(o, T_SMELL + 0.15 + 0.12 * k, T_SMELL + 1.0 + 0.12 * k); pulse(o, T_DIRTY, T_DIRTY + 0.7 * int((T_PEE + 0.6 - T_DIRTY) / 0.7), 0.7, 0.12, s=(1, 1, 1), ip='BEZIER'); key(o, 'scale', T_TRAP - 0.1, (1, 1, 1)); key(o, 'scale', T_TRAP + 0.1, Z); stinks.append(o)
for k in range(8):                                                              # sweat drops
    r_ = swimmers[k % 3][0]; x, y = r_.location.x + rnd.uniform(-0.2, 0.2), r_.location.y - 0.1; o = sphere('SWEAT', (x, y, WL + 0.45), 0.045, M_drop, sz=1.5, seg=6); ta = T_SWEAT - 0.25 + 0.08 * k
    show(o, ta, ta + 0.55); travel(o, [(ta, (x, y, WL + 0.45)), (ta + 0.5, (x + rnd.uniform(-0.3, 0.3), y - 0.2, WL))])
pee = sphere('PEE_cloud', (2.4, 1.2, WL - 0.55), 0.55, M_pee, sx=1.0, sy=0.8, sz=0.6, seg=12); pee.visible_shadow = False
hidden_until(pee, T_PEE); key(pee, 'scale', T_PEE, (0.1, 0.08, 0.06)); key(pee, 'scale', T_PEE + 0.8, (1.5, 1.1, 0.75)); key(pee, 'scale', T_TRAP - 0.1, (1.7, 1.25, 0.8)); key(pee, 'scale', T_TRAP + 0.1, Z)
r_ = swimmers[2][0]; key(r_, 'location', T_PEE + 0.25, (2.4, 1.4, WL - 1.40)); key(r_, 'location', T_PEE + 1.0, (1.5, 2.3, WL - 1.40))
one(arm_l, T_SMELL + 0.5, T_TRAP - 0.3, 150)

# ================================================================ S10: drained pool, ballast gone, groundwater lifts the empty shell
M_rain = new_mat('rain', (0.78, 0.90, 1.0), 0.3, emit=0.8); M_gapw = new_mat('gap_water', (0.12, 0.40, 0.85), 0.2, emit=0.1, alpha=0.85)
M_stone = new_mat('stone', (0.56, 0.55, 0.52), 0.95); M_red = new_mat('valve_red', (0.86, 0.12, 0.10), 0.4, emit=0.15); M_bucket = new_mat('bucket', (0.25, 0.45, 0.75), 0.5)
level(lvl, [(T_DRAIN, WL), (T_DRAIN + 1.45, ZD - 0.3)])
appear(tag_ton, T_BALLAST, 0.25, s=(1, 1, 1)); key(tag_ton, 'location', T_GONE - 0.02, (0.0, 2.0, 2.0)); key(tag_ton, 'location', T_GONE + 0.5, (0.0, 2.0, 5.4)); vanish(tag_ton, T_GONE + 0.25, 0.25)
T_R0, T_R1 = T_GW - 0.25, T_LIKE + 0.3
for k in range(48):
    x, y = rnd.uniform(-7.5, 7.5), rnd.uniform(0.3, 10.0); o = tube('RAIN', [(0, 0, 0), (0.06, 0, 0.55)], 0.013, M_rain, res=1); o.visible_shadow = False; show(o, T_R0, T_R1); t = T_R0 - rnd.uniform(0, 0.5)
    while t < T_R1: key(o, 'location', t, (x, y, 9.0), ip='LINEAR'); key(o, 'location', t + 0.5, (x - 0.5, y, -0.3), ip='CONSTANT'); t += 0.5
for t, e_ in ((T_GW - 0.3, 2.7), (T_GW + 0.3, 1.5), (T_ODD, 1.5), (T_ODD + 0.8, 2.7)): key(sun_d, 'energy', t, e_)
M_gw = new_mat('groundwater', (0.10, 0.40, 0.95), 0.35, emit=0.12, alpha=0.5); N_ = M_gw.node_tree.nodes; L_ = M_gw.node_tree.links
geo_ = N_.new('ShaderNodeNewGeometry'); sepz = N_.new('ShaderNodeSeparateXYZ'); L_.new(geo_.outputs['Position'], sepz.inputs[0]); gwl = N_.new('ShaderNodeValue'); gwl.outputs[0].default_value = -9.0
lt = N_.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; L_.new(sepz.outputs['Z'], lt.inputs[0]); L_.new(gwl.outputs[0], lt.inputs[1])
dep = N_.new('ShaderNodeMath'); dep.operation = 'SUBTRACT'; L_.new(gwl.outputs[0], dep.inputs[0]); L_.new(sepz.outputs['Z'], dep.inputs[1])
band = N_.new('ShaderNodeMath'); band.operation = 'LESS_THAN'; L_.new(dep.outputs[0], band.inputs[0]); band.inputs[1].default_value = 0.10
bm_ = N_.new('ShaderNodeMath'); bm_.operation = 'MULTIPLY'; L_.new(band.outputs[0], bm_.inputs[0]); bm_.inputs[1].default_value = 0.40
ba = N_.new('ShaderNodeMath'); ba.operation = 'ADD'; L_.new(bm_.outputs[0], ba.inputs[0]); ba.inputs[1].default_value = 0.36
al = N_.new('ShaderNodeMath'); al.operation = 'MULTIPLY'; L_.new(lt.outputs[0], al.inputs[0]); L_.new(ba.outputs[0], al.inputs[1]); L_.new(al.outputs[0], bsdf_of(M_gw).inputs['Alpha'])
def gw(t, z): gwl.outputs[0].default_value = z; gwl.outputs[0].keyframe_insert('default_value', frame=fr(t))
G_HI = -0.50
for t, z in ((T_GW - 0.1, -9.0), (T_LIFT - 0.1, G_HI), (T_TILE - 0.2, G_HI), (T_TILE + 0.9, -9.0)): gw(t, z)
gw_parts = [patch('GW_l', [(-45, -14), (XA, -14), (XA, -0.25), (-45, -0.25)], M_gw, y=-0.004), patch('GW_r', [(XB, -14), (45, -14), (45, -0.25), (XB, -0.25)], M_gw, y=-0.004),
            patch('GW_b', [(XA, -14), (XB, -14), (XB, ZB), (XA, zo(XA))], M_gw, y=-0.004)]
for o in gw_parts: show(o, T_GW - 0.3, T_TILE + 1.3)
ups = [arrow('UP_%d' % k, (x, -0.14, zo(x) - 1.55), (x, -0.14, zo(x) - 0.14), r=0.075) for k, x in enumerate((-3.0, -0.9, 1.2, 3.75))] + [arrow('UP_v', (1.95, -0.14, zo(1.95) - 1.2), (1.95, -0.14, zo(1.95) - 0.14), r=0.06)]
for k, a_ in enumerate(ups):
    hidden_until(a_, T_LIFT - 0.35); appear(a_, T_LIFT - 0.35 + 0.06 * k, 0.25, s=(1, 1, 1)); pulse(a_, T_LIFT, T_SAFE, 0.55, 0.16, s=(1, 1, 1))
    key(a_, 'scale', T_SAFE + 0.5, (0.45, 0.45, 0.45)); key(a_, 'scale', T_TILE - 0.25, (0.45, 0.45, 0.45)); key(a_, 'scale', T_TILE - 0.05, Z)
LIFT_DZ, LIFT_DEG = 0.31, 6.1
def pool_pose(t, dz, deg): key(POOL, 'location', t, zo(XA) + dz, index=2); key(POOL, 'rotation_euler', t, math.radians(-deg), index=1)
for t, dz, deg in ((T_LIFT + 0.1, 0.0, 0.0), (T_UP + 0.25, 0.34, 6.5), (T_UP + 0.6, 0.27, 5.6), (T_UP + 1.0, LIFT_DZ, LIFT_DEG), (T_ODD + 0.15, LIFT_DZ, LIFT_DEG), (T_ODD + 0.6, -0.02, -0.25), (T_ODD + 0.8, 0.0, 0.0)): pool_pose(t, dz, deg)
_a = math.radians(LIFT_DEG); _dx, _dz = XB - XA, ZB - zo(XA); z_r = zo(XA) + LIFT_DZ + _dx * math.sin(_a) + _dz * math.cos(_a)      # underside of the lifted shell at its right end
gapw = prismp('GAP_water', [(XA, ZB - 0.3), (XB, ZB - 0.3), (XB, z_r - 0.03), (XA, zo(XA) + LIFT_DZ - 0.03)], 0.004, YB, M_gapw, pivot=(0.0, ZB - 0.3)); show(gapw, T_LIFT + 0.1, T_ODD + 0.62, s=(1, 1, 0.2))
for t, s_ in ((T_LIFT + 0.1, 0.2), (T_UP + 0.25, 1.0), (T_ODD + 0.15, 1.0), (T_ODD + 0.6, 0.2)): key(gapw, 'scale', t, (1, 1, s_), ip='SINE', ease='EASE_IN_OUT')
for k in range(12):                                                             # clods kicked up along the edges
    x = rnd.choice((XA - 0.35, XB + 0.35)) if k % 3 else rnd.uniform(XA, XB); y = rnd.uniform(0.3, 4.0) if k % 3 else GY + 0.1
    o = sphere('CLOD', (x, y, 0.1), rnd.uniform(0.08, 0.15), M_dirt, seg=6, smooth=False); ta = T_UP + 0.02 * k; show(o, ta, ta + 0.7)
    travel(o, [(ta, (x, y, 0.1)), (ta + 0.3, (x + rnd.uniform(-0.4, 0.4), y, rnd.uniform(0.8, 1.5))), (ta + 0.68, (x + rnd.uniform(-0.8, 0.8), y, 0.05))])
both(T_UP, T_ODD + 0.3, 165)
bub = empty('BUBBLE', (-1.5, 1.0, 2.7)); bub.scale = (1.5, 1.5, 1.5); bub.constraints.new('COPY_ROTATION').target = cam                 # "like an empty bucket pushed into a tub"
bp = [cyl('BUB_rim', (0, 0, -0.035), 1.45, 0.02, M_ink, seg=40, parent=bub), cyl('BUB_plate', (0, 0, -0.012), 1.36, 0.02, M_sign, seg=40, parent=bub),
      box('BUB_tub_l', -0.88, -0.78, -0.80, 0.12, 0.012, 0.05, M_ink, parent=bub), box('BUB_tub_r', 0.78, 0.88, -0.80, 0.12, 0.012, 0.05, M_ink, parent=bub),
      box('BUB_tub_b', -0.88, 0.88, -0.90, -0.80, 0.012, 0.05, M_ink, parent=bub), box('BUB_water', -0.78, 0.78, -0.80, -0.18, 0.012, 0.03, M_drop, parent=bub)]
bk = empty('BUB_bucket', (0.0, 0.14, 0.035), parent=bub)
bp += [box('BUB_bucket_body', -0.30, 0.30, -0.34, 0.24, 0.0, 0.03, M_bucket, parent=bk), box('BUB_bucket_rim', -0.35, 0.35, 0.20, 0.27, 0.0, 0.035, M_bucket, parent=bk)]
hand = empty('BUB_hand', (0.0, 0.0, 0.0), parent=bk)
bp += [box('BUB_palm', -0.13, 0.13, 0.27, 0.42, 0.0, 0.03, M_skin, parent=hand), box('BUB_arm', -0.07, 0.07, 0.42, 1.25, 0.0, 0.03, M_skin, parent=hand)]
for o in bp: o.visible_shadow = False
pop(bub, T_LIKE - 0.05, 0.25); vanish(bub, T_ODD + 0.05, 0.15)
for t, y in ((T_LIKE, 0.14), (T_PUSH, 0.14), (T_PUSH + 0.4, -0.34), (T_TUB, -0.34), (T_TUB + 0.16, 0.78), (T_TUB + 0.36, 0.08), (T_TUB + 0.5, 0.2)): key(bk, 'location', t, y, index=1)
key(hand, 'scale', T_TUB - 0.02, (1, 1, 1), ip='CONSTANT'); key(hand, 'scale', T_TUB, Z, ip='CONSTANT')

# ================================================================ S11: the hydrostatic valve lets the groundwater in
ZV = zf(X_V)
valve = [patch('VALVE_port', [(X_V - 0.10, zo(X_V) - 0.02), (X_V + 0.10, zo(X_V) - 0.02), (X_V + 0.10, ZV + 0.01), (X_V - 0.10, ZV + 0.01)], M_tankw, y=-0.006),
         box('VALVE_seat', X_V - 0.27, X_V + 0.27, 0.0, 0.44, ZV - 0.005, ZV + 0.03, M_plastic)]
vcap = empty('VALVE_cap', (X_V, 0.0, ZV + 0.03)); box('VALVE_cap_top', -0.22, 0.22, -0.03, 0.42, 0.0, 0.09, M_red, parent=vcap); box('VALVE_stem', -0.035, 0.035, -0.04, 0.03, -0.27, 0.0, M_plastic, parent=vcap)
for o in valve + [vcap]: show(o, T_BOWL + 0.3)
for k in range(24):
    gx = X_V + rnd.uniform(-0.6, 0.6); o = sphere('GRAVEL', (gx, rnd.uniform(-0.13, -0.04), zo(gx) - rnd.uniform(0.08, 0.55)), rnd.uniform(0.06, 0.10), M_stone, sy=0.8, seg=7, smooth=False); show(o, T_BOWL + 0.3)
zc = ZV + 0.03
for t, dz in ((T_OPEN - 0.02, 0.0), (T_OPEN + 0.22, 0.20), (T_OPEN + 0.4, 0.15), (T_TILE - 0.3, 0.15), (T_TILE - 0.1, 0.0)): key(vcap, 'location', t, zc + dz, index=2)
for k, dx in enumerate((-0.95, 0.0, 0.95)):
    flow('FLOW_valve%d' % k, [(X_V, -0.09, zo(X_V) - 0.6), (X_V, -0.09, ZV + 0.14), (X_V + dx, -0.09 + 0.3 * abs(dx), ZV + 0.22 - 0.075 * dx)], T_OPEN + 0.1 + 0.08 * k, T_TILE - 0.3, speed=1.1, gap=0.3, r=0.04)
T_FULL = T_DUCK + 0.55
level(lvl, [(T_OPEN + 0.15, ZD - 0.3), (T_NAME, ZD + 0.34), (T_LAMP - 0.2, ZD + 0.34), (T_FULL, WL)])
GWC = (0.16, 0.36, 0.52); tint(M_water, [(T_DRAIN, BLUE, 0.58), (T_OPEN, GWC, 0.72), (T_LAMP - 0.2, GWC, 0.72), (T_FULL, (0.06, 0.60, 0.90), 0.56)])
tag_valve = label('TAG_valve', [('KATUP', 0.25, M_white), ('HIDROSTATIK', 0.25, M_yellow)], pos=(X_V - 0.1, 0.25, ZV + 1.12), billboard=True); pop(tag_valve, T_NAME, 0.28); vanish(tag_valve, T_TILE - 0.1, 0.15)
one(arm_r, T_SAFE, T_NAME + 0.8, 150)

# ================================================================ S12: tiles, lights at dusk, the duck, the payoff
M_tile = new_mat('tile', (0.35, 0.72, 0.90), 0.25, spec=0.6); n_ = M_tile.node_tree.nodes; l_ = M_tile.node_tree.links
geo2 = n_.new('ShaderNodeNewGeometry'); chk = n_.new('ShaderNodeTexChecker'); chk.inputs['Scale'].default_value = 3.3
chk.inputs['Color1'].default_value = (0.28, 0.66, 0.90, 1); chk.inputs['Color2'].default_value = (0.44, 0.80, 0.95, 1); l_.new(geo2.outputs['Position'], chk.inputs['Vector']); l_.new(chk.outputs['Color'], bsdf_of(M_tile).inputs['Base Color'])
tiles = [prismp('TILE_floor', [(X0, zf(X0)), (X1, zf(X1)), (X1, zf(X1) + 0.02), (X0, zf(X0) + 0.02)], 0.0, Y1, M_tile, pivot=(X0, zf(X0))),
         box('TILE_l', X0, X0 + 0.02, 0.0, Y1, zf(X0), 0.0, M_tile), box('TILE_r', X1 - 0.02, X1, 0.0, Y1, zf(X1), 0.0, M_tile),
         prismp('TILE_b', [(X0, zf(X0)), (X1, zf(X1)), (X1, 0.0), (X0, 0.0)], Y1 - 0.02, Y1, M_tile, pivot=(X0, zf(X1)))]
grow(tiles[0], T_TILE, T_TILE + 0.55, axis=0); grow(tiles[1], T_TILE + 0.2, T_TILE + 0.7, axis=2); grow(tiles[2], T_TILE + 0.2, T_TILE + 0.7, axis=2); grow(tiles[3], T_TILE + 0.1, T_TILE + 0.65, axis=0)
M_lamp = new_mat('lamp', (1.0, 0.95, 0.75), 0.3); lb = bsdf_of(M_lamp); lb.inputs['Emission Color'].default_value = (1.0, 0.93, 0.72, 1)
key_input(lb.inputs['Emission Strength'], T_LAMP - 0.05, 0.0); key_input(lb.inputs['Emission Strength'], T_LAMP + 0.15, 5.0)
lamps = []
for x in (-2.6, 0.0, 2.6):
    o = cyl('LAMP', (x, Y1 - 0.02, -0.74), 0.17, 0.04, M_lamp, seg=16); o.rotation_euler = (math.radians(90), 0, 0); pop(o, T_LAMP - 0.12, 0.2); lamps.append(o)
    ld = bpy.data.lights.new('LGT_pool', 'POINT'); ld.color = (0.60, 0.90, 1.0); ld.shadow_soft_size = 0.3; lo = bpy.data.objects.new('LGT_pool', ld); col.objects.link(lo); lo.location = (x, Y1 - 0.6, -0.72)
    key(ld, 'energy', T_LAMP - 0.05, 0.0); key(ld, 'energy', T_LAMP + 0.3, 110.0)
DUSK0, DUSK1 = T_LAMP - 0.4, T_LAMP + 1.4
key(sun_d, 'energy', DUSK0, 2.7); key(sun_d, 'energy', DUSK1, 0.85); key(sun_d, 'color', DUSK0, (1.0, 1.0, 1.0)); key(sun_d, 'color', DUSK1, (1.0, 0.62, 0.40))
key_input(bg.inputs['Strength'], DUSK0, 1.0); key_input(bg.inputs['Strength'], DUSK1, 0.50)
try:
    for t, cs in ((DUSK0, ((0.62, 0.80, 0.97), (0.10, 0.34, 0.82))), (DUSK1, ((0.98, 0.60, 0.36), (0.12, 0.13, 0.40)))):
        for el, c in zip(sky.color_ramp.elements, cs): el.color = (*c, 1); el.keyframe_insert('color', frame=fr(t))
except Exception as ex: print('sky keys skipped:', ex)
wb = bsdf_of(M_window)
for t, st, c in ((DUSK0, 0.25, (0.50, 0.75, 0.95)), (DUSK1, 3.2, (1.0, 0.80, 0.42))): key_input(wb.inputs['Emission Strength'], t, st); key_input(wb.inputs['Emission Color'], t, (*c, 1)); key_input(wb.inputs['Base Color'], t, (*c, 1))
wtr = bsdf_of(M_water); wtr.inputs['Emission Color'].default_value = (0.08, 0.72, 0.95, 1); key_input(wtr.inputs['Emission Strength'], T_LAMP, 0.0); key_input(wtr.inputs['Emission Strength'], T_FULL, 0.22)
def lv(t): return (ZD + 0.34) + (WL - ZD - 0.34) * min(1.0, max(0.0, (t - (T_LAMP - 0.2)) / (T_FULL - (T_LAMP - 0.2))))     # water level while the pool refills
key(duck, 'rotation_euler', T_DUCK - 0.1, (0, 0, 0)); key(duck, 'location', T_DUCK - 0.06, (-1.6, 1.3, 2.0), ip='LINEAR'); appear(duck, T_DUCK - 0.05, 0.2, s=(1.7, 1.7, 1.7))
for dt in (0.34, 0.45, 0.55, 0.75, 0.95): t = T_DUCK + dt; key(duck, 'location', t, (-1.6, 1.3, lv(t) + (0.05 if dt in (0.45, 0.75) else -0.02)), ip='LINEAR')
stk2 = label('STK_end', [('SELAMAT!', 0.66, M_ink)], pos=(2.3, 2.6, 3.0), plate=M_yellow, billboard=True); pop(stk2, T_END, 0.3, over=1.15)
both(T_END + 0.05, DUR + 1.0, 160)
for t, p in ((T_END + 0.2, (-2.6, 5.35, 0.02)), (T_END + 0.62, (-2.0, 4.3, 1.55)), (T_SPLASH, (-1.2, 3.0, WL - 0.5)), (T_SPLASH + 0.25, (-1.2, 3.0, WL - 1.75)), (T_SPLASH + 0.8, (-1.2, 3.0, WL - 1.40))): key(mascot, 'location', t, p)
for k in range(16):
    a = k * math.tau / 16; o = sphere('SPLASH', (-1.2, 3.0, WL), rnd.uniform(0.07, 0.12), M_gran, seg=6); show(o, T_SPLASH, T_SPLASH + 0.55); r1 = rnd.uniform(0.6, 1.1)
    travel(o, [(T_SPLASH, (-1.2, 3.0, WL)), (T_SPLASH + 0.25, (-1.2 + r1 * math.cos(a), 3.0 + r1 * math.sin(a), WL + rnd.uniform(0.8, 1.5))), (T_SPLASH + 0.55, (-1.2 + 1.6 * r1 * math.cos(a), 3.0 + 1.6 * r1 * math.sin(a), WL))])

# ================================================================ everything fixed to the shell follows it when it floats
pool_parts += skim + valve + [vcap] + tiles + lamps
bpy.context.view_layer.update(); _inv = POOL.matrix_world.inverted()
for o in pool_parts: o.parent = POOL; o.matrix_parent_inverse = _inv

# ================================================================ camera: one continuous move, no hard cuts
P_MASTER = orbit(82, 23, 18.5, (0.0, 1.0, -1.9))
shot(0.0, T_BUT, orbit(82, 24, 19.6, (0.0, 1.2, -1.7)), P_MASTER, cut=True)                       # the hole, the water, "selamat"
shot(T_BUT, T_FIX, orbit(87, 15, 15.5, (0.0, 0.6, -2.3)), mv=0.8)                                 # seepage and collapse, lower and closer
shot(T_FIX, T_BOWL, orbit(70, 27, 15.5, (0.4, 1.6, -1.6)), mv=0.8)                                # rebar cage and concrete
shot(T_BOWL, T_DAYS, P_MASTER, mv=0.9)                                                            # the giant bowl, 48 tonnes
shot(T_DAYS, T_MOVE, orbit(88, 21, 16.5, (-0.2, 1.0, -1.8)), mv=0.8)                              # green soup
shot(T_MOVE, T_PUMP, orbit(84, 20, 19.0, (3.0, 0.8, -1.9)), mv=0.8)                               # equipment arrives, skimmer at work
shot(T_PUMP, T_SAND - 0.3, orbit(88, 11, 8.8, (6.5, 0.0, -0.75)), mv=0.9)                         # pump and pipes
shot(T_SAND - 0.3, T_GERM, orbit(89, 6, 4.0, (CX - 0.15, 0.0, 0.70)), mv=0.8)                     # inside the sand filter
shot(T_GERM, T_GROW, pose(CX, 1.6, 0.62, 0.50), mv=0.8)                                           # between the sand grains
shot(T_GROW, T_SMELL, orbit(80, 24, 16.0, (-0.3, 1.6, -1.6)), mv=0.9)                             # algae, germs, chlorine
shot(T_SMELL, T_TRAP, orbit(86, 18, 13.8, (0.2, 1.4, -1.5)), mv=0.8)                              # swimmers and the smell
shot(T_TRAP, T_GW, P_MASTER, mv=0.8)                                                              # drained, ballast gone
shot(T_GW, T_LEAK, orbit(88, 13, 17.5, (0.0, 0.6, -2.6)), mv=0.9)                                 # groundwater rises, the shell floats
shot(T_LEAK, T_SAFE, orbit(87, 10, 4.9, (X_V + 0.15, 0.0, -2.35)), mv=1.0)                        # the valve
shot(T_SAFE, T_TILE, orbit(86, 13, 9.5, (1.4, 0.4, -2.0)), mv=0.9)
shot(T_TILE, T_NOW, P_MASTER, mv=0.8)                                                             # tiles, lights
shot(T_NOW, DUR + 0.2, orbit(66, 25, 19.5, (0.3, 1.8, -1.5)), orbit(62, 26, 20.5, (0.3, 1.8, -1.5)), mv=1.2)   # hero shot at dusk
if os.environ.get('KIT_PROBE'):
    for nm, ps, pt in (('bubble', orbit(88, 13, 17.5, (0.0, 0.6, -2.6)), (-1.7, 1.5, 3.9)), ('tag ton', P_MASTER, (0.0, 2.0, 2.0)), ('sticker end', orbit(66, 25, 19.5, (0.3, 1.8, -1.5)), (0.3, 2.2, 2.5))): print('PROJ', nm, project(ps, pt))
render_main()
