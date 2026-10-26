import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..") + "/"
DUR = dict(s1=6.5, s2=5.3, s3=6.5, s4=5.7, s5=6.4)

AAR = dict(Shirt=NAVY, Pants=(0.03, 0.03, 0.035), Skin=SKIN, Hair=BLACKHAIR, Details=(0.03, 0.022, 0.02))
SUNITA = dict(Shirt=(0.8, 0.75, 0.68), LightJacket=(0.28, 0.03, 0.06), Jacket=(0.28, 0.03, 0.06), Pants=(0.06, 0.06, 0.07),
              Shoes=(0.05, 0.04, 0.04), Skin=(0.42, 0.24, 0.15), HairBase=BLACKHAIR, Hair=BLACKHAIR, Eyebrows=BLACKHAIR)
NEHA = dict(SUNITA, LightJacket=(0.32, 0.32, 0.34), Jacket=(0.32, 0.32, 0.34), Shirt=(0.9, 0.9, 0.9), Pants=(0.12, 0.12, 0.14), Skin=(0.45, 0.27, 0.17))
VIKRAM = dict(Shirt=(0.42, 0.58, 0.8), Pants=(0.1, 0.1, 0.12), Skin=(0.33, 0.19, 0.11), Hair=BLACKHAIR)
EXTRA_M = dict(Shirt=(0.55, 0.5, 0.42), Pants=(0.15, 0.17, 0.25), Skin=(0.38, 0.22, 0.13), Hair=BLACKHAIR)
EXTRA_W = dict(SUNITA, LightJacket=(0.1, 0.3, 0.32), Jacket=(0.1, 0.3, 0.32), Shirt=(0.85, 0.82, 0.75), Skin=(0.4, 0.24, 0.15))
MAN_SUIT, MAN_LS, WOMAN = "mQnGoME1ez", "DLptRuewTn", "AQsd9ngvKU"
SIT0 = 50  # Man_/Female_Sitting: seated loop after the sit-down


def room(w, d, h, floor_m, wall_m, ceil=True, x0=0, y0=0):
    box("floor", (x0, y0, -0.05), (w, d, 0.1), floor_m)
    box("backwall", (x0, y0 + d / 2, h / 2), (w, 0.1, h), wall_m)
    box("lwall", (x0 - w / 2, y0, h / 2), (0.1, d, h), wall_m)
    box("rwall", (x0 + w / 2, y0, h / 2), (0.1, d, h), wall_m)
    if ceil:
        box("ceil", (x0, y0, h + 0.05), (w, d, 0.1), mat("ceil", (0.9, 0.9, 0.88), 0.9))


def chair(loc, rotz=0, seat=0.46, m=None, back=True):
    m = m or mat("chair", (0.12, 0.12, 0.13), 0.5)
    leg = mat("chrome", (0.7, 0.7, 0.72), 0.25, 1.0)
    parts = [box("seat", (0, 0, seat - 0.04), (0.5, 0.5, 0.08), m, 0.02)]
    if back: parts.append(box("back", (0, 0.24, seat + 0.32), (0.48, 0.06, 0.55), m, 0.02))
    parts.append(cyl("post", (0, 0, (seat - 0.08) / 2), 0.025, seat - 0.08, leg))
    parts.append(cyl("base", (0, 0, 0.02), 0.25, 0.04, leg))
    e = bpy.data.objects.new("chair", None); bpy.context.scene.collection.objects.link(e)
    for p in parts: p.parent = e
    e.location = loc; e.rotation_euler = (0, 0, rotz)
    return e


def plant(loc, s=1.0):
    pot = cyl("pot", (loc[0], loc[1], 0.22 * s), 0.18 * s, 0.44 * s, mat("pot", (0.85, 0.84, 0.8), 0.5))
    g = mat("leaf", (0.05, 0.22, 0.06), 0.6)
    import random; r = random.Random(int(loc[0] * 100 + loc[1] * 10))
    for i in range(14):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.16 * s,
            location=(loc[0] + r.uniform(-.2, .2) * s, loc[1] + r.uniform(-.2, .2) * s, (0.55 + r.uniform(0, .8)) * s))
        o = bpy.context.object; o.scale = (1, 0.5, 1.4); o.rotation_euler = (r.uniform(0, 1), r.uniform(0, 1), r.uniform(0, 3)); o.data.materials.append(g)


