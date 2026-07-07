# GL-3DPRT workspace checker for Rhino Grasshopper GhPython.
# Paste this whole file into a GhPython component.
#
# Suggested inputs:
#   device: "SP-M" or "SP-S"
#   L, W, H: box dimensions in mm
#   Y: inner-side Y position in mm
#   X: optional, defaults to 0
#   Z: optional, defaults to 0
#   yaw: optional, defaults to 360
#   makeWorkspace: optional bool, defaults to True
#   stlMesh: optional Rhino.Geometry.Mesh
#   showIntersection: optional bool, defaults to False
#
# Suggested outputs:
#   inside, message, workspaceMesh, boxBrep, intersectionCurves, invalidPoints, debug

import math

try:
    import Rhino.Geometry as rg
except Exception:
    rg = None


def ensure_ghpython_ports():
    """Keep existing RhinoCode/GhPython ports optional without creating incompatible ports.

    Rhino 8's Script Editor component uses RhinoCode-specific ScriptVariableParam
    objects. Registering normal Grasshopper Param_GenericObject inputs/outputs can
    make the component throw a cast exception before the script can run.
    """
    if "ghenv" not in globals():
        return

    comp = ghenv.Component
    changed = False

    def names(params):
        return [str(p.NickName) for p in params]

    optional_inputs = set(["X", "Z", "yaw", "makeWorkspace", "stlMesh", "showIntersection"])

    for p in comp.Params.Input:
        if str(p.NickName) == "u" and "yaw" not in names(comp.Params.Input):
            p.Name = "yaw"
            p.NickName = "yaw"
            changed = True
        if str(p.NickName) in optional_inputs and not p.Optional:
            p.Optional = True
            changed = True

    if changed:
        comp.Params.OnParametersChanged()


ensure_ghpython_ports()


DEVICE_DATA = {
    "SP-M": {
        "innerCircleY": -1118.0,
        "outerRadius": 10187.0,
        "innerRadius": 3115.5,
        "maxReachZ": 9602.0,
        "defaultY": 1998.0,
        "defaultL": 2000.0,
        "defaultW": 2000.0,
        "defaultH": 2000.0,
        "rz": [
            (1600, 0), (10187, 0), (10129, 1467), (9904, 3075),
            (9416, 4651), (8700, 6009), (7598, 7492), (6809, 8442),
            (6192, 9175), (5861, 9472), (5549, 9602), (5400, 9565),
            (5149, 9175), (4970, 8325), (4850, 7561), (4642, 6802),
            (3677, 6097), (2716, 5911), (1600, 5872)
        ]
    },
    "SP-S": {
        "innerCircleY": -786.0,
        "outerRadius": 7429.0,
        "innerRadius": 3407.5,
        "maxReachZ": 7400.0,
        "defaultY": 2622.0,
        "defaultL": 1200.0,
        "defaultW": 1200.0,
        "defaultH": 1200.0,
        "rz": [
            (1771, 0), (1771, 4728), (1820, 4778), (2029, 4868),
            (2203, 4999), (2326, 5109), (2487, 5274), (2607, 5412),
            (2722, 5559), (2824, 5703), (2934, 5877), (3032, 6054),
            (3106, 6203), (3174, 6357), (3229, 6496), (3275, 6627),
            (3332, 6804), (3387, 6993), (3437, 7162), (3504, 7342),
            (3562, 7429), (3629, 7469), (3728, 7480), (3832, 7401),
            (3907, 7346), (4005, 7264), (4076, 7200), (4153, 7119),
            (4229, 7061), (4333, 6964), (4496, 6818), (4638, 6694),
            (4785, 6568), (4937, 6438), (5089, 6304), (5229, 6173),
            (5384, 6015), (5504, 5884), (5665, 5694), (5808, 5510),
            (5956, 5306), (6083, 5118), (6194, 4945), (6304, 4763),
            (6429, 4547), (6533, 4353), (6638, 4148), (6751, 3907),
            (6857, 3664), (6945, 3442), (7018, 3239), (7101, 2983),
            (7229, 2505), (7308, 2108), (7373, 1658), (7410, 1273),
            (7438, 444), (7429, 0)
        ]
    }
}


def gh_value(name, default_value):
    return globals()[name] if name in globals() and globals()[name] is not None else default_value


def first_value(value):
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        if len(value) == 0:
            return None
        return first_value(value[0])
    return value


def as_float(value, default_value):
    value = first_value(value)
    if value is None:
        return float(default_value)
    return float(value)


def as_bool(value, default_value):
    value = first_value(value)
    if value is None:
        return default_value
    if isinstance(value, str):
        text = value.strip().lower()
        if text in ("false", "f", "0", "no", "n", "off", ""):
            return False
        if text in ("true", "t", "1", "yes", "y", "on"):
            return True
    return bool(value)


