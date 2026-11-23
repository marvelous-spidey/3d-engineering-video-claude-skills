# API kit scene (dibuat oleh make_api.py; jangan disunting tangan)

## explainer_kit.py - inti (dari video #1)

| Fungsi | Keterangan |
|---|---|
| `fr(t)` | detik -> nomor frame (pecahan) |
| `T(sid, word=None, nth=1, end=False)` | Video time (s) of a sentence (start, or end with end=True) or of the nth `word` inside it. Cues stay valid when the script is re-timed. |
| `fcurves_of(idb)` | f-curve sebuah datablock (Blender 5.3: lewat layers/strips/channelbag); dipakai untuk memeriksa kunci |
| `key(o, path, t, value=None, index=-1, ip=None, ease=None)` | Keyframe o.path at time t (seconds). ip: None(BEZIER) \| 'LINEAR' \| 'CONSTANT' \| 'SINE'... |
| `hidden_until(o, t0)` | objek tidak tampak sampai t0 |
| `appear(o, t, dur=0.3, s=None, over=1.12)` | muncul membesar dengan sedikit lewat (over), selama dur detik |
| `vanish(o, t, dur=0.2)` | mengecil lalu hilang |
| `grow(o, t0, t1, axis=2, s=None)` | Hidden until t0, then grows along one axis from its pivot. |
| `show(o, t0, t1=None, s=None)` | Hard on/off switch (constant interpolation). |
| `travel(o, stops)` | stops: [(t, (x,y,z)), ...] moved through at constant speed per leg. |
| `key_input(sock, t, value)` | animasikan nilai sebuah soket node material |
| `new_mat(name, color, rough=0.85, emit=0.0, spec=0.2, alpha=1.0)` | material Principled sederhana: warna, kekasaran, emisi, spekular, alpha |
| `bsdf_of(m)` | node Principled sebuah material |
| `link(o, m=None, parent=None)` | tautkan objek ke scene, beri material dan induk |
| `box(name, x0, x1, y0, y1, z0, z1, m, origin='bottom', parent=None)` | Axis-aligned box. origin: bottom \| top \| left \| right \| center (pivot for scale animation). |
| `tube(name, pts, r, m, parent=None, res=5, origin=None)` | tabung mengikuti daftar titik (kurva dengan bevel) |
| `pipe(name, pts, R=R_PIPE, bore=True)` | Sectioned-pipe look: white tube with a darker bore running along its front, so flow reads as inside it. |
| `extend(objs, t0, t1)` | pipa/tabung menggambar dirinya dari pangkal ke ujung antara t0 dan t1 |
| `smooth_path(pts, n=8)` | Catmull-Rom through pts -> denser polyline. |
| `sphere(name, loc, r, m, sx=1, sy=1, sz=1, seg=12, smooth=True, parent=None)` | bola (bisa dipipihkan dengan sx, sy, sz) |
| `cyl(name, loc, r, h, m, seg=16, r2=None, down=False, parent=None, smooth=False)` | silinder atau kerucut (r2) berdiri di loc; down=True menggantung ke bawah |
| `prism(name, pts_xz, y0, y1, m, parent=None)` | Extrude a polygon given in the XZ plane along +Y. |
| `patch(name, pts_xz, m, y=-0.006, parent=None)` | Flat single-sided shape lying just in front of the cut face (stains, water table). |
| `empty(name, loc=(0, 0, 0), parent=None)` | objek kosong sebagai induk atau engsel |
| `text(name, body, loc, size, m, extrude=0.004, parent=None, rot=(math.radians(90), 0, 0))` | teks 3D (Inter Bold bila tersedia) |
| `label(name, lines, x=0.0, z=0.0, size=0.17, y=-0.10, plate=None, ink=None, billboard=False, pos=None)` | Tag = dark plate + bright text, either flat on the cut face or always facing the camera. lines: 'TEXT' or [(text, size, material), ...]. Returns the root (scale it to show/hide). |
| `sign(name, body, x0, x1, y, z0, z1, size, board=None, ink=None)` | Board on two posts standing on the ground. Returns the root. |
| `screen_to_world(pose_, sx, sy, depth=None, plane_y=None)` | World point seen at screen fraction (sx, sy) (0,0 = top-left) for a camera pose, at a view depth or on a y-plane. |
| `soil_material()` | tanah berlapis menurut kedalaman |
| `grass_material()` | rumput bergaris halus |
| `gravel_material()` | kerikil |
| `pose(x, d, cz, tz)` | frontal view of the cut face |
| `push(p, k=0.04, dx=0.0)` | pose yang sedikit maju dari pose p (untuk drift) |
| `cam_key(t, p, ip, ease=None)` | kunci kamera + target pada detik t |
| `shot(t0, t1, main, end=None, mv=1.3, cut=False)` | Ease from where the last shot ended to `main` over mv seconds (or cut straight to it), then drift slowly to `end`. |
| `hero_pose(az, el, dist, target=(0.7, 0.5, -2.5))` | pose orbit: azimut (90 = lurus dari depan), elevasi, jarak, target; alias: orbit() |
| `render_main()` | Set up Cycles and run the mode given on the command line. Call it once the scene is built. |

