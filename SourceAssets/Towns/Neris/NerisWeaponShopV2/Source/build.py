"""Build the review asset in a fresh background Blender; never alter a live scene."""
import math
import sys
import json
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'Source'))
import geometry as g
from furnishings import arch, crystal, furnish

if not bpy.app.background or bpy.data.filepath:
    raise RuntimeError('Run with --background --factory-startup; preserve hand-edited revisions.')
bpy.ops.wm.read_factory_settings(use_empty=True)
g.palette()
scene = bpy.context.scene
scene.name = 'NERIS | Garran Weapon Shop V2'
scene.unit_settings.system = 'METRIC'

g.collection('01 | Continuous floor and foundation')
g.box('Foundation',(0,0,-.28),(16.7,14.7,.50),'WarmStone',.13)
g.box('One continuous polished floor',(0,0,-.015),(16,14,.10),'Floor',.035)
for side in (-1,1):
    g.box('Perimeter brass inlay',(side*7.43,0,.041),(.025,13.0,.010),'Gold',.002)
    g.box('Perimeter brass inlay',(0,side*6.46,.041),(14.88,.025,.010),'Gold',.002)
g.path('Single circular floor inlay',[(2.44*math.cos(i*math.tau/160),-.42+2.44*math.sin(i*math.tau/160),.044) for i in range(160)],.017,'Gold',True)
g.path('Single teal floor medallion rim',[(2.52*math.cos(i*math.tau/160),-.42+2.52*math.sin(i*math.tau/160),.044) for i in range(160)],.035,'Teal',True)
for i in range(8):
    t=i*math.pi/4
    g.path('Compass inlay',[(1.30*math.cos(t),-.42+1.30*math.sin(t),.049),(2.27*math.cos(t),-.42+2.27*math.sin(t),.049)],.019,'Gold')

g.collection('02 | Ivory columns and arch ribs')
for x in (-7.65,7.65):
    for y in (-6.62,-3.3,0,3.3,6.62):
        g.box('Column plinth',(x,y,.18),(.67,.65,.36),'Ivory',.065)
        g.box('Ivory pilaster',(x,y,2.43),(.33,.34,4.48),'Ivory',.047)
        g.box('Teal pilaster inset',(x-.18*(1 if x>0 else -1),y,2.45),(.035,.11,3.85),'Teal',.01)
        for z in (.42,4.42):
            g.box('Brass column collar',(x,y,z),(.43,.44,.10),'Gold',.02)
        g.box('Column capital',(x,y,4.59),(.61,.59,.22),'Ivory',.04)

wall_names=[]
for side in (-1,1):
    name=('08 | West wall' if side<0 else '09 | East wall')
    wall_names.append(name)
    g.collection(name)
    # A true clerestory aperture sits above the foreground weapon bays.
    g.box('Ivory wall lower',(side*8.08,0,1.66),(.30,14.3,3.32),'Ivory',.04)
    g.box('Ivory wall crown',(side*8.08,0,4.70),(.30,14.3,.54),'Ivory',.04)
    for y,depth in ((-5.14,4.0),(0,3.1),(5.14,4.0)):
        g.box('Window side masonry',(side*8.08,y,3.87),(.30,depth,1.12),'Ivory',.02)
    for y in (-2.55,2.55):
        g.box('Cyan clerestory glass',(side*8.085,y,3.86),(.035,1.48,1.10),'Crystal',.01)
        for yy in (y-.72,y,y+.72):
            g.box('Window mullion',(side*7.89,yy,3.86),(.065,.034,1.10),'Gold',.005)
    for z in (.19,1.36,4.43):
        g.box('Wall continuous molding',(side*7.87,0,z),(.13,14,.07),'Gold',.01)
    g.box('Teal wall dado',(side*7.91,0,.79),(.12,14,1.0),'Teal',.02)

g.collection('10 | Rear wall')
wall_names.append(g.ACTIVE.name)
g.box('Ivory rear wall',(0,7.10,2.48),(16.4,.35,4.96),'Ivory',.06)
g.box('Rear teal dado',(0,6.88,.80),(16,.13,1.10),'Teal',.03)
for z in (.20,1.38,4.48):
    g.box('Rear brass cornice',(0,6.79,z),(16,.14,.07),'Gold',.02)

g.collection('11 | Entrance facade - removable')
wall_names.append(g.ACTIVE.name)
for side in (-1,1):
    g.box('Entrance wall',(side*4.94,-7.10,2.47),(6.30,.35,4.94),'Ivory',.04)
    g.box('Entrance teal dado',(side*4.94,-6.89,.78),(6.2,.08,1.14),'Teal')
    for z in (.22,1.39,4.48):
        g.box('Entrance trim',(side*4.94,-6.80,z),(6.2,.09,.05),'Gold',.01)
    g.box('Teal exterior banner',(side*3.3,-7.32,2.70),(.77,.08,2.65),'Teal')
    g.star('Exterior banner star',(side*3.3,-7.38,3.04),.30)
    # Swing the double doors outward; the threshold remains open and walkable.
    leaf=g.box('Open walnut entrance door',(side*1.45,-7.9,1.44),(.16,1.54,2.86),'Walnut',.045)
    g.box('Door brass rail',(side*1.34,-7.91,1.40),(.038,1.42,.09),'Gold',.01)