def finish(sc, name, frames, test, res, samples):
    w, h = res
    setup_render(sc, frames, w, h, samples)
    if test:
        f = test
        sc.frame_set(f)
        sc.render.filepath = OUT + f"test_{name}_{f}.png"
        t = time.time(); bpy.ops.render.render(write_still=True)
        print("RENDER_TIME", name, f, round(time.time() - t, 2))
    else:
        sc.render.image_settings.file_format = "PNG"
        sc.render.filepath = OUT + f"frames/{name}/f_"
        bpy.ops.render.render(animation=True)


# ---------------------------------------------------------------- s1 apartment
def s1(frames):
    sc = bpy.context.scene
    world(sc, (0.75, 0.82, 1.0), 0.3)
    wall = mat("wall", (0.62, 0.55, 0.47), 0.85); floor = mat("wood", (0.32, 0.19, 0.1), 0.45)
    box("floor", (0, 0, -0.05), (9, 8, 0.1), floor)
    # back wall with big window (pieces)
    box("bw_l", (-3.2, 3, 1.4), (2.6, 0.12, 2.8), wall); box("bw_r", (3.6, 3, 1.4), (1.8, 0.12, 2.8), wall)
    box("bw_b", (0.3, 3, 0.3), (4.4, 0.12, 0.6), wall); box("bw_t", (0.3, 3, 2.6), (4.4, 0.12, 0.4), wall)
    fr = mat("frame", (0.9, 0.9, 0.9), 0.4)
    for x in (-1.9, 0.3, 2.5): box("mull", (x, 3, 1.5), (0.06, 0.16, 1.8), fr)
    box("sky", (0.3, 6, 1.5), (12, 0.1, 8), mat("sky", (0.9, 0.8, 0.7), emit=(1.0, 0.86, 0.7), estr=0.85))
    box("lwall", (-4.5, 0, 1.4), (0.12, 8, 2.8), wall)
    box("ceil", (0, 0, 2.85), (9, 8, 0.1), mat("ceil", (0.9, 0.9, 0.88), 0.9))
    # sofa (left part of frame), facing -Y toward camera-ish
    fab = mat("fabric", (0.38, 0.42, 0.45), 0.95)
    sx, sy = -1.0, 1.4
    box("sofa_base", (sx, sy, 0.19), (2.3, 0.95, 0.38), fab, 0.04)
    box("sofa_back", (sx, sy + 0.4, 0.7), (2.3, 0.2, 0.6), fab, 0.06)
    box("sofa_armL", (sx - 1.08, sy, 0.55), (0.18, 0.95, 0.3), fab, 0.06)
    box("sofa_armR", (sx + 1.08, sy, 0.55), (0.18, 0.95, 0.3), fab, 0.06)
    for i in (-0.55, 0.55): box("cushion", (sx + i, sy - 0.05, 0.42), (1.0, 0.8, 0.1), fab, 0.04)
    box("pillow", (sx + 0.85, sy + 0.22, 0.66), (0.4, 0.14, 0.38), mat("pillow", (0.75, 0.55, 0.25), 0.9), 0.06)
    box("rug", (sx, 0.2, 0.005), (3.2, 2.2, 0.01), mat("rug", (0.55, 0.5, 0.45), 1.0))
    wood = mat("table", (0.45, 0.3, 0.18), 0.4)
    box("ctable", (sx, 0.1, 0.38), (1.1, 0.6, 0.05), wood, 0.01)
    for dx in (-0.5, 0.5):
        for dy in (-0.25, 0.25): box("leg", (sx + dx, 0.1 + dy, 0.18), (0.04, 0.04, 0.36), wood)
    cyl("mug", (sx + 0.2, 0.1, 0.45), 0.04, 0.09, mat("mug", (0.9, 0.9, 0.88), 0.3))
    plant((-3.6, 2.3, 0), 1.3)
    plant((2.2, 2.4, 0), 1.0)
    # lamp
    cyl("lamp_pole", (0.6, 2.2, 0.75), 0.015, 1.5, mat("blk", (0.02, 0.02, 0.02), 0.4, 1))
    cyl("lamp_shade", (0.6, 2.2, 1.55), 0.18, 0.25, mat("shade", (0.95, 0.9, 0.8), 0.9, emit=(1, 0.8, 0.55), estr=1.5))
    # Aarav seated, slightly angled
    c = char(MAN_SUIT, "Man_Sitting", rotz=math.radians(20), colors=AAR, start=SIT0)
    place_bone(c, "Hips", (sx - 0.35, sy - 0.33, 0.53), 30)
    aim_override(c, [("UpperArm.R", (-0.05, -0.3, -1)), ("LowerArm.R", (0.85, -1, 0.2)), ("Palm.R", (0.7, -1, 0.5)), ("Head", (0.1, -0.7, 1))], list(range(1, frames + 1, 8)))
    ph = hold_phone(c, 30, up=0.07)
    sun((math.radians(70), 0, math.radians(200)), 4.0, (1, 0.85, 0.65))
    area((sx + 1.5, -1.5, 2.6), (math.radians(30), 0, math.radians(30)), 3, 150, (1, 0.95, 0.88))
    head = (sx - 0.35, sy - 0.2, 1.1)
    camera(sc, frames, (0.3, -2.3, 1.25), (0.1, -1.8, 1.2), (-0.35, sy, 0.8), (-0.45, sy, 0.8), lens=32, fstop=2.8, focus=4.0)
    return c