Material: `M_bore`, `M_conc`, `M_grass`, `M_gravel`, `M_helmet`, `M_ink`, `M_pants`, `M_plate`, `M_pvc`, `M_sign`, `M_skin`, `M_soil`, `M_steel`, `M_stripe`, `M_vest`, `M_white`, `M_wood`, `M_yellow`

## scene_extras.py - tambahan (dari video #2)

| Fungsi | Keterangan |
|---|---|
| `prismp(name, pts_xz, y0, y1, m, pivot=(0.0, 0.0), parent=None)` | prism() with its origin at pivot (x, z), so scale animations grow from there. |
| `prism_yz(name, pts_yz, x0, x1, m, tilt=0.0, pivot=(0.0, 0.0))` | Prism with its profile in the YZ plane, running along X (tilt = slope of that run, radians); origin at pivot (y, z). |
| `patchp(name, pts_xz, m, y, pivot)` | patch() with its origin at pivot (x, z), so it scales or rotates about that point. |
| `hinge(name, x0, x1, y0, y1, z0, z1, m, pivot)` | Box hanging on an empty at pivot; rotate the empty to tip the box. |
| `capsule(cx, z0, z1, hw, r=0.16)` | XZ outline of an upright capsule-shaped tank, for prism(). |
| `arrow(name, tail, head, r=0.06, m=None)` | White 3D arrow from tail to head. Returns the root (at the tail; scale it to show, hide or pulse). |
| `pulse(o, t0, t1, period=0.5, amp=0.14, s=None, ip=None)` | Scale pulse. Pass ip='BEZIER' for objects switched on with show()/extend(): new keys copy the CONSTANT interpolation of the key before them. |
| `pop(o, t, dur=0.28, over=1.1)` | Hide until t, then pop in with a small overshoot: tags, labels, stickers. |
| `level_box(name, z)` | Invisible cutter; its top is a water level. Boolean-intersected with a water body so sloped floors fill correctly. |
| `level(o, pts)` | Key a level_box up and down: pts = [(t, z), ...], linear. |
| `water_body(name, profile, y0, y1, m, lvl)` | Water volume: a prism of the basin profile, cut off at the top of the level_box `lvl` (boolean INTERSECT), so sloped floors fill correctly. |
| `water_material(name, color, alpha)` | Semi-transparent water with a slowly drifting ripple bump (animated over the whole video). |
| `tint(m, pts)` | Animate a material: pts = [(t, (r, g, b), alpha), ...]. |
| `flow(name, pts, t0, t1, speed=2.4, gap=0.8, r=0.045, m=None)` | Dots that run along a polyline between t0 and t1 and loop (flow inside a pipe). |
| `front(pts, y=-0.085)` | The same path pulled in front of the pipe bore (toward the camera), for flow dots that must stay visible. |
| `project(pose_, p)` | Screen fractions (x from the left, y from the top) of world point p for a camera pose. |
| `arm(a, t, deg)` | Key one mascot arm to `deg` degrees at time t (8 = hanging, 150 = raised; negative for the right arm). |
| `make_char(name, loc, vest=None, helmet=True)` | The series mascot. Faces the camera (-Y). Returns root, left arm, right arm. |
| `tree(x, y, h=3.2, r=1.5)` | Low-poly round tree (set dressing). |
| `palm(x, y, h=5.0, lean=0.5)` | Low-poly palm (set dressing). |
| `raise_arms(arms, t0, t1, deg=150, dn=0.35)` | Raise the mascot's arms between t0 and t1, then lower them. arms = (left, right) from make_char(); use None for an arm that stays down. |

Material: `M_arrow`, `M_drop`, `M_leaf`, `M_palm`, `M_trunk`

## Objek dunia dan mode

- Dunia: kamera `cam` (lensa 36 mm), matahari `sun` / `sun_d` (energi dan warna bisa di-keyframe), langit `sky` (color ramp), `sc` = scene.
- Waktu: `FPS`, `OFFSET`, `DUR`, `LAST` (frame terakhir), `WORDS` dari `kitjob.py`; `T(id, kata, ke, end)` memberi detik di video; `fr(t)` mengubah detik ke nomor frame.
- Mode (argumen pertama skrip scene): `still <rx> <ry> <spp> <dir> <detik...>`, `anim <rx> <ry> <spp> <dir> <awal> <akhir> [langkah]`, `list <rx> <ry> <spp> <dir> <berkas nomor frame>`, `blend <rx> <ry> <spp> <out.blend>`, `none` (hanya membangun scene).
- Variabel lingkungan: `KIT_DEVICE=CPU|GPU`, `KIT_FMT=PNG|JPEG`, `KIT_PERSIST=0|1` (biarkan 0), `SEPTIC_FONT=<font teks 3D>`.

