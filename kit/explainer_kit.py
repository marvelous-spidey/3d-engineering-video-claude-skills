"""explainer_kit.py - shared helpers for code-built 3D explainer shorts (Blender 5.3 as the bpy module).

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

# ================================================================ animation helpers
def fcurves_of(idb):
    ad = idb.animation_data
    if not ad or not ad.action: return []
    out = []
    for layer in ad.action.layers:
        for strip in layer.strips:
            cb = strip.channelbag(ad.action_slot)
            if cb: out += list(cb.fcurves)
    return out

def key(o, path, t, value=None, index=-1, ip=None, ease=None):
    """Keyframe o.path at time t (seconds). ip: None(BEZIER) | 'LINEAR' | 'CONSTANT' | 'SINE'..."""
    if value is not None:
        if index >= 0: getattr(o, path)[index] = value
        else: setattr(o, path, value)
    f = fr(t)
    o.keyframe_insert(data_path=path, frame=f, index=index)
    if ip:
        for fc in fcurves_of(o):
            if fc.data_path == path and (index < 0 or fc.array_index == index):
                for kp in fc.keyframe_points:
                    if abs(kp.co.x - f) < 1e-3:
                        kp.interpolation = ip
                        if ease: kp.easing = ease

def hidden_until(o, t0):
    if t0 > 0.02: key(o, 'scale', 0.0, Z, ip='CONSTANT')

def appear(o, t, dur=0.3, s=None, over=1.12):
    s = tuple(o.scale) if s is None else s
    key(o, 'scale', t, Z); key(o, 'scale', t + dur * 0.7, tuple(v * over for v in s)); key(o, 'scale', t + dur, s)

def vanish(o, t, dur=0.2):
    s = tuple(o.scale); key(o, 'scale', t, s); key(o, 'scale', t + dur, Z)

def grow(o, t0, t1, axis=2, s=None):
    """Hidden until t0, then grows along one axis from its pivot."""
    s = list(o.scale) if s is None else list(s); a = list(s); a[axis] = 0.001
    hidden_until(o, t0); key(o, 'scale', t0, tuple(a)); key(o, 'scale', t1, tuple(s))

def show(o, t0, t1=None, s=None):
    """Hard on/off switch (constant interpolation)."""
    s = tuple(o.scale) if s is None else s
    hidden_until(o, t0); key(o, 'scale', t0, s, ip='CONSTANT')
    if t1 is not None: key(o, 'scale', t1, Z, ip='CONSTANT')

def travel(o, stops):
    """stops: [(t, (x,y,z)), ...] moved through at constant speed per leg."""
    for t, p in stops: key(o, 'location', t, p, ip='LINEAR')

def key_input(sock, t, value):
    sock.default_value = value; sock.keyframe_insert('default_value', frame=fr(t))

# ================================================================ mesh helpers
def new_mat(name, color, rough=0.85, emit=0.0, spec=0.2, alpha=1.0):
    m = bpy.data.materials.new(name)
    try: m.use_nodes = True
    except Exception: pass
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is None:
        for n in list(nt.nodes): nt.nodes.remove(n)
        bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled'); out = nt.nodes.new('ShaderNodeOutputMaterial')
        nt.links.new(bsdf.outputs[0], out.inputs[0])
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = rough
    for k in ('Specular IOR Level', 'Specular'):
        if k in bsdf.inputs:
            bsdf.inputs[k].default_value = spec; break
    if emit > 0:
        bsdf.inputs['Emission Color'].default_value = (*color, 1); bsdf.inputs['Emission Strength'].default_value = emit
    if alpha < 1.0: bsdf.inputs['Alpha'].default_value = alpha
    m.diffuse_color = (*color, 1)
    return m

def bsdf_of(m): return next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')

def link(o, m=None, parent=None):
    col.objects.link(o)
    if m is not None: o.data.materials.append(m)
    if parent is not None: o.parent = parent
    return o

def box(name, x0, x1, y0, y1, z0, z1, m, origin='bottom', parent=None):
    """Axis-aligned box. origin: bottom | top | left | right | center (pivot for scale animation)."""
    w, d, h = x1 - x0, y1 - y0, z1 - z0
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    off = {'bottom': (0, 0, h / 2), 'top': (0, 0, -h / 2), 'left': (w / 2, 0, 0), 'right': (-w / 2, 0, 0), 'center': (0, 0, 0)}[origin]
    for v in bm.verts:
        v.co.x = v.co.x * w + off[0]; v.co.y = v.co.y * d + off[1]; v.co.z = v.co.z * h + off[2]
    bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me), m, parent)
    cx, cy, cz = (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2
    o.location = {'bottom': (cx, cy, z0), 'top': (cx, cy, z1), 'left': (x0, cy, cz), 'right': (x1, cy, cz), 'center': (cx, cy, cz)}[origin]
    return o

def tube(name, pts, r, m, parent=None, res=5, origin=None):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    ox, oy, oz = origin or (0, 0, 0)
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, co in zip(sp.points, pts): p.co = (co[0] - ox, co[1] - oy, co[2] - oz, 1)
    cu.bevel_depth = r; cu.bevel_resolution = res; cu.use_fill_caps = True
    o = link(bpy.data.objects.new(name, cu), m, parent); o.location = (ox, oy, oz)
    return o

R_PIPE = 0.10
def pipe(name, pts, R=R_PIPE, bore=True):
    """Sectioned-pipe look: white tube with a darker bore running along its front, so flow reads as inside it."""
    objs = [tube(name, pts, R, M_pvc)]
    if bore:
        r = R * 0.64; off = R - r + 0.012
        objs.append(tube(name + '_bore', [(x, y - off, z) for x, y, z in pts], r, M_bore))
    return objs

def extend(objs, t0, t1):
    for o in (objs if isinstance(objs, (list, tuple)) else [objs]):
        cu = o.data
        cu.bevel_factor_end = 0.0; cu.keyframe_insert('bevel_factor_end', frame=fr(t0))
        cu.bevel_factor_end = 1.0; cu.keyframe_insert('bevel_factor_end', frame=fr(t1))
        show(o, t0)

def smooth_path(pts, n=8):
    """Catmull-Rom through pts -> denser polyline."""
    P = [Vector(p) for p in pts]; P = [P[0]] + P + [P[-1]]; out = []
    for i in range(1, len(P) - 2):
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * P[i]) + (-P[i - 1] + P[i + 1]) * t + (2 * P[i - 1] - 5 * P[i] + 4 * P[i + 1] - P[i + 2]) * t2 + (-P[i - 1] + 3 * P[i] - 3 * P[i + 1] + P[i + 2]) * t3)))
    out.append(tuple(P[-2])); return out

def sphere(name, loc, r, m, sx=1, sy=1, sz=1, seg=12, smooth=True, parent=None):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(6, seg // 2), radius=r)
    for f in bm.faces: f.smooth = smooth
    bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me), m, parent); o.location = loc; o.scale = (sx, sy, sz)
    return o

def cyl(name, loc, r, h, m, seg=16, r2=None, down=False, parent=None, smooth=False):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += (-h / 2 if down else h / 2)
    if smooth:
        for f in bm.faces:
            if len(f.verts) == 4: f.smooth = True
    bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me), m, parent); o.location = loc
    return o

def prism(name, pts_xz, y0, y1, m, parent=None):
    """Extrude a polygon given in the XZ plane along +Y."""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    f = bm.faces.new([bm.verts.new((x, y0, z)) for x, z in pts_xz])
    res = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [g for g in res['geom'] if isinstance(g, bmesh.types.BMVert)]: v.co.y += (y1 - y0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    return link(bpy.data.objects.new(name, me), m, parent)

def patch(name, pts_xz, m, y=-0.006, parent=None):
    """Flat single-sided shape lying just in front of the cut face (stains, water table)."""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bm.faces.new([bm.verts.new((x, 0.0, z)) for x, z in pts_xz]); bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me), m, parent); o.location = (0, y, 0)
    return o

def empty(name, loc=(0, 0, 0), parent=None):
    o = bpy.data.objects.new(name, None); col.objects.link(o); o.location = loc
    if parent is not None: o.parent = parent
    return o

# in-scene lettering: Inter Bold when it is installed (same family as the captions), otherwise Blender's built-in font
FONT3D = None
try: _here = os.path.dirname(os.path.abspath(__file__))
except NameError: _here = os.getcwd()
for _fp in (os.environ.get('SEPTIC_FONT', ''), '/usr/share/fonts/opentype/inter/Inter-Bold.otf', '/usr/share/fonts/truetype/inter/Inter-Bold.ttf',
            os.path.join(_here, 'Inter-Bold.otf'), os.path.join(_here, 'Inter-Bold.ttf')):
    if _fp and os.path.exists(_fp):
        try:
            FONT3D = bpy.data.fonts.load(_fp); break
        except Exception as ex: print('font load failed', _fp, ex)
TEXT_SCALE = 1.25 if FONT3D is not None else 1.0      # Inter's capitals are smaller than the built-in font's at the same size
print('3D text font:', FONT3D.filepath if FONT3D else 'built-in', flush=True)

def text(name, body, loc, size, m, extrude=0.004, parent=None, rot=(math.radians(90), 0, 0)):
    fc = bpy.data.curves.new(name, 'FONT'); fc.body = body; fc.align_x = 'CENTER'; fc.align_y = 'CENTER'
    fc.size = size * TEXT_SCALE; fc.extrude = extrude
    if FONT3D is not None: fc.font = FONT3D
    o = link(bpy.data.objects.new(name, fc), m, parent); o.location = loc; o.rotation_euler = rot
    return o

def label(name, lines, x=0.0, z=0.0, size=0.17, y=-0.10, plate=None, ink=None, billboard=False, pos=None):
    """Tag = dark plate + bright text, either flat on the cut face or always facing the camera.
    lines: 'TEXT' or [(text, size, material), ...]. Returns the root (scale it to show/hide)."""
    if isinstance(lines, str): lines = [(lines, size, ink or M_white)]
    root = empty(name, pos if pos is not None else (x, y, z))
    if billboard:
        c = root.constraints.new('COPY_ROTATION'); c.target = cam
    else:
        root.rotation_euler = (math.radians(90), 0, 0)
    objs = [text(f'{name}_t{i}', body, (0, 0, 0.006), sz, mat, parent=root, rot=(0, 0, 0)) for i, (body, sz, mat) in enumerate(lines)]
    bpy.context.view_layer.update()
    bbs = []
    for o in objs:
        xs = [c[0] for c in o.bound_box]; ys = [c[1] for c in o.bound_box]
        bbs.append((min(xs), max(xs), min(ys), max(ys)))
    pad = lines[0][1] * TEXT_SCALE * 0.42; gap = lines[0][1] * TEXT_SCALE * 0.30
    H = sum(b[3] - b[2] for b in bbs) + gap * (len(bbs) - 1) + 2 * pad; Wd = max(b[1] - b[0] for b in bbs) + 2.5 * pad
    ycur = H / 2 - pad
    for o, b in zip(objs, bbs):
        h = b[3] - b[2]; o.location = (-(b[0] + b[1]) / 2, ycur - h / 2 - (b[2] + b[3]) / 2, 0.006); ycur -= h + gap
    pl = box(name + '_plate', -Wd / 2, Wd / 2, -H / 2, H / 2, -0.02, 0.0, plate or M_plate, origin='center', parent=root)
    if billboard:
        for o in objs + [pl]: o.visible_shadow = False
    return root

def sign(name, body, x0, x1, y, z0, z1, size, board=None, ink=None):
    """Board on two posts standing on the ground. Returns the root."""
    root = empty(name, ((x0 + x1) / 2, y, 0.0)); w = x1 - x0
    box(name + '_pa', -w / 2 + 0.14, -w / 2 + 0.21, 0.05, 0.12, 0.0, z1 - 0.05, M_wood, parent=root)
    box(name + '_pb', w / 2 - 0.21, w / 2 - 0.14, 0.05, 0.12, 0.0, z1 - 0.05, M_wood, parent=root)
    box(name + '_board', -w / 2, w / 2, 0.0, 0.05, z0, z1, board or M_sign, parent=root)
    if body: text(name + '_txt', body, (0, -0.012, (z0 + z1) / 2), size, ink or M_ink, parent=root)
    return root

def screen_to_world(pose_, sx, sy, depth=None, plane_y=None):
    """World point seen at screen fraction (sx, sy) (0,0 = top-left) for a camera pose, at a view depth or on a y-plane."""
    c = Vector(pose_[0]); f = (Vector(pose_[1]) - c).normalized(); r = f.cross(Vector((0, 0, 1))).normalized(); u = r.cross(f)
    d = f + r * ((sx - 0.5) * ASPECT) + u * (0.5 - sy)          # lens 36 on a 36 mm long side -> tan(half fov) = 0.5
    k = depth if plane_y is None else (plane_y - c.y) / d.y
    return tuple(c + d * k)

# base materials used by the helpers
M_conc = new_mat('concrete', (0.62, 0.62, 0.60), 0.9)
M_pvc = new_mat('pvc', (0.86, 0.87, 0.89), 0.35, spec=0.5)
M_bore = new_mat('pipe_bore', (0.33, 0.39, 0.47), 0.6)
M_wood = new_mat('wood', (0.70, 0.50, 0.33), 0.7)
M_sign = new_mat('sign', (0.96, 0.96, 0.94), 0.6)
M_ink = new_mat('ink', (0.10, 0.14, 0.22), 0.6)
M_plate = new_mat('plate', (0.05, 0.07, 0.12), 0.6)
M_white = new_mat('white_text', (1.0, 1.0, 1.0), 0.5, emit=1.0)
M_yellow = new_mat('yellow_text', (1.0, 0.82, 0.10), 0.5, emit=1.3)
M_vest = new_mat('vest', (1.0, 0.40, 0.05), 0.7)
M_stripe = new_mat('stripe', (0.93, 0.94, 0.86), 0.4, emit=0.2)
M_helmet = new_mat('helmet', (1.0, 0.78, 0.06), 0.35, spec=0.5)
M_pants = new_mat('pants', (0.15, 0.19, 0.30), 0.9)
M_skin = new_mat('skin', (0.80, 0.60, 0.45), 0.7)
M_steel = new_mat('steel', (0.55, 0.57, 0.60), 0.4, spec=0.6)

def soil_material():
    m = new_mat('soil', (0.3, 0.14, 0.07), 0.97); nt = m.node_tree; N = nt.nodes; L = nt.links; bsdf = bsdf_of(m)
    geo = N.new('ShaderNodeNewGeometry'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'], sep.inputs[0])
    n1 = N.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 0.55; n1.inputs['Detail'].default_value = 2.0
    L.new(geo.outputs['Position'], n1.inputs['Vector'])
    sub = N.new('ShaderNodeMath'); sub.operation = 'SUBTRACT'; sub.inputs[1].default_value = 0.5; L.new(n1.outputs[0], sub.inputs[0])
    mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 0.55; L.new(sub.outputs[0], mul.inputs[0])
    add = N.new('ShaderNodeMath'); add.operation = 'ADD'; L.new(sep.outputs['Z'], add.inputs[0]); L.new(mul.outputs[0], add.inputs[1])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = -40.0; mr.inputs['From Max'].default_value = 0.0
    L.new(add.outputs[0], mr.inputs['Value'])
    ramp = N.new('ShaderNodeValToRGB'); ramp.color_ramp.interpolation = 'CONSTANT'; cr = ramp.color_ramp
    # strata by depth: bedrock below -13 m, dark subsoil, red-brown subsoil (-5..-0.95 m), dark topsoil
    stops = [(0.0, (0.052, 0.042, 0.040)), (0.675, (0.085, 0.050, 0.035)), (0.875, (0.27, 0.095, 0.045)), (0.97625, (0.13, 0.07, 0.035)), (0.993, (0.11, 0.07, 0.04))]
    cr.elements[0].position = stops[0][0]; cr.elements[0].color = (*stops[0][1], 1)
    cr.elements[1].position = stops[1][0]; cr.elements[1].color = (*stops[1][1], 1)
    for p, c in stops[2:]:
        e = cr.elements.new(p); e.color = (*c, 1)
    L.new(mr.outputs[0], ramp.inputs[0])
    mr2 = N.new('ShaderNodeMapRange'); mr2.inputs['From Min'].default_value = -0.10; mr2.inputs['From Max'].default_value = -0.06
    L.new(sep.outputs['Z'], mr2.inputs['Value'])
    turf = N.new('ShaderNodeMix'); turf.data_type = 'RGBA'
    L.new(mr2.outputs[0], turf.inputs[0]); L.new(ramp.outputs[0], turf.inputs[6]); turf.inputs[7].default_value = (0.20, 0.34, 0.08, 1)
    vor = N.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 5.5; L.new(geo.outputs['Position'], vor.inputs['Vector'])
    pr = N.new('ShaderNodeValToRGB'); pr.color_ramp.elements[0].position = 0.07; pr.color_ramp.elements[0].color = (1, 1, 1, 1)
    pr.color_ramp.elements[1].position = 0.11; pr.color_ramp.elements[1].color = (0, 0, 0, 1); L.new(vor.outputs['Distance'], pr.inputs[0])
    pmul = N.new('ShaderNodeMath'); pmul.operation = 'MULTIPLY'; pmul.inputs[1].default_value = 0.55; L.new(pr.outputs[0], pmul.inputs[0])
    peb = N.new('ShaderNodeMix'); peb.data_type = 'RGBA'
    L.new(pmul.outputs[0], peb.inputs[0]); L.new(turf.outputs[2], peb.inputs[6]); peb.inputs[7].default_value = (0.42, 0.25, 0.16, 1)
    n2 = N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 38.0; n2.inputs['Detail'].default_value = 3.0
    L.new(geo.outputs['Position'], n2.inputs['Vector'])
    gr = N.new('ShaderNodeMapRange'); gr.inputs['To Min'].default_value = 0.72; gr.inputs['To Max'].default_value = 1.25; L.new(n2.outputs[0], gr.inputs['Value'])
    grain = N.new('ShaderNodeMix'); grain.data_type = 'RGBA'; grain.blend_type = 'MULTIPLY'; grain.inputs[0].default_value = 1.0
    L.new(peb.outputs[2], grain.inputs[6]); L.new(gr.outputs[0], grain.inputs[7]); L.new(grain.outputs[2], bsdf.inputs['Base Color'])
    return m

def grass_material():
    m = new_mat('grass', (0.3, 0.5, 0.12), 0.95); nt = m.node_tree; N = nt.nodes; L = nt.links; bsdf = bsdf_of(m)
    geo = N.new('ShaderNodeNewGeometry')
    wave = N.new('ShaderNodeTexWave'); wave.wave_type = 'BANDS'; wave.bands_direction = 'X'
    wave.inputs['Scale'].default_value = 0.16; wave.inputs['Distortion'].default_value = 0.0; L.new(geo.outputs['Position'], wave.inputs['Vector'])
    ramp = N.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.42; ramp.color_ramp.elements[0].color = (0.25, 0.43, 0.10, 1)
    ramp.color_ramp.elements[1].position = 0.58; ramp.color_ramp.elements[1].color = (0.33, 0.52, 0.13, 1); L.new(wave.outputs[0], ramp.inputs[0])
    n2 = N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 9.0; n2.inputs['Detail'].default_value = 4.0; L.new(geo.outputs['Position'], n2.inputs['Vector'])
    gr = N.new('ShaderNodeMapRange'); gr.inputs['To Min'].default_value = 0.8; gr.inputs['To Max'].default_value = 1.18; L.new(n2.outputs[0], gr.inputs['Value'])
    mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs[0].default_value = 1.0
    L.new(ramp.outputs[0], mix.inputs[6]); L.new(gr.outputs[0], mix.inputs[7]); L.new(mix.outputs[2], bsdf.inputs['Base Color'])
    return m

def gravel_material():
    m = new_mat('gravel', (0.5, 0.5, 0.48), 0.95); nt = m.node_tree; N = nt.nodes; L = nt.links; bsdf = bsdf_of(m)
    geo = N.new('ShaderNodeNewGeometry'); vor = N.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 15.0
    L.new(geo.outputs['Position'], vor.inputs['Vector'])
    ramp = N.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (0.66, 0.66, 0.63, 1)
    ramp.color_ramp.elements[1].position = 0.42; ramp.color_ramp.elements[1].color = (0.14, 0.14, 0.14, 1)
    L.new(vor.outputs['Distance'], ramp.inputs[0]); L.new(ramp.outputs[0], bsdf.inputs['Base Color'])
    return m

M_soil = soil_material(); M_grass = grass_material(); M_gravel = gravel_material()

# ================================================================ world + light
w = bpy.data.worlds.new('World'); sc.world = w
try: w.use_nodes = True
except Exception: pass
nt = w.node_tree; N = nt.nodes; L = nt.links
for n in list(N): N.remove(n)
out = N.new('ShaderNodeOutputWorld'); bg = N.new('ShaderNodeBackground'); L.new(bg.outputs[0], out.inputs[0])
tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Generated'], sep.inputs[0])
mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.0; mr.inputs['From Max'].default_value = 0.75; L.new(sep.outputs['Z'], mr.inputs['Value'])
sky = N.new('ShaderNodeValToRGB')
sky.color_ramp.elements[0].position = 0.0; sky.color_ramp.elements[0].color = (0.62, 0.80, 0.97, 1)
sky.color_ramp.elements[1].position = 1.0; sky.color_ramp.elements[1].color = (0.10, 0.34, 0.82, 1); L.new(mr.outputs[0], sky.inputs[0])
zc = N.new('ShaderNodeMath'); zc.operation = 'MAXIMUM'; zc.inputs[1].default_value = 0.04; L.new(sep.outputs['Z'], zc.inputs[0])
dx = N.new('ShaderNodeMath'); dx.operation = 'DIVIDE'; L.new(sep.outputs['X'], dx.inputs[0]); L.new(zc.outputs[0], dx.inputs[1])
dy = N.new('ShaderNodeMath'); dy.operation = 'DIVIDE'; L.new(sep.outputs['Y'], dy.inputs[0]); L.new(zc.outputs[0], dy.inputs[1])
comb = N.new('ShaderNodeCombineXYZ'); L.new(dx.outputs[0], comb.inputs[0]); L.new(dy.outputs[0], comb.inputs[1])
cn = N.new('ShaderNodeTexNoise'); cn.inputs['Scale'].default_value = 0.55; cn.inputs['Detail'].default_value = 7.0; cn.inputs['Roughness'].default_value = 0.6
L.new(comb.outputs[0], cn.inputs['Vector'])
cramp = N.new('ShaderNodeValToRGB')
cramp.color_ramp.elements[0].position = 0.50; cramp.color_ramp.elements[0].color = (0, 0, 0, 1)
cramp.color_ramp.elements[1].position = 0.64; cramp.color_ramp.elements[1].color = (1, 1, 1, 1); L.new(cn.outputs[0], cramp.inputs[0])
hf = N.new('ShaderNodeMapRange'); hf.inputs['From Min'].default_value = 0.03; hf.inputs['From Max'].default_value = 0.16; L.new(sep.outputs['Z'], hf.inputs['Value'])
cm = N.new('ShaderNodeMath'); cm.operation = 'MULTIPLY'; L.new(cramp.outputs[0], cm.inputs[0]); L.new(hf.outputs[0], cm.inputs[1])
mixc = N.new('ShaderNodeMix'); mixc.data_type = 'RGBA'
L.new(cm.outputs[0], mixc.inputs[0]); L.new(sky.outputs[0], mixc.inputs[6]); mixc.inputs[7].default_value = (1.0, 1.0, 1.0, 1)
below = N.new('ShaderNodeMath'); below.operation = 'LESS_THAN'; below.inputs[1].default_value = 0.0; L.new(sep.outputs['Z'], below.inputs[0])
mixg = N.new('ShaderNodeMix'); mixg.data_type = 'RGBA'
L.new(below.outputs[0], mixg.inputs[0]); L.new(mixc.outputs[2], mixg.inputs[6]); mixg.inputs[7].default_value = (0.30, 0.47, 0.13, 1)
L.new(mixg.outputs[2], bg.inputs['Color']); bg.inputs['Strength'].default_value = 1.0

sun_d = bpy.data.lights.new('LGT_key', 'SUN'); sun_d.energy = 2.7; sun_d.angle = math.radians(6)
sun = bpy.data.objects.new('LGT_key', sun_d); col.objects.link(sun)
sun.rotation_euler = Vector((0.42, 0.72, -0.55)).normalized().to_track_quat('-Z', 'Y').to_euler()

# camera (animated at the end; created early so camera-facing tags can reference it)
cam_d = bpy.data.cameras.new('CAM_main'); cam_d.lens = 36; cam_d.clip_end = 3000
cam = bpy.data.objects.new('CAM_main', cam_d); col.objects.link(cam); sc.camera = cam
tgt = empty('CAM_target')
con = cam.constraints.new('TRACK_TO'); con.target = tgt; con.track_axis = 'TRACK_NEGATIVE_Z'; con.up_axis = 'UP_Y'

# ================================================================ camera moves
def pose(x, d, cz, tz): return ((x, -d, cz), (x, 0.0, tz))       # frontal view of the cut face
def push(p, k=0.04, dx=0.0):
    (cx, cy, cz), (gx, gy, gz) = p
    return ((cx + (gx - cx) * k + dx, cy + (gy - cy) * k, cz + (gz - cz) * k), (gx + dx, gy, gz))
def cam_key(t, p, ip, ease=None):
    key(cam, 'location', t, p[0], ip=ip, ease=ease); key(tgt, 'location', t, p[1], ip=ip, ease=ease)
_last = [None]
def shot(t0, t1, main, end=None, mv=1.3, cut=False):
    """Ease from where the last shot ended to `main` over mv seconds (or cut straight to it), then drift slowly to `end`."""
    end = end or push(main)
    if cut or _last[0] is None:
        cam_key(t0, main, 'LINEAR')
    else:
        cam_key(t0, _last[0], 'SINE', 'EASE_IN_OUT'); cam_key(min(t0 + mv, t1 - 0.3), main, 'LINEAR')
    cam_key(t1 - 1.0 / FPS, end, 'CONSTANT'); _last[0] = end

def hero_pose(az, el, dist, target=(0.7, 0.5, -2.5)):
    a, e = math.radians(az), math.radians(el)
    d = Vector((-math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), -math.sin(e)))
    return (tuple(Vector(target) - d * dist), target)

def render_main():
    """Set up Cycles and run the mode given on the command line. Call it once the scene is built."""
    sc.render.fps = FPS; sc.frame_start = 1; sc.frame_end = LAST
    sc.render.engine = 'CYCLES'; cy = sc.cycles
    cy.device = 'CPU'
    if DEVICE == 'GPU':
        try:
            prefs = bpy.context.preferences.addons['cycles'].preferences
            for dt in ('OPTIX', 'CUDA'):
                prefs.compute_device_type = dt; prefs.get_devices()
                devs = [d for d in prefs.devices if d.type == dt]
                if devs:
                    for d in prefs.devices: d.use = (d.type == dt)
                    cy.device = 'GPU'; print('GPU device:', dt, [d.name for d in devs]); break
            try: cy.denoising_use_gpu = True
            except Exception: pass
        except Exception as ex:
            print('GPU setup failed, using CPU:', ex)
    cy.samples = SPP; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.05
    cy.max_bounces = 4; cy.diffuse_bounces = 2; cy.glossy_bounces = 1; cy.transmission_bounces = 0; cy.transparent_max_bounces = 16
    cy.caustics_reflective = False; cy.caustics_refractive = False
    try:
        cy.use_denoising = True; cy.denoiser = 'OPENIMAGEDENOISE'
    except Exception as ex: print('denoise setup:', ex)
    sc.render.use_persistent_data = os.environ.get('KIT_PERSIST', '0') == '1'      # off by default: stale-state glitches in multi-process renders (video #2)
    sc.render.resolution_x = RX; sc.render.resolution_y = RY; sc.render.resolution_percentage = 100
    try:
        sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
    except Exception as ex: print('view:', ex)
    FMT = os.environ.get('KIT_FMT', os.environ.get('SEPTIC_FMT', 'PNG')); EXT = 'jpg' if FMT == 'JPEG' else 'png'
    sc.render.image_settings.file_format = FMT
    if FMT == 'JPEG': sc.render.image_settings.quality = 97
    else: sc.render.image_settings.compression = 15
    print(f'scene built: {len(bpy.data.objects)} objects, {LAST} frames, device={cy.device}', flush=True)

    t_all = time.time()
    if MODE == 'still':
        os.makedirs(OUT, exist_ok=True)
        for ts in REST:
            t = float(ts); f = fr(t); fi = int(f); tf = time.time()
            sc.frame_set(fi, subframe=f - fi)
            sc.render.filepath = os.path.join(OUT, f't_{int(round(t * 100)):05d}.{EXT}')
            bpy.ops.render.render(write_still=True)
            print(f'STILL t={t:.2f}s {time.time() - tf:.1f}s', flush=True)
    elif MODE == 'anim':
        os.makedirs(OUT, exist_ok=True)
        f0, f1 = int(REST[0]), int(REST[1]); step = int(REST[2]) if len(REST) > 2 else 1; n = 0
        for f in range(f0, f1 + 1, step):
            path = os.path.join(OUT, f'f_{f:05d}.{EXT}')
            if os.path.exists(path) and os.path.getsize(path) > 1000: continue
            tf = time.time(); sc.frame_set(f); sc.render.filepath = path
            bpy.ops.render.render(write_still=True); n += 1
            if n % 10 == 1: print(f'FRAME {f} {time.time() - tf:.2f}s', flush=True)
        print(f'ANIM {f0}-{f1} step {step}: {n} frames in {time.time() - t_all:.1f}s', flush=True)
    elif MODE == 'list':                                        # list <rx> <ry> <spp> <out_dir> <file with frame numbers> [k0] [step]: (re)render those frames, overwriting
        os.makedirs(OUT, exist_ok=True); fl = [int(v) for v in open(REST[0]).read().split()]; n = 0
        k0 = int(REST[1]) if len(REST) > 1 else 0; kn = int(REST[2]) if len(REST) > 2 else 1
        for f in fl[k0::kn]:
            path = os.path.join(OUT, f'f_{f:05d}.{EXT}'); tf = time.time(); sc.frame_set(f); sc.render.filepath = path
            bpy.ops.render.render(write_still=True); n += 1
            if n % 10 == 1: print(f'FRAME {f} {time.time() - tf:.2f}s', flush=True)
        print(f'LIST: {n} frames in {time.time() - t_all:.1f}s', flush=True)
    elif MODE == 'blend':
        bpy.ops.wm.save_as_mainfile(filepath=OUT); print('saved', OUT)
