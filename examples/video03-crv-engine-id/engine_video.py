"""Mesin CR-V tembus seribu tenaga kuda (ID, 9:16) - video #3, kit v1.0. A sectioned inline-four on a stand, built and animated from code.
Every cue follows the voice-over word timings in words.json; the crank, pistons, rods, valves and flashes are baked per frame from one
crank-angle curve, so they stay mechanically consistent at any speed.

  python3 engine_video.py still 405 720 16 st 3.0 14.2 27.0      quick stills at those seconds (CPU)
  python3 engine_video.py anim 1080 1920 64 frames 1 2277 [step]  all frames (box/render.sh calls this)
  python3 engine_video.py blend 1080 1920 64 engine.blend         save the scene for Blender

Scale: about 7.5 x real size. X runs along the crankshaft, Z is up, the section plane is y = 0, the camera looks along +Y.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from kitjob import FPS, OFFSET, WORDS, DUR
exec(open(os.path.join(HERE, 'explainer_kit.py'), encoding='utf8').read())
exec(open(os.path.join(HERE, 'scene_extras.py'), encoding='utf8').read())
PI = math.pi; DT = 1.0 / FPS; NF = LAST; FAR = (0.0, 300.0, 0.0)

# ================================================================ materials (amber section, cool metals, navy shop)
def metal(name, color, rough, metallic=1.0, emit=0.0):
    m = new_mat(name, color, rough, spec=0.5, emit=emit); bsdf_of(m).inputs['Metallic'].default_value = metallic; return m
M_alu = metal('alu', (0.78, 0.80, 0.82), 0.42); M_alu2 = metal('alu_dark', (0.50, 0.53, 0.57), 0.5); M_block = metal('block', (0.78, 0.80, 0.82), 0.42)
M_iron = metal('iron', (0.20, 0.22, 0.25), 0.55); M_chrome = metal('chrome', (0.90, 0.91, 0.93), 0.16); M_crank = metal('crank', (0.88, 0.89, 0.92), 0.2)
M_forged = metal('forged', (0.30, 0.34, 0.42), 0.32); M_copper = metal('copper', (0.86, 0.50, 0.26), 0.35); M_gold = metal('gold', (0.95, 0.72, 0.25), 0.3)
M_blue_st = metal('blue_steel', (0.22, 0.42, 0.85), 0.3); M_inconel = metal('inconel', (0.62, 0.42, 0.30), 0.28); M_ti = metal('titanium', (0.72, 0.70, 0.78), 0.3)
M_cut = new_mat('section', (1.0, 0.63, 0.10), 0.75); M_cut_a = new_mat('section_head', (1.0, 0.82, 0.42), 0.75); M_cut_b = new_mat('section_head_r', (0.90, 0.22, 0.13), 0.7); M_cut2 = new_mat('section_iron', (0.86, 0.36, 0.10), 0.7); M_bore_in = metal('bore', (0.42, 0.45, 0.50), 0.3)
M_dark = new_mat('dark', (0.045, 0.055, 0.075), 0.7); M_cover_a = new_mat('cover_stock', (0.16, 0.17, 0.19), 0.45, spec=0.4); M_cover_b = new_mat('cover_r', (0.80, 0.08, 0.07), 0.38, spec=0.5)
M_stand = new_mat('stand', (0.07, 0.20, 0.42), 0.5, spec=0.4); M_floor = new_mat('floor', (0.50, 0.51, 0.52), 0.85); M_wall = new_mat('wall', (0.10, 0.14, 0.22), 0.9)
M_rubber = new_mat('rubber', (0.03, 0.03, 0.035), 0.8); M_cab = new_mat('cabinet', (0.62, 0.10, 0.08), 0.5, spec=0.4); M_car = new_mat('car', (0.10, 0.30, 0.34), 0.45, spec=0.5)
M_glass = new_mat('car_glass', (0.05, 0.08, 0.11), 0.2, spec=0.6); M_coolant = new_mat('coolant', (0.10, 0.55, 0.98), 0.25, emit=0.7)
M_fire = new_mat('fire', (1.0, 0.78, 0.25), 0.5, emit=7.0); M_knock = new_mat('knock', (1.0, 0.22, 0.05), 0.5, emit=8.0); M_red = new_mat('red_text', (1.0, 0.25, 0.20), 0.5, emit=1.4)
M_redplate = new_mat('red_plate', (0.45, 0.04, 0.04), 0.6); M_puff = new_mat('puff', (0.95, 0.96, 1.0), 0.9, emit=0.5)
M_pipe_hot = metal('pipe_hot', (0.78, 0.80, 0.82), 0.4); M_pipe_cool = metal('pipe_cool', (0.55, 0.75, 0.95), 0.35); M_e85 = new_mat('e85', (0.10, 0.55, 0.25), 0.5)
H_face = new_mat('hud_face', (0.02, 0.03, 0.06), 0.9, emit=0.0); H_rim = new_mat('hud_rim', (1.0, 0.63, 0.10), 0.5, emit=1.4); H_tick = new_mat('hud_tick', (0.9, 0.93, 1.0), 0.5, emit=1.2)
H_needle = new_mat('hud_needle', (1.0, 0.25, 0.15), 0.5, emit=2.2); H_plate = new_mat('hud_plate', (0.03, 0.045, 0.09), 0.9, emit=0.0)

# ================================================================ helpers
def carve(o, cutter, op='DIFFERENCE'):
    """Boolean with the result baked into the mesh (no live modifier at render time)."""
    md = o.modifiers.new('carve', 'BOOLEAN'); md.operation = op; md.object = cutter; md.solver = 'EXACT'
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); o.modifiers.clear(); old = o.data; o.data = me
    bpy.data.meshes.remove(old); bpy.data.objects.remove(cutter, do_unlink=True)

def paint_section(o, mats, bores=()):
    """Faces on the section plane get mats[1]; faces of the bores (x, r, z0, z1) get mats[2]."""
    me = o.data; me.materials.clear()
    for m in mats: me.materials.append(m)
    bpy.context.view_layer.update()
    for p in me.polygons:
        c = o.matrix_world @ p.center; n = p.normal; p.material_index = 0
        if n.y < -0.9 and abs(c.y) < 0.004: p.material_index = 1
        for bx, br, z0, z1 in bores:
            if abs(n.z) < 0.3 and z0 - 0.01 <= c.z <= z1 + 0.01 and abs(math.hypot(c.x - bx, c.y) - br) < 0.03: p.material_index = 2

def xcyl(name, x0, x1, y, z, r, m, seg=24, smooth=True, parent=None):
    o = cyl(name, (x0, y, z), r, x1 - x0, m, seg=seg, smooth=smooth, parent=parent); o.rotation_euler = (0, PI / 2, 0); return o
def ycyl(name, x, y0, y1, z, r, m, seg=24, smooth=True, r2=None, parent=None):
    o = cyl(name, (x, y0, z), r, y1 - y0, m, seg=seg, smooth=smooth, r2=r2, parent=parent); o.rotation_euler = (-PI / 2, 0, 0); return o
def helix(name, x, y, z0, z1, r, turns, wire, m, parent=None):
    n = int(turns * 14); pts = [(x + r * math.cos(2 * PI * turns * i / n), y + r * math.sin(2 * PI * turns * i / n), z0 + (z1 - z0) * i / n) for i in range(n + 1)]
    return tube(name, pts, wire, m, parent=parent, res=3, origin=(x, y, z0))
def area(name, loc, target, size, watts, color=(1, 1, 1)):
    d = bpy.data.lights.new(name, 'AREA'); d.size = size; d.energy = watts; d.color = color
    o = bpy.data.objects.new(name, d); col.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o

def bake(o, path, index, vals):
    """One linear key per frame on o.path[index]; vals[f - 1] is the value at frame f."""
    getattr(o, path)[index] = vals[0]; o.keyframe_insert(data_path=path, frame=1, index=index)
    fc = [c for c in fcurves_of(o) if c.data_path == path and c.array_index == index][0]
    kp = fc.keyframe_points; kp.clear(); kp.add(len(vals)); co = [0.0] * (2 * len(vals)); co[0::2] = range(1, len(vals) + 1); co[1::2] = vals
    kp.foreach_set('co', co); kp.foreach_set('interpolation', [1] * len(vals)); fc.update()

def bake_input(tree, sock, vals):
    """Same as bake(), for a node input (one value per frame)."""
    sock.default_value = vals[0]; sock.keyframe_insert('default_value', frame=1); path = sock.path_from_id('default_value')
    fc = [c for c in fcurves_of(tree) if c.data_path == path][0]
    kp = fc.keyframe_points; kp.clear(); kp.add(len(vals)); co = [0.0] * (2 * len(vals)); co[0::2] = range(1, len(vals) + 1); co[1::2] = vals
    kp.foreach_set('co', co); kp.foreach_set('interpolation', [1] * len(vals)); fc.update()

def gas_mat(name):
    """Flame material: glow and opacity fall off from the top of the object to its bottom. Returns (material, strength socket, opacity socket) for baking."""
    m = new_mat(name, (1.0, 0.24, 0.05), 0.6, emit=1.0); nt = m.node_tree; b = bsdf_of(m); b.inputs['Base Color'].default_value = (0.35, 0.05, 0.01, 1)
    tc = nt.nodes.new('ShaderNodeTexCoord'); sp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Generated'], sp.inputs[0])
    pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; nt.links.new(sp.outputs['Z'], pw.inputs[0]); pw.inputs[1].default_value = 1.6
    v_e = nt.nodes.new('ShaderNodeValue'); v_a = nt.nodes.new('ShaderNodeValue')
    m_e = nt.nodes.new('ShaderNodeMath'); m_e.operation = 'MULTIPLY'; nt.links.new(pw.outputs[0], m_e.inputs[0]); nt.links.new(v_e.outputs[0], m_e.inputs[1]); nt.links.new(m_e.outputs[0], b.inputs['Emission Strength'])
    m_a = nt.nodes.new('ShaderNodeMath'); m_a.operation = 'MULTIPLY'; m_a.use_clamp = True; nt.links.new(sp.outputs['Z'], m_a.inputs[0]); nt.links.new(v_a.outputs[0], m_a.inputs[1]); nt.links.new(m_a.outputs[0], b.inputs['Alpha'])
    return m, v_e.outputs[0], v_a.outputs[0]

def hold(root, t, p, ip='CONSTANT', ease=None): key(root, 'location', t, p, ip=ip, ease=ease)
def lift_away(root, t, h=2.6, d=0.36):
    """Rise off the engine, then jump out of the scene (behind the back wall)."""
    hold(root, t, (0, 0, 0), 'SINE', 'EASE_IN'); hold(root, t + d, (0, 0, h)); hold(root, t + d + DT, FAR)
def drop_in(root, t, h=2.6, d=0.36):
    """Jump back above the engine at t, settle by t + d."""
    hold(root, t, (0, 0, h), 'SINE', 'EASE_OUT'); hold(root, t + d, (0, 0, 0))
def tag(name, lines, pos, t0, t1=None, red=False, d=12.5):
    """World tag that faces the camera. Line sizes are capital heights in % of the screen height when seen from distance d."""
    if isinstance(lines, str): lines = [(lines, 2.0, M_white)]
    lines = [(b, pct / 100.0 * d / (TEXT_SCALE * 0.73), m) for b, pct, m in lines]
    r = label(name, lines, pos=pos, billboard=True, plate=M_redplate if red else None); pop(r, t0)
    if t1 is not None: vanish(r, t1)
    return r

def frame(az, el, d, focus, sy=0.45, sx=0.5):
    """Orbit pose seen from (az, el, d) with `focus` at screen fraction (sx, sy) instead of the centre: keeps the top strip free for the gauges."""
    c, g = orbit(az, el, d, focus); f = (Vector(g) - Vector(c)).normalized(); r = f.cross(Vector((0, 0, 1))).normalized(); u = r.cross(f)
    sh = u * ((sy - 0.5) * d) + r * ((0.5 - sx) * ASPECT * d)
    return (tuple(Vector(c) + sh), tuple(Vector(g) + sh))

# ---------------------------------------------------------------- HUD: things fixed to the screen (children of the camera)
HD = 1.25                                                                # depth in front of the lens
def hud_pos(sx, sy): return ((sx - 0.5) * ASPECT * HD, (0.5 - sy) * HD, -HD)
def hud_label(name, lines, sx, sy, k, t0, t1=None, plate=None, out=0.2, dur=0.28):
    """Kit tag on the screen at fractions (sx, sy); k = text height of a size-1.0 line as a fraction of the screen height."""
    r = label('HUD_' + name, lines, pos=(0, 0, 0), billboard=False, plate=plate or H_plate); r.parent = cam; r.location = hud_pos(sx, sy)
    r.rotation_euler = (0, 0, 0); s = k * HD / TEXT_SCALE; r.scale = (s, s, s); pop(r, t0, dur=dur)
    if t1 is not None: vanish(r, t1, out)
    return r
def dial(name, sx, sy, rad, vmin, vmax, nums, unit, t0, t1):
    """Round gauge: rad = radius as a fraction of the screen width. Returns a function v -> needle angle and the needle object."""
    root = empty('HUD_' + name, hud_pos(sx, sy), parent=cam); s = rad * ASPECT * HD; root.scale = (s, s, s)
    cyl(f'HUD_{name}_face', (0, 0, -0.03), 1.0, 0.03, H_face, seg=56, parent=root)
    tube(f'HUD_{name}_rim', [(math.cos(a * PI / 28), math.sin(a * PI / 28), 0.0) for a in range(57)], 0.045, H_rim, parent=root, res=3)
    ang = lambda v: math.radians(225 - 270 * (v - vmin) / (vmax - vmin))
    for k in range(len(nums)):
        a = math.radians(225 - 270 * k / (len(nums) - 1))
        tk = box(f'HUD_{name}_tick{k}', -0.08, 0.08, -0.022, 0.022, 0.0, 0.012, H_tick, origin='center', parent=root); tk.location = (0.84 * math.cos(a), 0.84 * math.sin(a), 0.006); tk.rotation_euler = (0, 0, a)
        text(f'HUD_{name}_num{k}', nums[k], (0.57 * math.cos(a), 0.57 * math.sin(a), 0.01), 0.21, H_tick, parent=root, rot=(0, 0, 0))
    text(f'HUD_{name}_unit', unit, (0, -0.73, 0.01), 0.15, H_rim, parent=root, rot=(0, 0, 0))
    nd = box(f'HUD_{name}_needle', 0.0, 0.80, -0.03, 0.03, 0.02, 0.04, H_needle, origin='left', parent=root); nd.location = (0, 0, 0.03)
    cyl(f'HUD_{name}_hub', (0, 0, 0.02), 0.09, 0.04, H_tick, seg=20, parent=root)
    pop(root, t0); vanish(root, t1)
    return ang, nd
def needle(nd, ang, pts, jitter=None):
    """pts = [(t, value), ...] linear; jitter = (t0, t1, amplitude) adds a tremble."""
    for t, v in pts: key(nd, 'rotation_euler', t, ang(v), index=2, ip='LINEAR')
    if jitter:
        t0, t1, v0, amp = jitter; t = t0; k = 0
        while t < t1: key(nd, 'rotation_euler', t, ang(v0 + (amp if k % 2 else -amp)), index=2, ip='LINEAR'); t += 0.07; k += 1

# ================================================================ shop: floor, wall, dressing
FLOOR = -1.9
box('ENV_floor', -40, 40, -30, 14, FLOOR - 0.3, FLOOR, M_floor); box('ENV_wall', -40, 40, 9.0, 9.4, FLOOR, 16, M_wall)
box('ENV_stripe', -40, 40, 8.96, 9.0, FLOOR + 2.3, FLOOR + 2.55, M_cut)
box('ENV_cab', 6.4, 9.0, 7.4, 8.9, FLOOR, FLOOR + 3.4, M_cab)
for k in range(5): box(f'ENV_cab_h{k}', 6.9, 8.5, 7.34, 7.4, FLOOR + 0.45 + k * 0.6, FLOOR + 0.53 + k * 0.6, M_chrome)
for k in range(4): tube(f'ENV_tire{k}', [(11.4 + 1.0 * math.cos(a * PI / 12), 7.6 + 1.0 * math.sin(a * PI / 12), FLOOR + 0.42 + k * 0.84) for a in range(25)], 0.42, M_rubber, res=4)
# a generic family SUV parked at the back (plain two-box shape, no brand details)
box('CAR_body', -12.5, -3.6, 5.2, 8.6, FLOOR + 0.9, FLOOR + 3.3, M_car); box('CAR_cabin', -11.9, -5.6, 5.3, 8.5, FLOOR + 3.3, FLOOR + 5.1, M_car)
box('CAR_glass', -11.6, -5.9, 5.22, 5.3, FLOOR + 3.45, FLOOR + 4.85, M_glass); box('CAR_bumper', -12.7, -3.4, 5.1, 8.7, FLOOR + 0.9, FLOOR + 1.5, M_dark)
for k, x in enumerate((-10.6, -5.5)):
    ycyl(f'CAR_wheel{k}', x, 5.0, 5.7, FLOOR + 1.05, 1.05, M_rubber, seg=28); ycyl(f'CAR_hub{k}', x, 4.97, 5.0, FLOOR + 1.05, 0.55, M_alu2, seg=20)

# ================================================================ block: back half, open deck, bores and crankcase opened by the section
CX = (-1.26, -0.42, 0.42, 1.26); BORE = 0.365; DECK = 3.0; ZC = 0.62; RC = 0.40; ROD = 1.64; HEAD = 3.95
PHI = (0.0, PI, PI, 0.0); FIRE = (0.0, 3 * PI, PI, 2 * PI)             # crank-pin phase and firing angle of cylinders 1-4 (order 1-3-4-2)
blk = box('BLOCK_main', -2.0, 2.0, 0.0, 1.2, -0.25, DECK, M_block)
for i, x in enumerate(CX): carve(blk, cyl(f'cut_jacket{i}', (x, 0.0, 2.0), 0.60, DECK - 2.0 + 0.1, None, seg=56))
for i, x in enumerate(CX): carve(blk, cyl(f'cut_bore{i}', (x, 0.0, 1.18), BORE, 1.0, None, seg=56))
carve(blk, box('cut_crank', -1.8, 1.8, -0.2, 0.9, 0.0, 1.24, None))
paint_section(blk, (M_block, M_cut, M_bore_in), [(x, BORE, 1.18, 2.0) for x in CX])
box('BLOCK_pan', -2.0, 2.0, 0.0, 1.2, -0.62, -0.25, M_iron)
for i in range(5): box(f'BLOCK_rib{i}', -2.0 + i * 1.0 - 0.03, -2.0 + i * 1.0 + 0.03, 1.2, 1.25, 0.2, DECK - 0.1, M_alu2)
def ring_half(name, r_out, z0, z1, m_out, m_cut, xs, clip=None):
    """Back half of one or more cylinder walls (r_out outside, BORE inside), section faces painted."""
    o = cyl(name, (xs[0], 0.0, z0), r_out, z1 - z0, m_out, seg=56)
    for x in xs[1:]: carve(o, cyl(name + '_u', (x, 0.0, z0), r_out, z1 - z0, None, seg=56), 'UNION')
    if clip: carve(o, box(name + '_clip', xs[0] - clip, xs[0] + clip, -1.0, 1.0, z0 - 0.1, z1 + 0.1, None), 'INTERSECT')
    for x in xs: carve(o, cyl(name + '_b', (x, 0.0, z0 - 0.1), BORE, z1 - z0 + 0.2, None, seg=56))
    carve(o, box(name + '_f', xs[0] - 3.5, xs[-1] + 3.5, -1.0, 0.0, z0 - 0.2, z1 + 0.2, None))
    paint_section(o, (m_out, m_cut, M_bore_in), [(x, BORE, z0, z1) for x in xs]); return o
liner = ring_half('BLOCK_liners', 0.43, 2.0, DECK, M_block, M_cut, CX)                 # thin cast-in walls standing free in the coolant
cool = cyl('BLOCK_coolant', (CX[0], 0.0, 2.03), 0.585, DECK - 0.1 - 2.03, M_coolant, seg=56)
for x in CX[1:]: carve(cool, cyl('cool_u', (x, 0.0, 2.03), 0.585, DECK - 0.1 - 2.03, None, seg=56), 'UNION')
for x in CX: carve(cool, cyl('cool_b', (x, 0.0, 1.9), 0.432, 1.3, None, seg=56))
carve(cool, box('cool_f', -4, 4, -1.0, 0.0, 1.8, 3.2, None))
cool2 = cyl('BLOCK_coolant2', (CX[0], 0.0, 2.03), 0.595, DECK - 0.1 - 2.03, M_coolant, seg=56)   # what is left of the jacket once the sleeves are in
for x in CX[1:]: carve(cool2, cyl('cool2_u', (x, 0.0, 2.03), 0.595, DECK - 0.1 - 2.03, None, seg=56), 'UNION')
for x in CX: carve(cool2, cyl('cool2_b', (x, 0.0, 1.9), 0.562, 1.3, None, seg=56))
carve(cool2, box('cool2_f', -4, 4, -1.0, 0.0, 1.8, 3.2, None))
sleeves = [ring_half(f'SLEEVE_{i}', 0.56, 2.0, DECK, M_iron, M_cut2, (x,), clip=0.418) for i, x in enumerate(CX)]

# ================================================================ crank, rods, pistons: empties baked per frame, stock and forged parts as children
crank = empty('CRANK_root', (0, 0, ZC))
xcyl('CRANK_main', -2.2, 2.2, 0.0, 0.0, 0.15, M_crank, parent=crank); xcyl('CRANK_pulley', -2.45, -2.2, 0.0, 0.0, 0.46, M_iron, parent=crank)
fly = xcyl('CRANK_fly', 2.2, 2.37, 0.0, 0.0, 0.78, M_iron, seg=40, parent=crank)
for k in range(4): xcyl(f'CRANK_flyhole{k}', 2.37, 2.39, 0.5 * math.sin(k * PI / 2), 0.5 * math.cos(k * PI / 2), 0.10, M_dark, seg=12, parent=crank)   # 4 holes: no strobing up to 3.7 rev/s at 30 fps
pist, rods, P_stock, P_forged, R_stock, R_forged = [], [], [], [], [], []
for i, x in enumerate(CX):
    cz = RC * math.cos(PHI[i])
    xcyl(f'CRANK_pin{i}', x - 0.17, x + 0.17, 0.0, cz, 0.13, M_crank, parent=crank)
    for s in (-1, 1): xcyl(f'CRANK_web{i}{s}', x + s * 0.20 - 0.045, x + s * 0.20 + 0.045, 0.0, cz * 0.25, 0.42, M_iron, seg=32, parent=crank)
    pe = empty(f'PISTON_{i}', (x, 0, 2.0)); pist.append(pe); re_ = empty(f'ROD_{i}', (x, 0, 1.0)); rods.append(re_)
    for kind, mp, lst in (('stock', M_alu, P_stock), ('forged', M_forged, P_forged)):
        g = empty(f'PISTON_{i}_{kind}', (0, 0, 0), parent=pe); lst.append(g)
        cyl(f'PISTON_{i}_{kind}_body', (0, 0, -0.26), BORE - 0.012, 0.52, mp, seg=56, smooth=True, parent=g)
        cyl(f'PISTON_{i}_{kind}_crown', (0, 0, 0.26), BORE - 0.012, 0.04, mp, seg=56, r2=BORE - 0.07, smooth=True, parent=g)
        for k in range(3): cyl(f'PISTON_{i}_{kind}_ring{k}', (0, 0, 0.15 - k * 0.075), BORE - 0.004, 0.028, M_dark, seg=56, parent=g)
        xcyl(f'PISTON_{i}_{kind}_pin', -0.2, 0.2, 0.0, 0.0, 0.07, M_chrome, parent=g)
    for kind, mr, lst, w in (('stock', M_iron, R_stock, 0.075), ('forged', M_forged, R_forged, 0.105)):
        g = empty(f'ROD_{i}_{kind}', (0, 0, 0), parent=re_); lst.append(g)
        box(f'ROD_{i}_{kind}_beam', -w, w, -0.05, 0.05, 0.0, ROD, mr, parent=g)
        xcyl(f'ROD_{i}_{kind}_big', -0.11, 0.11, 0.0, 0.0, 0.21, mr, parent=g); xcyl(f'ROD_{i}_{kind}_small', -0.11, 0.11, 0.0, ROD, 0.12, mr, parent=g)
crack = tube('PISTON_crack', [(-0.10, -BORE + 0.004, 0.27), (-0.04, -BORE + 0.004, 0.12), (-0.13, -BORE + 0.004, 0.02), (-0.05, -BORE + 0.004, -0.12), (-0.12, -BORE + 0.004, -0.25)], 0.014, M_dark, parent=P_stock[0], res=2)
bent = tube('ROD_bent', smooth_path([(0, 0, 0), (0.10, 0, ROD * 0.33), (0.19, 0, ROD * 0.55), (0.07, 0, ROD * 0.8), (0, 0, ROD)], 8), 0.075, M_iron, parent=rods[1], res=4)

# ================================================================ studs and bolts (they stay with the block)
SX = (-1.68, -0.84, 0.0, 0.84, 1.68); bolts, studs = [], []
for k, x in enumerate(SX):
    b = empty(f'BOLT_{k}', (x, -0.03, 0)); cyl(f'BOLT_{k}_s', (0, 0, DECK - 0.45), 0.035, HEAD - DECK + 0.45, M_alu2, seg=10, parent=b); cyl(f'BOLT_{k}_h', (0, 0, HEAD), 0.07, 0.07, M_alu2, seg=6, parent=b); bolts.append(b)
    s_ = empty(f'STUD_{k}', (x, -0.03, 0)); cyl(f'STUD_{k}_s', (0, 0, DECK - 0.95), 0.05, HEAD - DECK + 1.13, M_iron, seg=12, parent=s_); cyl(f'STUD_{k}_n', (0, 0, HEAD), 0.095, 0.11, M_gold, seg=6, parent=s_); studs.append(s_)

# ================================================================ top ends: stock head (A) and Type R head (B), same builder
def build_head(tag_, m_cover, m_lobe, m_sec):
    root = empty(f'HEAD{tag_}_root', (0, 0, 0)); P = dict(root=root, valve={}, spring={}, perf={}, cams=[])
    hd = box(f'HEAD{tag_}_main', -2.0, 2.0, 0.0, 1.2, DECK + 0.02, HEAD, M_alu, parent=root)
    for i, x in enumerate(CX): carve(hd, cyl(f'cut_dome{tag_}{i}', (x, 0.0, DECK - 0.1), BORE - 0.02, 0.38, None, seg=56, r2=0.22))
    paint_section(hd, (M_alu, m_sec, M_bore_in)); box(f'HEAD{tag_}_gasket', -2.0, 2.0, 0.0, 1.2, DECK, DECK + 0.02, M_copper, parent=root)
    for i, x in enumerate(CX):
        for s in (-1, 1):                                              # s = -1 intake valve, +1 exhaust valve (one of each drawn per cylinder)
            vx = x + s * 0.17; ve = empty(f'VALVE{tag_}_{i}{s}', (vx, -0.05, DECK + 0.10), parent=root); P['valve'][(i, s)] = ve
            g0 = empty(f'VALVE{tag_}_{i}{s}_std', (0, 0, 0), parent=ve); g1 = empty(f'VALVE{tag_}_{i}{s}_perf', (0, 0, 0), parent=ve)
            for g, mv_, mr_ in ((g0, M_chrome, M_copper), (g1, M_inconel if s == 1 else M_chrome, M_ti)):
                cyl(f'{g.name}_head', (0, 0, 0), 0.135, 0.06, mv_, seg=28, r2=0.05, smooth=True, parent=g); cyl(f'{g.name}_stem', (0, 0, 0.06), 0.032, 1.56, mv_, seg=12, parent=g)
                cyl(f'{g.name}_ret', (0, 0, 1.50), 0.125, 0.05, mr_, seg=20, parent=g)
            sp0 = helix(f'SPRING{tag_}_{i}{s}', vx, -0.05, HEAD + 0.02, HEAD + 0.65, 0.105, 5.5, 0.022, M_chrome, parent=root)
            sp1 = empty(f'SPRINGP{tag_}_{i}{s}', (vx, -0.05, HEAD + 0.02), parent=root)
            helix(f'SPRINGP{tag_}_{i}{s}_o', 0, 0, 0, 0.63, 0.112, 7.0, 0.030, M_blue_st, parent=sp1); helix(f'SPRINGP{tag_}_{i}{s}_i', 0, 0, 0, 0.63, 0.062, 8.0, 0.020, M_blue_st, parent=sp1)
            P['spring'][(i, s)] = (sp0, sp1); P['perf'][(i, s)] = (g0, g1)
    for c, (cy_, cz_) in enumerate(((-0.05, HEAD + 0.95), (0.42, HEAD + 1.22))):
        cam_ = empty(f'CAM{tag_}_{c}', (0, cy_, cz_), parent=root); P['cams'].append(cam_)
        xcyl(f'CAM{tag_}_{c}_shaft', -2.1, 2.1, 0, 0, 0.075, M_chrome, parent=cam_); xcyl(f'CAM{tag_}_{c}_gear', -2.4, -2.12, 0, 0, 0.36, M_iron, seg=28, parent=cam_)
        for i, x in enumerate(CX):
            for s in (-1, 1):
                lb = xcyl(f'CAM{tag_}_{c}_lobe{i}{s}', x + s * 0.17 - 0.06, x + s * 0.17 + 0.06, 0, 0.03, 0.15, m_lobe, seg=20, parent=cam_); lb.scale = (1.0, 0.70, 1.0)
    box(f'HEAD{tag_}_cover', -2.0, 2.0, 0.75, 1.2, HEAD, HEAD + 1.75, m_cover, parent=root); box(f'HEAD{tag_}_cover_top', -2.0, 2.0, 0.60, 1.2, HEAD + 1.6, HEAD + 1.75, m_cover, parent=root)
    for i, x in enumerate(CX): box(f'HEAD{tag_}_coil{i}', x - 0.16, x + 0.16, 0.7, 1.05, HEAD + 1.75, HEAD + 1.95, M_dark, parent=root)
    return P
HA = build_head('A', M_cover_a, M_alu2, M_cut_a); HB = build_head('B', M_cover_b, M_gold, M_cut_b)

# ================================================================ boost parts: turbo, manifold, charge pipes, intercooler (children of one root)
BOOST = empty('BOOST_root', (0, 0, 0)); TX, TY, TZ = 3.15, 0.65, 4.55
def ring(name, y, R, r, m): return tube(name, [(TX + R * math.cos(a * PI / 18), y, TZ + R * math.sin(a * PI / 18)) for a in range(37)], r, m, parent=BOOST, res=6)
ring('TURBO_comp_volute', TY - 0.95, 0.66, 0.30, M_alu); ycyl('TURBO_comp_face', TX, TY - 1.22, TY - 0.68, TZ, 0.66, M_alu, seg=48, parent=BOOST)
ycyl('TURBO_inlet', TX, TY - 1.72, TY - 1.2, TZ, 0.50, M_alu, seg=40, r2=0.44, parent=BOOST); ycyl('TURBO_inlet_in', TX, TY - 1.725, TY - 1.3, TZ, 0.40, M_dark, seg=40, parent=BOOST)
wheel = empty('TURBO_wheel_root', (TX, TY - 1.5, TZ), parent=BOOST)
ycyl('TURBO_wheel', 0, -0.12, 0.2, 0, 0.12, M_chrome, seg=20, r2=0.30, parent=wheel); ycyl('TURBO_nut', 0, -0.20, -0.1, 0, 0.075, M_copper, seg=6, parent=wheel)
for k in range(9):
    a = k * 2 * PI / 9; bl = box(f'TURBO_blade{k}', -0.015, 0.015, -0.13, 0.13, 0.10, 0.37, M_chrome, origin='center', parent=wheel)
    bl.location = (0.235 * math.sin(a), 0.0, 0.235 * math.cos(a)); bl.rotation_euler = (0, a, 0.5)
ycyl('TURBO_core', TX, TY - 0.68, TY - 0.2, TZ, 0.34, M_alu2, parent=BOOST); ring('TURBO_turb_volute', TY + 0.12, 0.60, 0.30, M_iron)
ycyl('TURBO_turb_face', TX, TY - 0.2, TY + 0.42, TZ, 0.60, M_iron, seg=48, parent=BOOST); ycyl('TURBO_exit', TX, TY + 0.42, TY + 1.0, TZ, 0.42, M_iron, seg=32, parent=BOOST)
for i, x in enumerate(CX): tube(f'MANI_{i}', smooth_path([(x, 1.2, HEAD - 0.45), (x + 0.2, 1.8, HEAD - 0.35), (2.2, 1.75, HEAD + 0.05), (TX - 0.35, TY + 0.15, TZ - 0.60)], 10), 0.13, M_copper, parent=BOOST, res=4)
PA = smooth_path([(TX + 0.66, TY - 0.95, TZ - 0.1), (TX + 0.95, TY - 0.95, TZ - 0.9), (TX + 0.3, 0.2, HEAD - 0.1), (2.0, 0.45, HEAD - 0.45)], 12)       # turbo straight into the head
pipeA = tube('PIPE_direct', PA, 0.21, M_pipe_hot, parent=BOOST, res=6)
PB = smooth_path([(TX + 0.66, TY - 0.95, TZ - 0.1), (TX + 1.0, TY - 0.95, TZ - 0.9), (TX + 0.95, -0.7, 2.6), (3.75, -1.0, 1.55)], 12)                 # turbo to the intercooler
PC = smooth_path([(2.75, -1.0, 1.55), (2.35, -0.9, 2.5), (2.25, -0.2, HEAD - 0.5), (2.0, 0.45, HEAD - 0.45)], 12)                                     # intercooler to the head
pipeB = tube('PIPE_hot', PB, 0.21, M_pipe_hot, parent=BOOST, res=6); pipeC = tube('PIPE_cool', PC, 0.21, M_pipe_cool, parent=BOOST, res=6)
IC = empty('IC_root', (3.25, -1.0, 0.85), parent=BOOST)
box('IC_core', -0.8, 0.8, -0.25, 0.25, -0.7, 0.65, M_alu2, parent=IC)
for k in range(13): box(f'IC_fin{k}', -0.8, 0.8, -0.29, -0.25, -0.65 + k * 0.1, -0.60 + k * 0.1, M_alu, parent=IC)
for s, x in ((0, -0.95), (1, 0.8)): box(f'IC_tank{s}', x, x + 0.15, -0.3, 0.28, -0.75, 0.70, M_alu, parent=IC)
M_fuel = new_mat('fuel_can', (0.75, 0.08, 0.06), 0.45, spec=0.4)
E85 = empty('FUEL_root', (5.0, -0.4, FLOOR))
box('FUEL_cart_top', -0.75, 0.75, -0.55, 0.55, 2.95, 3.1, M_stand, parent=E85)
for kx in (-0.65, 0.65):
    for ky in (-0.45, 0.45): box(f'FUEL_cart_leg{kx}{ky}', kx - 0.06, kx + 0.06, ky - 0.06, ky + 0.06, 0.0, 2.95, M_stand, parent=E85)
CAN = empty('FUEL_can', (0, 0, 3.1), parent=E85)
box('FUEL_can_body', -0.5, 0.5, -0.3, 0.3, 0.0, 1.45, M_fuel, parent=CAN); box('FUEL_can_cap', -0.12, 0.12, -0.1, 0.1, 1.45, 1.62, M_dark, parent=CAN)
box('FUEL_can_grip', 0.18, 0.46, -0.06, 0.06, 1.45, 1.58, M_dark, parent=CAN)
T_bensin = text('FUEL_txt_bensin', 'BENSIN', (0, -0.31, 0.75), 0.17, M_white, parent=CAN); T_e85 = text('FUEL_txt_e85', 'E85', (0, -0.31, 0.75), 0.36, M_white, parent=CAN)

# ================================================================ stand
for s, y in ((0, -0.9), (1, 1.6)): box(f'STAND_rail{s}', -2.6, 2.6, y - 0.09, y + 0.09, FLOOR + 0.16, FLOOR + 0.34, M_stand)
for s, x in ((0, -1.5), (1, 1.5)):
    box(f'STAND_cross{s}', x - 0.09, x + 0.09, -0.9, 1.6, FLOOR + 0.16, FLOOR + 0.34, M_stand)
    box(f'STAND_post{s}', x - 0.1, x + 0.1, 0.45, 0.65, FLOOR + 0.34, -0.62, M_stand); box(f'STAND_cradle{s}', x - 0.5, x + 0.5, 0.2, 0.9, -0.74, -0.62, M_stand)
for x in (-2.5, 2.5):
    for y in (-0.9, 1.6): xcyl(f'STAND_wheel{x}{y}', x - 0.07, x + 0.07, y, FLOOR + 0.16, 0.16, M_rubber)

# ================================================================ cue times
t_turbo = T('S03', 'turbo'); t_boost = T('S05', 'bar'); t_crack = T('S06', 'retak'); t_bend = T('S06', 'bengkok'); t_forge = T('S07', 'diganti')
t_lift = T('S08', 'terangkat'); t_stud = T('S08', 'diganti') + 0.1; t_top = T('S09'); t_sleeve = T('S10', 'tanam'); t_ch2 = T('S11')
t_stall = T('S12', 'napasnya'); t_swap = T('S13', 'menukarnya'); t_newhead = T('S13', 'kepala'); t_float = T('S15', 'kewalahan'); t_hit = T('S15', 'dihantam') + 0.12
t_spring = T('S16', 'diganti'); t_inconel = T('S16', 'Inconel'); t_hot = T('S18', 'panas'); t_knock = T('S18', 'meledak') + 0.05; t_ic = T('S19', 'intercooler')
t_e85 = T('S19', 'etanol'); t_full = T('S20', 'seribu'); t_orig = T('S21', 'Bloknya')

# ================================================================ one crank-angle curve for the whole video
def lerp_pts(pts, t):
    if t <= pts[0][0]: return pts[0][1]
    for (a, va), (b, vb) in zip(pts, pts[1:]):
        if t <= b: return va + (vb - va) * (t - a) / max(b - a, 1e-6)
    return pts[-1][1]
SPEED = [(0.0, 0.5), (T('S05'), 0.5), (t_boost, 2.4), (T('S06'), 2.4), (t_crack, 0.0),                       # idle, boost comes on, something lets go
         (t_ch2 + 0.5, 0.0), (t_stall, 2.2), (T('S12', end=True), 1.6), (T('S13'), 0.0),                      # revs climb, the head runs out of breath
         (T('S15'), 0.0), (T('S15', 'sembilan'), 2.8), (T('S15', 'per'), 2.8), (t_float, 0.30), (t_hit, 0.30), (t_hit + 0.07, 0.0),   # high revs, then slow motion for the valve
         (T('S17'), 0.0), (T('S18'), 2.0), (t_ic, 2.0), (T('S20'), 1.8), (t_full, 3.3), (T('S21'), 3.3), (t_orig, 0.35), (T('S22'), 0.35), (T('S22', 'enam'), 1.2), (DUR, 1.2)]   # rev/s on screen
TH = [0.0] * (NF + 1)
for f in range(1, NF + 1): TH[f] = TH[f - 1] + 2 * PI * lerp_pts(SPEED, (f - 1) * DT) * DT
def land(t_evt, target, t0, t1, cyc=4 * PI):
    """Make the crank angle at t_evt equal target (mod cyc) by running the engine a little faster or slower between t0 and t1 (t1 <= t_evt).
    The angle gained inside the window is scaled, so the engine never runs backwards and there is no jump."""
    f0, f1, fe = int(round(fr(t0))), int(round(fr(t1))), int(round(fr(t_evt))); d = (target - TH[fe]) % cyc
    if d > cyc / 2: d -= cyc
    gain = TH[f1] - TH[f0]; k = 1.0 + d / gain; assert 0.5 < k < 1.6, k
    for g in range(f0 + 1, NF + 1): TH[g] = TH[f0] + k * (TH[g] - TH[f0]) if g <= f1 else TH[g] + d
    return k
HIT_ANGLE = 0.349                                                        # crank angle before TDC at which the crown reaches the hanging valve (0.03 below its top position)
k1 = land(t_hit, 2 * PI - HIT_ANGLE, T('S15'), t_float)                  # cylinder 1 comes up on the exhaust stroke and meets the valve exactly on the word
k2 = land(t_knock, 4 * PI - 0.75, T('S17') + 0.2, t_knock)               # cylinder 1 is still coming up on compression when the charge goes off
print('engine phase landing: speed factors %.2f and %.2f' % (k1, k2))
LIFT = 0.16
def vlift(c, s):
    a, b = (PI - 0.6, 2 * PI + 0.2) if s == 1 else (2 * PI - 0.2, 3 * PI + 0.6)
    return LIFT * math.sin(PI * (c - a) / (b - a)) ** 2 if a < c < b else 0.0
amp_pts = [(0.0, 0.50), (T('S05'), 0.50), (t_boost, 0.95), (t_knock - 0.3, 0.95), (t_knock, 0.55), (t_ic, 0.55), (t_ic + 0.5, 0.95), (T('S20'), 0.95), (t_full, 1.15), (DUR, 1.15)]
vz, sz, fl, kn = {}, {}, [[] for _ in CX], [[] for _ in CX]; gz, gs, ge, ga = [[] for _ in CX], [[] for _ in CX], [[] for _ in CX], [[] for _ in CX]; pz = [[] for _ in CX]; ry, rz, rb = [[] for _ in CX], [[] for _ in CX], [[] for _ in CX]
for k in list(HA['valve'].keys()): vz[k] = []; sz[k] = []
for f in range(1, NF + 1):
    th = TH[f]; t = (f - 1) * DT; run = lerp_pts(SPEED, t) > 0.02; A = lerp_pts(amp_pts, t)
    for i in range(4):
        a = th + PHI[i]; yb = RC * math.sin(a); zb = ZC + RC * math.cos(a); zp = zb + math.sqrt(ROD ** 2 - yb ** 2)
        pz[i].append(zp); ry[i].append(yb); rz[i].append(zb); rb[i].append(math.asin(yb / ROD))
        c = (th - FIRE[i]) % (4 * PI)
        fl[i].append(max(A * math.exp(-c / 0.55), 0.001) if (c < 1.9 and run) else 0.001)
        burn = c < 2.75 and run
        gz[i].append(max(DECK + 0.03 - (zp + 0.30), 0.02) if burn else 0.001); gs[i].append(1.0 if burn else 0.001); ge[i].append(14.0 * A * math.exp(-c / 0.9) if burn else 0.0); ga[i].append(1.6 * math.exp(-c / 1.3) if burn else 0.0)
        early = c - (4 * PI - 0.75); kn[i].append(max(min(1.0, 1.35 * math.exp(-early / 0.45)), 0.001) if (0 <= early and t_knock - 0.2 <= t < t_ic and run) else 0.001)
        for s in (-1, 1):
            L = vlift(c, s)
            if i == 0 and s == 1 and t_float <= t < t_spring: L = max(L, 0.17 * min((t - t_float) / 0.3, 1.0))      # the exhaust valve of cylinder 1 hangs open
            vz[(i, s)].append(DECK + 0.10 - L); sz[(i, s)].append((0.63 - L) / 0.63)
bake(crank, 'rotation_euler', 0, [-TH[f] for f in range(1, NF + 1)])
for i in range(4):
    bake(pist[i], 'location', 2, pz[i]); bake(rods[i], 'location', 1, ry[i]); bake(rods[i], 'location', 2, rz[i]); bake(rods[i], 'rotation_euler', 0, rb[i])
for P in (HA, HB):
    for k, ve in P['valve'].items():
        bake(ve, 'location', 2, vz[k]); sp0, sp1 = P['spring'][k]; bake(sp0, 'scale', 2, sz[k]); bake(sp1, 'scale', 2, sz[k])
    for c, cam_ in enumerate(P['cams']): bake(cam_, 'rotation_euler', 0, [-(TH[f] / 2 + c * 0.9) for f in range(1, NF + 1)])
spin = [0.0]
for f in range(2, NF + 1): spin.append(spin[-1] + 2 * PI * DT * (0.0 if (f - 1) * DT < t_turbo + 0.9 else 0.5 + 0.3 * lerp_pts(SPEED, (f - 1) * DT)))   # under 20 degrees a frame: 9 blades do not strobe
bake(wheel, 'rotation_euler', 1, spin)
for i, x in enumerate(CX):
    fo = sphere(f'FLASH_{i}', (x, -0.04, DECK - 0.03), 0.30, M_fire, sx=1.0, sy=0.6, sz=0.42); ko = sphere(f'KNOCK_{i}', (x, -0.10, DECK - 0.12), 0.34, M_knock, sx=1.0, sy=0.6, sz=0.7, seg=24)
    mg, s_e, s_a = gas_mat(f'gas{i}'); go = cyl(f'GAS_{i}', (x, 0.0, DECK + 0.03), BORE - 0.02, 1.0, mg, seg=40, down=True, smooth=True); go.visible_shadow = False
    bake(go, 'scale', 2, gz[i]); bake(go, 'scale', 0, gs[i]); bake(go, 'scale', 1, gs[i]); bake_input(mg.node_tree, s_e, ge[i]); bake_input(mg.node_tree, s_a, ga[i])
    for o_, vals in ((fo, fl[i]), (ko, kn[i])):
        o_.visible_shadow = False
        base = tuple(o_.scale)
        for ax in range(3): bake(o_, 'scale', ax, [v * base[ax] for v in vals])

# ================================================================ cues: who is on the engine when
for i in range(4):                                                      # stock pistons and rods until they are replaced
    ts_ = t_forge + i * 0.07                                             # the new part grows in fast; the old one goes when the new one is nearly full size
    show(P_stock[i], 0.0, ts_ + 0.08); pop(P_forged[i], ts_, dur=0.16)
    if i == 1: show(R_stock[i], 0.0, t_bend); show(bent, t_bend, ts_ + 0.08)
    else: show(R_stock[i], 0.0, ts_ + 0.08)
    pop(R_forged[i], ts_, dur=0.16)
pop(crack, t_crack)
for k, b in enumerate(bolts): show(b, 0.0, t_stud - 0.2 + k * 0.03)
for k, s_ in enumerate(studs):
    hidden_until(s_, t_stud); key(s_, 'scale', t_stud + k * 0.04, (1, 1, 1), ip='CONSTANT'); travel(s_, [(t_stud + k * 0.04, (SX[k], -0.03, 2.2)), (t_stud + 0.3 + k * 0.04, (SX[k], -0.03, 0.0))])
# head A: lifts when the boost wins, comes off for the top view, leaves for good at the swap; head B arrives
hold(HA['root'], 0.0, (0, 0, 0)); hold(HA['root'], t_lift, (0, 0, 0), 'LINEAR'); hold(HA['root'], t_lift + 0.18, (0, 0, 0.17), 'LINEAR'); hold(HA['root'], t_stud + 0.5, (0, 0, 0.17), 'LINEAR'); hold(HA['root'], t_stud + 0.7, (0, 0, 0))
lift_away(HA['root'], t_top); drop_in(HA['root'], t_ch2 - 0.05); lift_away(HA['root'], t_swap, h=3.2, d=0.55)
hold(HB['root'], 0.0, FAR); drop_in(HB['root'], t_newhead, h=3.4, d=0.6)
hold(BOOST, 0.0, FAR); drop_in(BOOST, t_turbo, h=3.0, d=0.55); lift_away(BOOST, t_top); drop_in(BOOST, t_ch2 - 0.05)
show(pipeA, 0.0, t_ic); pop(pipeB, t_ic + 0.15); pop(pipeC, t_ic + 0.3); pop(IC, t_ic)
pop(E85, T('S17') + 0.25); vanish(E85, T('S20') - 0.15)
show(T_bensin, 0.0, t_e85); show(T_e85, t_e85); tint(M_fuel, [(0.0, (0.75, 0.08, 0.06), 1.0), (t_e85 - 0.03, (0.75, 0.08, 0.06), 1.0), (t_e85 + 0.03, (0.08, 0.50, 0.22), 1.0)])
key(CAN, 'scale', t_e85 - 0.05, (1, 1, 1)); key(CAN, 'scale', t_e85 + 0.1, (1.25, 1.25, 1.25)); key(CAN, 'scale', t_e85 + 0.3, (1, 1, 1))
tint(M_pipe_hot, [(0.0, (0.78, 0.80, 0.82), 1.0), (t_hot - 0.5, (0.78, 0.80, 0.82), 1.0), (t_hot + 0.3, (1.0, 0.32, 0.10), 1.0), (DUR, (1.0, 0.32, 0.10), 1.0)])
# open deck: thin walls in the coolant, then sleeves
show(liner, 0.0, t_sleeve + 0.55); show(cool, 0.0, t_sleeve + 0.55); show(cool2, t_sleeve + 0.55)
key(liner, 'scale', T('S09', 'berdiri'), (1, 1, 1), ip='LINEAR'); t = T('S09', 'berdiri'); k = 0
while t < T('S09', end=True): key(liner, 'scale', t, (1.0, 1.03 if k % 2 else 0.985, 1.0), ip='LINEAR'); t += 0.11; k += 1
key(liner, 'scale', T('S09', end=True), (1, 1, 1), ip='CONSTANT')
for i, sl in enumerate(sleeves):
    hidden_until(sl, t_sleeve); key(sl, 'scale', t_sleeve + i * 0.05, (1, 1, 1), ip='CONSTANT'); travel(sl, [(t_sleeve + i * 0.05, (CX[i], 0, 4.6)), (t_sleeve + 0.38 + i * 0.05, (CX[i], 0, 2.004))])
M_leak = new_mat('leak', (1.0, 0.11, 0.02), 0.5, emit=2.6); leak = box('LEAK_glow', -2.0, 2.0, -0.05, 0.0, DECK, DECK + 0.17, M_leak); leak.visible_shadow = False
show(leak, t_lift + 0.08, t_stud + 0.62)
for k in range(9):
    fl_ = cyl(f'LEAK_flame{k}', (-1.76 + k * 0.44, -0.10, DECK + 0.06), 0.085, 0.42 + 0.10 * (k % 3), M_leak, seg=10, r2=0.0, smooth=True); fl_.visible_shadow = False; fl_.rotation_euler = (math.radians(38), 0, 0)
    show(fl_, t_lift + 0.08 + 0.02 * (k % 4), t_stud + 0.62); t = t_lift + 0.12 + 0.03 * (k % 3); j = k
    while t < t_stud + 0.6: key(fl_, 'scale', t, (1.0, 1.0, 1.25 if j % 2 else 0.55), ip='LINEAR'); t += 0.08; j += 1
# valve gear upgrades on head B
for k, (sp0, sp1) in HB['spring'].items():
    i, s = k; g0, g1 = HB['perf'][k]; dt_ = (i * 2 + (s + 1) // 2) * 0.04
    for o_ in (sp0, g0): o_.scale = (1, 1, 1)
    key(sp0, 'scale', 0.0, 1.0, index=0, ip='CONSTANT'); key(sp0, 'scale', t_spring + dt_, 0.001, index=0, ip='CONSTANT'); key(sp0, 'scale', 0.0, 1.0, index=1, ip='CONSTANT'); key(sp0, 'scale', t_spring + dt_, 0.001, index=1, ip='CONSTANT')
    key(sp1, 'scale', 0.0, 0.001, index=0, ip='CONSTANT'); key(sp1, 'scale', t_spring + dt_, 1.0, index=0, ip='CONSTANT'); key(sp1, 'scale', 0.0, 0.001, index=1, ip='CONSTANT'); key(sp1, 'scale', t_spring + dt_, 1.0, index=1, ip='CONSTANT')
    tv = t_inconel + dt_ * 0.6 if s == 1 else t_spring + dt_
    show(g0, 0.0, tv); show(g1, tv)
for k, (sp0, sp1) in HA['spring'].items():
    g0, g1 = HA['perf'][k]; g1.scale = Z
    for ax in (0, 1): sp1.scale[ax] = 0.001
star = empty('HIT_star', (CX[0] + 0.17, -0.42, DECK - 0.03))
for k in range(10):
    L = 0.36 if k % 2 == 0 else 0.20; a_ = k * 2 * PI / 10
    sp_ = box(f'HIT_spike{k}', 0.05, L, -0.01, 0.01, -0.028, 0.028, M_fire if k % 2 == 0 else M_knock, origin='left', parent=star); sp_.location = (0.05 * math.cos(a_), 0, 0.05 * math.sin(a_)); sp_.rotation_euler = (0, -a_, 0); sp_.visible_shadow = False
sphere('HIT_core', (0, 0, 0), 0.075, M_fire, parent=star).visible_shadow = False
pop(star, t_hit, dur=0.12, over=1.5); pulse(star, t_hit + 0.14, t_hit + 0.5, period=0.12, amp=0.25); vanish(star, t_hit + 0.5)

# ================================================================ camera poses (the focus sits below the top strip that holds the gauges)
D_HERO, D_CUT, D_PIST, D_GAP, D_TOP, D_SWAP, D_HEAD, D_AIR, D_KNOCK, D_ORIG = 15.5, 13.5, 7.0, 7.0, 7.8, 12.0, 5.6, 13.5, 6.5, 10.0
P_open = frame(66, 10, 13.5, (0.3, 0.0, 2.0), 0.50); P_hero = frame(66, 10, D_HERO, (0.9, 0.0, 2.2), 0.48); P_hero2 = frame(71, 9, 14.5, (1.2, 0.0, 2.4), 0.47); P_cut = frame(90, 5, D_CUT, (1.0, 0.0, 2.6), 0.47)
P_pist = frame(92, 4, D_PIST, (0.0, 0.0, 1.9), 0.42); P_gap = frame(85, 9, D_GAP, (0.0, 0.0, 3.2), 0.45); P_top = frame(90, 52, D_TOP, (0.0, 0.2, 3.0), 0.47)
P_swap = frame(88, 8, D_SWAP, (0.4, 0.0, 3.8), 0.47); P_frank = frame(80, 7, 12.5, (0.8, 0.0, 2.3), 0.47); P_head = frame(96, 8, D_HEAD, (-0.75, 0.0, 3.6), 0.44)
P_air = frame(60, 9, D_AIR, (2.0, -0.3, 2.6), 0.46); P_knock = frame(93, 5, D_KNOCK, (-0.6, 0.0, 2.7), 0.44); P_orig = frame(86, 6, D_ORIG, (0.0, 0.0, 1.3), 0.45)

# ================================================================ tags in the scene (they face the camera)
tag('TAG_turbo', [('TURBO', 2.2, M_white)], (TX - 0.2, -1.9, TZ + 1.55), t_turbo + 0.5, T('S04') - 0.1, d=14.5)
tag('TAG_crack', [('RETAK', 2.0, M_white)], (CX[0] + 0.12, -1.0, 2.72), t_crack, t_forge, red=True, d=D_PIST)
tag('TAG_bend', [('BENGKOK', 2.0, M_white)], (CX[1] + 0.85, -1.0, 1.15), t_bend, t_forge, red=True, d=D_PIST)
tag('TAG_forged', [('PISTON + SETANG', 1.7, M_white), ('TEMPA', 2.4, M_yellow)], (0.0, -1.0, 1.2), T('S07', 'tempa'), T('S08') + 0.2, d=D_PIST)
tag('TAG_stud', [('STUD BAJA', 2.0, M_yellow)], (0.9, -1.0, HEAD + 0.6), T('S08', 'stud'), t_top, d=D_GAP)
tag('TAG_deck', [('DINDING TIPIS', 1.9, M_white), ('DIKEPUNG AIR', 1.9, M_white)], (-0.95, -0.2, DECK + 1.5), T('S09', 'berdiri'), t_sleeve - 0.1, d=D_TOP)
tag('TAG_sleeve', [('SELONGSONG', 1.9, M_white), ('BESI', 2.4, M_yellow)], (0.95, -0.2, DECK + 1.5), t_sleeve + 0.5, t_ch2 - 0.3, d=D_TOP)
tag('TAG_eco', [('KEPALA IRIT', 2.0, M_white), ('MENTOK 6.500 RPM', 2.0, M_white)], (-0.2, -1.0, HEAD + 0.55), T('S12', 'irit'), t_swap, red=True, d=D_CUT)
tag('TAG_typer', [('KEPALA TYPE R', 2.0, M_white), ('VTEC DI 2 NOKEN AS', 1.8, M_yellow)], (0.7, -1.0, HEAD + 2.0), T('S13', 'Type') + 0.55, T('S14') + 0.1, d=D_SWAP)
tag('TAG_k24', [('BLOK K24', 2.0, M_white)], (-0.9, -1.0, 2.0), T('S14', 'Blok'), T('S15') - 0.1, d=12.5)
tag('TAG_k20', [('KEPALA K20', 2.0, M_white)], (0.75, -1.0, HEAD + 0.55), T('S14', 'kepala'), T('S15') - 0.1, d=12.5)
tag('TAG_frank', [('FRANKENSTEIN', 2.6, M_yellow)], (0.0, -1.4, 0.95), T('S14', 'Frankenstein'), T('S15') - 0.1, d=12.5)
tag('TAG_float', [('KLEP MELAYANG', 2.0, M_white)], (CX[0] + 1.0, -0.8, DECK + 0.42), t_float + 0.2, T('S16') + 0.1, red=True, d=D_HEAD)
tag('TAG_spring', [('PER LEBIH KERAS', 1.9, M_white)], (CX[1] + 0.2, -0.8, HEAD + 0.36), T('S16', 'keras'), T('S17'), d=D_HEAD)
tag('TAG_inconel', [('KLEP INCONEL', 1.9, M_yellow)], (CX[0] + 1.0, -0.8, DECK + 0.42), t_inconel + 0.3, T('S17'), d=D_HEAD)
tag('TAG_knock', [('NGELITIK', 2.6, M_white)], (CX[0] + 1.25, -1.0, DECK + 0.38), T('S18', 'ngelitik'), T('S19') + 0.1, red=True, d=D_KNOCK)
tag('TAG_ic', [('INTERCOOLER', 2.0, M_white)], (3.3, -1.9, 2.35), t_ic + 0.4, T('S20') - 0.1, d=D_AIR)
tag('TAG_e85', [('ETANOL', 2.0, M_yellow)], (5.0, -0.9, FLOOR + 5.3), t_e85 + 0.2, T('S20') - 0.1, d=D_AIR)
tag('TAG_blok', [('BLOK', 2.2, M_yellow)], (-1.3, -1.0, 2.35), t_orig, T('S22') - 0.1, d=D_ORIG)
tag('TAG_kruk', [('KRUK AS BAWAAN', 2.0, M_yellow)], (0.9, -1.0, -0.15), T('S21', 'kruk'), T('S22') - 0.1, d=D_ORIG)
for m_, c_ in ((M_block, (1.0, 0.63, 0.10)), (M_crank, (1.0, 0.63, 0.10))):                                   # the two original parts glow
    b = bsdf_of(m_); b.inputs['Emission Color'].default_value = (*c_, 1)
    for t, v in ((0.0, 0.0), (t_orig - 0.1, 0.0), (t_orig + 0.4, 0.55), (T('S22') - 0.4, 0.55), (T('S22'), 0.0)): key_input(b.inputs['Emission Strength'], t, v)

# ================================================================ HUD: top strip of the screen. Left: gauge. Right: chapter banner and its value. Sizes are fractions of the screen height.
M_cool = new_mat('cool_text', (0.45, 0.80, 1.0), 0.5, emit=1.4)
HPX, HPY = 0.705, 0.155
hud_label('engine', [('MESIN K24', 0.030, M_white), ('HONDA CR-V 2.4 L', 0.018, M_white)], 0.265, 0.150, 1.0, 0.5, T('S03') + 0.1)
hud_label('hp160', [('160', 0.050, M_white), ('TENAGA KUDA', 0.020, M_white)], HPX, HPY, 1.0, T('S01', 'seratus'), T('S02', 'seribu'), out=0.03)
hud_label('hp1000', [('1.000+', 0.050, M_yellow), ('TENAGA KUDA', 0.020, M_white)], HPX, HPY, 1.0, T('S02', 'seribu'), T('S03') + 0.1)
for k, (w, tw) in enumerate((('TEKANAN', T('S03', 'kalahkan')), ('PUTARAN', T('S03', 'tiga')), ('PANAS', T('S03', 'musuh')))):
    hud_label(f'enemy{k}', [(f'{k + 1}   {w}', 0.028, M_white)], 0.30, 0.100 + k * 0.060, 1.0, tw, T('S04') + 0.1 + k * 0.04)
BX, BY, VY = 0.63, 0.118, 0.192
for k, (w, ta, tb) in enumerate((('TEKANAN', T('S04', 'pertama'), t_ch2 - 0.3), ('PUTARAN', T('S11', 'kedua'), T('S17') - 0.1), ('PANAS', T('S17', 'ketiga'), T('S20') - 0.1))):
    hud_label(f'chap{k}', [(f'MUSUH {k + 1}', 0.022, M_white), (w, 0.036, M_yellow)], BX, BY, 1.0, ta, tb)
GX, GY, GR = 0.175, 0.158, 0.13
a_b, n_b = dial('boost', GX, GY, GR, 0.0, 3.0, ['0', '1', '2', '3'], 'BAR', T('S05') - 0.1, t_top - 0.1)
needle(n_b, a_b, [(0.0, 0.0), (T('S05'), 0.0), (T('S05', 'sampai'), 0.6), (t_boost, 2.2), (t_crack - 0.05, 2.2), (t_crack + 0.3, 0.0)], jitter=(t_boost + 0.1, t_crack - 0.1, 2.2, 0.05))
a_r, n_r = dial('rpm', GX, GY, GR, 0.0, 10.0, ['0', '2', '4', '6', '8', '10'], 'RPM x1000', t_ch2 + 0.35, T('S17') - 0.15)
needle(n_r, a_r, [(0.0, 0.0), (t_ch2 + 0.5, 0.8), (t_stall, 6.5), (T('S12', end=True), 6.4), (T('S13'), 0.0), (T('S15'), 0.0), (T('S15', 'sembilan'), 9.3), (t_float - 0.1, 9.3), (t_float + 0.2, 9.1), (t_hit, 9.1), (t_hit + 0.3, 0.0)],
       jitter=(t_stall + 0.1, T('S12', end=True) - 0.1, 6.4, 0.12))
a_t, n_t = dial('temp', GX, GY, GR, 0.0, 4.0, ['C', '', '', '', 'H'], 'SUHU UDARA', T('S17', 'panas'), T('S20') - 0.15)
needle(n_t, a_t, [(0.0, 1.0), (T('S18'), 1.0), (t_hot + 0.3, 3.7), (t_ic + 0.3, 3.7), (t_ic + 1.1, 1.0)], jitter=(t_hot + 0.4, t_ic + 0.2, 3.7, 0.06))
a_f, n_f = dial('rpm2', GX, GY, GR, 0.0, 10.0, ['0', '2', '4', '6', '8', '10'], 'RPM x1000', T('S20'), T('S22') - 0.1)
needle(n_f, a_f, [(0.0, 2.0), (T('S20'), 2.0), (T('S20', 'sepuluh'), 9.76), (T('S21'), 9.76), (t_orig, 1.5), (DUR, 1.5)], jitter=(T('S20', 'sepuluh') + 0.1, T('S21') - 0.1, 9.76, 0.08))
hud_label('v_boost', [('2,2 BAR', 0.026, M_yellow)], BX, VY, 1.0, t_boost, t_crack + 0.2)
hud_label('v_6500', [('6.500 RPM', 0.026, M_white)], BX, VY, 1.0, t_stall, T('S13'), plate=M_redplate)
hud_label('v_9000', [('9.000+ RPM', 0.026, M_yellow)], BX, VY, 1.0, T('S15', 'sembilan'), t_hit + 0.3)
hud_label('v_hot', [('UDARA PANAS', 0.026, M_white)], BX, VY, 1.0, t_hot + 0.3, t_ic + 0.7, plate=M_redplate)
hud_label('v_cool', [('UDARA DINGIN', 0.026, M_cool)], BX, VY, 1.0, t_ic + 1.1, T('S20') - 0.15)
hud_label('v_9760', [('9.760 RPM', 0.024, M_yellow)], GX + 0.02, GY + 0.100, 1.0, T('S20', 'sepuluh'), T('S21') + 0.2)
steps = ['160', '320', '540', '790', '1.038']; ts = [T('S20', 'lebih') + k * (t_full + 0.25 - T('S20', 'lebih')) / 4 for k in range(5)]
for k, (v, tk) in enumerate(zip(steps, ts)):
    hud_label(f'hp_s{k}', [(v, 0.050, M_yellow if k == 4 else M_white), ('TENAGA KUDA', 0.020, M_white)], HPX, HPY, 1.0, tk, ts[k + 1] if k < 4 else T('S22') - 0.1, out=0.03 if k < 4 else 0.2, dur=0.12 if k < 4 else 0.28)
hud_label('final', [('160  →  1.000+', 0.038, M_white), ('TENAGA KUDA', 0.020, M_white)], 0.5, 0.118, 1.0, T('S22') + 0.15)
hud_label('x6', [('× 6', 0.060, M_yellow)], 0.5, 0.245, 1.0, T('S22', 'enam') + 0.1)
for o in bpy.data.objects:
    if o.name.startswith('HUD_'): o.visible_shadow = False; o.visible_diffuse = False; o.visible_glossy = False

# ================================================================ light and camera path (no hard cuts)
sun_d.energy = 0.55; sun.rotation_euler = Vector((0.30, 0.85, -0.70)).normalized().to_track_quat('-Z', 'Y').to_euler()
sky.color_ramp.elements[0].color = (0.20, 0.23, 0.29, 1); sky.color_ramp.elements[1].color = (0.05, 0.06, 0.09, 1)
area('LGT_soft_key', (-6.5, -9.0, 9.5), (0.5, 0.0, 2.5), 7.0, 1150); area('LGT_fill', (8.0, -7.0, 3.5), (0.5, 0.0, 2.5), 6.0, 260, (0.80, 0.88, 1.0))
area('LGT_rim', (5.5, 7.0, 9.0), (0.5, 0.5, 3.0), 5.0, 900, (1.0, 0.93, 0.82))
shot(0.0, T('S03'), P_open, end=push(P_open, 0.07), cut=True); shot(T('S03'), T('S04'), P_hero2, mv=1.0)
shot(T('S04'), T('S05', 'sampai'), P_cut, mv=1.1); shot(T('S05', 'sampai'), T('S08'), P_pist, mv=1.0); shot(T('S08'), t_top, P_gap, mv=0.9)
shot(t_top, t_ch2 - 0.1, P_top, mv=0.9); shot(t_ch2 - 0.1, T('S13') - 0.1, P_cut, mv=1.0); shot(T('S13') - 0.1, T('S14'), P_swap, mv=0.9)
shot(T('S14'), T('S15'), P_frank, mv=0.9); shot(T('S15'), T('S17'), P_head, mv=0.9); shot(T('S17'), T('S18', 'sampai') - 0.4, P_air, mv=1.2)
shot(T('S18', 'sampai') - 0.4, T('S19'), P_knock, mv=1.1); shot(T('S19'), T('S20'), P_air, mv=1.2); shot(T('S20'), T('S21'), P_hero2, mv=1.0)
shot(T('S21'), T('S22'), P_orig, mv=0.9); shot(T('S22'), DUR, P_hero, mv=1.1)
render_main()
