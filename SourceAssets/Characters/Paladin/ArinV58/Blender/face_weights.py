"""Repair v5.8 facial skin ownership without changing geometry or animation."""


def smooth(value):
    value = max(0.0, min(1.0, value))
    return value*value*(3.0-2.0*value)


def repair_face_weights(objects):
    report = {'changedVertices':0, 'faceVerticesRigidToHead':0,
              'maximumRestPositionChange':0.0, 'removedFaceInfluences':{},
              'neckBlendStartZ':.805, 'rigidFaceStartZ':.852}
    # These are the inspected new source's face/neck, hair, eyes and mouth.
    for obj in objects:
        part = obj.name.removeprefix('ArinV58.')
        if part not in ('tripo_part_12','tripo_part_1','tripo_part_29',
                        'tripo_part_30','tripo_part_45'):
            continue
        groups = {name:obj.vertex_groups.get(name) or obj.vertex_groups.new(name=name)
                  for name in ('mixamorig:Head','mixamorig:Neck','mixamorig:Spine2')}
        for vertex in obj.data.vertices:
            z = vertex.co.z
            if part != 'tripo_part_12' or z >= .852:
                weights = {'mixamorig:Head':1.0}
                report['faceVerticesRigidToHead'] += 1
                for link in vertex.groups:
                    name = obj.vertex_groups[link.group].name
                    if name != 'mixamorig:Head' and link.weight > .00001:
                        counts = report['removedFaceInfluences']
                        counts[name] = counts.get(name,0)+1
            elif z >= .823:
                head = smooth((z-.823)/(.852-.823))
                weights = {'mixamorig:Head':head,'mixamorig:Neck':1-head}
            else:
                neck = smooth((z-.805)/(.823-.805))
                weights = {'mixamorig:Neck':neck,'mixamorig:Spine2':1-neck}
            for link in list(vertex.groups):
                obj.vertex_groups[link.group].remove([vertex.index])
            for name, weight in weights.items():
                if weight > 0:
                    groups[name].add([vertex.index],weight,'REPLACE')
            report['changedVertices'] += 1
    return report