def clamp(value, low, high):
    return max(low, min(high, value))


def catmull_rom(p0, p1, p2, p3, t):
    t2 = t * t
    t3 = t2 * t
    return 0.5 * (
        2 * p1
        + (-p0 + p2) * t
        + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
        + (-p0 + 3 * p1 - 3 * p2 + p3) * t3
    )


def smooth_closed_profile(points, samples_per_segment, max_z):
    smooth = []
    count = len(points)
    for i in range(count):
        p0 = points[(i - 1 + count) % count]
        a = points[i]
        b = points[(i + 1) % count]
        p3 = points[(i + 2) % count]
        for j in range(samples_per_segment):
            t = float(j) / float(samples_per_segment)
            r = catmull_rom(p0[0], a[0], b[0], p3[0], t)
            z = catmull_rom(p0[1], a[1], b[1], p3[1], t)
            r = clamp(r, min(a[0], b[0]) - 120.0, max(a[0], b[0]) + 120.0)
            z = clamp(z, min(a[1], b[1]) - 120.0, max(a[1], b[1]) + 120.0)
            smooth.append((r, min(z, max_z)))
    return smooth


def device_key(value):
    text = str(value or "SP-M").upper().replace("GL-3DPRT-", "").strip()
    if text in ("M", "SPM", "SP-M"):
        return "SP-M"
    if text in ("S", "SPS", "SP-S"):
        return "SP-S"
    return "SP-M"


class WorkspaceModel(object):
    def __init__(self, key):
        self.key = key
        self.data = DEVICE_DATA[key]
        self.inner_y = self.data["innerCircleY"]
        self.outer_r = self.data["outerRadius"]
        self.inner_r = self.data["innerRadius"]
        self.profile = smooth_closed_profile(self.data["rz"], 10, self.data["maxReachZ"])
        self.min_r = min([p[0] for p in self.profile])
        self.max_r = max([p[0] for p in self.profile])
        self.min_z = min([p[1] for p in self.profile])
        self.max_z = max([p[1] for p in self.profile])

    def largest_rz_interval_at_z(self, z):
        clamped_z = clamp(z, self.min_z + 0.001, self.max_z - 0.001)
        crossings = []
        count = len(self.profile)
        for i in range(count):
            a = self.profile[i]
            b = self.profile[(i + 1) % count]
            if (a[1] <= clamped_z and b[1] > clamped_z) or (b[1] <= clamped_z and a[1] > clamped_z):
                t = (clamped_z - a[1]) / (b[1] - a[1])
                crossings.append(a[0] + (b[0] - a[0]) * t)
        crossings.sort()
        unique = []
        for r in crossings:
            if len(unique) == 0 or abs(r - unique[-1]) > 0.5:
                unique.append(r)
        best = None
        for i in range(0, len(unique) - 1, 2):
            interval = (unique[i], unique[i + 1])
            if best is None or interval[1] - interval[0] > best[1] - best[0]:
                best = interval
        return best

    def radial_range_at_yaw(self, yaw_rad):
        s = math.sin(yaw_rad)
        c = math.cos(yaw_rad)
        cy = self.inner_y
        discriminant = self.inner_r * self.inner_r - cy * cy * c * c
        forbidden_exit = self.min_r if discriminant < 0 else cy * s + math.sqrt(discriminant)
        min_r = max(self.min_r, forbidden_exit)
        max_r = min(self.outer_r, self.max_r)
        return (min(min_r, max_r), max(min_r, max_r))

    def radial_range_at_yaw_z(self, yaw_rad, z):
        xy = self.radial_range_at_yaw(yaw_rad)
        rz = self.largest_rz_interval_at_z(z)
        if rz is None:
            return (0.0, 0.0)
        min_r = max(xy[0], rz[0])
        max_r = min(xy[1], rz[1])
        if min_r <= max_r:
            return (min_r, max_r)
        mid = (min_r + max_r) * 0.5
        return (mid, mid)

    def point_inside(self, p, yaw_deg=360.0):
        dx = p.X
        dy = p.Y
        radius = math.sqrt(dx * dx + dy * dy)
        yaw = math.degrees(math.atan2(dy, dx))
        yaw_limit = yaw_deg * 0.5
        outer_distance = radius
        inner_distance = math.sqrt(dx * dx + (dy - self.inner_y) * (dy - self.inner_y))
        rz_inside = self.rz_point_inside(radius, p.Z)
        return (
            outer_distance <= self.outer_r + 0.001
            and inner_distance >= self.inner_r - 0.001
            and abs(yaw) <= yaw_limit + 0.001
            and rz_inside
        )

    def rz_point_inside(self, r, z):
        inside = False
        count = len(self.profile)
        for i in range(count):
            a = self.profile[i]
            b = self.profile[(i - 1 + count) % count]
            if ((a[1] > z) != (b[1] > z)) and r < ((b[0] - a[0]) * (z - a[1])) / (b[1] - a[1]) + a[0]:
                inside = not inside
        return inside