arch('Entrance arch',0,-7.22,.08,3.20,2.82,'Ivory',.17)
arch('Entrance brass arch',0,-7.41,.10,3.18,2.82,'Gold',.034)
g.box('Entrance header',(0,-7.10,4.73),(3.8,.35,.44),'Ivory')
for i in range(48):
    xa=-1.6+i*3.2/48
    xb=-1.6+(i+1)*3.2/48
    za=2.82+math.sqrt(max(0,1.6**2-xa**2))
    zb=2.82+math.sqrt(max(0,1.6**2-xb**2))
    verts=[(xa,-7.275,za),(xb,-7.275,zb),(xb,-7.275,4.52),(xa,-7.275,4.52),
           (xa,-6.925,za),(xb,-6.925,zb),(xb,-6.925,4.52),(xa,-6.925,4.52)]
    g.mesh('Entrance arch spandrel',verts,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(3,2,6,7)],'Ivory')
g.box('Entrance threshold',(0,-7.04,.05),(3.20,.68,.10),'WarmStone')
g.text('Shop exterior sign','NERIS  WEAPON SHOP',(0,-7.37,4.76),.21)
for i in range(3):
    g.box('Front step',(0,-7.65-i*.38,-.07-i*.12),(3.8+i*.48,.68,.18),'Ivory',.035)

furnish()
g.collection('07 | Crystal sconces and showroom lights')
for side in (-1,1):
    for y in (-4.85,.28,4.9):
        x=side*7.42
        g.box('Sconce wall mount',(x,y,2.63),(.16,.32,.54),'Gold')
        g.rod('Sconce arm',(x,y,2.68),(x-side*.48,y,2.68),.044,'Gold')
        g.cylinder('Crystal socket',(x-side*.48,y,2.73),.20,.16,'Gold',24)
        crystal('Cyan crystal sconce',(x-side*.48,y,2.80),.12,.55)
        lamp=bpy.data.lights.new('Warm crystal spill','POINT')
        lamp.energy, lamp.color, lamp.shadow_soft_size=100,(.51,.83,1),.6
        obj=bpy.data.objects.new(lamp.name,lamp)
        g.ACTIVE.objects.link(obj)
        obj.location=(x-side*.72,y,3.05)

g.collection('12 | Teal dome and roof - removable')
roof_name=g.ACTIVE.name
verts=[]
for z in (4.73,4.94):
    for inner in (False,True):
        for i in range(96):
            t=i*math.tau/96
            c,s=math.cos(t),math.sin(t)
            if inner:
                x,y=7.85*c,6.85*s
            else:
                scale=min(8.36/max(abs(c),1e-9),7.36/max(abs(s),1e-9))
                x,y=scale*c,scale*s
            verts.append((x,y,z))
faces=[]
for i in range(96):
    j=(i+1)%96
    faces.extend([(i,j,96+j,96+i),(192+i,288+i,288+j,192+j),
                  (i,192+i,192+j,j),(96+i,96+j,288+j,288+i)])
g.mesh('Solid roof terrace around dome',verts,faces,'Ivory')
# A double shell has real interior and exterior surfaces beneath the crown.
for inner in (False,True):
    verts=[]
    count, rings=96,20
    for j in range(rings):
        phi=(math.pi/2)*j/rings
        r=math.cos(phi)
        height=(2.82 if inner else 3.0)*math.sin(phi)+4.85
        for i in range(count):
            t=i*math.tau/count
            verts.append(((7.96 if inner else 8.18)*r*math.cos(t),(6.96 if inner else 7.18)*r*math.sin(t),height))
    verts.append((0,0,4.85+(2.82 if inner else 3.0)))
    faces=[(j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i) for j in range(rings-1) for i in range(count)]
    faces.extend([((rings-1)*count+i,(rings-1)*count+(i+1)%count,rings*count) for i in range(count)])
    if inner: faces=[tuple(reversed(f)) for f in faces]
    dome=g.mesh('Vault interior' if inner else 'Teal exterior dome',verts,faces,'Ivory' if inner else 'Teal')
    for face in dome.data.polygons: face.use_smooth=True