# ---------------------------------------------------------------- s2 reception
def s2(frames):
    sc = bpy.context.scene
    world(sc, (0.8, 0.82, 0.85), 0.4)
    wall = mat("wall", (0.86, 0.86, 0.84), 0.8); floor = mat("tile", (0.55, 0.55, 0.56), 0.25)
    room(12, 10, 3.2, floor, wall, x0=0, y0=1)
    box("accent", (-0.8, 5.9, 1.7), (4.5, 0.05, 2.2), mat("accent", (0.08, 0.2, 0.3), 0.5))
    white = mat("desk", (0.92, 0.92, 0.9), 0.35)
    dx, dy = -0.8, 1.6
    box("desk_front", (dx, dy, 0.53), (2.8, 0.12, 1.06), white, 0.01)
    box("desk_top", (dx, dy + 0.05, 1.08), (2.9, 0.42, 0.04), mat("desktop", (0.25, 0.25, 0.27), 0.3), 0.005)
    box("desk_work", (dx, dy + 0.55, 0.74), (2.8, 0.7, 0.04), white)
    box("desk_strip", (dx, dy - 0.07, 0.15), (2.8, 0.02, 0.04), mat("strip", (0.2, 0.6, 0.9), emit=(0.3, 0.7, 1), estr=4))
    # scanner stand on the counter
    sx = dx - 0.15
    cyl("scan_base", (sx, dy + 0.05, 1.11), 0.07, 0.02, mat("blk", (0.03, 0.03, 0.03), 0.3))
    cyl("scan_post", (sx, dy + 0.05, 1.19), 0.012, 0.16, mat("chrome", (0.7, 0.7, 0.72), 0.25, 1))
    sp = box("scan_head", (sx, dy + 0.05, 1.29), (0.16, 0.02, 0.11), mat("scanner", (0.03, 0.03, 0.04), 0.2, emit=(0.2, 1.0, 0.5), estr=0.6), 0.008)
    sp.rotation_euler = (math.radians(-25), 0, 0)
    box("monitor", (dx + 0.7, dy + 0.4, 1.0), (0.55, 0.03, 0.34), mat("mon", (0.02, 0.02, 0.02), 0.3), 0.01)
    plant((-3.6, 4.8, 0), 1.4); plant((2.8, 4.8, 0), 1.2)
    for i, x in enumerate((-3, -1, 1)):
        area((x, 1.5, 3.1), (0, 0, 0), 0.6, 120, (1, 0.97, 0.92), "DISK")
    # Sunita behind the counter facing -Y
    su = char(WOMAN, "Female_Idle", colors=SUNITA, height=1.62)
    su["root"].location = (sx + 0.1, dy + 0.75, 0); ground(su, 30)
    aim_override(su, [("Head", (-0.15, -0.8, 0.9))], list(range(1, frames + 1, 10)), name="look")
    # Aarav in front, facing +Y (toward desk), arm out with phone
    c = char(MAN_SUIT, "Man_Idle", rotz=math.radians(180 - 15), colors=AAR)
    c["root"].location = (sx - 0.35, dy - 0.75, 0); ground(c, 30)
    aims = [("UpperArm.R", (-0.15, -1, -0.45)), ("LowerArm.R", (0.15, -1, -0.05)), ("Palm.R", (0.1, -1, 0.1)), ("Head", (0.05, -0.6, 1))]
    aim_override(c, aims, list(range(1, frames + 1, 8)))
    hold_phone(c, 30, face_head=False)
    # background walkers (busy)
    for i, (fid, cols, y, x0, dirn, off) in enumerate([(MAN_LS, EXTRA_M, 3.9, 3.5, -1, 0), (WOMAN, EXTRA_W, 4.4, -4.5, 1, 7)]):
        w = char(fid, "Man_Walk" if fid != WOMAN else "Female_Walk", rotz=math.radians(90 * dirn), colors=cols, height=1.72 if fid != WOMAN else 1.62, offset=off)
        w["root"].location = (x0, y, 0); ground(w, 1)
        sp_ = 0.054 * (1.62 / 1.75 if fid == WOMAN else 1.72 / 1.75)
        w["root"].keyframe_insert("location", frame=1)
        w["root"].location.x += dirn * sp_ * frames; w["root"].keyframe_insert("location", frame=frames)
        for fc in w["root"].animation_data.action.layers[0].strips[0].channelbag(w["root"].animation_data.action_slot).fcurves:
            for k in fc.keyframe_points: k.interpolation = "LINEAR"
    camera(sc, frames, (2.2, -2.5, 1.55), (1.85, -2.1, 1.5), (-0.05, 1.5, 1.15), (-0.2, 1.5, 1.15), lens=32, fstop=3.5, focus=4.3)
    return c