def y_bounds(y, width):
    if y < 0:
        return (y - width, y)
    return (y, y + width)


def box_corners(x, y, z, l, w, h):
    y0, y1 = y_bounds(y, w)
    xs = [x - l * 0.5, x + l * 0.5]
    ys = [y0, y1]
    zs = [z, z + h]
    pts = []
    for px in xs:
        for py in ys:
            for pz in zs:
                pts.append(rg.Point3d(px, py, pz))
    return pts


def sample_range(a, b, count):
    if count <= 1:
        return [(a + b) * 0.5]
    return [a + (b - a) * float(i) / float(count - 1) for i in range(count)]


def box_sample_points(x, y, z, l, w, h):
    y0, y1 = y_bounds(y, w)
    xs = sample_range(x - l * 0.5, x + l * 0.5, 7)
    ys = sample_range(y0, y1, 7)
    zs = sample_range(z, z + h, 7)
    pts = []
    for px in xs:
        for py in ys:
            pts.append(rg.Point3d(px, py, z))
            pts.append(rg.Point3d(px, py, z + h))
    for pz in zs:
        for px in xs:
            pts.append(rg.Point3d(px, y0, pz))
            pts.append(rg.Point3d(px, y1, pz))
        for py in ys:
            pts.append(rg.Point3d(x - l * 0.5, py, pz))
            pts.append(rg.Point3d(x + l * 0.5, py, pz))
    return pts


def forbidden_cylinder_intersects(model, x, y, l, w):
    x0 = x - l * 0.5
    x1 = x + l * 0.5
    y0, y1 = y_bounds(y, w)
    closest_x = clamp(0.0, x0, x1)
    closest_y = clamp(model.inner_y, y0, y1)
    distance = math.sqrt(closest_x * closest_x + (closest_y - model.inner_y) * (closest_y - model.inner_y))
    return distance < model.inner_r - 0.001


def check_box(model, x, y, z, l, w, h, yaw_deg):
    invalid = []
    corners = box_corners(x, y, z, l, w, h)
    valid_corners = 0
    for p in corners:
        if model.point_inside(p, yaw_deg):
            valid_corners += 1
        else:
            invalid.append(p)
    invalid_samples = 0
    for p in box_sample_points(x, y, z, l, w, h):
        if not model.point_inside(p, yaw_deg):
            invalid_samples += 1
            if len(invalid) < 80:
                invalid.append(p)
    cyl = forbidden_cylinder_intersects(model, x, y, l, w)
    is_inside = valid_corners == 8 and invalid_samples == 0 and not cyl
    if is_inside:
        msg = "长方体在范围内。"
    elif cyl:
        msg = "长方体与内圆不可达区域相交。"
    elif invalid_samples > 0:
        msg = "长方体超出 R-Z 截面或 X-Y 可达区域。"
    else:
        msg = "有 {0} 个角点超出可达空间。".format(8 - valid_corners)
    return is_inside, msg, invalid


def make_box_brep(x, y, z, l, w, h):
    y0, y1 = y_bounds(y, w)
    box = rg.Box(rg.Plane.WorldXY, rg.Interval(x - l * 0.5, x + l * 0.5), rg.Interval(y0, y1), rg.Interval(z, z + h))
    return box.ToBrep()


def make_workspace_mesh(model, yaw_deg):
    yaw_half = math.radians(yaw_deg * 0.5)
    yaw_steps = max(96, int(math.ceil(yaw_deg / 2.0)))
    z_steps = 72
    rows = z_steps + 1
    mesh = rg.Mesh()

    for i in range(yaw_steps + 1):
        yaw_rad = -yaw_half + (2.0 * yaw_half * i) / float(yaw_steps)
        for j in range(z_steps + 1):
            z = model.min_z + (model.max_z - model.min_z) * float(j) / float(z_steps)
            rr = model.radial_range_at_yaw_z(yaw_rad, z)
            r = rr[1]
            mesh.Vertices.Add(math.cos(yaw_rad) * r, math.sin(yaw_rad) * r, z)

    inner_offset = (yaw_steps + 1) * rows
    for i in range(yaw_steps + 1):
        yaw_rad = -yaw_half + (2.0 * yaw_half * i) / float(yaw_steps)
        for j in range(z_steps + 1):
            z = model.min_z + (model.max_z - model.min_z) * float(j) / float(z_steps)
            rr = model.radial_range_at_yaw_z(yaw_rad, z)
            r = rr[0]
            mesh.Vertices.Add(math.cos(yaw_rad) * r, math.sin(yaw_rad) * r, z)

    for i in range(yaw_steps):
        for j in range(1, z_steps):
            a = i * rows + j
            b = (i + 1) * rows + j
            c = (i + 1) * rows + j + 1
            d = i * rows + j + 1
            mesh.Faces.AddFace(a, b, d)
            mesh.Faces.AddFace(b, c, d)
            ai = inner_offset + a
            bi = inner_offset + b
            ci = inner_offset + c
            di = inner_offset + d
            mesh.Faces.AddFace(ai, di, bi)
            mesh.Faces.AddFace(bi, di, ci)

    mesh.Normals.ComputeNormals()
    mesh.Compact()
    return mesh


