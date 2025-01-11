from echo import CallbackProperty
from glue_jupyter.common.state3d import Scatter3DViewerState


class XRScatter3DViewerState(Scatter3DViewerState):
    model_scaling_factor = CallbackProperty(docstring="The size of the markers")

    def __init__(self, viewer_state=None, layer=None, **kwargs):
        super().__init__(viewer_state=viewer_state, layer=layer, **kwargs)
        self.model_scaling_factor = 1.0
