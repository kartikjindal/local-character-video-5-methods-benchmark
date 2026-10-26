import os
import bpy, math, mathutils
from mathutils import Vector, Matrix
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets") + "/"
FPS = 30

SKIN = (0.36, 0.20, 0.12)
NAVY = (0.025, 0.04, 0.11)
WHITE = (0.85, 0.85, 0.85)
BLACKHAIR = (0.015, 0.012, 0.01)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = FPS
    return sc


def mat(name, rgb, rough=0.6, metal=0.0, emit=None, estr=1.0, alpha=None, transmission=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = estr
    if transmission:
        b.inputs["Transmission Weight"].default_value = transmission
        b.inputs["IOR"].default_value = 1.45
    if alpha is not None:
        b.inputs["Alpha"].default_value = alpha
    return m


def box(name, loc, size, m, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        bm = o.modifiers.new("b", "BEVEL"); bm.width = bevel; bm.segments = 3
    o.data.materials.append(m)
    return o


def cyl(name, loc, r, h, m, verts=32):
    bpy.ops.mesh.primitive_cylinder_add(location=loc, radius=r, depth=h, vertices=verts)
    o = bpy.context.object; o.name = name; o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


def load_glb(fid, loc=(0, 0, 0), rotz=0.0, scale=None):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=A + fid + ".glb")
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new(fid + "_root", None)
    bpy.context.scene.collection.objects.link(root)
    for o in new:
        if o.parent is None:
            o.parent = root
    if scale:
        root.scale = (scale,) * 3
    root.location = loc
    root.rotation_euler = (0, 0, rotz)
    return root, new


def char(fid, act, loc=(0, 0, 0), rotz=0.0, height=1.75, colors=None, offset=0, start=None, end=None, speed=1.0):
    """Import a Quaternius HumanArmature character, scale to height, play action `act`
    looped (optionally sub-range start..end in source frames), recolor materials by name prefix."""
    bacts = set(bpy.data.actions)
    root, new = load_glb(fid)
    arm = [o for o in new if o.type == "ARMATURE"][0]
    meshes = [o for o in new if o.type == "MESH"]
    # drop stray non-skinned helper meshes (e.g. Icosphere)
    for o in meshes[:]:
        if not any(md.type == "ARMATURE" for md in o.modifiers) and o.parent != arm:
            bpy.data.objects.remove(o); meshes.remove(o)
    bpy.context.view_layer.update()
    zs = [(o.matrix_world @ Vector(c)).z for o in meshes for c in o.bound_box]
    s = height / (max(zs) - min(zs))  # rest-pose (bind) height
    root.scale = (s, s, s)
    root.location = loc
    root.rotation_euler = (0, 0, rotz)
    acts = [x for x in bpy.data.actions if x not in bacts]
    ac = [x for x in acts if x.name.split("|")[-1].split(".")[0] == act][0]
    arm.animation_data_create()
    arm.animation_data.action = None
    for t in list(arm.animation_data.nla_tracks): arm.animation_data.nla_tracks.remove(t)
    tr = arm.animation_data.nla_tracks.new(); tr.name = "base"
    st = tr.strips.new("base", 1, ac)
    fs, fe = ac.frame_range
    if start is not None: st.action_frame_start = start
    if end is not None: st.action_frame_end = end
    st.scale = 1.0 / speed
    st.repeat = 30
    st.frame_start = 1 - offset
    # shift whole strip so `offset` frames are skipped
    st.use_auto_blend = False
    st.extrapolation = "HOLD"
    if colors:
        done = set()
        for o in meshes:
            for i, m in enumerate(o.data.materials):
                if m is None: continue
                key = m.name.split(".")[0]
                if key in colors and colors[key] is not None:
                    if (o.name, i) in done: continue
                    nm = m.copy(); o.data.materials[i] = nm
                    b = nm.node_tree.nodes.get("Principled BSDF")
                    if b:
                        for l in list(b.inputs["Base Color"].links): nm.node_tree.links.remove(l)
                        b.inputs["Base Color"].default_value = (*colors[key], 1)
                        b.inputs["Roughness"].default_value = 0.65
    return dict(root=root, arm=arm, meshes=meshes, scale=s, action=ac)


def bone_world(c, bone, frame):
    bpy.context.scene.frame_set(frame)
    pb = c["arm"].pose.bones[bone]
    return c["arm"].matrix_world @ pb.head, c["arm"].matrix_world @ pb.tail


def aim_override(c, aims, frames, influence=1.0, name="ovr"):
    """Layer a REPLACE NLA track that points the given bones (armature-local dirs) at
    `aims` = [(bone, dir_vec_in_character_space)] — char faces -Y, its right is -X.
    Keyed at each frame in `frames` so it follows the base motion."""
    arm = c["arm"]; sc = bpy.context.scene
    tr = arm.animation_data.nla_tracks.new(); tr.name = name
    arm.animation_data.action = None
    for f in frames:
        sc.frame_set(f)
        for bname, d in aims:
            pb = arm.pose.bones[bname]
            bpy.context.view_layer.update()
            M = pb.matrix.copy()  # armature space
            cur = (pb.tail - pb.head).normalized()
            # armature object space -> character dir: armature may have its own rotation
            rot_arm = (arm.matrix_world.to_3x3().normalized().inverted() @ c["root"].matrix_world.to_3x3().normalized())
            want = (rot_arm @ Vector(d)).normalized()
            q = cur.rotation_difference(want)
            R = q.to_matrix().to_4x4()
            newM = Matrix.Translation(M.to_translation()) @ R @ Matrix.Translation(-M.to_translation()) @ M
            pb.matrix = newM
            bpy.context.view_layer.update()
            pb.keyframe_insert("rotation_quaternion", frame=f, group=bname)
        # reset to evaluate fresh base next frame
    ac = arm.animation_data.action
    arm.animation_data.action = None
    st = tr.strips.new(name, frames[0], ac)
    st.blend_type = "REPLACE"; st.influence = influence; st.use_auto_blend = False
    st.extrapolation = "HOLD"
    return ac


def parent_to_bone(obj, c, bone):
    arm = c["arm"]
    bpy.context.view_layer.update()
    mw = obj.matrix_world.copy()
    obj.parent = arm; obj.parent_type = "BONE"; obj.parent_bone = bone
    bpy.context.view_layer.update()
    obj.matrix_world = mw


def phone(c, frame):
    """dark rounded slab in the right palm, screen faintly lit"""
    bpy.context.scene.frame_set(frame)
    arm = c["arm"]; pb = arm.pose.bones["Palm.R"]
    head = arm.matrix_world @ pb.head; tail = arm.matrix_world @ pb.tail
    bpy.ops.mesh.primitive_cube_add()
    p = bpy.context.object; p.name = "phone"
    p.scale = (0.036, 0.075, 0.004)
    bpy.ops.object.transform_apply(scale=True)
    bm = p.modifiers.new("b", "BEVEL"); bm.width = 0.006; bm.segments = 4
    p.data.materials.append(mat("phone", (0.55, 0.56, 0.6), 0.3, 1.0))
    scr = mat("screen", (0.05, 0.08, 0.12), 0.2, emit=(0.55, 0.7, 1.0), estr=1.2)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.0045))
    s = bpy.context.object; s.scale = (0.064, 0.14, 1); s.data.materials.append(scr); s.parent = p
    return p