def mesh_point(mesh, index):
    v = mesh.Vertices[index]
    return rg.Point3d(v.X, v.Y, v.Z)


def edge_crossing(model, a, b, yaw_deg):
    a_inside = model.point_inside(a, yaw_deg)
    b_inside = model.point_inside(b, yaw_deg)
    if a_inside == b_inside:
        return None
    lo = rg.Point3d(a)
    hi = rg.Point3d(b)
    lo_inside = a_inside
    for _ in range(6):
        mid = rg.Point3d((lo.X + hi.X) * 0.5, (lo.Y + hi.Y) * 0.5, (lo.Z + hi.Z) * 0.5)
        mid_inside = model.point_inside(mid, yaw_deg)
        if mid_inside == lo_inside:
            lo = mid
            lo_inside = mid_inside
        else:
            hi = mid
    return rg.Point3d((lo.X + hi.X) * 0.5, (lo.Y + hi.Y) * 0.5, (lo.Z + hi.Z) * 0.5)


def stl_intersection_curves(model, mesh, yaw_deg, max_faces=3000):
    curves = []
    mesh = first_value(mesh)
    if mesh is None or not hasattr(mesh, "Faces"):
        return curves
    face_count = mesh.Faces.Count
    if face_count <= 0:
        return curves
    step = max(1, int(math.ceil(float(face_count) / float(max_faces))))
    for i in range(0, face_count, step):
        face = mesh.Faces[i]
        tris = []
        if face.IsTriangle:
            tris.append((face.A, face.B, face.C))
        else:
            tris.append((face.A, face.B, face.C))
            tris.append((face.A, face.C, face.D))
        for tri in tris:
            a = mesh_point(mesh, tri[0])
            b = mesh_point(mesh, tri[1])
            c = mesh_point(mesh, tri[2])
            pts = []
            for pair in ((a, b), (b, c), (c, a)):
                p = edge_crossing(model, pair[0], pair[1], yaw_deg)
                if p is not None:
                    pts.append(p)
            if len(pts) >= 2:
                curves.append(rg.LineCurve(pts[0], pts[1]))
    return curves


if rg is None:
    inside = False
    message = "Rhino.Geometry is not available. Paste this script into Rhino Grasshopper GhPython."
    workspaceMesh = None
    boxBrep = None
    intersectionCurves = []
    invalidPoints = []
    debug = message
else:
    key = device_key(gh_value("device", "SP-M"))
    model = WorkspaceModel(key)
    x_value = as_float(gh_value("X", 0.0), 0.0)
    y_value = as_float(gh_value("Y", model.data["defaultY"]), model.data["defaultY"])
    z_value = as_float(gh_value("Z", 0.0), 0.0)
    l_value = as_float(gh_value("L", model.data["defaultL"]), model.data["defaultL"])
    w_value = as_float(gh_value("W", model.data["defaultW"]), model.data["defaultW"])
    h_value = as_float(gh_value("H", model.data["defaultH"]), model.data["defaultH"])
    yaw_value = as_float(gh_value("yaw", 360.0), 360.0)
    make_ws = as_bool(gh_value("makeWorkspace", True), True)
    show_x = as_bool(gh_value("showIntersection", False), False)
    mesh_input = first_value(gh_value("stlMesh", None))

    inside, message, invalidPoints = check_box(model, x_value, y_value, z_value, l_value, w_value, h_value, yaw_value)
    workspaceMesh = make_workspace_mesh(model, yaw_value) if make_ws else None
    boxBrep = make_box_brep(x_value, y_value, z_value, l_value, w_value, h_value)
    intersectionCurves = stl_intersection_curves(model, mesh_input, yaw_value) if show_x and mesh_input is not None else []
    debug = "{0}: {1}, invalid points: {2}, intersection segments: {3}".format(
        key, message, len(invalidPoints), len(intersectionCurves)
    )

# Compatibility for the default Grasshopper Python component outputs.
# If the component only has `out` and `a`, `out` carries the message and `a`
# carries a compact geometry package: workspace, box, intersections, invalid points.
out = debug if "debug" in globals() else message
a = [workspaceMesh, boxBrep, intersectionCurves, invalidPoints]
