"""How a septic system works (EN, 9:16, 66 s) - full scene + animation built from code.

Run with Blender or the bpy module:
  blender -b -P septic_video.py -- still <rx> <ry> <spp> <out_dir> <t1> <t2> ...     (times in seconds)
  blender -b -P septic_video.py -- anim  <rx> <ry> <spp> <out_dir> <f0> <f1> [step]  (frames, 1-based; skips existing files)
  blender -b -P septic_video.py -- blend <rx> <ry> <spp> <out.blend>
Env: SEPTIC_DEVICE=CPU|GPU (default CPU).
Every cue is tied to the voice-over word timings in WORDS, so the picture follows the narration.
"""
import bpy, bmesh, math, random, sys, time, os
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
MODE = argv[0]; RX, RY, SPP = int(argv[1]), int(argv[2]), int(argv[3]); OUT = argv[4]; REST = argv[5:]
DEVICE = os.environ.get('SEPTIC_DEVICE', 'CPU')
FPS = 30; DUR = 66.0; LAST = int(DUR * FPS); OFFSET = 0.30; ASPECT = 1080 / 1920

# voice-over word timings (faster-whisper on the final VO take): [word, start_s, end_s]
WORDS = [["No",0.0,0.22],["sewer",0.22,0.54],["on",0.54,0.84],["your",0.84,0.98],["street?",0.98,1.3],["Then",2.06,2.14],["your",2.14,2.26],["own",2.26,2.54],["yard",2.54,2.88],["has",2.88,3.18],["to",3.18,3.32],["handle",3.32,3.56],["every",3.56,4.06],["flush.",4.06,4.44],["Let's",5.18,5.44],["build",5.44,5.64],["the",5.64,5.88],["thing",5.88,6.08],["that",6.08,6.22],["does",6.22,6.46],["it.",6.46,6.64],["Start",7.2,7.34],["with",7.34,7.58],["a",7.58,7.66],["hole.",7.66,7.88],["Pipe",8.46,8.62],["the",8.62,8.82],["toilet",8.82,9.04],["into",9.04,9.46],["it.",9.46,9.74],["Problem.",10.3,10.58],["Sewage",11.38,11.82],["seeps",11.82,12.16],["into",12.16,12.38],["the",12.38,12.5],["ground",12.5,12.8],["and",12.8,13.22],["toward",13.22,13.38],["your",13.38,13.72],["well.",13.72,13.96],["So",14.7,14.8],["you",14.8,15.1],["seal",15.1,15.34],["the",15.34,15.58],["hole",15.58,15.8],["with",15.8,16.06],["concrete.",16.06,16.3],["Now",17.12,17.24],["nothing",17.24,17.88],["leaks.",17.88,18.1],["But",18.84,18.94],["nothing",18.94,19.24],["leaves",19.24,19.56],["and",19.56,20.14],["it",20.14,20.24],["fills",20.24,20.42],["up",20.42,20.74],["in",20.74,20.9],["days.",20.9,21.14],["So",21.98,22.1],["you",22.1,22.38],["add",22.38,22.58],["an",22.58,22.7],["outlet",22.7,23.0],["pipe.",23.0,23.3],["Problem.",23.94,24.48],["Solids",25.3,25.56],["flow",25.56,25.84],["out",25.84,26.1],["too",26.1,26.36],["and",26.36,26.88],["clog",26.88,27.24],["whatever",27.24,27.46],["comes",27.46,27.86],["next.",27.86,28.2],["So",28.68,28.98],["you",28.98,29.32],["add",29.32,29.5],["a",29.5,29.6],["wall",29.6,29.88],["and",29.88,30.36],["slow",30.36,30.66],["the",30.66,30.88],["water",30.88,31.1],["down.",31.1,31.46],["Heavy",32.12,32.44],["solids",32.44,32.84],["sink",32.84,33.14],["as",33.14,33.42],["sludge.",33.42,33.86],["Grease",34.4,34.82],["floats",34.82,35.0],["up",35.0,35.32],["as",35.32,35.54],["scum.",35.54,35.92],["Only",36.42,36.78],["the",36.78,36.92],["clearer",36.92,37.24],["water",37.24,37.66],["in",37.66,37.84],["the",37.84,37.92],["middle",37.92,38.2],["moves",38.2,38.46],["on.",38.46,38.76],["It",39.3,39.42],["still",39.42,39.7],["isn't",39.7,40.02],["clean.",40.02,40.28],["So",41.18,41.18],["perforated",41.18,42.04],["pipes",42.04,42.3],["spread",42.3,42.76],["it",42.76,42.94],["through",42.94,43.14],["gravel",43.14,43.42],["and",43.42,44.02],["the",44.02,44.12],["soil",44.12,44.44],["filters",44.44,44.76],["the",44.76,45.14],["rest.",45.14,45.34],["Bacteria",46.02,46.42],["in",46.42,46.82],["the",46.82,46.9],["tank",46.9,47.12],["make",47.12,47.48],["gas.",47.48,47.8],["It",48.58,48.64],["vents",48.64,48.82],["back",48.82,49.2],["through",49.2,49.48],["the",49.48,49.62],["plumbing",49.62,49.9],["out",49.9,50.4],["above",50.4,50.62],["your",50.62,50.88],["roof.",50.88,51.14],["And",51.84,51.9],["they",51.9,52.0],["can't",52.0,52.38],["digest",52.38,52.58],["everything.",52.58,53.18],["So",53.96,54.14],["every",54.14,54.56],["three",54.56,54.86],["to",54.86,55.02],["five",55.02,55.3],["years",55.3,55.6],["a",55.6,56.04],["truck",56.04,56.36],["pumps",56.36,56.76],["out",56.76,57.06],["the",57.06,57.24],["sludge.",57.24,57.56],["That's",58.2,58.6],["a",58.6,58.64],["septic",58.64,59.02],["system.",59.02,59.54],["One",60.14,60.24],["in",60.24,60.38],["five",60.38,60.68],["American",60.68,61.12],["homes",61.12,61.46],["runs",61.46,61.86],["on",61.86,62.14],["one.",62.14,62.34],["What",62.9,63.12],["should",63.12,63.28],["we",63.28,63.4],["build",63.4,63.6],["next?",63.6,63.88]]
def W(i): return WORDS[i][1] + OFFSET       # start of word i in video time
def WE(i): return WORDS[i][2] + OFFSET      # end of word i
def fr(t): return t * FPS + 1.0

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

