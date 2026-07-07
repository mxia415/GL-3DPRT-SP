# Grasshopper 使用例子

这个例子用于判断一个 `2000 x 2000 x 2000 mm` 的长方体是否在 GL-3DPRT-SP-M 的运动范围内。

## 1. 基础判定

在 Grasshopper 里，新建或使用已经放好的 `GhPython` 组件，把 `GL_3DPRT_workspace_ghpython.py` 全部粘贴进去并保存。

如果出现类似下面的红色错误：

```text
Unable to cast object of type 'Grasshopper.Kernel.Parameters.Param_GenericObject'
to type 'RhinoCodePluginGH.Parameters.ScriptVariableParam'
```

说明这个组件的端口类型已经被旧版自动建端口脚本污染了。删除这个 Python 组件，重新放一个干净的 Python 3 组件，然后用组件自己的输入/输出管理添加端口，不要复用这个报错组件。

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
showIntersection  Boolean Toggle: False
stlMesh           不接
```

`makeWorkspace`、`stlMesh`、`showIntersection` 在新版脚本里会被标记为 Optional。不过第一次粘贴脚本时，Grasshopper 可能会先在脚本执行前提示 `failed to collect data`。如果出现这个提示，先给 `showIntersection` 接一个 `Boolean Toggle: False`，组件运行一次后 Optional 设置就会生效。

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
5. 先保持 `showIntersection = False`，确认基础判定和 `workspaceMesh` 能正常显示。
6. 需要交线时，再把 `showIntersection` 改成 `True`。
7. 把 `intersectionCurves` 接到 `Curve` 参数或 `Custom Preview`。

注意：`intersectionCurves` 是 STL 网格和运动范围边界的近似交线，适合观察和判断，不是 Rhino Boolean 精确交线。脚本会对 STL 面进行抽样，避免大 STL 直接卡死 Grasshopper。