for i in range(16):
    theta=i*math.tau/16
    points=[]
    for j in range(45):
        phi=j*math.pi/88
        points.append((8.20*math.cos(phi)*math.cos(theta),7.20*math.cos(phi)*math.sin(theta),4.84+3.03*math.sin(phi)))
    g.path('Exterior brass dome rib',points,.039,'Gold')
    points=[(7.91*math.cos(j*math.pi/88)*math.cos(theta),6.91*math.cos(j*math.pi/88)*math.sin(theta),4.81+2.80*math.sin(j*math.pi/88)) for j in range(45)]
    g.path('Interior arch rib',points,.049,'Gold')
g.path('Dome spring brass band',[(8.19*math.cos(i*math.tau/160),7.19*math.sin(i*math.tau/160),4.90) for i in range(160)],.09,'Gold',True)
g.cylinder('Dome crown',(0,0,7.91),.40,.18,'Gold')
crystal('Dome crown crystal',(0,0,8.02),.25,1.1)

g.collection('13 | Studio camera and light rig')
def area(name, position, power, color, size, target):
    data=bpy.data.lights.new(name,'AREA')
    data.energy,data.color,data.shape,data.size=power,color,'DISK',size
    obj=bpy.data.objects.new(name,data)
    g.ACTIVE.objects.link(obj)
    obj.location=position
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
for args in [
    ('Oculus daylight',(0,0,6.65),2200,(.72,.88,1),6,(0,0,0)),
    ('Warm gallery fill',(-4,2,4.5),1400,(1,.78,.49),5,(-2,4,1)),
    ('Cool gallery fill',(4,-2,4.5),1500,(.61,.85,1),5,(4,3,1)),
    ('Entrance bounce',(0,-5,4.3),1900,(1,.88,.68),6,(0,2,2)),
    ('Exterior softbox',(7,-11,16),2700,(.85,.94,1),10,(0,0,1)),
]: area(*args)
data=bpy.data.cameras.new('Review camera')
camera=bpy.data.objects.new('Review camera',data)
g.ACTIVE.objects.link(camera)
scene.camera=camera
scene.render.engine='CYCLES'
scene.cycles.samples=32
scene.cycles.use_denoising=True
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='OPTIX'
    prefs.get_devices()
    for device in prefs.devices: device.use=device.type!='CPU'
    if any(d.use for d in prefs.devices): scene.cycles.device='GPU'
except Exception: pass
scene.world=bpy.data.worlds.new('Neris ambient')
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.15,.19,.22,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.view_settings.exposure=-.5
scene.render.image_settings.file_format='PNG'
scene.render.resolution_percentage=100
scene.render.film_transparent=False

full=scene.view_layers[0]
full.name='Complete shop'
interior=scene.view_layers.new('Interior - roof and entrance removed')
dollhouse=scene.view_layers.new('360 - all walls removed')
for layer,names in ((interior,[roof_name,wall_names[-1]]),(dollhouse,[roof_name]+wall_names)):
    for name in names: layer.layer_collection.children[name].exclude=True
for layer in scene.view_layers: layer.use=False
interior.use=True
bpy.context.window.view_layer=interior

def shot(position,target,lens,width,height,filename,layer):
    camera.location=position
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.lens=lens
    scene.render.resolution_x,scene.render.resolution_y=width,height
    for candidate in scene.view_layers: candidate.use=candidate==layer
    bpy.context.window.view_layer=layer
    scene.render.filepath=str(ROOT/'Previews'/filename)
    bpy.ops.render.render(write_still=True)

shot((.5,-6.65,2.85),(0,3.4,2.45),20,1600,1000,'Interior.png',full)
shot((18,-22,17),(0,0,1.55),45,1400,1100,'Cutaway.png',interior)
shot((-18,19,16),(0,0,1.35),43,1400,1100,'Reverse-360.png',dollhouse)
shot((21,-26,20),(0,0,2.6),47,1400,1100,'Complete-Shop.png',full)

# Save a comfortable interactive orbit view. Collections stay individually editable.
camera.location=(18,-22,17)
camera.rotation_euler=(Vector((0,0,1.55))-camera.location).to_track_quat('-Z','Y').to_euler()
for layer in scene.view_layers: layer.use=layer==interior
bpy.context.window.view_layer=interior
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.region_3d.view_distance=34.56
            space.region_3d.view_location=(0,0,1.7)
            space.region_3d.view_rotation=camera.rotation_euler.to_quaternion()
            space.shading.type='MATERIAL'
            space.overlay.show_overlays=False
            space.clip_end=300
scene['Review controls']='Middle mouse: orbit 360; wheel: zoom; Shift+middle: pan. Top-right View Layer: Complete shop / Interior / 360 all walls removed.'
scene['Design']='Ivory stone, teal enamel, brass, arched displays and cyan crystals match the Neris exterior. Continuous floor; spatial procedural finishes; no image tiles.'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Neris-Weapon-Shop-V2.blend'))
print('NERIS SHOP BLEND SAVED',flush=True)
