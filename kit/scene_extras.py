"""scene_extras.py (kit v1.0) - helpers promoted from the video #2 scene. exec() it right after explainer_kit.py:

    exec(open(os.path.join(HERE, 'explainer_kit.py'), encoding='utf8').read())
    exec(open(os.path.join(HERE, 'scene_extras.py'), encoding='utf8').read())

Shapes with a pivot: prismp, prism_yz, patchp, hinge, capsule   |  arrows and emphasis: arrow, pulse, pop
Water: level_box, level, water_body, water_material, tint        |  flow dots in pipes: flow, front
Camera maths: orbit, project                                     |  mascot and set dressing: make_char, arm, raise_arms, tree, palm
The function bodies are the ones that rendered video #2 (copied by make_extras.py); raise_arms generalises that scene's arm gestures.
"""
M_arrow = new_mat('arrow', (1.0, 1.0, 1.0), 0.5, emit=0.9)                       # arrows
M_drop = new_mat('drop_clean', (0.45, 0.86, 1.0), 0.2, emit=1.0)                 # flow dots (clean water)
M_trunk = new_mat('trunk', (0.30, 0.21, 0.14), 0.95); M_leaf = new_mat('leaf', (0.20, 0.38, 0.13), 0.95); M_palm = new_mat('palm', (0.24, 0.47, 0.14), 0.8)
orbit = hero_pose                                                                # orbit(azimuth, elevation, distance, target); azimuth 90 = straight on
def prismp(name, pts_xz, y0, y1, m, pivot=(0.0, 0.0), parent=None):
    """prism() with its origin at pivot (x, z), so scale animations grow from there."""
    o = prism(name, [(x - pivot[0], z - pivot[1]) for x, z in pts_xz], y0, y1, m, parent); o.location = (pivot[0], 0.0, pivot[1]); return o
def prism_yz(name, pts_yz, x0, x1, m, tilt=0.0, pivot=(0.0, 0.0)):
    """Prism with its profile in the YZ plane, running along X (tilt = slope of that run, radians); origin at pivot (y, z)."""
    o = prism(name, [(y - pivot[0], z - pivot[1]) for y, z in pts_yz], -x1, -x0, m)
    o.rotation_euler = (tilt, 0, math.radians(90)); o.location = (0.0, pivot[0], pivot[1]); return o
# patch() with its origin at pivot (x, z), so it scales or rotates about that point.
def patchp(name, pts_xz, m, y, pivot):
    o = patch(name, [(x - pivot[0], z - pivot[1]) for x, z in pts_xz], m, y); o.location = (pivot[0], y, pivot[1]); return o
def hinge(name, x0, x1, y0, y1, z0, z1, m, pivot):
    """Box hanging on an empty at pivot; rotate the empty to tip the box."""
    p = empty(name + '_hinge', pivot)
    box(name, x0 - pivot[0], x1 - pivot[0], y0 - pivot[1], y1 - pivot[1], z0 - pivot[2], z1 - pivot[2], m, origin='center', parent=p); return p
# XZ outline of an upright capsule-shaped tank, for prism().
def capsule(cx, z0, z1, hw, r=0.16):
    return [(cx - hw + r, z0), (cx - hw, z0 + r), (cx - hw, z1 - 2 * r), (cx - hw + 0.6 * r, z1 - 0.8 * r), (cx - 0.5 * hw, z1 - 0.15 * r), (cx, z1),
            (cx + 0.5 * hw, z1 - 0.15 * r), (cx + hw - 0.6 * r, z1 - 0.8 * r), (cx + hw, z1 - 2 * r), (cx + hw, z0 + r), (cx + hw - r, z0)]
def arrow(name, tail, head, r=0.06, m=None):
    """White 3D arrow from tail to head. Returns the root (at the tail; scale it to show, hide or pulse)."""
    d = Vector(head) - Vector(tail); L = d.length; root = empty(name, tail); root.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    cyl(name + '_s', (0, 0, 0), r, L - 3.2 * r, m or M_arrow, seg=10, parent=root)
    cyl(name + '_h', (0, 0, L - 3.2 * r), 2.4 * r, 3.2 * r, m or M_arrow, seg=12, r2=0.0, parent=root)
    return root
