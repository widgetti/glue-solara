import numpy as np
from glue.config import viewer_tool
from glue.viewers.common.tool import CheckableTool

from .roi import ConvexHullROI

__all__: list[str] = []


class XRCheckableTool(CheckableTool):
    def __init__(self, viewer, roi=None):
        self.viewer = viewer

        if roi is not None:
            self.update_from_roi(roi)

    def activate(self):
        self.viewer.on_selection = self.on_selection
        self.viewer.figure_widget.on_selection = self.on_selection
        super().activate()
        # self.viewer.redraw()

    def deactivate(self):
        self.viewer.on_selection = lambda *_ignore: None
        self.viewer.figure_widget.on_selection = lambda *_ignore: None
        super().deactivate()

    def on_selection(self, event_data):
        ar = np.array(event_data)
        ar.reshape((-1, 3))
        self.selection = ar


@viewer_tool
class XRHullSelectionTool(XRCheckableTool):
    icon = "glue_lasso"
    tool_id = "xr:lasso"
    action_text = "Hand selection"
    tool_tip = "Hand select a region of interest"

    selector = "lasso"

    def __init__(self, viewer, roi=None):
        self._roi = None
        super().__init__(viewer, roi)

    def on_selection(self, hull_array):
        if self._roi is None:
            self._roi = ConvexHullROI(hull_array)
        else:
            self._roi.update_selection(hull_array)

        self.viewer.apply_roi(self._roi)