# ================================================================ materials
M_conc = new_mat('concrete', (0.62, 0.62, 0.60), 0.9)
M_conc_d = new_mat('concrete_dark', (0.40, 0.40, 0.38), 0.95)
M_pvc = new_mat('pvc', (0.86, 0.87, 0.89), 0.35, spec=0.5)
M_bore = new_mat('pipe_bore', (0.33, 0.39, 0.47), 0.6)
M_hole = new_mat('pipe_hole', (0.05, 0.05, 0.05), 0.9)
M_liq = new_mat('liquid', (0.20, 0.14, 0.08), 0.25, spec=0.5)
M_liq2 = new_mat('liquid_2', (0.20, 0.14, 0.08), 0.25, spec=0.5)
M_scum = new_mat('scum', (0.66, 0.56, 0.26), 0.9)
M_sludge = new_mat('sludge', (0.09, 0.06, 0.03), 0.95)
M_solid = new_mat('solids', (0.13, 0.08, 0.04), 0.8)
M_grease = new_mat('grease', (0.95, 0.80, 0.25), 0.4, emit=0.35)
M_fine = new_mat('fines', (0.80, 0.74, 0.58), 0.6, emit=0.1)
M_bact = new_mat('bacteria', (0.25, 0.95, 0.55), 0.5, emit=1.6)
M_gas = new_mat('gas', (0.95, 0.97, 1.0), 0.3, emit=0.7)
M_arrow = new_mat('arrow', (1.0, 0.86, 0.25), 0.5, emit=1.2)
M_wall = new_mat('house_wall', (0.90, 0.84, 0.72), 0.9)
M_tile = new_mat('bath_tile', (0.70, 0.84, 0.90), 0.5)
M_roof = new_mat('roof', (0.62, 0.20, 0.12), 0.8)
M_ceramic = new_mat('ceramic', (0.96, 0.96, 0.95), 0.2, spec=0.6)
M_window = new_mat('window', (0.55, 0.78, 0.95), 0.2, emit=0.3)
M_wood = new_mat('wood', (0.70, 0.50, 0.33), 0.7)
M_sign = new_mat('sign', (0.96, 0.96, 0.94), 0.6)
M_ink = new_mat('ink', (0.10, 0.14, 0.22), 0.6)
M_plate = new_mat('plate', (0.05, 0.07, 0.12), 0.6)
M_plate_red = new_mat('plate_red', (0.78, 0.10, 0.08), 0.6, emit=0.25)
M_white = new_mat('white_text', (1.0, 1.0, 1.0), 0.5, emit=1.0)
M_yellow = new_mat('yellow_text', (1.0, 0.82, 0.10), 0.5, emit=1.3)
M_trunk = new_mat('trunk', (0.28, 0.20, 0.14), 0.95)
M_leaf = new_mat('leaf', (0.23, 0.36, 0.14), 0.95)
M_leaf2 = new_mat('leaf2', (0.30, 0.42, 0.16), 0.95)
M_stone = new_mat('stone', (0.50, 0.49, 0.46), 0.95)
M_dark = new_mat('shaft_dark', (0.05, 0.06, 0.08), 0.95)
M_water = new_mat('well_water', (0.12, 0.45, 0.85), 0.15, spec=0.6, emit=0.15)
M_gwater = new_mat('groundwater', (0.10, 0.42, 0.95), 0.4, alpha=0.46)
M_plume = new_mat('plume', (0.23, 0.17, 0.04), 0.9, alpha=0.62)
M_plume2 = new_mat('plume2', (0.23, 0.17, 0.04), 0.9, alpha=0.62)
M_moist = new_mat('moist', (0.05, 0.035, 0.03), 0.9, alpha=0.0)
M_drop = new_mat('drop_murky', (0.50, 0.40, 0.22), 0.3, emit=0.35)
M_drop_c = new_mat('drop_clean', (0.35, 0.70, 1.0), 0.2, emit=0.9)
M_dirt = new_mat('dirt', (0.22, 0.10, 0.05), 0.97)
M_vest = new_mat('vest', (1.0, 0.40, 0.05), 0.7)
M_stripe = new_mat('stripe', (0.93, 0.94, 0.86), 0.4, emit=0.2)
M_helmet = new_mat('helmet', (1.0, 0.78, 0.06), 0.35, spec=0.5)
M_pants = new_mat('pants', (0.15, 0.19, 0.30), 0.9)
M_skin = new_mat('skin', (0.80, 0.60, 0.45), 0.7)
M_steel = new_mat('steel', (0.55, 0.57, 0.60), 0.4, spec=0.6)
M_truck = new_mat('truck_cab', (0.13, 0.42, 0.78), 0.45, spec=0.5)
M_ttank = new_mat('truck_tank', (0.88, 0.89, 0.90), 0.35, spec=0.6)
M_tire = new_mat('tire', (0.04, 0.04, 0.045), 0.9)
M_chassis = new_mat('chassis', (0.12, 0.13, 0.15), 0.8)
M_hose = new_mat('hose', (0.10, 0.35, 0.22), 0.7)

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

# ================================================================ cues (seconds, from the narration)
T_FLUSH = W(9) - 0.1                     # "...has to handle every flush"
T_Q = W(13) + 0.25                       # question mark after "flush."
T_SHOVEL = W(14) + 0.1                   # "Let's build"
T_DIG0, T_DIG1 = W(21), WE(24) + 0.3     # "Start with a hole."
T_PIPE0, T_PIPE1 = W(25), W(28) + 0.2    # "Pipe the toilet into it."
T_PROB1 = W(30); T_SEEP = W(31)          # "Problem: sewage seeps"
T_WELL = W(36) - 0.15                    # cut to the well on "and toward your well"
T_SEAL0, T_SEAL1 = W(40), WE(46)         # "So you seal the hole with concrete."
T_FILL0, T_FILL1 = W(53), WE(58)         # "and it fills up in days"
T_OUT0, T_OUT1 = W(59) + 0.1, WE(64)     # "So you add an outlet pipe."
T_SOLIDS = W(66); T_CLOG = W(71)         # "Solids flow out too, and clog..."
T_WALL0, T_WALL1 = W(75) + 0.1, W(80)    # "So you add a wall,"
T_SINK = W(85); T_SLUDGE = W(89); T_GREASE = W(90); T_SCUM = W(94)
T_CLEAR = W(97); T_MOVES = W(102)
T_FIELD = W(108); T_GRAVEL = W(114); T_SOIL = W(117)
T_BACT = W(121); T_GAS = W(125); T_VENT = W(127) + 0.05; T_ROOF = W(133)
T_YEARS = W(137); T_TRUCK = W(148); T_PUMP = W(150)
T_HERO = W(154) - 0.2; T_STAT = W(158); T_NEXT = W(166)
# shot boundaries
C1 = W(14) - 0.2; C2 = W(21) - 0.15; C3 = W(30) - 0.1; C5 = W(40) - 0.25; C7 = W(59) - 0.15; C8 = W(65) - 0.1
C9 = W(75) - 0.2; C10 = W(85) - 0.2; C11 = W(95) - 0.2; C12 = W(104) - 0.2; C13 = W(121) - 0.25; C14 = W(137) - 0.2

PX0, PX1, PY1, PZB = -1.42, 1.42, 1.32, -2.17      # pit (outer tank) footprint
LEVEL = -0.76                                      # working liquid level (just above the outlet invert)
Z_IN, Z_OUT = -0.56, -0.70                         # pipe centre heights at the tank wall
# liquid surface height in the pit/tank over time
LEVELS = [(0.0, PZB + 0.001), (T_PIPE1, PZB + 0.001), (T_PIPE1 + 0.6, -2.02), (T_SEAL0, -1.82), (T_FILL0 - 1.5, -1.70), (T_FILL0, -1.25),
          (T_FILL1, -0.07), (T_OUT0 + 0.6, -0.07), (T_OUT1, LEVEL), (DUR, LEVEL)]
def level_at(t):
    for (t0, z0), (t1, z1) in zip(LEVELS, LEVELS[1:]):
        if t0 <= t <= t1: return z0 + (z1 - z0) * (t - t0) / max(1e-6, t1 - t0)
    return LEVELS[-1][1]