# ---------------------------------------------------------------- s3 lounge
def s3(frames):
    sc = bpy.context.scene
    world(sc, (0.85, 0.88, 0.95), 0.5)
    wall = mat("wall", (0.84, 0.83, 0.8), 0.85); floor = mat("carpet", (0.28, 0.29, 0.31), 0.95)
    box("floor", (0, 0, -0.05), (14, 10, 0.1), floor)
    box("lwall", (-5, 0, 1.6), (0.12, 10, 3.2), wall)
    box("ceil", (0, 0, 3.25), (14, 10, 0.1), mat("ceil", (0.9, 0.9, 0.88), 0.9))
    # back: floor-to-ceiling window
    fr = mat("frame", (0.15, 0.15, 0.16), 0.4, 0.8)
    for x in range(-5, 7, 2): box("mull", (x, 3.2, 1.6), (0.08, 0.12, 3.2), fr)
    box("sill", (0.5, 3.2, 0.05), (12, 0.2, 0.1), fr)
    box("sky", (0, 9, 2), (30, 0.1, 12), mat("sky", (0.7, 0.8, 1.0), emit=(0.8, 0.88, 1.0), estr=2.0))
    for i, x in enumerate((-3, 0, 3, 6)):
        box("bldg", (x * 2.2 - 2, 15, 3 + (i % 2) * 3), (3.5, 3, 6 + (i % 2) * 6), mat("bldg", (0.55, 0.6, 0.66), 0.3))
    seatm = mat("seat", (0.12, 0.32, 0.36), 0.8)
    xs = [-3.0, -2.25, -1.5, -0.75, 0.0]
    for x in xs: chair((x, 1.5, 0), 0, 0.44, seatm)
    box("side", (0.75, 1.5, 0.25), (0.5, 0.5, 0.5), mat("sidet", (0.85, 0.85, 0.83), 0.4), 0.01)
    plant((1.3, 2.4, 0), 1.3); plant((-4.3, 2.4, 0), 1.4)
    box("rug", (-1.5, 0.6, 0.005), (5, 2.2, 0.01), mat("rug2", (0.45, 0.42, 0.38), 1))
    sun((math.radians(55), 0, math.radians(165)), 3.5, (1, 0.96, 0.9))
    area((-1.5, -1.5, 3.0), (math.radians(20), 0, 0), 4, 300)
    # sitters: (model, colors, x, height, isAarav)
    sitters = [(WOMAN, EXTRA_W, -2.25, 1.62, False), (MAN_SUIT, AAR, -1.5, 1.75, True), (MAN_LS, VIKRAM | dict(Shirt=(0.65, 0.62, 0.55)), -0.0, 1.74, False)]
    aar = None
    for k, (fid, cols, x, h, me) in enumerate(sitters):
        c = char(fid, "Female_Sitting" if fid == WOMAN else "Man_Sitting", colors=cols, height=h, start=SIT0, offset=k * 13)
        place_bone(c, "Hips", (x, 1.6, 0.5), 30)
        if me:
            aar = c
            aim_override(c, [("UpperArm.R", (-0.12, -0.2, -1)), ("LowerArm.R", (0.5, -1, 0.15)), ("Palm.R", (0.4, -1, 0.35)), ("Head", (0, -0.7, 1))], list(range(1, frames + 1, 8)))
            ph = hold_phone(c, 30)
            # buzz: screen lights up + tiny shake from ~1.6s
            scr = ph.children[0].data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
            for f, v in ((1, 0.4), (45, 0.4), (48, 4.0), (frames, 3.0)):
                scr.default_value = v; scr.keyframe_insert("default_value", frame=f)
            base = ph.location.copy()
            for i, f in enumerate(range(48, 64, 2)):
                ph.location = base + Vector((0.004 * (1 if i % 2 else -1), 0, 0)); ph.keyframe_insert("location", frame=f)
            ph.location = base; ph.keyframe_insert("location", frame=64)
        else:
            head_nods(c, (1, frames + 30), every=40, amp=0.2, base=(0.1 if k == 0 else -0.1, -0.5, 1), name="look", seed=k)
    camera(sc, frames, (-0.1, -2.6, 1.3), (-0.3, -2.2, 1.25), (-0.35, 1.5, 0.85), (-0.5, 1.5, 0.85), lens=30, fstop=2.8, focus=4.0)
    return aar