def camera(sc, frames, p0, p1, t0, t1, lens=35, fstop=2.8, focus=None):
    cd = bpy.data.cameras.new("cam"); cd.lens = lens
    cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    tgt = bpy.data.objects.new("tgt", None); sc.collection.objects.link(tgt)
    con = cam.constraints.new("TRACK_TO"); con.target = tgt; con.track_axis = "TRACK_NEGATIVE_Z"; con.up_axis = "UP_Y"
    for f, p, t in ((1, p0, t0), (frames, p1, t1)):
        cam.location = p; cam.keyframe_insert("location", frame=f)
        tgt.location = t; tgt.keyframe_insert("location", frame=f)
    if focus is not None:
        cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop
        if isinstance(focus, bpy.types.Object): cd.dof.focus_object = focus
        else: cd.dof.focus_distance = focus
    return cam


def world(sc, rgb=(0.6, 0.65, 0.75), strength=0.6):
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (*rgb, 1); bg.inputs[1].default_value = strength


def sun(rot, energy=3.0, color=(1, 0.95, 0.88), angle=0.05):
    l = bpy.data.lights.new("sun", "SUN"); l.energy = energy; l.color = color; l.angle = angle
    o = bpy.data.objects.new("sun", l); bpy.context.scene.collection.objects.link(o)
    o.rotation_euler = rot
    return o


def area(loc, rot, size, energy, color=(1, 0.97, 0.92), shape="RECTANGLE", sy=None):
    l = bpy.data.lights.new("area", "AREA"); l.energy = energy; l.color = color
    l.shape = shape; l.size = size; l.size_y = sy or size
    o = bpy.data.objects.new("area", l); bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.rotation_euler = rot
    return o