def t_level_reaches(z):
    for (t0, z0), (t1, z1) in zip(LEVELS, LEVELS[1:]):
        if t1 <= T_FILL1 + 0.01 and z0 <= z <= z1 and z1 > z0: return t0 + (t1 - t0) * (z - z0) / (z1 - z0)
    return T_FILL1

# ================================================================ ground
soil = box('ENV_soil', -150, 150, 0.0, 400.0, -90.0, 0.0, M_soil)
cut = box('cutter', PX0, PX1, -0.5, PY1, PZB, 0.05, M_conc)
mod = soil.modifiers.new('cut', 'BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.object = cut
try: mod.solver = 'EXACT'
except Exception: pass
dg = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(soil.evaluated_get(dg)); soil.modifiers.clear(); soil.data = me
bpy.data.objects.remove(cut)
box('ENV_grass_L', -300, PX0, 0.0, 900.0, 0.0, 0.012, M_grass)
box('ENV_grass_R', PX1, 300, 0.0, 900.0, 0.0, 0.012, M_grass)
box('ENV_grass_B', PX0, PX1, PY1, 900.0, 0.0, 0.012, M_grass)
grass_patch = box('DIG_grass_patch', PX0, PX1, 0.0, PY1, 0.0, 0.012, M_grass)
plug = box('DIG_plug', PX0, PX1, 0.0, PY1, PZB, 0.0, M_soil)                       # soil still to be dug out
mound = sphere('DIG_mound', (-1.95, 0.72, 0.0), 0.50, M_dirt, sx=1.0, sy=0.9, sz=0.55, seg=10, smooth=False)
backfill = box('DIG_backfill', PX0, PX1, 0.0, PY1, -0.35, 0.0, M_soil)

T_LID = T_OUT1 - 0.1; T_BACKFILL = T_OUT1 + 0.2
key(grass_patch, 'scale', T_DIG0, (1, 1, 1)); key(grass_patch, 'scale', T_DIG0 + 0.25, Z)
key(grass_patch, 'scale', T_BACKFILL + 0.45, Z); key(grass_patch, 'scale', T_BACKFILL + 0.7, (1, 1, 1))
key(plug, 'scale', T_DIG0, (1, 1, 1)); key(plug, 'scale', T_DIG1, (1, 1, 0.001)); key(plug, 'scale', T_DIG1 + 0.04, Z, ip='CONSTANT')
appear(mound, T_DIG0 + 0.2, dur=0.9, s=(1.0, 0.9, 0.55), over=1.0)
vanish(mound, T_BACKFILL, dur=0.5)
grow(backfill, T_BACKFILL, T_BACKFILL + 0.5)

# ================================================================ tank
floor = box('TANK_floor', PX0, PX1, 0.0, PY1, -2.17, -2.05, M_conc, origin='center')
wall_l = box('TANK_wall_L', -1.42, -1.30, 0.0, PY1, -2.05, -0.45, M_conc)
wall_r = box('TANK_wall_R', 1.30, 1.42, 0.0, PY1, -2.05, -0.45, M_conc)
wall_b = box('TANK_wall_B', -1.42, 1.42, 1.20, PY1, -2.05, -0.45, M_conc_d)
lid = box('TANK_lid', -1.42, 1.42, 0.0, PY1, -0.45, -0.35, M_conc, origin='left')
baf_lo = box('TANK_baffle_lo', 0.40, 0.50, 0.0, 1.2, -2.05, -1.32, M_conc)
baf_hi = box('TANK_baffle_hi', 0.40, 0.50, 0.0, 1.2, -1.14, -0.45, M_conc, origin='top')
riser_a = box('TANK_riser_a', -1.00, -0.40, -0.004, 0.90, -0.35, 0.10, M_conc_d)
riser_b = box('TANK_riser_b', 0.55, 1.15, -0.004, 0.90, -0.35, 0.10, M_conc_d)
grow(floor, T_SEAL0, T_SEAL0 + 0.45, axis=0)
for o, d in ((wall_l, 0.30), (wall_r, 0.40), (wall_b, 0.35)): grow(o, T_SEAL0 + d, T_SEAL1 - 0.1)
grow(lid, T_LID, T_LID + 0.5, axis=0)
appear(riser_a, T_BACKFILL + 0.45, 0.3); appear(riser_b, T_BACKFILL + 0.55, 0.3)
grow(baf_lo, T_WALL0, T_WALL0 + 0.8); grow(baf_hi, T_WALL0 + 0.35, T_WALL1 + 0.3)

# liquids (one body spans the pit; concrete simply covers its edges once poured)
liq = box('LIQ_main', PX0, PX1, 0.004, 1.2, PZB, 0.0, M_liq)
for t, z in LEVELS: key(liq, 'scale', t, (1, 1, max(0.0005, (z - PZB) / (0.0 - PZB))), ip='LINEAR')
liq2 = box('LIQ_2', 0.50, 1.30, 0.002, 1.2, -2.05, LEVEL - 0.005, M_liq2)
show(liq2, T_WALL1 + 0.3)
c1 = bsdf_of(M_liq).inputs['Base Color']
key_input(c1, T_SINK, (0.20, 0.14, 0.08, 1)); key_input(c1, T_SCUM + 0.3, (0.34, 0.27, 0.16, 1))
c2 = bsdf_of(M_liq2).inputs['Base Color']
key_input(c2, T_CLEAR, (0.20, 0.14, 0.08, 1)); key_input(c2, T_MOVES + 0.5, (0.56, 0.49, 0.33, 1))
scum = box('LIQ_scum', -1.30, 0.40, 0.001, 1.2, LEVEL - 0.085, LEVEL + 0.012, M_scum, origin='top')
grow(scum, T_GREASE + 0.5, T_SCUM + 0.45)

def sludge(name, x0, x1, base, h, bump, m, seed):
    rnd = random.Random(seed); n = 26; xs = [x0 + (x1 - x0) * i / n for i in range(n + 1)]
    ph = [rnd.uniform(0, 6.28) for _ in range(3)]
    top = [h + bump * (0.5 * math.sin(3.1 * x + ph[0]) + 0.3 * math.sin(7.3 * x + ph[1]) + 0.2 * math.sin(13 * x + ph[2])) for x in xs]
    o = prism(name, [(x, 0.0) for x in xs] + [(x, t) for x, t in zip(reversed(xs), reversed(top))], 0.0, 1.2, m)
    o.location = (0, -0.004, base)
    return o
slu1 = sludge('SLUDGE_1', -1.30, 0.40, -2.05, 0.30, 0.05, M_sludge, 3)
slu2 = sludge('SLUDGE_2', 0.50, 1.30, -2.05, 0.09, 0.02, M_sludge, 5)
hidden_until(slu1, T_SINK); key(slu1, 'scale', T_SINK + 0.2, (1, 1, 0.02)); key(slu1, 'scale', T_SLUDGE + 0.6, (1, 1, 1))
key(slu1, 'scale', T_YEARS, (1, 1, 1)); key(slu1, 'scale', T_TRUCK - 0.2, (1, 1, 1.95))
key(slu1, 'scale', T_PUMP + 0.5, (1, 1, 1.95)); key(slu1, 'scale', T_PUMP + 1.5, (1, 1, 0.22))
hidden_until(slu2, T_MOVES); key(slu2, 'scale', T_MOVES, (1, 1, 0.02)); key(slu2, 'scale', T_MOVES + 1.5, (1, 1, 1))

# ================================================================ pipes
X_END = -3.40                                                    # where the first pipe stops before there is anything to drain into
def drain_z(x): return -0.45 - 0.11 * (x + 5.10) / 3.80          # gentle fall from the toilet to the tank inlet
pipe_a = pipe('PIPE_drain_a', [(-5.10, 0.0, 0.16), (-5.10, 0.0, -0.45), (X_END, 0.0, drain_z(X_END))])
pipe_b = pipe('PIPE_drain_b', [(X_END, 0.0, drain_z(X_END)), (-1.30, 0.0, Z_IN)])
extend(pipe_b, T_PIPE0, T_PIPE1)
tee_in = tube('PIPE_in_tee', [(-1.30, 0.0, Z_IN), (-1.13, 0.0, Z_IN), (-1.13, 0.0, -0.50), (-1.13, 0.0, -1.10)], 0.085, M_pvc, origin=(-1.13, 0.0, -0.8))
tee_out = tube('PIPE_out_tee', [(1.13, 0.0, -0.50), (1.13, 0.0, -1.15), (1.13, 0.0, Z_OUT), (1.30, 0.0, Z_OUT)], 0.085, M_pvc, origin=(1.13, 0.0, -0.8))
appear(tee_in, T_WALL1 + 0.35, 0.3); appear(tee_out, T_WALL1 + 0.6, 0.3)
pipe_out = pipe('PIPE_out', [(1.30, 0.0, Z_OUT), (3.00, 0.0, -0.75)])
extend(pipe_out, T_OUT0, T_OUT0 + 0.7)
X_VENT = -4.30
vent = pipe('PIPE_vent', [(X_VENT, 0.0, drain_z(X_VENT)), (X_VENT, 0.0, 3.75)], R=0.065)

# ================================================================ house (cut open on the same plane)
box('HOUSE_floor', -8.8, -4.4, 0.0, 4.0, 0.012, 0.16, M_conc)
box('HOUSE_wall_L', -8.8, -8.66, 0.0, 4.0, 0.16, 2.70, M_wall)
box('HOUSE_wall_R', -4.54, -4.40, 0.0, 4.0, 0.16, 2.70, M_wall)
box('HOUSE_wall_B', -8.66, -4.54, 3.86, 4.0, 0.16, 2.70, M_tile)
box('HOUSE_ceiling', -8.8, -4.4, 0.0, 4.0, 2.70, 2.82, M_wall)
prism('HOUSE_roof', [(-9.2, 2.82), (-4.0, 2.82), (-6.6, 4.25)], -0.25, 4.3, M_roof)
box('HOUSE_window', -7.9, -6.7, 3.84, 3.86, 1.25, 2.15, M_window)
box('HOUSE_partition', -6.10, -6.02, 0.0, 4.0, 0.16, 2.70, M_wall)
box('HOUSE_floor_tile', -6.02, -4.54, 0.02, 3.86, 0.16, 0.175, M_tile)
cyl('TOILET_base', (-5.10, 0.50, 0.16), 0.13, 0.22, M_ceramic, seg=16, smooth=True)
cyl('TOILET_bowl', (-5.10, 0.50, 0.36), 0.15, 0.20, M_ceramic, seg=18, r2=0.22, smooth=True)
cyl('TOILET_seat', (-5.10, 0.50, 0.56), 0.23, 0.035, M_ceramic, seg=18, smooth=True)
box('TOILET_tank', -4.86, -4.56, 0.22, 0.78, 0.50, 0.98, M_ceramic)
box('TOILET_lid', -4.88, -4.55, 0.20, 0.80, 0.98, 1.02, M_ceramic)

# ================================================================ sewage on the move
BY = -(R_PIPE + 0.012 + 0.06)                                    # just in front of the pipe bore
def blob(name, r=0.05, m=None): return sphere(name, (0, BY, -30), r, m or M_solid, seg=8)

lbl_nosewer = label('LBL_nosewer', 'NO SEWER', -3.55, -1.05, 0.23, plate=M_plate_red)
for k in range(4):                                               # pulse while the question is asked
    key(lbl_nosewer, 'scale', 0.35 + k * 0.62, (1, 1, 1)); key(lbl_nosewer, 'scale', 0.35 + k * 0.62 + 0.2, (1.13, 1.13, 1.13))
vanish(lbl_nosewer, T_FLUSH + 0.2, 0.2)
b0 = blob('BLOB_flush', 0.058)                                   # the first flush: the pipe leads nowhere yet
show(b0, T_FLUSH, T_PIPE0)
travel(b0, [(T_FLUSH, (-5.10, BY, 0.10)), (T_FLUSH + 0.4, (-5.10, BY, -0.45)), (T_Q - 0.25, (X_END, BY, drain_z(X_END))), (T_Q, (X_END + 0.14, BY, -0.74))])
puddle = sphere('BLOB_puddle', (X_END + 0.18, -0.03, -0.78), 0.24, M_solid, sx=1.0, sy=0.15, sz=0.5, seg=10)
appear(puddle, T_Q - 0.05, 0.3, s=(1.0, 0.15, 0.5)); vanish(puddle, T_PIPE0, 0.3)
qmark = text('LBL_question', '?', (-2.72, -0.10, -0.55), 0.66, M_yellow, extrude=0.02)
appear(qmark, T_Q, 0.3); vanish(qmark, T_DIG0 - 0.1, 0.2)

stream_times = [T_PIPE1 + 0.05, T_PIPE1 + 0.5, T_PIPE1 + 0.95, T_SEEP - 0.2, T_SEEP + 0.6, T_SEAL0 + 0.1, T_SEAL0 + 1.0,
                T_SEAL1 + 0.7, T_SEAL1 + 1.3, T_SEAL1 + 1.9, T_FILL0 - 0.9, T_FILL0 - 0.5, T_FILL0 - 0.1, T_FILL0 + 0.3, T_FILL0 + 0.7]
for i, t0 in enumerate(stream_times):
    b = blob(f'BLOB_stream_{i}', random.uniform(0.045, 0.058))
    z_land = max(level_at(t0 + 1.2), -2.10) - 0.02
    show(b, t0 - 0.75, t0 + 1.27)
    travel(b, [(t0 - 0.75, (-5.10, BY, -0.45)), (t0 + 0.85, (-1.36, BY, Z_IN)), (t0 + 0.97, (-1.20, BY, Z_IN - 0.12)), (t0 + 1.25, (-1.13, BY, z_land))])

solids = []                                                      # suspended in the tank once it fills
for i in range(34):
    x = random.uniform(-1.18, 0.30); z = random.uniform(-1.62, -0.92)
    o = sphere(f'SOLID_{i}', (x, -0.03, z), random.uniform(0.032, 0.052), M_solid, seg=8); solids.append(o)
    appear(o, t_level_reaches(z + 0.12) + 0.05, 0.25)
    f_a = T_SINK + random.uniform(0.05, 0.9); f_b = f_a + 0.55 + 0.9 * (z + 1.80)
    key(o, 'location', f_a); key(o, 'location', min(f_b, T_SLUDGE + 0.9), -1.76 + random.uniform(-0.01, 0.03), index=2)
    vanish(o, T_PUMP + 0.6 + random.uniform(0, 0.5), 0.25)
greases = []
for i in range(18):
    x = random.uniform(-1.18, 0.30); z = random.uniform(-1.55, -0.95)
    o = sphere(f'GREASE_{i}', (x, -0.032, z), random.uniform(0.024, 0.036), M_grease, seg=8); greases.append(o)
    appear(o, t_level_reaches(z + 0.12) + 0.05, 0.25)
    f_a = T_GREASE + random.uniform(0.0, 0.7)
    key(o, 'location', f_a); key(o, 'location', f_a + 0.5 + 0.6 * (-0.8 - z), LEVEL - 0.04 + random.uniform(-0.02, 0.02), index=2)

clog = []                                                        # solids that escape through the bare outlet and pile up at the pipe's end
for i in range(9):
    b = blob(f'BLOB_out_{i}', 0.05); clog.append(b)
    t0 = T_SOLIDS + 0.1 + i * 0.2; x_end = 2.92 - 0.105 * i; z_end = Z_OUT - 0.05 * (x_end - 1.30) / 1.70
    show(b, t0)
    travel(b, [(t0, (random.uniform(0.6, 1.0), BY, random.uniform(-1.15, -0.9))), (t0 + 0.45, (1.30, BY, Z_OUT)), (t0 + 0.45 + 0.6 * (x_end - 1.3) / 1.62, (x_end, BY, z_end))])
    key(b, 'scale', T_WALL0 - 0.3, (1, 1, 1), ip='BEZIER'); key(b, 'scale', T_WALL0 - 0.05, Z, ip='CONSTANT')
lbl_clog = label('LBL_clog', 'CLOGGED', 2.62, -0.30, 0.20, plate=M_plate_red)
appear(lbl_clog, T_CLOG + 0.3, 0.3); vanish(lbl_clog, T_WALL0 - 0.3, 0.2)
lbl_full = label('LBL_full', 'FULL', 0.0, -0.66, 0.34, plate=M_plate_red)
appear(lbl_full, T_FILL1 - 0.25, 0.3); vanish(lbl_full, T_OUT0 + 0.15, 0.2)

# ================================================================ leak: stain in the soil, then the well
core = smooth_path([(-3.25, -0.28), (-2.6, -0.95), (-1.2, -1.35), (0.4, -1.7), (1.9, -2.1), (3.3, -1.6), (4.0, -0.6), (3.7, 0.5), (2.6, 1.15), (1.2, 1.42), (0.28, 1.46)], 6)
plume = patch('PLUME_pit', [(0.0, 0.0), (-2.84, 0.0)] + [(p[0], p[1]) for p in core] + [(0.0, 1.38)], M_plume)   # wraps the pit's floor and right wall
plume.location = (PX1, -0.006, PZB)
hidden_until(plume, T_PIPE1 + 0.5)
key(plume, 'scale', T_PIPE1 + 0.5, (0.03, 1, 0.03)); key(plume, 'scale', T_PROB1, (0.12, 1, 0.12)); key(plume, 'scale', T_SEEP, (0.42, 1, 0.42)); key(plume, 'scale', T_WELL, (1, 1, 1))
key(plume, 'scale', T_SEAL1 + 0.45, (1, 1, 1), ip='CONSTANT'); key(plume, 'scale', T_SEAL1 + 0.5, Z, ip='CONSTANT')
a1 = bsdf_of(M_plume).inputs['Alpha']
key_input(a1, T_SEAL0, 0.62); key_input(a1, T_SEAL1 + 0.4, 0.0)

WX = 30.0; WT, WB = -2.0, -3.6                                   # the well is its own set far to the right; water table / shaft bottom
box('WELL_shaft', WX - 0.40, WX + 0.40, -0.010, 0.8, WB, 0.0, M_dark)
box('WELL_lining_L', WX - 0.52, WX - 0.40, -0.012, 0.8, WB - 0.12, 0.95, M_stone)
box('WELL_lining_R', WX + 0.40, WX + 0.52, -0.012, 0.8, WB - 0.12, 0.95, M_stone)
box('WELL_lining_bottom', WX - 0.40, WX + 0.40, -0.012, 0.8, WB - 0.12, WB, M_stone)
box('WELL_head_back', WX - 0.40, WX + 0.40, 0.68, 0.8, 0.0, 0.95, M_stone)
box('WELL_water', WX - 0.40, WX + 0.40, -0.013, 0.8, WB, WT, M_water)
box('WELL_post_L', WX - 0.50, WX - 0.42, 0.30, 0.38, 0.95, 2.05, M_wood)
box('WELL_post_R', WX + 0.42, WX + 0.50, 0.30, 0.38, 0.95, 2.05, M_wood)
box('WELL_beam', WX - 0.62, WX + 0.62, 0.28, 0.40, 2.05, 2.17, M_wood)
tube('WELL_rope', [(WX, 0.34, 2.05), (WX, 0.34, 1.30)], 0.012, M_ink)
cyl('WELL_bucket', (WX, 0.34, 1.06), 0.13, 0.24, M_steel, seg=14, r2=0.16)
sign('SIGN_well', 'WELL', WX + 0.64, WX + 1.84, 1.2, 1.0, 1.6, 0.34)
patch('WELL_groundwater', [(WX - 14, WT), (WX + 14, WT), (WX + 14, WT - 1.9), (WX - 14, WT - 1.9)], M_gwater, y=-0.004)
lbl_gw = label('LBL_groundwater', 'GROUNDWATER', WX - 1.95, WT - 1.50, 0.21)
tongue = smooth_path([(0.0, 0.9), (1.5, 0.75), (2.6, 0.2), (3.4, -0.3), (3.85, -0.75), (3.2, -1.35), (2.2, -1.75), (1.0, -1.9), (0.0, -1.95)], 6)
plume2 = patch('PLUME_well', [(p[0], p[1]) for p in tongue], M_plume2, y=-0.016); plume2.location = (WX - 4.2, -0.016, -1.6)
key(plume2, 'scale', T_WELL - 0.1, (0.3, 1, 1)); key(plume2, 'scale', T_WELL + 1.0, (1, 1, 1))
cw = bsdf_of(M_water).inputs['Base Color']
key_input(cw, T_WELL + 0.75, (0.12, 0.45, 0.85, 1)); key_input(cw, T_WELL + 1.3, (0.30, 0.27, 0.10, 1))
ew = bsdf_of(M_water).inputs['Emission Color']
key_input(ew, T_WELL + 0.75, (0.12, 0.45, 0.85, 1)); key_input(ew, T_WELL + 1.3, (0.30, 0.27, 0.10, 1))
warn = empty('WARN_root', (WX - 1.75, -0.05, 1.05))
prism('WARN_tri', [(-0.58, -0.44), (0.58, -0.44), (0.0, 0.56)], 0.0, 0.04, M_plate_red, parent=warn)
text('WARN_txt', '!', (0, -0.012, -0.10), 0.62, M_white, parent=warn)
appear(warn, T_WELL + 1.05, 0.3)

# ================================================================ in the tank: tags, arrows, bacteria, gas
lbl_sludge = label('LBL_sludge', 'SLUDGE', -0.45, -1.92, 0.17)
lbl_scum = label('LBL_scum', 'SCUM', -0.45, -0.60, 0.14)
lbl_clear = label('LBL_clear', 'CLEARER WATER', -0.45, -1.28, 0.17)
appear(lbl_sludge, T_SLUDGE, 0.3); appear(lbl_scum, T_SCUM, 0.3); appear(lbl_clear, T_CLEAR + 0.1, 0.3)
for o in (lbl_sludge, lbl_scum, lbl_clear): vanish(o, T_FIELD - 0.35, 0.25)

def arrow(name, loc, length=0.42):
    h, hw, hl = 0.05, 0.12, 0.17
    o = prism(name, [(-length / 2, -h), (length / 2 - hl, -h), (length / 2 - hl, -hw), (length / 2, 0), (length / 2 - hl, hw), (length / 2 - hl, h), (-length / 2, h)], -0.02, 0.0, M_arrow)
    o.location = loc; return o
arr1 = arrow('ARROW_slot', (0.45, -0.07, -1.23), 0.46); arr2 = arrow('ARROW_out', (1.86, -0.12, -0.46), 0.52)
for a, t0 in ((arr1, T_MOVES), (arr2, T_MOVES + 0.3)):
    appear(a, t0, 0.3); x = a.location.x
    key(a, 'location', t0 + 0.3, index=0); key(a, 'location', T_FIELD + 1.5, x + 0.12, index=0)
    vanish(a, T_FIELD + 1.6, 0.25)
fines = []
for i in range(14):
    o = sphere(f'FINE_{i}', (random.uniform(0.60, 1.02), -0.03, random.uniform(-1.75, LEVEL - 0.15)), random.uniform(0.016, 0.024), M_fine, seg=8); fines.append(o)
    appear(o, T_MOVES + random.uniform(0.0, 0.6), 0.25)
    key(o, 'location', T_MOVES + 0.9, index=2); key(o, 'location', T_MOVES + 4.0, o.location.z - random.uniform(0.1, 0.3), index=2)
    vanish(o, T_FIELD + 2.5, 0.4)

bact = []
for i in range(46):
    o = sphere(f'BACT_{i}', (random.uniform(-1.22, 0.33), -0.036, random.uniform(-1.80, -1.66)), 0.017, M_bact, sx=2.6, seg=8)
    o.rotation_euler = (0, random.uniform(0, 3.14), 0); bact.append(o)
    appear(o, T_BACT + random.uniform(0.0, 0.9), 0.25, s=(2.6, 1, 1))
gas = []
for i in range(14):
    x0 = random.uniform(-1.05, 0.25); t0 = T_GAS - 0.5 + i * 0.12
    o = sphere(f'GAS_{i}', (x0, -0.04, -1.70), random.uniform(0.024, 0.038), M_gas, seg=8); gas.append(o)
    show(o, t0)
    travel(o, [(t0, (x0, -0.04, -1.70)), (t0 + 0.9, (x0 + random.uniform(-0.1, 0.1), -0.04, LEVEL + 0.10)),
               (T_VENT + 0.5 + i * 0.03, (-1.02 + random.uniform(-0.06, 0.06), -0.04, -0.53 + random.uniform(-0.02, 0.02)))])
    key(o, 'scale', T_YEARS - 0.2, (1, 1, 1), ip='BEZIER'); key(o, 'scale', T_YEARS + 0.2, Z, ip='CONSTANT')
VY = -(0.065 + 0.012 + 0.05)
for i in range(8):                                               # gas running back up the drain line and out of the vent stack
    t0 = T_VENT - 0.1 + i * 0.26
    o = sphere(f'VENTGAS_{i}', (X_VENT, VY, -0.4), 0.045, M_gas, seg=8); show(o, t0, t0 + 1.62)
    travel(o, [(t0, (-2.0, BY, drain_z(-2.0))), (t0 + 0.5, (X_VENT, VY, drain_z(X_VENT))), (t0 + 1.6, (X_VENT, VY, 3.72))])
for i in range(7):
    t0 = T_ROOF - 0.15 + i * 0.27
    o = sphere(f'PUFF_{i}', (X_VENT, 0.0, 3.8), 0.26, M_gas, seg=10)
    key(o, 'scale', 0.0, Z, ip='CONSTANT'); key(o, 'scale', t0, Z); key(o, 'scale', t0 + 0.5, (1, 1, 1)); key(o, 'scale', t0 + 1.3, Z)
    travel(o, [(t0, (X_VENT, 0.0, 3.80)), (t0 + 1.3, (X_VENT + random.uniform(0.2, 0.7), 0.0, 5.0))])
lbl_vent = label('LBL_vent', 'VENT', -3.42, 3.42, 0.26)
appear(lbl_vent, T_VENT + 0.45, 0.3); key(lbl_vent, 'scale', C14, (1, 1, 1), ip='CONSTANT'); key(lbl_vent, 'scale', C14 + 0.03, Z, ip='CONSTANT')

# ================================================================ drain field
gravel = box('FIELD_gravel', 3.0, 7.4, -0.015, 0.9, -1.25, -0.62, M_gravel, origin='left')
grow(gravel, T_FIELD + 0.2, T_GRAVEL, axis=0)
def perf_z(x): return -0.75 - 0.07 * (x - 3.0) / 4.3
pipe_perf = pipe('PIPE_perf', [(3.0, 0.0, -0.75), (7.30, 0.0, perf_z(7.30))])
extend(pipe_perf, T_FIELD + 0.1, T_GRAVEL - 0.2)
wet = smooth_path([(7.4, -1.25), (7.62, -1.7), (7.3, -2.25), (6.5, -2.52), (5.6, -2.38), (4.7, -2.56), (3.8, -2.4), (3.05, -2.3), (2.78, -1.75), (3.0, -1.25)], 6)
moist = patch('FIELD_moist', [(p[0], p[1]) for p in wet], M_moist, y=-0.004)
show(moist, T_GRAVEL)
am = bsdf_of(M_moist).inputs['Alpha']
key_input(am, T_GRAVEL, 0.0); key_input(am, T_SOIL + 1.2, 0.42)
for i in range(8):
    hx = 3.45 + 0.5 * i; hz = perf_z(hx)
    hsp = sphere(f'FIELD_hole_{i}', (hx, -0.088, hz - 0.075), 0.03, M_hole, sy=0.3, seg=8); appear(hsp, T_GRAVEL - 0.3 + i * 0.05, 0.2, s=(1, 0.3, 1))
    for c in range(4):
        t0 = T_GRAVEL + 0.05 + c * 0.75 + (i % 3) * 0.22
        d1 = sphere(f'DROP_m_{i}_{c}', (hx, -0.14, hz - 0.12), 0.045, M_drop, seg=8); show(d1, t0, t0 + 0.5)
        travel(d1, [(t0, (hx, -0.14, hz - 0.12)), (t0 + 0.5, (hx + random.uniform(-0.05, 0.05), -0.14, -1.24))])
        d2 = sphere(f'DROP_c_{i}_{c}', (hx, -0.05, -1.3), 0.042, M_drop_c, seg=8)
        key(d2, 'scale', 0.0, Z, ip='CONSTANT'); key(d2, 'scale', t0 + 0.5, (1, 1, 1)); key(d2, 'scale', t0 + 1.5, Z)
        travel(d2, [(t0 + 0.5, (hx, -0.05, -1.31)), (t0 + 1.5, (hx + random.uniform(-0.08, 0.08), -0.05, -2.32))])
sgn_field = sign('SIGN_field', 'DRAIN FIELD', 3.85, 6.55, 1.5, 1.0, 1.66, 0.32)
appear(sgn_field, T_FIELD + 0.5, 0.3)
key(sgn_field, 'scale', T_HERO - 0.03, (1, 1, 1), ip='CONSTANT'); key(sgn_field, 'scale', T_HERO, Z, ip='CONSTANT')

# ================================================================ counter sign (days, then years)
sgn_count = sign('SIGN_count', '', 1.50, 2.90, 1.7, 0.95, 1.65, 0.3)
appear(sgn_count, T_SEAL1 + 0.5, 0.3)
def counter(bodies_times, t_end):
    for (body, t0), nxt in zip(bodies_times, bodies_times[1:] + [(None, t_end)]):
        t = text('COUNT_' + body.replace(' ', '_'), body, (0, -0.014, 1.30), 0.30, M_ink, parent=sgn_count); show(t, t0, nxt[1])
counter([('DAY 1', T_SEAL1 + 0.5), ('DAY 2', T_SEAL1 + 1.6), ('DAY 3', T_FILL0 - 0.6), ('DAY 4', T_FILL0 + 0.15), ('DAY 5', T_FILL0 + 0.75)], T_OUT0 + 0.4)
counter([('YEAR 1', T_YEARS), ('YEAR 2', T_YEARS + 1.2), ('YEAR 3', W(144)), ('YEAR 4', W(145)), ('YEAR 5', W(146))], T_HERO)
key(sgn_count, 'scale', T_OUT0 + 0.15, (1, 1, 1)); key(sgn_count, 'scale', T_OUT0 + 0.35, Z)
key(sgn_count, 'scale', T_YEARS - 0.2, Z); key(sgn_count, 'scale', T_YEARS, (1, 1, 1))
key(sgn_count, 'scale', T_TRUCK - 0.25, (1, 1, 1)); key(sgn_count, 'scale', T_TRUCK - 0.1, Z)

# ================================================================ pump truck
TRX = -0.6
truck = empty('TRUCK_root', (17.0, 0.0, 0.0))
box('TRUCK_chassis', -0.9, 4.3, 2.3, 3.9, 0.55, 0.72, M_chassis, parent=truck)
box('TRUCK_cab', 2.7, 4.3, 2.25, 3.95, 0.72, 2.25, M_truck, parent=truck)
box('TRUCK_window', 3.05, 3.95, 2.235, 2.25, 1.42, 2.02, M_window, parent=truck)
tk = cyl('TRUCK_tank', (-0.75, 3.1, 1.55), 0.78, 3.2, M_ttank, seg=24, parent=truck, smooth=True); tk.rotation_euler = (0, math.radians(90), 0)
for bx in (0.0, 1.7):
    bd = cyl('TRUCK_band', (bx, 3.1, 1.55), 0.80, 0.09, M_chassis, seg=24, parent=truck); bd.rotation_euler = (0, math.radians(90), 0)
for wx in (-0.25, 0.75, 3.5):
    for wy in (2.52, 4.0):
        wh = cyl('TRUCK_wheel', (wx, wy, 0.432), 0.42, 0.30, M_tire, seg=18, parent=truck); wh.rotation_euler = (math.radians(90), 0, 0)
        hb = cyl('TRUCK_hub', (wx, wy - 0.30, 0.432), 0.18, 0.02, M_steel, seg=12, parent=truck); hb.rotation_euler = (math.radians(90), 0, 0)
box('TRUCK_plate', -0.05, 1.95, 2.285, 2.305, 1.30, 1.80, M_sign, parent=truck)
text('TRUCK_txt', 'PUMP TRUCK', (0.95, 2.275, 1.55), 0.25, M_ink, parent=truck)
key(truck, 'location', T_TRUCK - 0.75, (17.0, 0, 0), ip='SINE', ease='EASE_OUT'); key(truck, 'location', T_TRUCK + 0.45, (TRX, 0, 0), ip='CONSTANT')
show(truck, T_TRUCK - 0.8, T_HERO)
hose = tube('TRUCK_hose', smooth_path([(TRX - 0.72, 2.45, 1.30), (TRX - 0.9, 1.6, 1.6), (-1.0, 0.7, 1.05), (-0.72, -0.02, 0.5), (-0.70, -0.07, -0.25), (-0.70, -0.07, -1.74)], 8), 0.05, M_hose, res=4)
extend(hose, T_TRUCK + 0.5, T_PUMP + 0.4)
key(hose, 'scale', T_HERO - 0.03, (1, 1, 1), ip='CONSTANT'); key(hose, 'scale', T_HERO, Z, ip='CONSTANT')

# ================================================================ trees
for i in range(75):
    x = random.uniform(-150, 90); y = random.uniform(16, 110); s = random.uniform(0.8, 1.5)
    cyl(f'TREE_trunk_{i}', (x, y, 0), 0.16 * s, 1.6 * s, M_trunk, seg=7, r2=0.10 * s)
    for k in range(3):
        sphere(f'TREE_leaf_{i}_{k}', (x + random.uniform(-0.7, 0.7) * s, y + random.uniform(-0.5, 0.5) * s, (2.1 + random.uniform(-0.2, 0.7)) * s),
               random.uniform(0.75, 1.15) * s, random.choice([M_leaf, M_leaf2]), sz=0.72, seg=8, smooth=False)

# ================================================================ mascot (original 'little engineer')
mascot = empty('MASCOT_root', (-3.35, 0.9, 0.0))
for sx in (-0.11, 0.11):
    cyl('CHAR_leg', (sx, 0, 0.012), 0.075, 0.80, M_pants, seg=10, parent=mascot)
    box('CHAR_boot', sx - 0.085, sx + 0.085, -0.17, 0.10, 0.012, 0.11, M_ink, parent=mascot)
box('CHAR_torso', -0.21, 0.21, -0.13, 0.13, 0.80, 1.42, M_vest, parent=mascot)
box('CHAR_stripe', -0.215, 0.215, -0.135, 0.135, 1.02, 1.09, M_stripe, parent=mascot)
arms = []
for sx in (-0.27, 0.27):
    a = cyl('CHAR_arm', (sx, 0, 1.37), 0.052, 0.58, M_skin, seg=10, down=True, parent=mascot)
    a.rotation_euler = (0, math.radians(8 if sx < 0 else -8), 0); arms.append(a)
    sphere('CHAR_shoulder', (sx * 0.95, 0, 1.36), 0.085, M_vest, seg=10, parent=mascot)
arm_l, arm_r = arms
cyl('CHAR_neck', (0, 0, 1.42), 0.05, 0.08, M_skin, seg=10, parent=mascot)
sphere('CHAR_head', (0, 0, 1.63), 0.15, M_skin, sz=1.1, parent=mascot)
me = bpy.data.meshes.new('helmet'); bm = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=18, v_segments=10, radius=0.178)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -1e-4], context='VERTS')
for f in bm.faces: f.smooth = True
bm.to_mesh(me); bm.free()
helmet = link(bpy.data.objects.new('CHAR_helmet', me), M_helmet, mascot); helmet.location = (0, 0, 1.69); helmet.scale = (1, 1, 0.82)
cyl('CHAR_helmet_brim', (0, -0.04, 1.682), 0.205, 0.022, M_helmet, seg=22, parent=mascot)
shovel = empty('SHOVEL_root', (0, -0.07, -0.30), parent=arm_r)
cyl('SHOVEL_handle', (0, 0, 0), 0.022, 0.95, M_wood, seg=8, down=True, parent=shovel)
box('SHOVEL_blade', -0.10, 0.10, -0.012, 0.012, -1.22, -0.93, M_steel, parent=shovel)

