import numpy as np
from glue.core.command import ApplySubsetState
from glue.core.subset import RoiSubsetState3d
from glue_jupyter.view import IPyWidgetView

from .components import XRViewer
from .layer_artist import XRLayerArtist
from .roi import ConvexHullROI
from .viewer_state import XRScatter3DViewerState
from .widgets import XRLayerStateWidget, XRStateWidget

__all__ = ["XRBaseView"]


# TODO: Looks like unsupported data format will make the viewer not work, without being able to recover it
#       by selecting the right data.
class XRBaseView(IPyWidgetView):
    allow_duplicate_data = False
    allow_duplicate_subset = False

    _state_cls = XRScatter3DViewerState
    _options_cls = XRStateWidget
    _data_artist_cls = XRLayerArtist
    _subset_artist_cls = XRLayerArtist
    _layer_style_widget_cls = XRLayerStateWidget

    tools: list[str] = []  # TODO: make selecting "xr:lasso" work

    def __init__(self, *args, **kwargs):
        super(XRBaseView, self).__init__(*args, **kwargs)

        self._scatters = []
        self._roi = None

        self._figure_widget = XRViewer(layers=self._scatters, on_selection=self.on_selection)

        self.create_layout()

    def get_data_layer_artist(self, layer=None, layer_state=None):
        return self.get_layer_artist(self._data_artist_cls, layer=layer, layer_state=layer_state)

    def get_subset_layer_artist(self, layer=None, layer_state=None):
        return self.get_layer_artist(self._subset_artist_cls, layer=layer, layer_state=layer_state)

    def add_scatter(self, layer):
        self._scatters.append(layer)
        self._figure_widget.add_layer(layer)

    def redraw(self):
        self._figure_widget.redraw()

    def apply_roi(self, roi):
        if isinstance(roi, ConvexHullROI) and len(self.layers) > 0:
            x = self.state.x_att
            y = self.state.y_att
            z = self.state.z_att
            subset_state = RoiSubsetState3d(x, y, z, roi)
            cmd = ApplySubsetState(data_collection=self._data, subset_state=subset_state)
            self._session.command_stack.do(cmd)

        self.redraw()

    def on_selection(self, hull_array):
        ar = np.array(hull_array)
        hull_array = ar.reshape((-1, 3))
        # Invert scaling factor to get original coordinates
        hull_array /= self.state.model_scaling_factor

        if self._roi is None:
            self._roi = ConvexHullROI(hull_array)
        else:
            self._roi.update_selection(hull_array)

        self.apply_roi(self._roi)

    @property
    def figure_widget(self):
        return self._figure_widget

    def close(self):
        # self._figure_widget.close()
        self._element = None