# ---------------------------------------------------------------- s4 meeting room
def s4(frames):
    sc = bpy.context.scene
    world(sc, (0.8, 0.82, 0.86), 0.5)
    floor = mat("floor", (0.32, 0.3, 0.29), 0.5); wall = mat("wall", (0.82, 0.82, 0.8), 0.85)
    box("floor", (0, 0, -0.05), (16, 14, 0.1), floor)
    box("ceil", (0, 0, 3.05), (16, 14, 0.1), mat("ceil", (0.9, 0.9, 0.88), 0.9))
    glass = mat("glass", (0.85, 0.92, 0.95), 0.03, transmission=1.0)
    fr = mat("frame", (0.12, 0.12, 0.13), 0.4, 0.8)
    # glass wall behind the panel
    box("glass_back", (0, 2.6, 1.5), (8, 0.02, 3), glass)
    for x in (-3, -1.5, 0, 1.5, 3): box("mull", (x, 2.6, 1.5), (0.05, 0.06, 3), fr)
    box("frost", (0, 2.6, 1.1), (8, 0.025, 0.12), mat("frost", (0.9, 0.9, 0.9), 0.5))
    box("glass_left", (-3.6, 0.3, 1.5), (0.02, 4.6, 3), glass)
    # outside office beyond glass
    box("far_wall", (0, 6.5, 1.5), (16, 0.1, 3), wall)
    for x in (-3, 0, 3):
        box("desk_out", (x, 4.8, 0.74), (1.6, 0.7, 0.04), mat("dsk", (0.85, 0.85, 0.83), 0.4))
        box("mon_out", (x, 5.0, 1.0), (0.5, 0.03, 0.3), mat("mon", (0.02, 0.02, 0.02), 0.3))
    plant((4.0, 5.6, 0), 1.3); plant((-4.5, 5.6, 0), 1.3)
    for x in (-2, 0, 2): area((x, 4.5, 2.9), (0, 0, 0), 1.2, 150)
    # table
    tm = mat("tabletop", (0.9, 0.9, 0.88), 0.3)
    tx, ty = -0.5, 0.6
    box("table", (tx, ty, 0.74), (2.2, 1.1, 0.05), tm, 0.01)
    for dx in (-0.9, 0.9): box("tleg", (tx + dx, ty, 0.36), (0.06, 0.8, 0.72), fr)
    # laptop in front of Neha (screen faces her)
    nx, vx = tx - 0.45, tx + 0.45
    box("lap_base", (nx, ty + 0.05, 0.775), (0.34, 0.24, 0.015), mat("alu", (0.6, 0.6, 0.62), 0.3, 0.8))
    lid = box("lap_lid", (nx, ty - 0.07, 0.89), (0.34, 0.012, 0.23), mat("alu2", (0.6, 0.6, 0.62), 0.3, 0.8))
    lid.rotation_euler = (math.radians(-15), 0, 0)
    box("notepad", (vx + 0.15, ty - 0.05, 0.77), (0.21, 0.29, 0.01), mat("paper", (0.95, 0.95, 0.93), 0.8))
    cyl("glass1", (tx + 0.1, ty - 0.3, 0.82), 0.035, 0.12, glass)
    cm = mat("chairm", (0.1, 0.1, 0.11), 0.5)
    # panel faces -Y (camera), behind table
    panel = []
    for k, (fid, cols, x, h) in enumerate([(WOMAN, NEHA, nx, 1.62), (MAN_LS, VIKRAM, vx + 0.1, 1.76)]):
        chair((x, ty + 0.95, 0), 0, 0.47, cm)
        c = char(fid, "Female_Sitting" if fid == WOMAN else "Man_Sitting", colors=cols, height=h, start=SIT0, offset=k * 20)
        place_bone(c, "Hips", (x, ty + 0.95, 0.57), 30)
        head_nods(c, (1, frames + 30), every=22 + k * 6, amp=0.18, base=(0.2 if k == 0 else -0.1, -0.35, 1), name="talk", seed=k + 3)
        panel.append(c)
    # glasses for Neha: thin dark frame in front of her eyes
    # Aarav foreground, back to camera, facing +Y
    chair((tx - 0.75, ty - 0.95, 0), math.pi - 0.3, 0.47, cm)
    a = char(MAN_SUIT, "Man_Sitting", rotz=math.pi - 0.3, colors=AAR, start=SIT0, offset=33)
    place_bone(a, "Hips", (tx - 0.75, ty - 0.95, 0.57), 30)
    head_nods(a, (1, frames + 30), every=30, amp=0.15, base=(0.0, -0.4, 1), name="talk", seed=9)
    area((tx, ty, 2.9), (0, 0, 0), 2.0, 300)
    sun((math.radians(50), 0, math.radians(-30)), 2.5)
    camera(sc, frames, (0.9, -2.7, 1.5), (0.7, -2.35, 1.45), (-0.55, ty + 0.3, 0.95), (-0.65, ty + 0.3, 0.95), lens=30, fstop=3.2, focus=3.6)
    return a