def pulse(o, t0, t1, period=0.5, amp=0.14, s=None, ip=None):
    """Scale pulse. Pass ip='BEZIER' for objects switched on with show()/extend(): new keys copy the CONSTANT interpolation of the key before them."""
    s = tuple(o.scale) if s is None else s; t = t0; k = 0
    while t < t1:
        key(o, 'scale', t, tuple(v * (1 + amp * (k % 2)) for v in s), ip=ip); t += period / 2; k += 1
    key(o, 'scale', t1, s, ip=ip)
# Hide until t, then pop in with a small overshoot: tags, labels, stickers.
def pop(o, t, dur=0.28, over=1.1):
    s = tuple(o.scale); hidden_until(o, t); appear(o, t, dur, s=s, over=over)
def level_box(name, z):
    """Invisible cutter; its top is a water level. Boolean-intersected with a water body so sloped floors fill correctly."""
    o = box(name, -14, 14, -1.0, 9.0, -8.0, 0.0, M_conc, origin='top'); o.location.z = z; o.hide_render = True; o.display_type = 'BOUNDS'; return o
# Key a level_box up and down: pts = [(t, z), ...], linear.
def level(o, pts):
    for t, z in pts: key(o, 'location', t, z, index=2, ip='LINEAR')
# Water volume: a prism of the basin profile, cut off at the top of the level_box `lvl` (boolean INTERSECT), so sloped floors fill correctly.
def water_body(name, profile, y0, y1, m, lvl):
    o = prism(name, profile, y0, y1, m); mod = o.modifiers.new('level', 'BOOLEAN'); mod.operation = 'INTERSECT'; mod.object = lvl; mod.solver = 'EXACT'; return o
# Semi-transparent water with a slowly drifting ripple bump (animated over the whole video).
def water_material(name, color, alpha):
    m = new_mat(name, color, 0.06, spec=0.7, alpha=alpha); N = m.node_tree.nodes; L = m.node_tree.links; b = bsdf_of(m)
    geo = N.new('ShaderNodeNewGeometry'); nz = N.new('ShaderNodeTexNoise'); nz.noise_dimensions = '4D'
    nz.inputs['Scale'].default_value = 2.4; nz.inputs['Detail'].default_value = 1.5; L.new(geo.outputs['Position'], nz.inputs['Vector'])
    bump = N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.30; bump.inputs['Distance'].default_value = 0.05
    L.new(nz.outputs[0], bump.inputs['Height']); L.new(bump.outputs[0], b.inputs['Normal'])
    key_input(nz.inputs['W'], 0.0, 0.0); key_input(nz.inputs['W'], DUR, DUR * 0.5)
    b.inputs['Emission Color'].default_value = (*color, 1)
    return m
def tint(m, pts):
    """Animate a material: pts = [(t, (r, g, b), alpha), ...]."""
    b = bsdf_of(m)
    for t, c, a in pts:
        key_input(b.inputs['Base Color'], t, (*c, 1)); key_input(b.inputs['Alpha'], t, a)
def flow(name, pts, t0, t1, speed=2.4, gap=0.8, r=0.045, m=None):
    """Dots that run along a polyline between t0 and t1 and loop (flow inside a pipe)."""
    P = [Vector(p) for p in pts]; seg = [(P[i + 1] - P[i]).length for i in range(len(P) - 1)]; Lt = sum(seg); per = Lt / speed; n = max(1, round(Lt / gap)); dots = []
    for k in range(n):
        d = sphere(name, pts[0], r, m or M_drop, seg=8); show(d, t0, t1); dots.append(d); t = t0 - per * k / n
        while t < t1:
            acc = 0.0
            for i, p in enumerate(P):
                last = i == len(P) - 1                  # the wrap key sits just before the next loop's first key; at the same time that key would replace it
                key(d, 'location', t + acc / Lt * per - (0.004 if last else 0.0), tuple(p), ip='CONSTANT' if last else 'LINEAR')
                if i < len(seg): acc += seg[i]
            t += per
    return dots
