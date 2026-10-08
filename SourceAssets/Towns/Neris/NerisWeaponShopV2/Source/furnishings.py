"""Neris armory furniture and individually modeled weapons; no image stand-ins."""
import math
import bpy
from mathutils import Matrix, Vector
import geometry as g


def arch(name, x, y, bottom, width, spring, material='Gold', radius=.065):
    r = width / 2
    points = [(x-r, y, bottom), (x-r, y, spring)]
    points += [(x+r*math.cos(t), y, spring+r*math.sin(t))
               for t in [math.pi-i*math.pi/40 for i in range(41)]]
    points.append((x+r, y, bottom))
    return g.path(name, points, radius, material)


def crystal(name, center, radius=.16, height=.8):
    x,y,z = center
    vertices = [(x+radius*math.cos(i*math.pi/3), y+radius*math.sin(i*math.pi/3), z)
                for i in range(6)]
    vertices += [(a,b,c+height*.7) for a,b,c in vertices]
    vertices += [(x,y,z+height), (x,y,z-.12)]
    faces = [(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)]
    faces += [(i+6,(i+1)%6+6,12) for i in range(6)]
    faces += [((i+1)%6,i,13) for i in range(6)]
    return g.mesh(name,vertices,faces,'Crystal')


def sword(name, center, length=1.5, width=.12, tilt=0, material='Steel'):
    before = set(bpy.context.scene.objects)
    # Local sword points upward, with the hilt at its base.
    g.cylinder(name+' pommel',(0,0,.05),.105,.10,'Gold',24)
    g.cylinder(name+' grip',(0,0,.26),.063,.32,'Leather',16)
    for i in range(7):
        g.cylinder(name+' grip binding',(0,0,.105+i*.048),.067,.012,'Gold',16)
    g.path(name+' curved guard',[(-.35,0,.37),(-.24,-.025,.45),(0,0,.47),(.24,-.025,.45),(.35,0,.37)],.045,'Gold')
    verts=[]
    for z,w in ((.50,width),(length*.86,width*.65)):
        verts.extend([(-w,0,z),(0,-.043,z),(w,0,z),(0,.043,z)])
    verts.append((0,0,length))
    faces=[(0,3,2,1)]
    faces += [(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]
    faces += [(i+4,(i+1)%4+4,8) for i in range(4)]
    g.mesh(name+' diamond-section blade',verts,faces,material)
    g.path(name+' fuller',[(0,-.046,.64),(0,-.046,length*.82)],.009,'DeepTeal')
    transform=Matrix.Translation(Vector(center)) @ Matrix.Rotation(tilt,4,'Y')
    for obj in set(bpy.context.scene.objects)-before:
        obj.matrix_world=transform @ obj.matrix_world


def shield(name, center, radius=.6):
    x,y,z=center
    g.cylinder(name+' brass rim',center,radius,.11,'Gold',64,(math.pi/2,0,0))
    g.cylinder(name+' enamel',(x,y-.07,z),radius*.92,.075,'Teal',64,(math.pi/2,0,0))
    g.star(name+' Neris star',(x,y-.12,z),radius*.7)
    g.cylinder(name+' boss',(x,y-.15,z),radius*.16,.15,'Gold',32,(math.pi/2,0,0))
    for i in range(12):
        t=i*math.tau/12
        g.cylinder(name+' rivet',(x+radius*.96*math.cos(t),y-.073,z+radius*.96*math.sin(t)),.024,.04,'Gold',12,(math.pi/2,0,0))


def cabinet(x,y,width=2.7):
    g.box('Fitted cabinet plinth',(x,y,.13),(width+.12,.84,.26),'DeepTeal')
    g.box('Walnut cabinet carcass',(x,y,.65),(width,.76,1.15),'Walnut',.04)
    g.box('Ivory display worktop',(x,y,1.24),(width+.17,.96,.13),'Ivory',.04)
    for dx in (-width/4,width/4):
        g.box('Teal inset door',(x+dx,y-.396,.67),(width/2-.10,.045,.86),'Teal')
        g.box('Brass door pull',(x+dx+.15,y-.448,.80),(.28,.065,.037),'Gold',.014)
    for dx in (-width/2+.08,width/2-.08):
        g.box('Cabinet corner trim',(x+dx,y-.41,.65),(.032,.03,1.0),'Gold',.007)


def display(x,y,label,weapons=3):
    cabinet(x,y)
    g.box('Recessed teal display backing',(x,y+.16,2.67),(2.55,.13,2.70),'DeepTeal',.09)
    arch('Ivory niche arch',x,y-.03,1.25,2.45,3.26,'Ivory',.11)
    arch('Gold niche reveal',x,y-.15,1.35,2.25,3.26,'Gold',.029)
    g.box('Floating weapon shelf',(x,y-.13,1.58),(2.3,.46,.09),'Walnut')
    g.text('Display title',label,(x,y-.26,3.87),.13)
    for i in range(weapons):
        dx=(i-(weapons-1)/2)*.61
        sword(label+' '+str(i+1),(x+dx,y-.23,1.64),1.62+(i%2)*.22,.095)
        for zz in (2.0,2.85):
            g.rod('Display bracket',(x+dx,y+.06,zz),(x+dx,y-.30,zz),.018,'Gold')


def counter():
    # Rounded, asymmetric sales desk: visitors approach from the open central aisle.
    g.box('Counter shadow plinth',(-1.1,3.72,.13),(6.5,1.60,.26),'DeepTeal',.13)
    g.box('Solid teal counter',(-1.1,3.72,.66),(6.30,1.44,1.12),'Teal',.16)
    g.box('Brass counter rim',(-1.1,3.72,1.245),(6.58,1.68,.06),'Gold',.17)
    g.box('Walnut counter top',(-1.1,3.72,1.33),(6.62,1.73,.12),'Walnut',.17)
    for x in (-3.45,-2.27,-1.1,.07,1.25):
        arch('Counter arched brass inlay',x,2.982,.27,.93,.79,'Gold',.014)
    g.star('Counter insignia',(-1.1,2.958,.71),.31)
    g.box('Leather transaction mat',(-1.05,3.42,1.397),(1.9,.70,.014),'Leather',.03)
    book=g.box('Open order ledger',(.50,3.64,1.455),(.47,.35,.085),'Linen',.006)
    book.rotation_euler.z=.18
    g.box('Ledger spine',(.50,3.64,1.51),(.022,.36,.02),'Gold',.005)
    for i in range(5):
        g.box('Ledger page line',(.41,3.53+i*.039,1.50),(.12,.007,.002),'Walnut',0)
    g.cylinder('Coin tray',(-2.6,3.35,1.415),.21,.035,'Gold',48)
    for i in range(5):
        g.cylinder('Coin',(-2.65+i*.023,3.36,1.45+i*.013),.05,.012,'Gold',24)
    g.cylinder('Counter stool foot',(-.8,4.96,.14),.39,.12,'Gold',32)
    g.cylinder('Counter stool stem',(-.8,4.96,.50),.07,.72,'Gold',20)
    g.cylinder('Counter stool cushion',(-.8,4.96,.91),.40,.13,'Leather',48)


def workshop():
    g.box('Workshop table',(5.64,4.77,.97),(3.35,1.15,.20),'Walnut',.055)
    for x in (4.26,7.0):
        for y in (4.35,5.20):
            g.box('Workshop leg',(x,y,.46),(.15,.15,.92),'Iron')
    g.box('Anvil base',(5.48,4.72,1.13),(.67,.40,.10),'Iron')
    g.box('Anvil waist',(5.48,4.72,1.32),(.38,.29,.28),'Iron',.08)
    g.box('Anvil face',(5.43,4.72,1.49),(.96,.37,.15),'Steel')
    g.mesh('Anvil horn',[(5.91,4.57,1.42),(5.91,4.87,1.42),(5.91,4.87,1.56),(5.91,4.57,1.56),(6.40,4.72,1.49)],[(0,3,2,1),(0,1,4),(1,2,4),(2,3,4),(3,0,4)],'Steel')
    g.rod('Hammer handle',(6.26,4.31,1.09),(6.79,4.80,1.09),.035,'Walnut')
    hammer=g.box('Forging hammer head',(6.8,4.82,1.13),(.30,.13,.15),'Steel')
    hammer.rotation_euler.z=.74
    for i in range(4):
        g.box('Steel stock',(4.30+i*.17,4.70,1.11),(.11,.54,.07),'Steel')
    g.box('Workshop tool panel',(5.6,6.59,2.52),(3.2,.14,1.74),'Walnut')
    for i in range(6):
        x=4.35+i*.46
        g.rod('Hanging tool',(x,6.43,2.07),(x,6.43,2.91),.036,'Iron')
        g.path('Tongs curved jaw',[(x-.1,6.43,3.15),(x-.12,6.43,2.97),(x,6.43,2.80),(x+.12,6.43,2.97),(x+.1,6.43,3.15)],.026,'Steel')
    g.text('Workshop name','THE ARMORER',(5.6,6.41,3.74),.21)


def furnish():
    g.collection('03 | Rear counter and sword gallery')
    counter()
    display(-5.45,6.29,'BLADES OF NERIS',3)
    display(0,6.29,'MASTERWORKS',2)
    shield('Garran crest',(-2.8,6.40,3.14),.64)
    g.text('Merchant name','GARRAN',(-2.8,6.30,4.12),.25)
    g.collection('04 | Armorer workshop')
    workshop()
    g.collection('05 | Freestanding hero display')
    for r,z,h,mat in ((1.2,.12,.24,'DeepTeal'),(1.10,.27,.07,'Gold'),(.94,.53,.5,'Ivory'),(.97,.81,.06,'Gold')):
        g.cylinder('Hero display pedestal',(0,-.42,z),r,h,mat,96)
    g.cylinder('Teal velvet display',(0,-.42,.859),.90,.025,'Teal',96)
    sword('Neris crystal greatsword',(0,-.42,.89),2.65,.18,0,'Crystal')
    g.rod('Greatsword rear rest',(0,-.16,.86),(0,-.16,2.85),.025,'Gold')
    g.box('Pedestal nameplate',(0,-1.34,.58),(.68,.055,.21),'DeepTeal',.02)
    g.text('Hero label','DAWNSTAR',(0,-1.38,.58),.10)
    g.collection('06 | Side weapon bays')
    for side in (-1,1):
        before=set(bpy.context.scene.objects)
        display(0,0,'FIELD ARMS' if side<0 else 'THE GUARD',2)
        transform=Matrix.Translation(Vector((side*7.24,-1.3,0))) @ Matrix.Rotation(side*-math.pi/2,4,'Z')
        for obj in set(bpy.context.scene.objects)-before:
            obj.matrix_world=transform @ obj.matrix_world
        before=set(bpy.context.scene.objects)
        cabinet(0,0,2.7)
        shield('Shield in bay',(-.62,-.05,2.32),.56)
        shield('Shield in bay',(.63,-.05,2.65),.65)
        transform=Matrix.Translation(Vector((side*7.24,2.0,0))) @ Matrix.Rotation(side*-math.pi/2,4,'Z')
        for obj in set(bpy.context.scene.objects)-before:
            obj.matrix_world=transform @ obj.matrix_world