def arm(a, t, deg): key(a, 'rotation_euler', t, math.radians(deg), index=1)
for a_, s_ in ((arm_l, 1), (arm_r, -1)):                         # a shrug at "No sewer on your street?"
    arm(a_, 0.45, 8 * s_); arm(a_, 0.8, 42 * s_); arm(a_, 1.45, 42 * s_); arm(a_, 1.85, 8 * s_)
arm(arm_l, T_Q - 0.2, 8); arm(arm_l, T_Q + 0.25, 158); arm(arm_l, T_Q + 0.6, 140); arm(arm_l, T_Q + 0.95, 158); arm(arm_l, T_SHOVEL + 0.5, 8)   # scratches head at the '?'
appear(shovel, T_SHOVEL, 0.3)
arm(arm_r, T_SHOVEL, -8); arm(arm_r, T_SHOVEL + 0.45, -128); arm(arm_r, T_DIG0 - 0.5, -128); arm(arm_r, T_DIG0 - 0.1, -25)
n_dig = 3; span = (T_DIG1 - T_DIG0) / n_dig
for k in range(n_dig):
    arm(arm_r, T_DIG0 + k * span + span * 0.5, -78); arm(arm_r, T_DIG0 + (k + 1) * span, -22)
arm(arm_r, T_DIG1 + 0.4, -8)
vanish(shovel, T_SEAL0 - 0.3, 0.25)
arm(arm_l, T_VENT + 0.2, 8); arm(arm_l, T_VENT + 0.75, 142); arm(arm_l, C14, 142)            # points up at the vent
key(mascot, 'location', T_SHOVEL + 0.9, (-3.35, 0.9, 0.0)); key(mascot, 'location', T_DIG0 - 0.15, (-2.80, 0.9, 0.0))
key(mascot, 'location', C5 - 0.03, (-2.80, 0.9, 0.0), ip='CONSTANT'); key(mascot, 'location', C5, (-3.62, 0.9, 0.0), ip='CONSTANT')
key(mascot, 'location', T_HERO, (0.1, 0.5, 0.0), ip='CONSTANT')
for a, sgn_ in ((arm_l, 1), (arm_r, -1)):                        # both arms up for the finale
    arm(a, T_HERO - 0.03, 142 if sgn_ > 0 else -8)
    for k in range(6):
        arm(a, T_HERO + 0.45 + k * 0.7, 155 * sgn_); arm(a, T_HERO + 0.8 + k * 0.7, 125 * sgn_)
    arm(a, T_HERO + 4.9, 150 * sgn_)

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
HERO_A = hero_pose(30, 25, 20.5); HERO_B = hero_pose(33, 26, 19.5)

