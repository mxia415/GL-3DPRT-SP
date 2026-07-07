# GL-3DPRT Grasshopper 脚本说明

文件：

```text
grasshopper/GL_3DPRT_workspace_ghpython.py
```

## 用法

1. 在 Rhino 里打开 Grasshopper。
2. 新建一个 `GhPython` 组件。
3. 把 `GL_3DPRT_workspace_ghpython.py` 的全部代码粘贴进去。
4. 运行一次脚本，组件会自动添加下面的建议输入和建议输出端口。

如果组件原来有默认输入 `u`，脚本会把它改名为 `yaw`。默认输出 `out` 和 `a` 会保留，便于兼容旧组件。

## 建议输入

```text
device            文本，"SP-M" 或 "SP-S"
L                 长方体 X 方向长度，mm
W                 长方体 Y 方向宽度，mm
H                 长方体 Z 方向高度，mm
Y                 Y 向内侧边位置，mm
X                 可选，默认 0
Z                 可选，默认 0
yaw               可选，默认 360
makeWorkspace     可选，布尔值，是否输出运动范围 Mesh
stlMesh           可选，Rhino Mesh，用于计算近似交线
showIntersection  可选，布尔值，是否输出 STL 与运动范围近似交线
```

## 建议输出

```text
inside              是否在运动范围内
message             中文判定提示
workspaceMesh       运动范围 Mesh
boxBrep             当前长方体 Brep
intersectionCurves  STL 与运动范围边界的近似交线
invalidPoints       不可达采样点
debug               调试信息
```

如果你使用默认的 GhPython 输出端口 `out` 和 `a`，脚本也能直接工作：

```text
out  调试/判定文本
a    几何列表：[workspaceMesh, boxBrep, intersectionCurves, invalidPoints]
```

## 说明

- 判定逻辑来自网页工具的 `X-Y 平面范围 + R-Z 垂直截面范围` 交集。
- `stlMesh` 只用于近似交线计算，不参与长方体可达判定。
- 近似交线通过 STL 三角面边上“范围内/范围外”变化的位置生成，不是 CAD 布尔精确交线。
- 单位按 `mm` 处理。
- 如果 Grasshopper 卡顿，可以先把 `makeWorkspace` 或 `showIntersection` 设为 `False`。
