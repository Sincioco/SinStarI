"""Straighten the inherited sword grip in geometry, preserving topology and UVs."""
import math
import numpy as np
from mathutils import Matrix, Vector


def section_centers(points, edges, samples):
    centers = []
    for position in samples:
        hits = []
        for first, second in edges:
            a, b = points[first], points[second]
            if (a[0]-position)*(b[0]-position) < 0:
                hits.append(a+(b-a)*(position-a[0])/(b[0]-a[0]))
        if not hits:
            raise RuntimeError('Missing sword cross section')
        hits = np.array(hits)
        centers.append((hits.min(axis=0)+hits.max(axis=0))/2)
    return np.array(centers)


def line_fit(centers):
    slope, intercept = np.polyfit(centers[:, 0], centers[:, 1:], 1)
    return slope, intercept


def direction(slope):
    result = Vector((1, slope[0], slope[1]))
    return result.normalized()


def straighten_sword(obj):
    points = np.array([v.co[:] for v in obj.data.vertices], dtype=float)
    mean = points.mean(axis=0)
    _, _, axes = np.linalg.svd(points-mean, full_matrices=False)
    basis = axes.T
    # The original's tip is its low-Z endpoint; keep PCA sign deterministic.
    if basis[2, 0] < 0:
        basis[:, 0] *= -1
    coordinates = (points-mean) @ basis
    edges = [tuple(edge.vertices) for edge in obj.data.edges]
    blade_samples = np.linspace(-.32, -.09, 12)
    grip_samples = np.linspace(.022, .078, 12)
    blade_slope, blade_intercept = line_fit(section_centers(coordinates, edges, blade_samples))
    grip_slope, grip_intercept = line_fit(section_centers(coordinates, edges, grip_samples))
    before_angle = math.degrees(direction(blade_slope).angle(direction(grip_slope)))
    join = .012
    source_anchor = Vector((join, *(grip_slope*join+grip_intercept)))
    target_anchor = Vector((join, *(blade_slope*join+blade_intercept)))
    rotation = direction(grip_slope).rotation_difference(direction(blade_slope))
    corrected = coordinates.copy()
    for index, point in enumerate(coordinates):
        if point[0] <= -.010:
            continue
        blend = max(0, min(1, (point[0]+.010)/.024))
        blend = blend*blend*(3-2*blend)
        aligned = rotation @ (Vector(point)-source_anchor)+target_anchor
        corrected[index] = Vector(point).lerp(aligned, blend)
    after_slope, after_intercept = line_fit(section_centers(corrected, edges, grip_samples))
    # Re-measure the actual faceted, tapered surface after rotation, then remove
    # its small remaining centerline bias instead of loosening the acceptance.
    for _ in range(3):
        for point in corrected:
            blend = max(0, min(1, (point[0]+.010)/.024))
            blend = blend*blend*(3-2*blend)
            point[1:] += blend*((blade_slope-after_slope)*point[0]
                               + blade_intercept-after_intercept)
        after_slope, after_intercept = line_fit(section_centers(corrected, edges, grip_samples))
    after_angle = math.degrees(direction(blade_slope).angle(direction(after_slope)))
    if after_angle > .15:
        raise RuntimeError(f'Sword grip remains bent: {after_angle:.4f} degrees')
    unchanged_blade = np.max(np.abs(corrected[coordinates[:, 0] <= -.010]
                                    - coordinates[coordinates[:, 0] <= -.010]))
    if unchanged_blade != 0:
        raise RuntimeError('Straightening modified blade vertices')
    # Give the editable prop an upright blade and an origin at the handle center.
    grip_position = .050
    origin = mean + basis @ np.array((grip_position, *(blade_slope*grip_position+blade_intercept)))
    up = -(Vector(basis @ np.array(direction(blade_slope))))
    across = Vector(basis[:, 1])
    depth = up.cross(across).normalized()
    across = depth.cross(up).normalized()
    to_local = Matrix((across, depth, up))
    original_upright = []
    for index, vertex in enumerate(obj.data.vertices):
        original_upright.append(list(to_local @ (Vector(points[index])-Vector(origin))))
        world = mean + basis @ corrected[index]
        vertex.co = to_local @ (Vector(world)-Vector(origin))
    obj.data.update()
    report = {
        'repair': 'Rigid grip/pommel alignment with a short guard transition',
        'bladeHandleAngleBeforeDegrees': before_angle,
        'bladeHandleAngleAfterDegrees': after_angle,
        'bladeMaximumVertexChange': float(unchanged_blade),
        'maximumVertexDisplacement': float(np.linalg.norm(corrected-coordinates, axis=1).max()),
        'topologyAndUVsPreserved': True,
        'vertices': len(points),
    }
    return report, original_upright