shot(0.0, C1, pose(-5.2, 10.2, 1.2, 0.3), pose(-4.9, 9.6, 1.1, 0.15), cut=True)            # no sewer: the flush has nowhere to go
shot(C1, C2, pose(-3.5, 9.4, 0.9, -0.2), mv=1.1)                                          # "Let's build..."
shot(C2, C3, pose(-1.0, 10.4, 0.6, -0.95), mv=1.3)                                        # dig + pipe
shot(C3, T_WELL, pose(1.4, 11.2, 0.5, -1.7), mv=1.6)                                      # seepage spreads
shot(T_WELL, C5, pose(WX - 0.75, 10.2, 0.5, -2.4), cut=True)                               # ...to the well
shot(C5, C7, pose(0.3, 9.4, 0.45, -1.0), pose(0.4, 9.0, 0.44, -1.0), cut=True)            # seal, then it fills
shot(C7, C8, pose(1.0, 9.2, 0.4, -1.0), mv=1.0)                                           # outlet pipe
shot(C8, C9, pose(1.7, 8.9, 0.38, -1.0), mv=1.2)                                          # solids escape and clog
shot(C9, C10, pose(0.0, 6.9, 0.3, -1.36), pose(0.0, 6.5, 0.3, -1.36), cut=True)           # the wall
shot(C10, C11, pose(-0.2, 6.2, 0.3, -1.36), mv=1.0)                                       # sludge + scum
shot(C11, C12, pose(0.5, 6.4, 0.3, -1.34), mv=1.0)                                        # clearer water moves on
shot(C12, C13, pose(5.15, 9.8, 0.35, -1.15), pose(5.25, 9.3, 0.33, -1.18), mv=2.2)        # along the pipe to the drain field
shot(C13, T_VENT, pose(-0.35, 5.9, 0.3, -1.33), pose(-0.5, 5.5, 0.3, -1.28), cut=True)    # bacteria + gas
shot(T_VENT, C14, pose(-5.0, 11.4, 1.7, 1.0), pose(-4.9, 10.9, 1.75, 1.05), cut=True)     # out through the roof vent
shot(C14, T_TRUCK - 0.6, pose(0.3, 8.9, 0.4, -1.0), pose(0.35, 8.6, 0.4, -1.0), cut=True) # sludge builds up over the years
shot(T_TRUCK - 0.6, T_HERO, pose(1.2, 13.4, 1.1, -0.6), mv=1.2)                           # the pump truck
shot(T_HERO, DUR + 0.2, HERO_A, HERO_B, cut=True)                                         # the whole system

