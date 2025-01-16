from pathlib import Path
from typing import TypedDict

import ipyreact
import numpy as np
import traitlets

# Ipyreact module defn
ipyreact.define_module("three", Path(__file__).parent / "js" / "build" / "three.esm.js")
ipyreact.define_module(
    "@react-three/fiber", Path(__file__).parent / "js" / "build" / "@react-three" / "fiber.esm.js"
)
ipyreact.define_module(
    "@react-three/drei", Path(__file__).parent / "js" / "build" / "@react-three" / "drei.esm.js"
)
ipyreact.define_module(
    "@react-three/xr", Path(__file__).parent / "js" / "build" / "@react-three" / "xr.esm.js"
)
ipyreact.define_module(
    "glue-xr-viewer", Path(__file__).parent / "js" / "build" / "glue-xr-viewer.esm.js"
)


class CoordinateArray(TypedDict):
    dataView: memoryview
    dtype: str
    shape: tuple


def array_to_binary(ar, obj=None, force_contiguous=True) -> CoordinateArray | None:
    if ar is None:
        return None
    if ar.dtype.kind not in ["u", "i", "f"]:  # ints and floats
        raise ValueError("unsupported dtype: %s" % (ar.dtype))
    if ar.dtype == np.float64:  # WebGL does not support float64, case it here
        ar = ar.astype(np.float32)
    if ar.dtype == np.int64:  # JS does not support int64
        ar = ar.astype(np.int32)
    if force_contiguous and not ar.flags["C_CONTIGUOUS"]:  # make sure it's contiguous
        ar = np.ascontiguousarray(ar)
    return {"dataView": memoryview(ar), "dtype": str(ar.dtype), "shape": ar.shape}


sar = array_to_binary


class Canvas(ipyreact.Widget):
    def __init__(self, props={}, events={}, children=[]):
        super().__init__(
            _module="@react-three/fiber",
            _type="Canvas",
            props=props,
            events=events,
            children=children,
        )


class OrbitControls(ipyreact.Widget):
    def __init__(self, props={}, events={}, children=[]):
        super().__init__(
            _module="@react-three/drei",
            _type="OrbitControls",
            props=props,
            events=events,
            children=children,
        )


class ConditionalOrbitControls(ipyreact.Widget):
    def __init__(self, props={}, events={}, children=[]):
        super().__init__(
            _module="glue-xr-viewer",
            _type="ConditionalOrbitControls",
            props=props,
            events=events,
            children=children,
        )


class DirectionalLight(ipyreact.Widget):
    def __init__(self, props={}, events={}, children=[]):
        # starts with a lower case, should be available globally, so we don't need to pass _module
        super().__init__(_type="directionalLight", props=props, events=events, children=children)


class AmbientLight(ipyreact.Widget):
    def __init__(self, props={}, events={}, children=[]):
        super().__init__(_type="ambientLight", props=props, events=events, children=children)


class Div(ipyreact.Widget):
    def __init__(self, style={}, props={}, events={}, children=[]):
        # we use a ipyreact based div to avoid an extra wrapper div which will affect layout
        super().__init__(
            _type="div", props={**props, **dict(style=style)}, children=children, events=events
        )


class XRStoreProvider(ipyreact.Widget):
    def __init__(self, children=[]):
        super().__init__(_module="glue-xr-viewer", _type="XRStoreProvider", children=children)


class XRStore(ipyreact.Widget):
    def __init__(self, children=[]):
        super().__init__(_module="glue-xr-viewer", _type="XRStore", children=children)


class XRWrapper(Div):
    def __init__(self, children=[], props={}):
        provider = XRStoreProvider(
            children=[
                ipyreact.Widget(_type="XRButtons", _module="glue-xr-viewer"),
                Canvas(events={"onClick": lambda *_ignore: None}, children=children),
            ]
        )
        super().__init__(
            style={"height": "1024px", "flexGrow": 1}, children=[provider], props=props
        )


class XRViewer(XRWrapper):
    def __init__(self, layers=[], on_selection=lambda *_ignore: None):
        """
        Parameters
        ----------
        layers : solara.Reactive[list[solara.Element]]
            The list of layers to display
        on_hull : Callable
            The function to call when a hull is selected
        """
        self.layers = layers

        orbit_controls = ConditionalOrbitControls()
        directional_light = DirectionalLight(
            props=dict(color="#ffffff", intensity=12, position=[-1, 2, 4])
        )
        ambient_light = AmbientLight(props=dict(color="#ffffff", intensity=0.5))
        hand_selection = ipyreact.Widget(
            _type="HandSelection", _module="glue-xr-viewer", events={"onHull": on_selection}
        )

        self.children_wrapper = XRStore(
            children=[
                orbit_controls,
                directional_light,
                ambient_light,
                hand_selection,
                *self.layers,
            ]
        )

        super().__init__(children=[self.children_wrapper])

    def redraw(self):
        for layer in self.layers:
            layer.redraw()

    def add_layer(self, layer):
        self.layers += [layer]
        self.children_wrapper.children = [*self.children_wrapper.children, layer]


class MeshPhongMaterial(ipyreact.Widget):
    color = traitlets.Unicode("#f56f42").tag(sync=True)
    opacity = traitlets.Float(1.0).tag(sync=True)

    def __init__(self, children=[]):
        super().__init__(
            _type="meshPhongMaterial",
            props=dict(color=self.color, opacity=self.opacity, transparent=True),
            children=children,
        )


class DodecahedronGeometry(ipyreact.Widget):
    args = traitlets.List([1.0, 0]).tag(sync=True)

    def __init__(self, children=[]):
        super().__init__(
            _type="dodecahedronGeometry", props=dict(args=self.args), children=children
        )


class XRScatterLayer(ipyreact.Widget):
    limit = traitlets.Int(0).tag(sync=True)
    x = traitlets.Any([]).tag(sync=True)
    y = traitlets.Any([]).tag(sync=True)
    z = traitlets.Any([]).tag(sync=True)

    opacity = traitlets.Float(1.0).tag(sync=True)
    color = traitlets.Unicode("#f56f42").tag(sync=True)
    size = traitlets.Float(1.0).tag(sync=True)
    model_scaling_factor = traitlets.Float(1.0).tag(sync=True)

    data = traitlets.Dict({})

    def __init__(self, props={}, events={}):
        self.color = "#f56f42"
        self.number = 0

        self.material = MeshPhongMaterial()
        self.point = DodecahedronGeometry()

        super().__init__(
            _module="glue-xr-viewer",
            _type="CustomInstancedMesh",
            props={
                **props,
                **dict(
                    limit=self.limit,
                    x=self.x,
                    y=self.y,
                    z=self.z,
                    model_scaling_factor=self.model_scaling_factor,
                ),
            },
            children=[self.point, self.material],
            events=events,
        )

        self.redraw()

    def _update_color(self):
        self.material.color = self.color

    def _update_opacity(self):
        self.material.opacity = self.opacity

    def _update_size(self):
        self.point.args = [self.size, 0]

    def redraw(self, *args):
        if len(self.data) != 0:
            self.limit = len(self.data["x"])
            self.x = sar(self.data["x"])
            self.y = sar(self.data["y"])
            self.z = sar(self.data["z"])

        self._update_opacity()
        self._update_color()
        self._update_size()
