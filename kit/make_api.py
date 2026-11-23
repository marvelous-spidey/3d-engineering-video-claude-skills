"""make_api.py - list what the scene kit offers: python3 make_api.py > API.md   (functions with their arguments, materials, modes)"""
import ast, re, os
NOTES = {'fr': 'detik -> nomor frame (pecahan)', 'fcurves_of': 'f-curve sebuah datablock (Blender 5.3: lewat layers/strips/channelbag); dipakai untuk memeriksa kunci',
 'key': 'sisipkan keyframe pada detik t dan atur interpolasinya (ip) dan easing; kunci pada frame yang sama MENGGANTI kunci lama',
 'hidden_until': 'objek tidak tampak sampai t0', 'appear': 'muncul membesar dengan sedikit lewat (over), selama dur detik', 'vanish': 'mengecil lalu hilang',
 'grow': 'tumbuh dari pangkal sepanjang satu sumbu antara t0 dan t1', 'show': 'tampil/sembunyi keras (kunci CONSTANT) antara t0 dan t1',
 'travel': 'bergerak lewat titik-titik berwaktu: stops = [(t, (x, y, z)), ...]', 'key_input': 'animasikan nilai sebuah soket node material',
 'new_mat': 'material Principled sederhana: warna, kekasaran, emisi, spekular, alpha', 'bsdf_of': 'node Principled sebuah material', 'link': 'tautkan objek ke scene, beri material dan induk',
 'box': 'kotak dari batas x, y, z; origin = bottom | top | center (pusat skala/rotasi)', 'tube': 'tabung mengikuti daftar titik (kurva dengan bevel)',
 'extend': 'pipa/tabung menggambar dirinya dari pangkal ke ujung antara t0 dan t1', 'sphere': 'bola (bisa dipipihkan dengan sx, sy, sz)',
 'cyl': 'silinder atau kerucut (r2) berdiri di loc; down=True menggantung ke bawah', 'prism': 'prisma dari profil di bidang XZ, ditarik dari y0 ke y1',
 'patch': 'bidang satu sisi dari profil XZ (noda, lapisan tipis) di depan bidang potong', 'empty': 'objek kosong sebagai induk atau engsel',
 'text': 'teks 3D (Inter Bold bila tersedia)', 'sign': 'papan nama dengan teks', 'screen_to_world': 'posisi layar (pecahan) -> titik dunia untuk sebuah pose kamera',
 'soil_material': 'tanah berlapis menurut kedalaman', 'grass_material': 'rumput bergaris halus', 'gravel_material': 'kerikil',
 'pose': 'pose kamera frontal: x, jarak, tinggi kamera, tinggi target', 'push': 'pose yang sedikit maju dari pose p (untuk drift)', 'cam_key': 'kunci kamera + target pada detik t',
 'hero_pose': 'pose orbit: azimut (90 = lurus dari depan), elevasi, jarak, target; alias: orbit()'}
HERE = os.path.dirname(os.path.abspath(__file__)); out = ['# API kit scene (dibuat oleh make_api.py; jangan disunting tangan)', '']
for fn, title in (('explainer_kit.py', 'explainer_kit.py - inti (dari video #1)'), ('scene_extras.py', 'scene_extras.py - tambahan (dari video #2)')):
    src = open(os.path.join(HERE, fn), encoding='utf8').read(); lines = src.split('\n'); tree = ast.parse(src)
    out += [f'## {title}', '', '| Fungsi | Keterangan |', '|---|---|']
    for n in tree.body:
        if not isinstance(n, ast.FunctionDef) or n.name.startswith('_'): continue
        sig = re.sub(r'^def |:\s*$', '', lines[n.lineno - 1].split(':')[0] if lines[n.lineno - 1].rstrip().endswith(':') else re.match(r'def [^:]*\)', lines[n.lineno - 1]).group(0)[4:])
        doc = ast.get_docstring(n) or ''
        if not doc and n.lineno >= 2 and lines[n.lineno - 2].startswith('# ') and '====' not in lines[n.lineno - 2] and '----' not in lines[n.lineno - 2]: doc = lines[n.lineno - 2][2:]
        if not doc and '#' in lines[n.lineno - 1]: doc = lines[n.lineno - 1].split('#', 1)[1].strip()
        doc = doc or NOTES.get(n.name, '')
        out.append(f"| `{sig}` | {' '.join(doc.split()).replace('|', chr(92) + '|')} |")
    mats = sorted(set(re.findall(r'^(M_[A-Za-z0-9_]+) = ', src, re.M)) | set(re.findall(r'; (M_[A-Za-z0-9_]+) = ', src)))
    out += ['', 'Material: ' + ', '.join(f'`{m}`' for m in mats), '']
out += ['## Objek dunia dan mode', '', '- Dunia: kamera `cam` (lensa 36 mm), matahari `sun` / `sun_d` (energi dan warna bisa di-keyframe), langit `sky` (color ramp), `sc` = scene.',
        '- Waktu: `FPS`, `OFFSET`, `DUR`, `LAST` (frame terakhir), `WORDS` dari `kitjob.py`; `T(id, kata, ke, end)` memberi detik di video; `fr(t)` mengubah detik ke nomor frame.',
        '- Mode (argumen pertama skrip scene): `still <rx> <ry> <spp> <dir> <detik...>`, `anim <rx> <ry> <spp> <dir> <awal> <akhir> [langkah]`, `list <rx> <ry> <spp> <dir> <berkas nomor frame>`, `blend <rx> <ry> <spp> <out.blend>`, `none` (hanya membangun scene).',
        '- Variabel lingkungan: `KIT_DEVICE=CPU|GPU`, `KIT_FMT=PNG|JPEG`, `KIT_PERSIST=0|1` (biarkan 0), `SEPTIC_FONT=<font teks 3D>`.', '']
print('\n'.join(out))