def setup_render(sc, frames, w=1920, h=1080, samples=32, out=None):
    sc.render.engine = "BLENDER_EEVEE_NEXT"
    sc.eevee.taa_render_samples = samples
    try:
        sc.eevee.use_shadows = True
        sc.eevee.use_raytracing = True
        sc.eevee.ray_tracing_options.resolution_scale = "2"
    except Exception:
        pass
    sc.render.resolution_x = w; sc.render.resolution_y = h; sc.render.resolution_percentage = 100
    sc.frame_start = 1; sc.frame_end = frames
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.render.film_transparent = False


def place_bone(c, bone, target, frame):
    """move the character root so `bone` head sits at world `target` (x,y,z) at `frame`"""
    sc = bpy.context.scene; sc.frame_set(frame); bpy.context.view_layer.update()
    h = c["arm"].matrix_world @ c["arm"].pose.bones[bone].head
    c["root"].location += Vector(target) - h
    bpy.context.view_layer.update()


def lowest_z(c, frame):
    bpy.context.scene.frame_set(frame)
    dg = bpy.context.evaluated_depsgraph_get()
    z = 1e9
    for o in c["meshes"]:
        e = o.evaluated_get(dg); m = e.to_mesh()
        mw = o.matrix_world
        for v in m.vertices:
            z = min(z, (mw @ v.co).z)
        e.to_mesh_clear()
    return z


def ground(c, frame, z=0.0):
    c["root"].location.z += z - lowest_z(c, frame)


def stride_speed(c, frames):
    """metres/frame the feet travel backwards in an in-place walk loop (world space)"""
    sc = bpy.context.scene; ys = []
    for f in frames:
        sc.frame_set(f)
        ys.append((c["arm"].matrix_world @ c["arm"].pose.bones["Foot.L"].head).copy())
    # foot planted phase: largest consecutive displacement magnitude median
    d = sorted((ys[i + 1] - ys[i]).length for i in range(len(ys) - 1))
    return d[len(d) // 2]


def head_nods(c, frames, every=24, amp=0.25, base=(0, -0.2, 1), name="nod", seed=0):
    import random
    r = random.Random(seed)
    aims = []
    keys = list(range(frames[0], frames[1], every))
    arm = c["arm"]; sc = bpy.context.scene
    tr = arm.animation_data.nla_tracks.new(); tr.name = name
    arm.animation_data.action = None
    for f in keys:
        sc.frame_set(f); bpy.context.view_layer.update()
        d = Vector(base) + Vector((r.uniform(-amp, amp), r.uniform(-amp * .5, amp * .5), r.uniform(-amp, amp * .5)))
        pb = arm.pose.bones["Head"]
        M = pb.matrix.copy(); cur = (pb.tail - pb.head).normalized()
        rot_arm = (arm.matrix_world.to_3x3().normalized().inverted() @ c["root"].matrix_world.to_3x3().normalized())
        q = cur.rotation_difference((rot_arm @ d).normalized())
        pb.matrix = Matrix.Translation(M.to_translation()) @ q.to_matrix().to_4x4() @ Matrix.Translation(-M.to_translation()) @ M
        bpy.context.view_layer.update()
        pb.keyframe_insert("rotation_quaternion", frame=f, group="Head")
    ac = arm.animation_data.action; arm.animation_data.action = None
    st = tr.strips.new(name, keys[0], ac); st.blend_type = "REPLACE"; st.extrapolation = "HOLD"


PHONE_AIMS = [("UpperArm.R", (-0.12, -0.12, -1)), ("LowerArm.R", (0.5, -1, 0.3)), ("Palm.R", (0.4, -1, 0.5)), ("Head", (0, -0.75, 1))]


def hold_phone(c, frame, face_head=True, up=0.0):
    ph = phone(c, frame)
    arm = c["arm"]; pb = arm.pose.bones["Palm.R"]
    bpy.context.scene.frame_set(frame); bpy.context.view_layer.update()
    h = arm.matrix_world @ pb.head; t = arm.matrix_world @ pb.tail
    ph.location = h + (t - h) * 0.6
    tgt = arm.matrix_world @ arm.pose.bones["Head"].head if face_head else ph.location + (t - h)
    ph.rotation_euler = (tgt - ph.location).to_track_quat("Z", "Y").to_euler()
    ph.location += (tgt - ph.location).normalized() * 0.035
    ph.location += (t - h).normalized() * up
    ph.scale = (1.15, 1.15, 1.15)
    parent_to_bone(ph, c, "Palm.R")
    return ph