# ================================================================ finale tags (always facing the camera)
tag_tank = label('TAG_tank', 'SEPTIC TANK', size=0.38, billboard=True, pos=screen_to_world(HERO_A, 0.44, 0.54, plane_y=-1.5))
tag_field = label('TAG_field', 'DRAIN FIELD', size=0.31, billboard=True, pos=screen_to_world(HERO_A, 0.715, 0.395, depth=15.5))
tag_stat = label('TAG_stat', [('1 in 5', 1.05, M_yellow), ('U.S. HOMES', 0.42, M_white)], billboard=True, pos=screen_to_world(HERO_A, 0.755, 0.205, depth=24.0))
appear(tag_tank, W(156), 0.3); appear(tag_field, W(157) + 0.15, 0.3); appear(tag_stat, T_STAT, 0.35)

# ================================================================ render
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
sc.render.use_persistent_data = True
sc.render.resolution_x = RX; sc.render.resolution_y = RY; sc.render.resolution_percentage = 100
try:
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
except Exception as ex: print('view:', ex)
FMT = os.environ.get('SEPTIC_FMT', 'PNG'); EXT = 'jpg' if FMT == 'JPEG' else 'png'
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
elif MODE == 'blend':
    bpy.ops.wm.save_as_mainfile(filepath=OUT); print('saved', OUT)
