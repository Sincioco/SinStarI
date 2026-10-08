"""A complete, low-cost cutaway 3D armory. All displays are mesh geometry."""
import bpy
import json
import math
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
bpy.ops.wm.read_factory_settings(use_empty=True)
materials={}
groups={}
for name,color,metal,rough in [
    ('Limestone',(.31,.29,.265),0,.9),('Oak',(.25,.115,.043),0,.72),
    ('DarkOak',(.065,.032,.017),0,.8),('Steel',(.38,.48,.55),.75,.28),
    ('Brass',(.58,.34,.095),.7,.3),('Navy',(.027,.075,.11),0,.75),
    ('Lantern',(.95,.48,.09),0,.4)]:
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    bsdf=m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=(*color,1)
    bsdf.inputs['Metallic'].default_value=metal
    bsdf.inputs['Roughness'].default_value=rough
    if name=='Lantern':
        bsdf.inputs['Emission Color'].default_value=(1,.37,.025,1)
        bsdf.inputs['Emission Strength'].default_value=.8
    materials[name]=m
    groups[name]=[]

def finish(obj, name, mat):
    obj.name=name
    obj.data.materials.append(materials[mat])
    groups[mat].append(obj)
    return obj

def box(name, center, size, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center)
    o=bpy.context.object
    o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        m=o.modifiers.new('Soft edges','BEVEL');m.width=bevel;m.segments=1
        bpy.ops.object.modifier_apply(modifier=m.name)
    return finish(o,name,mat)

def cylinder(name,center,radius,depth,mat,rotation=(0,0,0),vertices=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,
        location=center,rotation=rotation)
    return finish(bpy.context.object,name,mat)

# The camera-side wall is cut away; the room has physical side/back walls and a door frame.
for row in range(28):
    for col in range(8):
        box('Floor plank',(col*2-7,row*.5-6.75,-.07),(1.985,.485,.14),'Oak' if (row+col)%3 else 'DarkOak')
for row in range(9):
    for col in range(12):
        box('Back stone',(col*1.34-7.37,7.10,.25+row*.53),(1.30,.32,.49),'Limestone',.035)
    for side in (-1,1):
        for col in range(10):
            box('Side stone',(side*8.12,col*1.4-6.3,.25+row*.53),(.30,1.36,.49),'Limestone',.035)
for x in (-7.8,-4,4,7.8):
    box('Wall oak beam',(x,6.88,2.4),(.23,.24,4.8),'DarkOak',.025)
box('Rear header',(0,6.82,4.7),(16,.33,.35),'DarkOak',.035)
for side in (-1,1):
    box('Door post',(side*1.4,-6.85,1.75),(.30,.35,3.5),'DarkOak',.03)
    box('Front half wall',(side*4.7,-6.95,.6),(6.3,.25,1.2),'Limestone',.025)
box('Door lintel',(0,-6.85,3.5),(3.15,.40,.3),'DarkOak',.03)
box('Threshold',(0,-6.86,.025),(2.6,.5,.05),'Brass')

# Counter and joinery: all surfaces have depth and block walking.
box('Counter body',(0,3.6,.62),(8.0,1.2,1.24),'DarkOak',.05)
box('Counter top',(0,3.6,1.29),(8.6,1.65,.18),'Oak',.045)
box('Counter plinth',(0,3.6,.12),(8.25,1.4,.24),'Oak',.02)
for x in (-3,-1,1,3):
    box('Recessed front panel',(x,2.96,.66),(1.82,.07,.86),'Oak',.025)
    cylinder('Brass rivet',(x,2.90,.98),.034,.06,'Brass',(math.pi/2,0,0),8)
box('Counter runner',(0,3.5,1.398),(3,.95,.025),'Navy')

