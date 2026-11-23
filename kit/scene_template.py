"""scene_template.py (kit v1.1) - the smallest complete scene. Copy it to <topic>_video.py and replace the middle part.
Demo topic: a rooftop water tank (words.json and script.txt are in demo/). The whole scene is built from code, and every cue
comes from the voice-over word timings, so re-timing the narration moves the animation with it.

  python scene_template.py still 270 480 4 out_dir 1.0 3.2 5.5       quick stills at those seconds (CPU, a few seconds each)
  python scene_template.py anim 1080 1920 64 frames 1 240 [step]     frames f_00001.png ... (box/render.sh calls this)
  python scene_template.py blend 1080 1920 64 out.blend              save the scene for Blender

Conventions: metres. The cut face is the plane y = 0 and the camera looks along +Y. Z is up, ground level is z = 0.
Lens 36 mm on a 36 mm sensor: the frame is as tall as the camera distance and 0.5625 x that wide.
Keep the subject between 15% and 60% of the frame height: captions sit at 67-70%, and platform buttons cover the bottom 20%.
Name objects by group (ENV_, TANK_, PIPE_, TAG_ ...): the names show up in Blender and in the frame-scan reports.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from kitjob import FPS, OFFSET, WORDS, DUR                     # job.env + words.json: the same numbers captions.py and the box scripts use
exec(open(os.path.join(HERE, 'explainer_kit.py'), encoding='utf8').read())
exec(open(os.path.join(HERE, 'scene_extras.py'), encoding='utf8').read())

# ---------------------------------------------------------------- cues: T(sentence id, word, nth=1, end=False) -> seconds in the video
# The word must match the script exactly ("air" does not find "airnya"). Derive every time from a cue, never type seconds.
T_TANK = T('S01', 'tandon'); T_PUMP = T('S02', 'pompa'); T_UP = T('S02', 'naik'); T_DOWN = T('S02', 'turun'); T_END = T('S02', end=True)

# ---------------------------------------------------------------- set: ground, house, open tank on the roof, pump, riser pipe
box('ENV_soil', -60, 60, 0.0, 120.0, -30.0, 0.0, M_soil); box('ENV_lawn', -60, 60, 0.0, 40.0, 0.0, 0.012, M_grass)
box('HOUSE_wall', -0.6, 2.6, 0.0, 3.2, 0.0, 3.0, M_conc); box('HOUSE_roof', -0.9, 2.9, 0.0, 3.5, 3.0, 3.2, M_wood)
for nm, x0, x1, y0, y1, z0, z1 in (('TANK_floor', 0.3, 1.7, 0.0, 1.2, 3.2, 3.28), ('TANK_left', 0.3, 0.38, 0.0, 1.2, 3.28, 4.6),
                                   ('TANK_right', 1.62, 1.7, 0.0, 1.2, 3.28, 4.6), ('TANK_back', 0.38, 1.62, 1.12, 1.2, 3.28, 4.6)):
    box(nm, x0, x1, y0, y1, z0, z1, M_pvc)                                   # an open shell: the cut face shows the inside
box('PUMP_body', -2.3, -1.6, 0.0, 0.6, 0.0, 0.5, M_steel); cyl('PUMP_motor', (-1.95, 0.3, 0.5), 0.2, 0.25, M_ink)
PIPE = [(-1.6, 0.0, 0.3), (-1.0, 0.0, 0.3), (-1.0, 0.0, 4.95), (1.0, 0.0, 4.95), (1.0, 0.0, 4.5)]
riser = pipe('PIPE_riser', PIPE); extend(riser, T_PUMP - 0.4, T_PUMP)       # the pipe draws itself just before it is named

# ---------------------------------------------------------------- water: a prism cut off by a level box that moves up
M_water = water_material('water', (0.10, 0.55, 0.85), 0.62)
lvl = level_box('LVL_tank', 3.3); water_body('WATER_tank', [(0.38, 3.28), (0.38, 4.6), (1.62, 4.6), (1.62, 3.28)], 0.004, 1.12, M_water, lvl)
level(lvl, [(T_PUMP, 3.3), (T_UP + 1.2, 4.45)])                              # the tank fills while the pump runs
flow('FLOW_riser', front(PIPE), T_PUMP, T_UP + 1.2)                         # dots that loop along the pipe

# ---------------------------------------------------------------- tags, arrow, mascot
tag = label('TAG_tank', [('TANDON', 0.30, M_white), ('DI ATAP', 0.30, M_yellow)], pos=(1.0, -0.2, 5.6), billboard=True); pop(tag, T_TANK + 0.1)
down = arrow('ARROW_down', (2.25, 0.0, 4.3), (2.25, 0.0, 3.3)); pop(down, T_DOWN); pulse(down, T_DOWN + 0.4, T_DOWN + 1.4, ip='BEZIER')
mascot, arm_l, arm_r = make_char('MASCOT', (-3.4, 0.8, 0.012)); raise_arms((arm_l, arm_r), T_TANK + 0.3, T_TANK + 1.3)

# ---------------------------------------------------------------- camera: orbit(azimuth, elevation, distance, target); azimuth 90 = straight on
# shot(t0, t1, pose, mv=seconds) eases from the previous pose and then drifts; cut=True jumps. project(pose, point) gives screen fractions.
P_WIDE = orbit(86, 8, 13.0, (-0.3, 0.0, 1.2))
shot(0.0, T_PUMP - 0.3, P_WIDE, cut=True)
shot(T_PUMP - 0.3, T_DOWN, orbit(88, 7, 11.0, (-0.2, 0.0, 1.9)), mv=0.9)
shot(T_DOWN, DUR, orbit(90, 6, 8.0, (1.1, 0.0, 2.7)), mv=0.8)
if MODE == 'none':                                                           # python scene_template.py none 270 480 4 x  -> numbers only, no render
    for nm, p in (('tank top', (1.0, 0.0, 4.6)), ('ground', (0.0, 0.0, 0.0)), ('mascot head', (-3.4, 0.8, 1.7)), ('tag', (1.0, -0.2, 5.6))): print(nm, 'on screen (x, y):', project(P_WIDE, p))
render_main()
