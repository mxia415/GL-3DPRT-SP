# Grasshopper 使用例子

这个例子用于判断一个 `2000 x 2000 x 2000 mm` 的长方体是否在 GL-3DPRT-SP-M 的运动范围内。

## 1. 基础判定

在 Grasshopper 里，新建或使用已经放好的 `GhPython` 组件，把 `GL_3DPRT_workspace_ghpython.py` 全部粘贴进去并保存。

给组件输入端口连接这些值：

```text
device            Panel: SP-M
L                 Panel 或 Number Slider: 2000
W                 Panel 或 Number Slider: 2000
H                 Panel 或 Number Slider: 2000
Y                 Panel 或 Number Slider: 1998
X                 Panel 或 Number Slider: 0
Z                 Panel 或 Number Slider: 0
yaw               Panel 或 Number Slider: 360
makeWorkspace     Boolean Toggle: True
showIntersection  不接，或 Boolean Toggle: False
stlMesh           不接
```

`makeWorkspace`、`stlMesh`、`showIntersection` 是可选输入。新版脚本会把它们标记为 Optional，所以不接线时不应该出现 “failed to collect data” 警告。

建议先把这三个输出接到 `Panel`：

```text
inside
message
debug
```

预期结果：

```text
inside  True
message 长方体在范围内。
```

如果把 `Y` 改小，例如改成 `1500`，长方体更靠近内侧不可达圆，通常会输出不可达提示。

## 2. 显示几何

把这些输出接到 Grasshopper 的预览组件或参数：

```text
workspaceMesh  接 Mesh 参数或 Custom Preview
boxBrep        接 Brep 参数或 Custom Preview
invalidPoints  接 Point 参数
```

这样可以同时看到运动范围 Mesh、当前长方体和超出范围的采样点。

## 3. STL 交线

1. 在 Rhino 里导入 STL。
2. 在 Grasshopper 里放一个 `Mesh` 参数。
3. 右键 `Mesh` 参数，选择 `Set one Mesh`，点选导入的 STL。
4. 把这个 `Mesh` 参数接到 `stlMesh`。
5. 把 `showIntersection` 接一个 `Boolean Toggle: True`。
6. 把 `intersectionCurves` 接到 `Curve` 参数或 `Custom Preview`。

注意：`intersectionCurves` 是 STL 网格和运动范围边界的近似交线，适合观察和判断，不是 Rhino Boolean 精确交线。