# ---------------------------------------------------------------- s5 entrance
def s5(frames):
    sc = bpy.context.scene
    world(sc, (0.55, 0.7, 0.95), 0.55)
    box("ground", (0, 0, -0.05), (40, 40, 0.1), mat("pave", (0.3, 0.3, 0.29), 0.8))
    box("plaza", (0, -2, 0.0), (14, 12, 0.02), mat("stone", (0.45, 0.43, 0.4), 0.6))
    glass = mat("cw", (0.2, 0.3, 0.38), 0.05, 0.6)
    fr = mat("frame", (0.75, 0.76, 0.78), 0.3, 1.0)
    by = 8.0
    box("facade", (0, by + 0.3, 6), (20, 0.5, 12), glass)
    for x in range(-10, 11, 2): box("fin", (x, by, 6), (0.12, 0.3, 12), fr)
    for z in range(0, 13, 3): box("band", (0, by, z + 0.0), (20, 0.32, 0.25), fr)
    box("canopy", (0, by - 1.2, 3.3), (6, 2.6, 0.18), fr)
    box("door_glass", (0, by - 0.05, 1.35), (3.0, 0.04, 2.7), mat("door", (0.6, 0.7, 0.75), 0.05, transmission=0.6))
    box("lobby", (0, by + 0.6, 1.5), (5, 0.1, 3), mat("lobby", (0.9, 0.85, 0.75), emit=(1, 0.9, 0.75), estr=1.0))
    for x in (-3.8, 3.8, 6.5, -6.5): plant((x, by - 1.4, 0), 1.6)
    box("planter", (-5.2, 1.5, 0.25), (3, 1, 0.5), mat("planter", (0.4, 0.4, 0.42), 0.6))
    # Aarav walks toward camera (-Y), phone in right hand
    c = char(MAN_SUIT, "Man_Walk", rotz=0, colors=AAR)
    c["root"].location = (-0.6, by - 1.2, 0); ground(c, 1)
    v = 0.054  # m/frame: matches planted-foot travel of Man_Walk (no foot slide)
    c["root"].keyframe_insert("location", frame=1)
    c["root"].location.y -= v * frames; c["root"].keyframe_insert("location", frame=frames)
    for fc in c["root"].animation_data.action.layers[0].strips[0].channelbag(c["root"].animation_data.action_slot).fcurves:
        for k in fc.keyframe_points: k.interpolation = "LINEAR"
    aim_override(c, [("UpperArm.R", (-0.15, -0.25, -1)), ("LowerArm.R", (0.3, -1, 0.0)), ("Palm.R", (0.2, -1, 0.1))], list(range(1, frames + 1, 4)), name="phonearm")
    hold_phone(c, 1, face_head=False)
    head_nods(c, (1, frames + 30), every=45, amp=0.12, base=(0.0, -0.25, 1), name="look", seed=2)
    sun((math.radians(50), 0, math.radians(25)), 3.5, (1, 0.93, 0.82))
    y0 = by - 1.2
    camera(sc, frames, (1.2, -4.5, 1.55), (1.2, -7.4, 1.5), (0.8, y0, 1.3), (0.5, y0 - v * frames, 1.2), lens=40, fstop=4, focus=None)
    sc.camera.data.dof.use_dof = True; sc.camera.data.dof.aperture_fstop = 4
    sc.camera.data.dof.focus_object = c["arm"]
    return c


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:]
    name = argv[0]; test = int(argv[1]) if len(argv) > 1 and argv[1] != "full" else None
    res = (int(argv[2]), int(argv[3])) if len(argv) > 3 else (1920, 1080)
    samples = int(argv[4]) if len(argv) > 4 else 32
    sc = reset()
    frames = round(DUR[name] * FPS)
    globals()[name](frames)
    finish(sc, name, frames, test, res, samples)