# The same path pulled in front of the pipe bore (toward the camera), for flow dots that must stay visible.
def front(pts, y=-0.085): return [(x, y, z) for x, _, z in pts]                 # same path, pulled in front of the pipe bore
def project(pose_, p):
    """Screen fractions (x from the left, y from the top) of world point p for a camera pose."""
    c = Vector(pose_[0]); f = (Vector(pose_[1]) - c).normalized(); r = f.cross(Vector((0, 0, 1))).normalized(); u = r.cross(f)
    v = Vector(p) - c; d = v.dot(f); return (round(0.5 + v.dot(r) / d / ASPECT, 3), round(0.5 - v.dot(u) / d, 3))
# Key one mascot arm to `deg` degrees at time t (8 = hanging, 150 = raised; negative for the right arm).
def arm(a, t, deg): key(a, 'rotation_euler', t, math.radians(deg), index=1)
def make_char(name, loc, vest=None, helmet=True):
    """The series mascot. Faces the camera (-Y). Returns root, left arm, right arm."""
    root = empty(name, loc); vest = vest or M_vest
    for sx in (-0.11, 0.11):
        cyl(name + '_leg', (sx, 0, 0.012), 0.075, 0.80, M_pants, seg=10, parent=root)
        box(name + '_boot', sx - 0.085, sx + 0.085, -0.17, 0.10, 0.012, 0.11, M_ink, parent=root)
    box(name + '_torso', -0.21, 0.21, -0.13, 0.13, 0.80, 1.42, vest, parent=root)
    arms = []
    for sx in (-0.27, 0.27):
        a = cyl(name + '_arm', (sx, 0, 1.37), 0.052, 0.58, M_skin, seg=10, down=True, parent=root)
        a.rotation_euler = (0, math.radians(8 if sx < 0 else -8), 0); arms.append(a)
        sphere(name + '_sh', (sx * 0.95, 0, 1.36), 0.085, vest, seg=10, parent=root)
    cyl(name + '_neck', (0, 0, 1.42), 0.05, 0.08, M_skin, seg=10, parent=root)
    sphere(name + '_head', (0, 0, 1.63), 0.15, M_skin, sz=1.1, parent=root)
    if helmet:
        me = bpy.data.meshes.new(name + '_helmet'); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=18, v_segments=10, radius=0.178)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -1e-4], context='VERTS')
        for f in bm.faces: f.smooth = True
        bm.to_mesh(me); bm.free()
        h = link(bpy.data.objects.new(name + '_helmet', me), M_helmet, root); h.location = (0, 0, 1.69); h.scale = (1, 1, 0.82)
        cyl(name + '_brim', (0, -0.04, 1.682), 0.205, 0.022, M_helmet, seg=22, parent=root)
    return root, arms[0], arms[1]
# Low-poly round tree (set dressing).
def tree(x, y, h=3.2, r=1.5):
    cyl('TREE_trunk', (x, y, 0), 0.17, h, M_trunk, seg=8)
    for dx, dy, dz, k in ((0, 0, 0.3, 1.0), (0.7, 0.2, -0.3, 0.72), (-0.6, -0.3, -0.2, 0.78), (0.1, 0.5, 0.7, 0.6)):
        sphere('TREE_crown', (x + dx * r, y + dy * r, h + dz * r + r * 0.4), r * k, M_leaf, seg=10, smooth=False)
# Low-poly palm (set dressing).
def palm(x, y, h=5.0, lean=0.5):
    tube('PALM_trunk', smooth_path([(x, y, 0), (x + lean * 0.3, y, h * 0.5), (x + lean, y, h)], 5), 0.14, M_trunk, res=3)
    for k in range(9):
        a = k * math.tau / 9 + 0.3
        f = sphere('PALM_frond', (x + lean + math.cos(a) * 1.05, y + math.sin(a) * 1.05, h - 0.28), 1.25, M_palm, sx=1.0, sy=0.17, sz=0.05, seg=8, smooth=False)
        f.rotation_euler = (0, math.radians(24), a)
def raise_arms(arms, t0, t1, deg=150, dn=0.35):
    """Raise the mascot's arms between t0 and t1, then lower them. arms = (left, right) from make_char(); use None for an arm that stays down."""
    for a, sg in zip(arms, (1, -1)):
        if a is not None: arm(a, t0 - 0.02, 8 * sg); arm(a, t0 + 0.25, deg * sg); arm(a, t1, deg * sg); arm(a, t1 + dn, 8 * sg)
