"""Measure v5.8 equipment sockets from approved geometry, without old offsets."""
import bpy
import json
import math
import numpy as np
from pathlib import Path
from mathutils import Vector

PACKAGE = Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(PACKAGE/'Blender/arin-v5.8-all-animations.blend'))
rig = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
scene = bpy.context.scene
scene.frame_set(1)
bpy.context.view_layer.update()
path = PACKAGE/'ArinV58.sm3d.json'
descriptor = json.loads(path.read_text())
sockets = descriptor['sockets']


def socket(name, obj, local):
    hand = rig.matrix_world @ rig.pose.bones[obj.parent_bone].matrix
    point = hand.inverted() @ obj.matrix_world @ Vector(local)
    sockets[name] = {'node':obj.parent_bone, 'translation':list(point)}


shield = bpy.data.objects['Shield']
points = np.array([v.co[:] for v in shield.data.vertices])
center = points.mean(axis=0)
_, _, axes = np.linalg.svd(points-center, full_matrices=False)
up = axes[0] if axes[0, 2] > 0 else -axes[0]
across = axes[1] if axes[1, 0] > 0 else -axes[1]
plane = np.column_stack(((points-center) @ across, (points-center) @ up))
# The silhouette's convex hull excludes the raised face emblem and rear handle.
ordered = sorted(set(map(tuple, plane)))


def cross(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


lower, upper = [], []
for point in ordered:
    while len(lower) > 1 and cross(lower[-2], lower[-1], point) <= 0:
        lower.pop()
    lower.append(point)
for point in reversed(ordered):
    while len(upper) > 1 and cross(upper[-2], upper[-1], point) <= 0:
        upper.pop()
    upper.append(point)
hull = np.array(lower[:-1]+upper[:-1])
mid = (hull.min(axis=0)+hull.max(axis=0))/2
extent = (hull.max(axis=0)-hull.min(axis=0))/2
rim = []
for index in range(8):
    angle = math.pi/2 + index*math.pi/4
    ray = np.array((math.cos(angle), math.sin(angle)))*extent
    hits = []
    for first, second in zip(hull, np.roll(hull,-1,axis=0)):
        matrix = np.column_stack((ray, first-second))
        if abs(np.linalg.det(matrix)) < 1e-12:
            continue
        distance, edge = np.linalg.solve(matrix, first-mid)
        if distance >= 0 and 0 <= edge <= 1:
            # Interpolate actual outline vertices, preserving the shield curvature.
            a = points[np.argmin(np.linalg.norm(plane-first,axis=1))]
            b = points[np.argmin(np.linalg.norm(plane-second,axis=1))]
            hits.append((distance, a+(b-a)*edge))
    assert hits, index
    rim.append(min(hits,key=lambda h:h[0])[1])
    socket(f'ShieldRim{index}',shield,rim[-1])
for name, index in (('ShieldFireLeft',1),('ShieldFireRight',7),('ShieldFireTip',4)):
    socket(name,shield,rim[index])
sword = bpy.data.objects['Sword']
tip = max(v.co.z for v in sword.data.vertices)
# The cleaned blade starts beyond the decorative guard at local Z=.10.
socket('SwordBase',sword,(0,0,.10))
socket('SwordTip',sword,(0,0,tip))
path.write_text(json.dumps(descriptor,indent=2)+'\n', newline='\n')
report = {'source':'approved v5.8 equipment geometry','socketCount':len(sockets),
          'shieldRimLocal':[p.tolist() for p in rim],
          'swordBladeLocalZ':[.10,tip],'oldCalibrationImported':False}
(PACKAGE/'Diagnostics/flame-sockets.json').write_text(json.dumps(report,indent=2)+'\n', newline='\n')
print('FLAME_SOCKETS='+json.dumps(report))
