import numpy as np
from glue.core.data import Subset
from glue.core.exceptions import IncompatibleAttribute
from glue.utils import color2hex, ensure_numerical
from glue.viewers.common.layer_artist import LayerArtist
from glue.viewers.scatter.state import ScatterLayerState
from glue_jupyter.link import on_change

from .components import XRScatterLayer


class XRLayerArtist(LayerArtist):
    _layer_state_cls = ScatterLayerState

    def __init__(self, view, viewer_state, layer_state=None, layer=None):
        super(XRLayerArtist, self).__init__(viewer_state, layer_state=layer_state, layer=layer)
        self.state.alpha = 1.0

        self.view = view

        self.scatter = XRScatterLayer()

        self.view.add_scatter(self.scatter)

        on_change(
            [(self.state, "cmap_mode", "cmap_att", "cmap_vmin", "cmap_vmax", "cmap", "color")]
        )(self._update_color)
        on_change([(self.state, "size", "size_scaling", "size_mode", "size_vmin", "size_vmax")])(
            self._update_size
        )

        viewer_state.add_callback("x_att", self._update_xyz_att)
        viewer_state.add_callback("y_att", self._update_xyz_att)
        viewer_state.add_callback("z_att", self._update_xyz_att)
        self._update_color()

        self.state.add_callback("visible", self._update_visibility)
        self.state.add_callback("alpha", self._update_opacity)
        self._viewer_state.add_callback("model_scaling_factor", self._update_scaling_factor)
        self._update_scaling_factor(self._viewer_state.model_scaling_factor)

    def _update_color(self, ignore=None):
        cmap = self.state.cmap
        if self.state.cmap_mode == "Linear":
            values = self.layer.data[self.state.cmap_att].astype(np.float32).ravel()
            normalized_values = (values - self.state.cmap_vmin) / (
                self.state.cmap_vmax - self.state.cmap_vmin
            )
            color_values = cmap(normalized_values).astype(np.float32)
            self.scatter.color = color_values
        else:
            self.scatter.color = color2hex(self.state.color)
        self.update()

    def _update_opacity(self, value):
        self.scatter.opacity = value
        self.scatter.redraw()

    def _update_visibility(self, visible):
        self._update_opacity(self.state.alpha if visible else 0.0)

    def _update_xyz_att(self, *args):
        self.update()

    def _cast_to_float(self, arr):
        if np.issubdtype(arr.dtype, np.floating):
            return arr

        # `itemsize` returns the byte size of the dtype
        size = 8 * arr.dtype.itemsize
        return arr.astype(f"float{size}")

    def redraw(self):
        pass

    def update(self):
        data = self._get_data_to_draw()

        if isinstance(self.layer, Subset):
            try:
                mask = self.layer.to_mask()
            except IncompatibleAttribute:
                self.disable("Could not compute subset")
                self._clear_selection()
                return

            selected_indices = np.nonzero(mask)[0]

            self.scatter.selected = selected_indices

        self.scatter.data = data
        self._update_size()

    def _clear_selection(self):
        self.scatter.selected = np.array([])

    def _update_size(self):
        size = self.state.size
        scale = self.state.size_scaling
        if self.state.size_mode == "Linear":
            size = self.layer.data[self.state.size_att].ravel()
            size = (size - self.state.size_vmin) / (self.state.size_vmax - self.state.size_vmin)
            size *= 5
        value = size * scale
        if isinstance(self.layer, Subset):
            # TODO: figure out a solution - threejs dodecahedron radius starts at one
            self.scatter.size = 1.15 * (1 + value)
            self.scatter.size_selected = value
        else:
            self.scatter.size = 1 + value
            self.scatter.size_selected = value

        value = self.state.size * scale * 5
        self.scatter.redraw()

    def _update_scaling_factor(self, value):
        self.scatter.model_scaling_factor = value

    def _get_data_to_draw(self):
        data = {}
        # we don't use layer, but layer.data to get everything
        data["z"] = self._cast_to_float(
            ensure_numerical(self.layer.data[self._viewer_state.x_att]).ravel()
        )
        data["y"] = self._cast_to_float(
            ensure_numerical(self.layer.data[self._viewer_state.z_att]).ravel()
        )
        data["x"] = self._cast_to_float(
            ensure_numerical(self.layer.data[self._viewer_state.y_att]).ravel()
        )

        if isinstance(self.layer, Subset):
            # Trim away unselected data
            selected_indices = self.layer.to_index_list()

            for key in data.keys():
                data[key] = data[key][selected_indices]

        return data