def sword(x,y,z,length=1.2):
    box('Sword grip',(x,y,z+.15),(.075,.07,.28),'DarkOak',.012)
    cylinder('Sword pommel',(x,y,z),.075,.08,'Brass',(math.pi/2,0,0))
    box('Sword guard',(x,y,z+.32),(.45,.08,.07),'Brass',.02)
    verts=[(x-.085,y-.025,z+.37),(x+.085,y-.025,z+.37),(x+.055,y-.025,z+length),
        (x,y-.025,z+length+.25),(x-.055,y-.025,z+length),
        (x-.085,y+.025,z+.37),(x+.085,y+.025,z+.37),(x+.055,y+.025,z+length),
        (x,y+.025,z+length+.25),(x-.055,y+.025,z+length)]
    faces=[(0,1,2,3,4),(9,8,7,6,5)]+[(i,(i+1)%5,(i+1)%5+5,i+5) for i in range(5)]
    mesh=bpy.data.meshes.new('Forged blade');mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new('Steel sword',mesh);bpy.context.collection.objects.link(o);finish(o,'Steel sword','Steel')

for side in (-1,1):
    x=side*5.7
    box('Weapon rack',(x,6.56,2.1),(3.1,.18,3.3),'DarkOak',.04)
    box('Rack crossbar',(x,6.32,2.25),(3.3,.18,.14),'Oak')
    for i in range(5):
        sword(x-1.12+i*.56,6.22,1.05,.95+.14*(i%3))
    box('Display bench',(side*6.6,2.3,.78),(1.7,4.2,.16),'Oak',.03)
    for y in (.6,4):
        box('Bench leg',(side*6.6,y,.38),(1.45,.18,.76),'DarkOak')
    for y in (.9,2.4,3.9):
        # Round shield with boss, rim and central band on the side wall.
        cylinder('Shield',(side*7.83,y,2.6),.64,.12,'Navy',(0,math.pi/2,0),24)
        cylinder('Shield boss',(side*7.73,y,2.6),.17,.20,'Brass',(0,math.pi/2,0),16)
        box('Shield band',(side*7.74,y,2.6),(.06,.08,1.14),'Brass')
    for y in (-3,-1.9,-.8):
        cylinder('Spear shaft',(side*7.25,y,1.1),.045,2.2,'Oak')
        bpy.ops.mesh.primitive_cone_add(vertices=6,radius1=.15,radius2=0,depth=.52,location=(side*7.25,y,2.45))
        finish(bpy.context.object,'Spear point','Steel')
    for y in (-4.6,5.6):
        box('Lantern bracket',(side*7.6,y,3.1),(.7,.1,.1),'Brass')
        box('Lantern warm glass',(side*7.25,y,2.93),(.24,.24,.45),'Lantern',.02)
        for z in (2.67,3.19):
            box('Lantern cap',(side*7.25,y,z),(.34,.34,.1),'Brass',.025)

# Central armorer emblem and small stock behind the counter.
cylinder('Armory shield',(0,6.78,3.25),.82,.13,'Navy',(math.pi/2,0,0),32)
cylinder('Emblem boss',(0,6.66,3.25),.2,.17,'Brass',(math.pi/2,0,0),16)
for side in (-1,1):
    sword(side*1.35,6.50,2.3,1.35)
for x in (-3.4,3.4):
    box('Stock crate',(x,5.85,.42),(1.1,.85,.84),'Oak',.04)
    for z in (.12,.70):
        box('Crate metal band',(x,5.40,z),(1.12,.06,.09),'Steel')

# Collapse by material to seven static draw parts; no invisible lights/cameras exported.
for name,objects in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.join()
    bpy.context.object.name='Armory - '+name
    # Solid-color materials still need valid derivatives for the native tangent cooker.
    mesh=bpy.context.object.data
    for layer in list(mesh.uv_layers):mesh.uv_layers.remove(layer)
    uv=mesh.uv_layers.new(name='UVMap')
    for face in mesh.polygons:
        dominant=max(range(3),key=lambda axis:abs(face.normal[axis]))
        axes=[axis for axis in range(3) if axis!=dominant]
        for loop_index in face.loop_indices:
            co=mesh.vertices[mesh.loops[loop_index].vertex_index].co
            uv.data[loop_index].uv=(co[axes[0]],co[axes[1]])
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(ROOT/'Armory-Room.glb'),export_format='GLB',
    use_selection=True,export_animations=False)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Armory-Room.blend'))
report={'parts':len(groups),'materials':len(materials),
    'triangles':sum(len(p.vertices)-2 for o in bpy.context.scene.objects for p in o.data.polygons),
    'nativeScalePercent':1000,'sha256':hashlib.sha256((ROOT/'Armory-Room.glb').read_bytes()).hexdigest()}
(ROOT/'room-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
